"""
Выводит сравнительную таблицу метрик по формулам (14)-(19) раздела 2.7.
Строки — модели, столбцы — категории + среднее F̄₁.
"""
import csv
from pathlib import Path

REF_FILE   = Path("../buggy_shop_defects.csv")
OUTPUT_DIR = Path("output")

MODELS = ["gemini_flash", "claude_haiku", "deepseek_v3", "gemini_pro"]

CATEGORY_PREFIXES = {
    "codestyle":    ["STYLE", "STRUCT", "CodeStyle"],
    "architecture": ["ARCH"],
    "solid":        ["SOLID"],
    "security":     ["OWASP"],
}

SEVERITY_NORM = {
    "error": "Error", "warning": "Warning", "info": "Info",
    "Error ": "Error", "Warning ": "Warning", "Info ": "Info",
}


def norm_sev(s: str) -> str:
    s = s.strip()
    return SEVERITY_NORM.get(s, s.split()[0] if s else "Info")


def load_ref(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            line_raw = row.get("Line Number", "0").strip().split(":")[0].replace("-", "0")
            try:
                line_start = int(line_raw) if line_raw else 0
            except ValueError:
                line_start = 0
            rows.append({
                "file":       row.get("File Path", "").strip(),
                "line_start": line_start,
                "category":   row.get("Category", "").strip(),
                "severity":   norm_sev(row.get("Description", "Info"))
            })
    return rows


def load_output(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                ls = int(row.get("line_start", 0))
            except ValueError:
                ls = 0
            rows.append({
                "file":       row.get("file", "").strip(),
                "line_start": ls,
                "category":   row.get("category", "").strip(),
                "severity":   norm_sev(row.get("severity", "Info"))
            })
    return rows


def filter_ref(ref: list[dict], prefixes: list[str]) -> list[dict]:
    return [r for r in ref if any(r["category"].startswith(p) for p in prefixes)]


def metrics(predicted: list[dict], reference: list[dict]) -> dict:
    ref_keys  = {(r["file"], r["line_start"]) for r in reference}
    pred_keys = {(r["file"], r["line_start"]) for r in predicted}

    tp = len(ref_keys & pred_keys)
    fp = len(pred_keys - ref_keys)
    fn = len(ref_keys - pred_keys)

    p  = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    pred_map = {(r["file"], r["line_start"]): r for r in predicted}
    ref_map  = {(r["file"], r["line_start"]): r for r in reference}
    correct  = sum(
        1 for k in ref_keys & pred_keys
        if pred_map[k]["severity"] == ref_map[k]["severity"]
    )
    acc_s = correct / tp if tp > 0 else 0.0

    return {
        "P":  round(p,  3),
        "R":  round(r,  3),
        "F1": round(f1, 3),
        "Acc_s": round(acc_s, 3)
    }


def main():
    ref_all = load_ref(REF_FILE)

    # Шапка таблицы
    cats = list(CATEGORY_PREFIXES.keys())
    header = f"{'Модель':<16}" + "".join(f"{c.upper():>14}" for c in cats) + f"{'F̄₁':>8}  {'Ācc_s':>8}"
    print(header)
    print("-" * len(header))

    for model_key in MODELS:
        row_f1   = []
        row_accs = []
        cells    = ""

        for category, prefixes in CATEGORY_PREFIXES.items():
            ref_cat   = filter_ref(ref_all, prefixes)
            predicted = load_output(OUTPUT_DIR / model_key / f"{category}.csv")
            m         = metrics(predicted, ref_cat)
            row_f1.append(m["F1"])
            row_accs.append(m["Acc_s"])
            cells += f"  F1={m['F1']:.2f}  "

        f1_avg   = round(sum(row_f1) / len(row_f1), 3)
        accs_avg = round(sum(row_accs) / len(row_accs), 3)
        print(f"{model_key:<16}{cells}  {f1_avg:.3f}    {accs_avg:.3f}")

    print()

    # Детальный вывод для лучшей модели
    print("Детализация по лучшей модели:")
    for model_key in MODELS:
        f1_vals = []
        for category, prefixes in CATEGORY_PREFIXES.items():
            ref_cat   = filter_ref(ref_all, prefixes)
            predicted = load_output(OUTPUT_DIR / model_key / f"{category}.csv")
            m         = metrics(predicted, ref_cat)
            f1_vals.append(m["F1"])
        avg = sum(f1_vals) / len(f1_vals)
        print(f"  {model_key}: F̄₁ = {avg:.3f}")


if __name__ == "__main__":
    main()