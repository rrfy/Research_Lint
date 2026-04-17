import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={"HTTP-Referer": "test", "X-Title": "test"}
)

# ← Меняйте эти две строки под нужный тест
MODEL    = "google/gemini-2.0-flash-001"
CATEGORY = "security"

PROJECT_DIR = Path("../buggy-shop")
PROMPT_FILE = Path(f"prompts/{CATEGORY}/Instructions.md")

FILE_FILTERS = {
    "codestyle":    lambda p: p.suffix == ".py",
    "architecture": lambda p: p.name in ["routes.py","services.py","models.py","database.py"],
    "solid":        lambda p: p.suffix == ".py",
    "security":     lambda p: p.suffix in [".py", ".txt"] or p.name == "Dockerfile",
}

# Собираем файлы
files = {
    str(p.relative_to(PROJECT_DIR.parent)): p.read_text(errors="ignore")
    for p in sorted(PROJECT_DIR.rglob("*"))
    if p.is_file() and FILE_FILTERS[CATEGORY](p)
}

context = ""
for path, content in files.items():
    context += f"### File: {path}\n```python\n{content}\n```\n\n"

prompt = PROMPT_FILE.read_text(encoding="utf-8")

print(f"Модель   : {MODEL}")
print(f"Категория: {CATEGORY}")
print(f"Файлов   : {len(files)}")
print("Отправляю запрос...\n")

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": prompt},
        {"role": "user",   "content": context}
    ],
    temperature=0
)

text = response.choices[0].message.content

# Вырезаем JSON
if "```" in text:
    for part in text.split("```"):
        s = part.strip()
        if s.startswith("json"): text = s[4:]; break
        elif s.startswith("["): text = s; break

start, end = text.find("["), text.rfind("]") + 1
results = json.loads(text[start:end]) if start != -1 else []

print(f"Найдено нарушений: {len(results)}\n")
for r in results[:5]:  # показываем первые 5
    print(f"  [{r.get('severity','?')}] {r.get('file','')} : {r.get('lines','')}")
    print(f"    {r.get('description','')}")
    print()

if len(results) > 5:
    print(f"  ... и ещё {len(results) - 5} нарушений")

# Сохраняем сырой ответ для проверки
Path("output").mkdir(exist_ok=True)
Path("output/test_raw.json").write_text(
    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(f"\nПолный ответ сохранён: output/test_raw.json")