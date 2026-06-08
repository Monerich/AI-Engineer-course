#!/usr/bin/env python3
"""
normalize_lectures.py — БЕЗОПАСНАЯ нормализация заголовков в lecture.md.

Подход: только строчные замены, никакого перестраивания файла.
Правила:
1. Первый заголовок недели → # Неделя N: <Название>
2. Повторяющиеся заголовки недели (# Неделя N...) → удаляются
3. Заголовки блоков (# Глава N:, ## Глава N:, # Неделя N, Глава N:,
   ## 9. Блок 9..., ## Block N (...):, etc.) → ## Блок N: <Тема из curriculum>
4. Одиночные # заголовки внутри тела (не блок-маркеры, не внутри кода) → ###
5. Контент не удаляется и не перемещается
"""

import os
import re
import glob
import sys

LESSONS_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "data", "lessons")


def get_curriculum():
    sys.path.insert(0, os.path.dirname(__file__))
    import generate_lessons as gl
    return gl.WEEKLY_BLOCKS


def block_topic(blocks: list[str], n: int) -> str:
    if n < 1 or n > len(blocks):
        return ''
    defn = blocks[n - 1]
    defn = re.sub(r'^(?:Блок|Block)\s+\d+\s*\([^)]*\):\s*', '', defn, flags=re.IGNORECASE)
    return defn.strip()


def normalize_lecture(filepath: str, week_num: int, lang: str,
                      week_title_ru: str, week_title_en: str,
                      blocks_ru: list[str], blocks_en: list[str]) -> bool:
    with open(filepath, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    blocks = blocks_ru if lang == 'ru' else blocks_en
    week_title = week_title_ru if lang == 'ru' else week_title_en

    # Pattern: matches block-marker headings (lines that identify a specific block)
    # These are H1/H2/H3 headings containing Глава N / Chapter N / Блок N / Block N
    if lang == 'ru':
        block_marker_re = re.compile(
            r'^(#{1,3})\s+'
            r'(?:'
            r'(?:Неделя\s+\d+[,\.]\s*)?'        # optional "Неделя N, "
            r'(?:Глава|Chapter)\s+(\d+)'          # "Глава N" or "Chapter N"
            r'|'
            r'(?:\d+\.\s+)?(?:Блок|Block)\s+(\d+)'  # "9. Блок 9" or "Блок 9"
            r')'
            r'[:\s–—].*$',
            re.IGNORECASE
        )
        week_title_re = re.compile(
            r'^#\s+(?:Неделя|Лекция)\s+\d+[\.,:\s]',
            re.IGNORECASE
        )
    else:
        block_marker_re = re.compile(
            r'^(#{1,3})\s+'
            r'(?:'
            r'Chapter\s+(\d+)'               # "Chapter N"
            r'|'
            r'(?:\d+\.\s+)?(?:Block)\s+(\d+)'  # "Block N" or "9. Block 9"
            r')'
            r'[:\s–—(].*$',
            re.IGNORECASE
        )
        week_title_re = re.compile(
            r'^#\s+(?:Week|Lecture|Лекция)\s+\d+[\.,:\s]',
            re.IGNORECASE
        )

    in_code = False
    fence_char = None
    new_lines = []
    week_header_written = False
    seen_block_nums: set[int] = set()

    for raw_line in original_lines:
        line = raw_line.rstrip('\n')
        stripped = line.strip()

        # ── Track code fences ──────────────────────────────────────────────
        m_fence = re.match(r'^(`{3,}|~{3,})', stripped)
        if m_fence:
            ch = m_fence.group(1)[0]
            if not in_code:
                in_code = True
                fence_char = ch
            elif ch == fence_char:
                in_code = False
                fence_char = None
            new_lines.append(line)
            continue

        # ── Inside code block: never touch ────────────────────────────────
        if in_code:
            new_lines.append(line)
            continue

        # ── H1 week-title line ─────────────────────────────────────────────
        if week_title_re.match(stripped):
            if not week_header_written:
                # First occurrence: replace with canonical H1
                if lang == 'ru':
                    new_lines.append(f'# Неделя {week_num}: {week_title}')
                else:
                    new_lines.append(f'# Week {week_num}: {week_title}')
                week_header_written = True
            else:
                # Subsequent occurrences: delete (skip empty line after if next is blank)
                # we simply skip this line
                pass
            continue

        # ── Block marker heading ───────────────────────────────────────────
        bm = block_marker_re.match(stripped)
        if bm:
            # Extract block number from whichever group matched
            num = None
            for g in bm.groups()[1:]:
                if g is not None:
                    try:
                        num = int(g)
                        break
                    except (ValueError, TypeError):
                        pass

            if num is not None and 1 <= num <= len(blocks):
                # Only emit canonical heading once per block number
                topic = block_topic(blocks, num)
                if lang == 'ru':
                    canonical = f'## Блок {num}: {topic}'
                else:
                    canonical = f'## Block {num}: {topic}'

                if num not in seen_block_nums:
                    new_lines.append(canonical)
                    seen_block_nums.add(num)
                # else: duplicate block heading — skip it
            else:
                # Unknown block number — demote to ###
                new_lines.append(re.sub(r'^#{1,6}\s+', '### ', stripped))
            continue

        # ── Stray H1 (not week title, not block marker) ───────────────────
        if re.match(r'^# [^#]', stripped) and stripped.startswith('#'):
            # Only demote if it really looks like a section header, not code
            # (code-fence tracking above should have caught code blocks)
            new_lines.append('### ' + stripped[2:])
            continue

        # ── Everything else: pass through unchanged ────────────────────────
        new_lines.append(line)

    # If we never saw the week H1 (file starts differently), prepend it
    if not week_header_written:
        if lang == 'ru':
            new_lines.insert(0, f'# Неделя {week_num}: {week_title}')
        else:
            new_lines.insert(0, f'# Week {week_num}: {week_title}')
        new_lines.insert(1, '')

    # Remove consecutive blank lines (max 1)
    cleaned = []
    prev_blank = False
    for line in new_lines:
        is_blank = line.strip() == ''
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank

    new_content = '\n'.join(cleaned)
    original_content = ''.join(original_lines)

    if new_content.rstrip() == original_content.rstrip():
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content + '\n')
    return True


def main():
    curriculum = get_curriculum()
    changed = 0
    total = 0

    for lang in ['ru', 'en']:
        lang_dir = os.path.join(LESSONS_DIR, lang)
        if not os.path.isdir(lang_dir):
            continue

        for week_dir in sorted(glob.glob(os.path.join(lang_dir, 'week-*'))):
            lecture_file = os.path.join(week_dir, 'lecture.md')
            if not os.path.isfile(lecture_file):
                continue

            basename = os.path.basename(week_dir)
            try:
                week_num = int(basename.replace('week-', ''))
            except ValueError:
                continue

            week_data = curriculum.get(week_num)
            if not week_data:
                print(f'  [SKIP] No curriculum data for {basename}')
                continue

            total += 1
            did_change = normalize_lecture(
                filepath=lecture_file,
                week_num=week_num,
                lang=lang,
                week_title_ru=week_data['title_ru'],
                week_title_en=week_data['title_en'],
                blocks_ru=week_data['ru'],
                blocks_en=week_data['en'],
            )
            status = '✓ Updated' if did_change else '· No change'
            if did_change:
                changed += 1
            print(f'  {status} [{lang}] {basename}/lecture.md')

    print(f'\n✓ Done. {changed}/{total} lecture files normalized.')


if __name__ == '__main__':
    main()
