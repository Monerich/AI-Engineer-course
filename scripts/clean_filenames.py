#!/usr/bin/env python3
"""
Post-processing script: removes all raw filename references from lesson markdown files.
Run: python3 scripts/clean_filenames.py
"""
import os
import re
import glob

LESSONS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "data", "lessons")

# --- Russian replacements ---
RU_REPLACEMENTS = [
    # Backtick-wrapped filenames
    (r"`prompt_engineering_guide_ru`", "руководство по промпт-инжинирингу"),
    (r"`agent_roadmap_ru`", "карта развития ИИ-Агентов"),
    (r"`ai_builder_ru`", "карта развития ИИ-Инженера"),
    (r"`50_automations_ru`", "руководство по автоматизации"),
    (r"`AI_Money_Hunter_RU`", "руководство по монетизации ИИ"),
    (r"`5_pipelines_ru`", "руководство по конвейерам данных"),
    (r"`ai_trends_ru`", "анализ трендов ИИ"),
    (r"`ai_trends_en`", "анализ трендов ИИ"),
    (r"`карта развития ИИ-Инженера`", "карта развития ИИ-Инженера"),
    (r"`карта развития ИИ-Агентов`", "карта развития ИИ-Агентов"),
    (r"`курс по Harness-инженерии`", "курс по Harness-инженерии"),
    # Plain filenames with/without .pdf
    (r"prompt_engineering_guide_ru(?:\.pdf)?", "руководство по промпт-инжинирингу"),
    (r"agent_roadmap_ru(?:\.pdf)?", "карта развития ИИ-Агентов"),
    (r"ai_builder_ru(?:\.pdf)?", "карта развития ИИ-Инженера"),
    (r"50_automations_ru(?:\.pdf)?", "руководство по автоматизации"),
    (r"AI_Money_Hunter_RU(?:\.pdf)?", "руководство по монетизации ИИ"),
    (r"5_pipelines_ru(?:\.pdf)?", "руководство по конвейерам данных"),
    (r"ai_trends_ru(?:\.pdf)?", "анализ трендов ИИ"),
    (r"ai_trends_en(?:\.pdf)?", "анализ трендов ИИ"),
    # Specific known filenames
    (r"Hermes Agent\s*—\s*сборник кейсов\.md", "разбор кейсов Hermes Agent"),
    (r"Claude_Cowork_Guide_RU(?:\.pdf)?", "корпоративный гайд по Claude"),
    (r"\[Make a Copy\]\s*Anthropic's Prompt Engineering Interactive Tutorial \[PUBLIC ACCESS\]",
     "интерактивный туториал Anthropic по промпт-инжинирингу"),
    (r"Anthropic's Prompt Engineering Interactive Tutorial \[PUBLIC ACCESS\]",
     "интерактивный туториал Anthropic по промпт-инжинирингу"),
    # NotebookLM source patterns like В {filename} подчеркивается / В {filename} говорится
    (r"В\s+`[A-Za-z0-9_\-]+`\s+", "В источниках "),
    (r"В\s+`[A-Za-z0-9_\- ]+`\s+", "В источниках "),
    # Generic .md filenames
    (r"\b[A-Za-z0-9_\-]+\.md\b", ""),
    # Remaining bare .pdf extensions after replacements
    (r"\b([A-Za-z0-9_\-]+)\.pdf\b", r"\1"),
    # Footnote numbers [1], [2,3] etc.
    (r"\[\d+(?:\s*,\s*\d+)*\]", ""),
]

# --- English replacements ---
EN_REPLACEMENTS = [
    # Backtick-wrapped filenames
    (r"`prompt_engineering_guide_ru`", "Prompt Engineering Guide"),
    (r"`agent_roadmap_ru`", "AI Agent roadmap"),
    (r"`ai_builder_ru`", "AI Engineer roadmap"),
    (r"`50_automations_ru`", "automations guide"),
    (r"`AI_Money_Hunter_RU`", "AI monetization guide"),
    (r"`5_pipelines_ru`", "pipelines guide"),
    (r"`ai_trends_ru`", "AI trends analysis"),
    (r"`ai_trends_en`", "AI trends analysis"),
    (r"`AI Engineer roadmap`", "AI Engineer roadmap"),
    (r"`AI Agent roadmap`", "AI Agent roadmap"),
    (r"`Harness Engineering course`", "Harness Engineering course"),
    # Plain filenames with/without .pdf
    (r"prompt_engineering_guide_ru(?:\.pdf)?", "Prompt Engineering Guide"),
    (r"agent_roadmap_ru(?:\.pdf)?", "AI Agent roadmap"),
    (r"ai_builder_ru(?:\.pdf)?", "AI Engineer roadmap"),
    (r"50_automations_ru(?:\.pdf)?", "automations guide"),
    (r"AI_Money_Hunter_RU(?:\.pdf)?", "AI monetization guide"),
    (r"5_pipelines_ru(?:\.pdf)?", "pipelines guide"),
    (r"ai_trends_ru(?:\.pdf)?", "AI trends analysis"),
    (r"ai_trends_en(?:\.pdf)?", "AI trends analysis"),
    # Specific known filenames
    (r"Hermes Agent\s*—\s*.*?\.md", "Hermes Agent case study"),
    (r"Claude_Cowork_Guide_RU(?:\.pdf)?", "Claude enterprise guide"),
    (r"\[Make a Copy\]\s*Anthropic's Prompt Engineering Interactive Tutorial \[PUBLIC ACCESS\]",
     "Anthropic's Prompt Engineering Tutorial"),
    (r"Anthropic's Prompt Engineering Interactive Tutorial \[PUBLIC ACCESS\]",
     "Anthropic's Prompt Engineering Tutorial"),
    # In {filename} says patterns
    (r"In\s+`[A-Za-z0-9_\- ]+`\s+", "According to the sources, "),
    (r"the `AI Engineer roadmap` roadmap", "the AI Engineer roadmap"),
    (r"the `AI Agent roadmap` roadmap", "the AI Agent roadmap"),
    (r"the `AI Agent roadmap`", "the AI Agent roadmap"),
    (r"the `AI Engineer roadmap`", "the AI Engineer roadmap"),
    # Generic .md filenames
    (r"\b[A-Za-z0-9_\-]+\.md\b", ""),
    # Remaining bare .pdf
    (r"\b([A-Za-z0-9_\-]+)\.pdf\b", r"\1"),
    # Footnote numbers
    (r"\[\d+(?:\s*,\s*\d+)*\]", ""),
]


def clean_file(filepath: str, lang: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    replacements = RU_REPLACEMENTS if lang == "ru" else EN_REPLACEMENTS

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    # Clean up any double spaces introduced
    content = re.sub(r"  +", " ", content)
    # Remove spaces before punctuation
    content = re.sub(r" +([.,!?;:])", r"\1", content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return 1
    return 0


def main():
    changed = 0
    total = 0
    for lang in ["ru", "en"]:
        lang_dir = os.path.join(LESSONS_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue
        for filepath in glob.glob(os.path.join(lang_dir, "**", "*.md"), recursive=True):
            total += 1
            changed += clean_file(filepath, lang)
            print(f"  Processed [{lang}]: {os.path.basename(filepath)} (in {os.path.basename(os.path.dirname(filepath))})")

    print(f"\n✓ Done. {changed}/{total} files updated.")


if __name__ == "__main__":
    main()
