from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import torch

# Укажите правильные пути!
ADAPTER_PATH = "./final_adapter"  # <-- сюда пишем путь к папке вашего адаптера
MERGED_MODEL_PATH = "./merged_model" # <-- путь для сохранения объединённой модели

# 1. Загружаем адаптер
model = AutoPeftModelForCausalLM.from_pretrained(
    ADAPTER_PATH,
    torch_dtype=torch.bfloat16,  # используем bfloat16
    device_map="auto"
)

# 2. Сливаем его с базовой моделью и сохраняем
# Этот метод загружает базовую модель и "пришивает" к ней обученные веса LoRA
merged_model = model.merge_and_unload()
tokenizer = AutoTokenizer.from_pretrained(ADAPTER_PATH)

merged_model.save_pretrained(MERGED_MODEL_PATH)
tokenizer.save_pretrained(MERGED_MODEL_PATH)
print(f"Объединённая модель сохранена по адресу: {MERGED_MODEL_PATH}")