#!/usr/bin/env python3
import os
import sys

# Ensure nlm is in PATH
os.environ["PATH"] = "/Users/andreizelenov/.local/bin:" + os.environ.get("PATH", "")

import json
import time
import subprocess
import argparse
from typing import Dict, List, Any, Optional


NOTEBOOK_ID = "5a520c9c-d47f-4354-95b1-8d208079f55d"

# Detailed curriculum configuration for weeks that require materials
WEEKS_CONFIG = {
    1: {
        "title_ru": "Ландшафт AI и основы веб-технологий",
        "title_en": "AI Landscape and Web Tech Foundations",
        "focus_ru": "доходчивая база по HTML, JSON, XML, RSS, разным статусам, реквестам, респонсам, Webhooks, основам Python",
        "focus_en": "clear foundations of HTML, JSON, XML, RSS, HTTP statuses, requests, responses, Webhooks, and Python basics"
    },
    2: {
        "title_ru": "Контекст-инжиниринг и современные методы промптинга",
        "title_en": "Context Engineering and Modern Prompting Methods",
        "focus_ru": "Контекст-инжиниринг и современные методы промптинга, фреймворки System Prompts, Few-shot, Chain of Thought, ReAct",
        "focus_en": "Context engineering, modern prompting methods, frameworks for System Prompts, Few-shot, Chain of Thought, and ReAct patterns"
    },
    3: {
        "title_ru": "Основы n8n и первый рабочий процесс",
        "title_en": "n8n Foundations and Your First Workflow",
        "focus_ru": "Основы n8n, интерфейс платформы, переменные, синтаксис выражений, ноды ветвления IF, Switch и Merge",
        "focus_en": "n8n foundations, platform interface, variables, expression syntax, and branching nodes (IF, Switch, Merge)"
    },
    4: {
        "title_ru": "Кейс-проект: Сборщик лидов и Telegram-фильтр",
        "title_en": "Case Study: Lead Scraper and Telegram Filter",
        "focus_ru": "Кейс-проект в n8n: сборщик лидов из писем и умный Telegram-фильтр с использованием LLM",
        "focus_en": "n8n case study: lead scraping from emails and smart Telegram message filtering using LLMs"
    },
    5: {
        "title_ru": "Продвинутый n8n: Подпроцессы и массивы данных",
        "title_en": "Advanced n8n: Sub-workflows and Data Arrays",
        "focus_ru": "Item Lists, циклы и итерации в n8n, нода Code (JS/Python), Execute Workflow нода для вызова подпроцессов",
        "focus_en": "Item Lists, loops and iterations in n8n, Code Node (JS/Python), Execute Workflow node for sub-workflows"
    },
    6: {
        "title_ru": "ИИ-ноды n8n и интеграция с LangChain",
        "title_en": "n8n AI Nodes and LangChain Integration",
        "focus_ru": "Архитектура AI-нод в n8n, Advanced AI Agent нода, подключение инструментов (Tools), Window Buffer Memory и сплиттеры текста",
        "focus_en": "n8n AI Nodes architecture, Advanced AI Agent node, tool attachments, Window Buffer Memory, and text splitters"
    },
    7: {
        "title_ru": "Векторные базы данных и RAG в автоматизациях",
        "title_en": "Vector Databases and RAG in Automations",
        "focus_ru": "Семантический поиск, эмбеддинги, Pinecone, Supabase с pgvector, загрузка документов в векторную БД, Retriever нода в n8n",
        "focus_en": "Semantic search, embeddings, Pinecone, Supabase with pgvector, document uploading, Retriever node in n8n"
    },
    8: {
        "title_ru": "Кейс-проект: Автопилот лидогенерации и холодного аутрича",
        "title_en": "Case Study: Lead Gen and Cold Outreach Autopilot",
        "focus_ru": "Скрейперы Apollo и Clay, ИИ-персонализация на основе LinkedIn, интеграция с Instantly/Smartlead, CRM воронки",
        "focus_en": "Apollo and Clay scrapers, AI personalization using LinkedIn, Instantly/Smartlead integration, CRM pipelines"
    },
     9: {
        "title_ru": "Python для AI-разработчиков: Развитые скрипты",
        "title_en": "Python for AI Engineers: Advanced Scripting",
        "focus_ru": "Playwright и BeautifulSoup для скрейпинга динамических сайтов, извлечение структурированных JSON-данных, работа с cookies, заголовками и User-Agents, асинхронный asyncio и семафоры",
        "focus_en": "Playwright and BeautifulSoup for scraping dynamic sites, extracting structured JSON data, handling cookies, headers, and User-Agents, asynchronous asyncio and semaphores"
    },
    10: {
        "title_ru": "OpenAI & Anthropic SDK: Structured Outputs",
        "title_en": "OpenAI & Anthropic SDKs: Structured Outputs",
        "focus_ru": "Проектирование REST JSON-схем, валидация вложенных структур данных через Pydantic, обработка сетевых ошибок, rate limits и OpenAI/Anthropic SDKs",
        "focus_en": "Designing REST JSON schemas, structured data validation via Pydantic, handling API exceptions, rate limits, and OpenAI/Anthropic SDKs"
    },
    11: {
        "title_ru": "Функции (Tools) и первый агентный цикл на Python",
        "title_en": "Tools and Your First Python Agentic Loop",
        "focus_ru": "Function calling на уровне API, JSON-схемы инструментов, написание ReAct цикла с нуля на Python, обработка tool_calls",
        "focus_en": "Function calling at API level, tool JSON schemas, writing ReAct loops from scratch in Python, handling tool_calls"
    },
    12: {
        "title_ru": "Кейс-проект: Локальный CLI Агент с инструментами",
        "title_en": "Local CLI Agent with Tools",
        "focus_ru": "структурирование CLI интерфейса для AI-инструментов, выполнение цикла агента в терминале, парсинг ввода, локальный вызов инструментов",
        "focus_en": "structuring CLI interfaces for AI tools, handling agent execution loop in terminal, parsing user input, local tool execution"
    },
    13: {
        "title_ru": "Введение в мультиагентные системы: CrewAI",
        "title_en": "Introduction to Multi-Agent Systems: CrewAI",
        "focus_ru": "проектирование конфигураций Crew, задачи агентов, входные данные, делегирование, последовательная и иерархическая оркестрация",
        "focus_en": "designing crew configurations, agent tasks, inputs, crew delegation, sequential vs hierarchical orchestration"
    },
    14: {
        "title_ru": "Продвинутые команды и кастомные инструменты в CrewAI",
        "title_en": "Advanced Commands and Custom Tools in CrewAI",
        "focus_ru": "кастомные инструменты в CrewAI, файловые операции, поиск в сети, кастомные задачи, оркестрация агентов со сложными входами",
        "focus_en": "custom tools in CrewAI, file operations, web search, custom tasks, orchestrating crew agents with complex inputs"
    },
    15: {
        "title_ru": "Введение в граф-ориентированные потоки: LangGraph Foundations",
        "title_en": "Introduction to Graph-Based Flows: LangGraph Foundations",
        "focus_ru": "Граф-ориентированное программирование, StateGraph, Nodes, Edges, State management, компиляция графов и визуализация",
        "focus_en": "Graph-based programming, StateGraph, Nodes, Edges, State management, compiling and visualizing graphs"
    },
    16: {
        "title_ru": "Долгосрочная память и Человек в контуре в LangGraph",
        "title_en": "Long-Term Memory and Human-in-the-Loop in LangGraph",
        "focus_ru": "персистентность в LangGraph, память состояния, прерывания Human-in-the-loop, чекпоинты, редактирование состояния и возобновление",
        "focus_en": "persistence in LangGraph, state memory, human-in-the-loop interrupts, checkpointing, editing state and resuming"
    },
    17: {
        "title_ru": "Продвинутый RAG для продакшна",
        "title_en": "Advanced RAG for Production",
        "focus_ru": "трансляция и маршрутизация запросов, расширение запросов, оптимизация извлечения из векторных БД, ранжирование, correctives RAG",
        "focus_en": "query translation, routing, query expansion, vector databases retrieval optimization, page ranking, correctives RAG"
    },
    18: {
        "title_ru": "Основы Harness Engineering: Тестирование и Сквозные прогоны",
        "title_en": "Harness Engineering Foundations: E2E and Testing Loops",
        "focus_ru": "Архитектура Harness, слепые зоны юнит-тестирования, Playwright сквозное клик-тестирование, превращение правил в выполнимые проверки",
        "focus_en": "Harness architecture, blind spots of unit testing, Playwright E2E click-testing, turning rules into executable checks"
    },
    19: {
        "title_ru": "Оценки качества и регрессионный Harness",
        "title_en": "Evaluation Metrics and Regression Harness",
        "focus_ru": "создание датасетов оценки, тестирование ответов агентов, использование LLM-as-a-judge для точности, замеры latency и токенов",
        "focus_en": "building evaluation datasets, benchmarking agent outputs, using LLM-as-a-judge for accuracy, measuring latency and token usage"
    },
    20: {
        "title_ru": "Окончание сессии и дисциплина состояния (Session Handover)",
        "title_en": "Session Handover and State Discipline",
        "focus_ru": "Проблема сломанного состояния, чистое состояние (5 условий), Session Handover (передача контекста), cleanup loop, идемпотентная очистка",
        "focus_en": "Broken state issues, clean state (5 conditions), Session Handover (passing context), cleanup loops, idempotent cleanups"
    },
    21: {
        "title_ru": "Безопасность, Инъекции и Песочницы",
        "title_en": "Security, Injections, and Sandboxes",
        "focus_ru": "таксономия ИИ угроз, промпт-инъекции (джейлбрейки, косвенные инъекции), санитаризация вебхуков, выполнение кода в песочницах",
        "focus_en": "taxonomy of LLM security threats, prompt injections (jailbreaks, indirect PI), sanitizing webhooks, running code in isolated sandboxes"
    },
    22: {
        "title_ru": "Деплой и Надежное Выполнение",
        "title_en": "Deployment and Reliable Execution",
        "focus_ru": "деплой агентов как микросервисов, обработка асинхронных бэкграунд задач, Docker контейнеры, мониторинг логов и health checks",
        "focus_en": "deploying AI agents as microservices, handling asynchronous background tasks, Docker containers, monitoring logs, health checks"
    },
    23: {
        "title_ru": "Голосовые и Мультимодальные Агенты",
        "title_en": "Voice and Multimodal Agents",
        "focus_ru": "голосовые агенты реального времени, перевод речи в текст (Whisper), генерация голоса, мультимодальные входы (изображения, аудио)",
        "focus_en": "real-time voice agents, speech-to-text (Whisper), text-to-speech, processing multimodal inputs (images, audio)"
    },
    24: {
        "title_ru": "Капстон-проект и Карьерный старт (Дипломный проект)",
        "title_en": "Capstone Project and Career Start",
        "focus_ru": "Дипломный проект, упаковка ИИ-услуг, value-based pricing, фриланс-старт, договора автоматизации, Loom-портфолио",
        "focus_en": "Capstone project, packaging AI services, value-based pricing, freelance start, contracts, Loom portfolio"
    },
    25: {
        "title_ru": "Капстон-проект и Карьерный старт (Дипломный проект)",
        "title_en": "Capstone Project and Career Start",
        "focus_ru": "Дипломный проект, упаковка ИИ-услуг, value-based pricing, фриланс-старт, договора автоматизации, Loom-портфолио",
        "focus_en": "Capstone project, packaging AI services, value-based pricing, freelance start, contracts, Loom portfolio"
    },
    26: {
        "title_ru": "Капстон-проект и Карьерный старт (Дипломный проект)",
        "title_en": "Capstone Project and Career Start",
        "focus_ru": "Дипломный проект, упаковка ИИ-услуг, value-based pricing, фриланс-старт, договора автоматизации, Loom-портфолио",
        "focus_en": "Capstone project, packaging AI services, value-based pricing, freelance start, contracts, Loom portfolio"
    }
}

def run_command(args: List[str]) -> str:
    """Helper to run a shell command and return its stdout."""
    if args and args[0] == "nlm":
        args = ["/Users/andreizelenov/.local/bin/nlm"] + args[1:]
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def get_studio_status() -> List[Dict[str, Any]]:
    """Fetches the list of all studio artifacts and their status from NotebookLM."""
    try:
        output = run_command(["nlm", "studio", "status", NOTEBOOK_ID, "--json"])
        return json.loads(output)
    except Exception as e:
        print(f"Error fetching studio status: {e}", file=sys.stderr)
        return []

def poll_artifact_status(artifact_id: str, timeout_mins: int = 15, interval_secs: int = 60) -> bool:
    """Polls the status of an artifact until it is completed or failed."""
    start_time = time.time()
    max_seconds = timeout_mins * 60
    
    print(f"Polling status of artifact {artifact_id}...")
    
    while (time.time() - start_time) < max_seconds:
        status_list = get_studio_status()
        target = next((item for item in status_list if item.get("id") == artifact_id), None)
        
        if not target:
            print(f"Artifact {artifact_id} not found in the status list. Retrying...", file=sys.stderr)
        else:
            status = target.get("status")
            print(f"  Current Status: '{status}' (Elapsed: {int(time.time() - start_time)}s)")
            if status == "completed":
                print("✓ Artifact is completed!")
                return True
            elif status == "failed":
                print("✗ Artifact generation failed on NotebookLM's server.", file=sys.stderr)
                return False
                
        time.sleep(interval_secs)
        
    print(f"✗ Polling timed out after {timeout_mins} minutes.", file=sys.stderr)
    return False

def trigger_slides(focus_prompt: str, lang: str) -> Optional[str]:
    """Triggers the creation of a slide deck in NotebookLM and returns the artifact ID with retry on any error."""
    print(f"-> Triggering native Slide Deck in NotebookLM (Lang: {lang.upper()})...")
    retries = 10
    wait_time = 900  # 15 minutes
    for attempt in range(retries):
        try:
            args = ["/Users/andreizelenov/.local/bin/nlm", "slides", "create", NOTEBOOK_ID, "--language", lang, "--focus", focus_prompt, "-y"]
            res = subprocess.run(args, capture_output=True, text=True)
            output = res.stdout + "\n" + res.stderr
            
            if res.returncode == 0:
                for line in output.split("\n"):
                    if "Artifact ID:" in line:
                        artifact_id = line.split("Artifact ID:")[-1].strip()
                        print(f"✓ slide deck triggered successfully! ID: {artifact_id}")
                        return artifact_id
            
            print(f"Failed to trigger slides (exit code {res.returncode}): {output}", file=sys.stderr)
            print(f"Waiting {wait_time}s before retrying (attempt {attempt+1}/{retries})...", file=sys.stderr)
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error triggering slides: {e}", file=sys.stderr)
            time.sleep(60)
    return None

def trigger_video(focus_prompt: str, lang: str) -> Optional[str]:
    """Triggers the creation of a video overview in NotebookLM and returns the artifact ID with retry on any error."""
    print(f"-> Triggering native Video Overview in NotebookLM (Lang: {lang.upper()})...")
    retries = 10
    wait_time = 900  # 15 minutes
    for attempt in range(retries):
        try:
            args = ["/Users/andreizelenov/.local/bin/nlm", "video", "create", NOTEBOOK_ID, "--format", "explainer", "--language", lang, "--focus", focus_prompt, "-y"]
            res = subprocess.run(args, capture_output=True, text=True)
            output = res.stdout + "\n" + res.stderr
            
            if res.returncode == 0:
                for line in output.split("\n"):
                    if "Artifact ID:" in line:
                        artifact_id = line.split("Artifact ID:")[-1].strip()
                        print(f"✓ Video triggered successfully! ID: {artifact_id}")
                        return artifact_id
            
            print(f"Failed to trigger video (exit code {res.returncode}): {output}", file=sys.stderr)
            print(f"Waiting {wait_time}s before retrying (attempt {attempt+1}/{retries})...", file=sys.stderr)
            time.sleep(wait_time)
        except Exception as e:
            print(f"Error triggering video: {e}", file=sys.stderr)
            time.sleep(60)
    return None



def download_slides(artifact_id: str, output_path: str):
    """Downloads the slide deck PDF file."""
    print(f"-> Downloading slide deck {artifact_id} to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    run_command([
        "nlm", "download", "slide-deck", NOTEBOOK_ID,
        "--id", artifact_id,
        "--format", "pdf",
        "--output", output_path
    ])
    print(f"✓ Slide deck saved successfully.")

def download_video(artifact_id: str, output_path: str):
    """Downloads the video MP4 file."""
    print(f"-> Downloading video {artifact_id} to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    run_command([
        "nlm", "download", "video", NOTEBOOK_ID,
        "--id", artifact_id,
        "--output", output_path
    ])
    print(f"✓ Video saved successfully.")

def process_week(week_num: int, lang: str) -> bool:
    """Handles triggering, polling, and downloading slides + video for a week and language."""
    if week_num not in WEEKS_CONFIG:
        print(f"Week {week_num} is not configured in WEEKS_CONFIG. Skipping.", file=sys.stderr)
        return False
        
    config = WEEKS_CONFIG[week_num]
    focus_prompt = config["focus_ru"] if lang == "ru" else config["focus_en"]
    
    print(f"\n========================================================")
    print(f"🎬 Processing WEEK {week_num} in {lang.upper()}")
    print(f"   Topic: {config['title_ru'] if lang == 'ru' else config['title_en']}")
    print(f"========================================================")
    
    out_pdf = f"public/lessons/week-{week_num}/{lang}/slides.pdf" if lang == "en" else f"public/lessons/week-{week_num}/slides.pdf"
    out_mp4 = f"public/lessons/week-{week_num}/{lang}/video.mp4" if lang == "en" else f"public/lessons/week-{week_num}/video.mp4"

    generated = False

    # 1. Trigger & Process Slide Deck
    if os.path.exists(out_pdf) and os.path.getsize(out_pdf) > 1000:
        print(f"✓ Slides PDF already exists at {out_pdf}, skipping generation.")
    else:
        generated = True
        slides_id = trigger_slides(focus_prompt, lang)
        if slides_id:
            # Cooldown safety delay after trigger
            time.sleep(20)
            if poll_artifact_status(slides_id):
                download_slides(slides_id, out_pdf)
            
    # Cooldown safety delay between RPC types
    if not (os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 1000):
        generated = True
        print("Waiting 40 seconds before triggering video overview...")
        time.sleep(40)
    
        # 2. Trigger & Process Video Overview
        video_id = trigger_video(focus_prompt, lang)
        if video_id:
            # Cooldown safety delay after trigger
            time.sleep(20)
            if poll_artifact_status(video_id, timeout_mins=35):
                download_video(video_id, out_mp4)
    else:
        print(f"✓ Video MP4 already exists at {out_mp4}, skipping generation.")

    return generated


def main():
    parser = argparse.ArgumentParser(description="NotebookLM Native Slide and Video Generator.")
    parser.add_argument("--weeks", type=str, default="1", help="Comma-separated week numbers to process, e.g., '1,2'")
    parser.add_argument("--lang", type=str, default="ru", help="Language code (ru or en or 'both')")
    
    # Handle direct arguments when run without parser helper or in CLI
    # Typer/argparse workaround if executing raw
    args, unknown = parser.parse_known_args()
    
    week_nums = [int(w.strip()) for w in args.weeks.split(",") if w.strip().isdigit()]
    languages = ["ru", "en"] if args.lang == "both" else [args.lang]
    
    print("🚀 Initializing NotebookLM Native Media Generation Pipeline...")
    print(f"Weeks to process: {week_nums}")
    print(f"Languages: {languages}")
    
    for week in week_nums:
        for lang in languages:
            try:
                any_generated = process_week(week, lang)
                if any_generated:
                    # Cooldown safety delay between weeks
                    print("\nCooldown sleep for 80 seconds before starting next block...")
                    time.sleep(80)
            except Exception as e:
                print(f"Error processing Week {week} ({lang}): {e}", file=sys.stderr)

                
    print("\n🎉 Native Media Generation and Download Pipeline completed successfully!")

if __name__ == "__main__":
    main()
