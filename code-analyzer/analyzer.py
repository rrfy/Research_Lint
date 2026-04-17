import os
import json
import csv
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "https://github.com/rrfy/Research_Lint",
        "X-Title": "Research Lint Analyzer"
    }
)

PROJECT_DIR = Path("../buggy-shop")
PROMPTS_DIR = Path("prompts")
OUTPUT_DIR  = Path("output")

MODELS = {
    "gemini_flash":  "google/gemini-2.0-flash-001",
    "claude_haiku":  "anthropic/claude-3.5-haiku",
    "deepseek_v3":   "deepseek/deepseek-chat-v3-0324",
    "gemini_pro":    "google/gemini-2.5-pro-exp-03-25",
}

CATEGORIES = ["codestyle", "architecture", "solid", "security"]

FILE_FILTERS = {
    "codestyle":    lambda p: p.suffix == ".py",
    "architecture": lambda p: p.name in [
        "routes.py", "services.py", "models.py", "database.py"
    ],
    "solid":        lambda p: p.suffix == ".py",
    "security":     lambda p: (
        p.suffix in [".py", ".txt"]
        or p.name == "Dockerfile"
        or p.suffix == ".yml"
    ),
}


def load_files(directory: Path, filter_fn) -> dict:
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_file() and filter_fn(path):
            rel = path.relative_to(directory.parent)
            files[str(rel)] = path.read_text(errors="ignore")
    return files


def load_prompt(category: str) -> str:
    return (PROMPTS_DIR / category / "Instructions.md").read_text(encoding="utf-8")


def build_context(files: dict) -> str:
    context = ""
    for filepath, content in files.items():
        context += f"### File: {filepath}\n```python\n{content}\n```\n\n"
    return context


def extract_json(text: str) -> list:
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                text = stripped[4:]
                break
            elif stripped.startswith("["):
                text = stripped
                break
    start = text.find("[")
    end   = text.rfind("]") + 1
    if start == -1 or end == 0:
        return []
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError as e:
        print(f"    [WARN] JSON parse error: {e}")
        return []


def call_agent(context: str, prompt: str, model: str) -> list:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": context}
        ],
        temperature=0
    )
    return extract_json(response.choices[0].message.content)


def parse_lines(lines_raw) -> tuple[int, int]:
    if isinstance(lines_raw, int):
        return lines_raw, lines_raw
    if isinstance(lines_raw, list) and len(lines_raw) == 2:
        return int(lines_raw[0]), int(lines_raw[1])
    if isinstance(lines_raw, str):
        parts = str(lines_raw).replace(" ", "").split(":")
        if len(parts) == 2:
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                pass
        try:
            v = int(parts[0])
            return v, v
        except ValueError:
            return 0, 0
    return 0, 0


def deduplicate(results: list) -> list:
    severity_rank = {"Error": 3, "Warning": 2, "Info": 1}
    seen = {}
    for r in results:
        key = (r["file"], r["line_start"], r["category"])
        if key not in seen:
            seen[key] = r
        else:
            if severity_rank.get(r["severity"], 1) > severity_rank.get(seen[key]["severity"], 1):
                seen[key] = r
    return list(seen.values())


def sort_results(results: list) -> list:
    rank = {"Error": 3, "Warning": 2, "Info": 1}
    return sorted(results, key=lambda r: (
        -rank.get(r["severity"], 1),
         r["file"]
    ))


def normalize(raw_results: list, category: str) -> list:
    normalized = []
    for item in raw_results:
        line_start, line_end = parse_lines(
            item.get("lines", item.get("line", 0))
        )
        normalized.append({
            "file":           item.get("file", "").strip(),
            "line_start":     line_start,
            "line_end":       line_end,
            "category":       category.upper(),
            "description":    item.get("description", "").strip(),
            "severity":       item.get("severity", "Info").strip(),
            "recommendation": item.get("recommendation", item.get("rec", "")).strip()
        })
    return normalized


def write_csv(results: list, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "file", "line_start", "line_end",
            "category", "description", "severity", "recommendation"
        ])
        writer.writeheader()
        writer.writerows(results)


def run_model(model_key: str, model_id: str):
    """Запускает одну модель по всем 4 категориям."""
    print(f"\n{'='*60}")
    print(f"  МОДЕЛЬ: {model_key} ({model_id})")
    print(f"{'='*60}")

    model_dir = OUTPUT_DIR / model_key
    all_results = []

    for category in CATEGORIES:
        print(f"\n  [{category.upper()}] Загружаю файлы...")
        files   = load_files(PROJECT_DIR, FILE_FILTERS[category])
        prompt  = load_prompt(category)
        context = build_context(files)
        print(f"  [{category.upper()}] Файлов: {len(files)} | Запускаю агента...")

        try:
            raw = call_agent(context, prompt, model_id)
        except Exception as e:
            print(f"  [{category.upper()}] Ошибка: {e}")
            continue

        if not raw:
            print(f"  [{category.upper()}] Агент не вернул нарушений")
            continue

        normed   = normalize(raw, category)
        deduped  = deduplicate(normed)
        sorted_r = sort_results(deduped)

        # Сохраняем отдельный CSV для каждой модели и категории
        write_csv(sorted_r, model_dir / f"{category}.csv")
        all_results.extend(sorted_r)

        errors   = sum(1 for r in sorted_r if r["severity"] == "Error")
        warnings = sum(1 for r in sorted_r if r["severity"] == "Warning")
        info     = sum(1 for r in sorted_r if r["severity"] == "Info")
        print(f"  [{category.upper()}] Error: {errors} | Warning: {warnings} | Info: {info} | Итого: {len(sorted_r)}")

    # Сводный CSV по всем категориям для модели
    if all_results:
        write_csv(sort_results(all_results), model_dir / "_all.csv")
        print(f"\n  Сводный отчёт: {model_dir}/_all.csv ({len(all_results)} нарушений)")


def main():
    for model_key, model_id in MODELS.items():
        run_model(model_key, model_id)

    print(f"\n{'='*60}")
    print("Все прогоны завершены. Запустите evaluate.py для метрик.")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()