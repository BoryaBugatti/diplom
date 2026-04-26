import io
import json
import torch
import asyncio
import pandas as pd
from docx import Document
import pdfplumber
from fastapi import UploadFile, File, HTTPException, Request, APIRouter
from pydantic import BaseModel
from typing import Dict, Any


MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

async def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(400, "Файл пуст")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"Файл слишком большой (макс. {MAX_FILE_SIZE // (1024*1024)} МБ)")
    
    try:
        if filename.endswith('.pdf'):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
        elif filename.endswith('.xls'):
            df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
        elif filename.endswith('.docx'):
            doc = Document(io.BytesIO(content))
            text = '\n'.join(paragraph.text for paragraph in doc.paragraphs)
        elif filename.endswith('.json'):
            data = json.loads(content.decode('utf-8'))
            text = json.dumps(data, ensure_ascii=False, indent=2)
        elif filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(400, f"Неподдерживаемый формат файла: {filename}")
        
        if not text or not text.strip():
            raise HTTPException(400, "Не удалось извлечь текст из файла")
        return text.strip()
    except Exception as e:
        raise HTTPException(500, f"Ошибка при извлечении текста: {str(e)}")

async def generate_response(model, tokenizer, prompt: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "Ты — эксперт по анализу закупочной документации. "
                "Твоя задача — извлечь из приведённого текста все требования к участникам и условиям закупки, "
                "а затем выделить из них ключевые (наиболее важные для допуска и победы). "
                "Ответ представь в формате JSON с полями 'TenderSummary', 'all_requirements', 'key_requirements'. "
                "Всегда отвечай ТОЛЬКО валидным JSON. Никаких пояснений до или после JSON. "
                "Не используй markdown, не добавляй лишние пробелы и переносы строк внутри JSON."
            )
        },
        {
            "role": "user",
            "content": (
                "Извлеки из следующего тендера:\n"
                "- TenderSummary (строка, краткая сводка: заказчик, предмет, НМЦ, сроки, обеспечение)\n"
                "- all_requirements (массив строк, полный список всех требований и условий, извлечённых из документации)\n"
                "- key_requirements (массив строк, 5-10 наиболее критичных требований для допуска и победы)\n\n"
                "Верни ТОЛЬКО JSON в точном формате, как в примере ниже. Не добавляй ничего лишнего.\n"
                "Пример:\n"
                "{\n"
                "  \"TenderSummary\": \"Заказчик: ФБУЗ «Центр гигиены и эпидемиологии в Воронежской области». Предмет: поставка химических реактивов. НМЦ: 911 291,26 руб. Срок поставки: 60 календарных дней. Обеспечение: не установлено.\",\n"
                "  \"all_requirements\": [\n"
                "    \"Закупка проводится по 223-ФЗ на ЭТП com.roseltorg.ru\",\n"
                "    \"Участник должен быть аккредитован на электронной площадке\",\n"
                "    \"Заявка подаётся в форме двух электронных документов, подписанных УКЭП\",\n"
                "    \"Первая часть заявки должна содержать согласие на поставку и конкретные показатели товара\",\n"
                "    \"Вторая часть заявки должна содержать выписку из ЕГРЮЛ, решение об одобрении крупной сделки, декларацию о соответствии\",\n"
                "    \"Участник не должен находиться в реестре недобросовестных поставщиков (223-ФЗ и 44-ФЗ)\",\n"
                "    \"Установлено ограничение закупок иностранных товаров в соответствии с ПП №1875\"\n"
                "  ],\n"
                "  \"key_requirements\": [\n"
                "    \"Наличие в первой части заявки конкретных показателей товара без слов «или эквивалент»\",\n"
                "    \"Обязательное декларирование страны происхождения товара\",\n"
                "    \"Отсутствие в РНП по 223-ФЗ и 44-ФЗ\",\n"
                "    \"Предоставление выписки из ЕГРЮЛ не старше 1 месяца\",\n"
                "    \"Применение национального режима – преимущество российским товарам\"\n"
                "  ]\n"
                "}\n\n"
                f"Текст тендера:\n{prompt}"
            )
        }
    ]
    
    text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    def _generate():
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        # Установка pad_token_id, если он не задан
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token_id = tokenizer.eos_token_id
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.1,         # низкая температура для детерминированности
                do_sample=True,          # оставляем True с низкой температурой для небольшой вариативности
                top_p=0.95,
                repetition_penalty=1.05,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.pad_token_id,
            )
        # Декодируем только новые токены (без входного промпта)
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        return response
    
    response = await asyncio.to_thread(_generate)
    
    # Попытка извлечь JSON из ответа (на случай, если модель добавила лишний текст)
    try:
        # Ищем JSON, начиная с первой фигурной скобки
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Проверяем валидность JSON
            json.loads(json_str)
            return json_str
        else:
            # Если не нашли JSON, возвращаем ответ как есть (может быть ошибка)
            return response
    except json.JSONDecodeError:
        # Если невалидный JSON, возвращаем сырой ответ для отладки
        return response

class TenderAnalysisResponse(BaseModel):
    status: str
    extracted_text_preview: str
    key_requirements: Dict[str, Any]

router = APIRouter(prefix="/TenderAnalysis")

@router.post("", response_model=TenderAnalysisResponse)
async def analyze_tender(
    request: Request,
    file: UploadFile = File(...)
):
    try:
        extracted_text = await extract_text_from_file(file)
        
        model = request.app.state.model
        tokenizer = request.app.state.tokenizer
        
        model_response = await generate_response(model, tokenizer, extracted_text)
        
        try:
            import json
            json_start = model_response.find('{')
            json_end = model_response.rfind('}') + 1
            if json_start != -1 and json_end != 0:
                key_requirements = json.loads(model_response[json_start:json_end])
            else:
                key_requirements = {"raw_response": model_response}
        except:
            key_requirements = {"error": "Failed to parse model response", "raw_response": model_response}
        
        return TenderAnalysisResponse(
            status="success",
            extracted_text_preview=extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            key_requirements=key_requirements
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")