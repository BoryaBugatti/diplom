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
    {"role": "system", "content": "Ты — ассистент для анализа тендерной документации. Извлеки ключевые требования и верни ТОЛЬКО валидный JSON. Не добавляй пояснений."},
    {"role": "user", "content": f"Проанализируй текст и верни JSON с полями: deadline, requirements, budget, contacts, description, additional_conditions. Текст:\n\n{prompt}"}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    def _generate():
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
        return tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    return await asyncio.to_thread(_generate)

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