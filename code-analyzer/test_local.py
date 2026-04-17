"""Проверяет что файлы, промпты и контекст собираются корректно."""
from pathlib import Path

PROJECT_DIR = Path("../buggy-shop")
PROMPTS_DIR = Path("prompts")

FILE_FILTERS = {
    "codestyle":    lambda p: p.suffix == ".py",
    "architecture": lambda p: p.name in ["routes.py","services.py","models.py","database.py"],
    "solid":        lambda p: p.suffix == ".py",
    "security":     lambda p: p.suffix in [".py", ".txt"] or p.name == "Dockerfile",
}

for category, fn in FILE_FILTERS.items():
    files = [p for p in PROJECT_DIR.rglob("*") if p.is_file() and fn(p)]
    prompt_path = PROMPTS_DIR / category / "Instructions.md"
    print(f"[{category.upper()}]")
    print(f"  Файлов: {len(files)}")
    for f in files:
        print(f"    {f.relative_to(PROJECT_DIR.parent)}")
    print(f"  Промпт: {'OK' if prompt_path.exists() else 'НЕТ ФАЙЛА — ' + str(prompt_path)}")
    print()