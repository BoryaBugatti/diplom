import io
import json
import re
from difflib import SequenceMatcher
from typing import List, Dict, Any

import httpx
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.dbconfig import SessionLocal
from crud.analysis_crud import save_analysis_result

from auth.dependencies import get_current_user
from Models.models import User

LLAMA_API_URL = "http://localhost:8080" 
LLAMA_COMPLETION_ENDPOINT = f"{LLAMA_API_URL}/completion"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 МБ

MAX_CHUNK_CHARS = 20000
OVERLAP_CHARS = 500

MAX_SUMMARY_CHARS = 4000

MAX_REQUIREMENTS_FOR_KEY_EXTRACTION = 50


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()


async def extract_text_from_file(file: UploadFile) -> str:
    """Извлекает текст из загруженного файла (поддерживает PDF, DOCX, XLSX, JSON, TXT)."""
    filename = file.filename.lower()
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(400, "Файл пуст")
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, f"Файл слишком большой (макс. {MAX_FILE_SIZE // (1024*1024)} МБ)")

    try:
        if filename.endswith('.pdf'):
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        elif filename.endswith('.xlsx'):
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content), engine='openpyxl')
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
        elif filename.endswith('.xls'):
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            text = df.astype(str).apply(lambda x: ' '.join(x), axis=1).str.cat(sep='\n')
        elif filename.endswith('.docx'):
            from docx import Document
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


# ---------------------------------------------------------------
# Функции для работы с llama.cpp API
# ---------------------------------------------------------------
async def ask_llama(
    prompt: str,
    max_tokens: int = 1500,          # осторожное значение для контекста 8192
    temperature: float = 0.1,
    top_p: float = 0.9,
    repeat_penalty: float = 1.15,
    stop: List[str] = None
) -> str:
    """Отправляет запрос к эндпоинту /completion и возвращает сгенерированный текст."""
    payload = {
        "prompt": prompt,
        "n_predict": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "repeat_penalty": repeat_penalty,
        "stop": stop or [],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(LLAMA_COMPLETION_ENDPOINT, json=payload)
        if resp.status_code != 200:
            raise HTTPException(500, f"Ошибка llama.cpp: {resp.text}")
        data = resp.json()
        return data.get("content", "").strip()


# ---------------------------------------------------------------
# Разбиение текста на чанки по символам
# ---------------------------------------------------------------
def chunk_text_by_chars(text: str, max_chunk_size: int = MAX_CHUNK_CHARS, overlap: int = OVERLAP_CHARS) -> List[str]:
    """Разбивает текст на чанки заданного размера (в символах) с перекрытием."""
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + max_chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap
    return chunks


# ---------------------------------------------------------------
# Промпты и функции извлечения требований через API
# ---------------------------------------------------------------
async def extract_tender_summary(text: str) -> Dict[str, str]:
    """Извлекает название и краткое описание тендера (использует только начало документа)."""
    system = (
        "Ты — эксперт по анализу закупочной документации. "
        "Извлеки полное официальное название тендера и его краткое описание (одно-два предложения). "
        "Верни строго JSON с ключами \"name\" и \"description\". Если название не найдено, верни пустую строку."
    )
    short_text = text[:MAX_SUMMARY_CHARS]
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\nПроанализируй начало документа:\n{short_text}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    response = await ask_llama(prompt, max_tokens=300, temperature=0.1)
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return {
                "name": data.get("name", "").strip(),
                "description": data.get("description", "").strip()
            }
    except Exception:
        print("Ошибка извлечения summary тендера, возвращены пустые значения.")
    return {"name": "", "description": ""}


async def extract_requirements_from_chunk(chunk_text: str) -> List[str]:
    """Извлекает все требования из одного чанка."""
    system = (
        "Ты — эксперт по анализу закупочной документации. "
        "Извлеки все требования к участникам и условиям закупки из данного фрагмента документа. "
        "Ответ должен быть строго в формате JSON с ключом \"all_requirements\" (массив строк)."
    )
    print(f"[DEBUG] Обработка чанка размером {len(chunk_text)} символов (≈{len(chunk_text)//4} токенов)")
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\nПроанализируй фрагмент:\n{chunk_text}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    response = await ask_llama(prompt, max_tokens=2000, temperature=0.1)
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("all_requirements", [])
    except Exception:
        print("Ошибка парсинга требований из чанка")
    return []


async def extract_key_requirements(all_requirements: List[str]) -> List[str]:
    """Выделяет ключевые требования из полного списка (ограничивает количество элементов)."""
    if not all_requirements:
        return []
    
    if len(all_requirements) > MAX_REQUIREMENTS_FOR_KEY_EXTRACTION:
        print(f"[INFO] Сокращаем список требований с {len(all_requirements)} до {MAX_REQUIREMENTS_FOR_KEY_EXTRACTION}")
        all_requirements = all_requirements[:MAX_REQUIREMENTS_FOR_KEY_EXTRACTION]
    
    system = (
        "Ты — эксперт по закупкам. Из приведённого списка требований выбери наиболее важные (ключевые), "
        "которые критичны для допуска к закупке или влияют на победу. "
        "Ответ должен быть строго в формате JSON с ключом \"key_requirements\" (массив строк)."
    )
    req_list = json.dumps(all_requirements, ensure_ascii=False, indent=2)
    if len(req_list) > 8000:
        req_list = json.dumps(all_requirements[:30], ensure_ascii=False, indent=2)
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\nСписок требований:\n{req_list}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    response = await ask_llama(prompt, max_tokens=1500, temperature=0.1)
    try:
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("key_requirements", [])
    except Exception:
        print("Ошибка извлечения ключевых требований")
    return []


def deduplicate_requirements(requirements: List[str], threshold: float = 0.85) -> List[str]:
    """Убирает дубликаты по коэффициенту схожести."""
    unique = []
    for req in requirements:
        if not any(SequenceMatcher(None, req, u).ratio() > threshold for u in unique):
            unique.append(req)
    return unique


async def analyze_document(text: str) -> Dict[str, Any]:
    """Полный пайплайн обработки документа через HTTP API llama.cpp."""
    tender_summary = await extract_tender_summary(text)
    chunks = chunk_text_by_chars(text)
    all_reqs = []
    for chunk in chunks:
        reqs = await extract_requirements_from_chunk(chunk)
        all_reqs.extend(reqs)
    all_reqs = deduplicate_requirements(all_reqs)
    key_reqs = await extract_key_requirements(all_reqs)
    return {
        "tender_summary": tender_summary,
        "all_requirements": all_reqs,
        "key_requirements": key_reqs,
    }


# ---------------------------------------------------------------
# Модели ответа
# ---------------------------------------------------------------
class TenderSummary(BaseModel):
    name: str
    description: str


class TenderAnalysisResponse(BaseModel):
    status: str
    extracted_text_preview: str
    tender_summary: TenderSummary
    all_requirements: List[str]
    key_requirements: List[str]


# ---------------------------------------------------------------
# Роутер
# ---------------------------------------------------------------
router = APIRouter(prefix="/TenderAnalysis", tags=["Tender Analysis"])


@router.post("", response_model=TenderAnalysisResponse)
async def analyze_tender(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        extracted_text = await extract_text_from_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")

    try:
        result = await analyze_document(extracted_text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Ошибка анализа через LLM: {str(e)}")

    try:
        save_analysis_result(
            db=db,
            user_id=current_user.user_id,  
            file_name=file.filename,
            tender_name=result["tender_summary"]["name"],
            tender_description=result["tender_summary"]["description"],
            all_requirements=result["all_requirements"],
            key_requirements=result["key_requirements"]
        )
    except Exception as e:
        print(f"[WARN] Не удалось сохранить результат: {e}")

    preview = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text

    return TenderAnalysisResponse(
        status="success",
        extracted_text_preview=preview,
        tender_summary=TenderSummary(**result["tender_summary"]),
        all_requirements=result["all_requirements"],
        key_requirements=result["key_requirements"],
    )