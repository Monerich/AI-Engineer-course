#!/usr/bin/env python3
import os

CURRICULUM_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "data", "curriculum.ts"))

# Weekly 10 blocks data mapping
WEEKLY_BLOCKS = {
    1: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Инфраструктура REST API — настройка GET/POST/PUT/DELETE, Headers, Query/Body параметров в клиенте.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Коды ответов и Rate Limiting — семантика HTTP-статусов (2xx, 3xx, 4xx, 5xx) и заголовков Retry-After.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Форматирование данных JSON — вложенные объекты, массивы и валидация JSON-схем.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Событийное управление через Webhooks — настройка живого Webhook-слушателя и обработка входящих POST-запросов.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Работа с публичными API — сборка сквозного конвейера импорта данных Weather/GitHub API.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Безопасность и авторизация в веб-интеграциях — настройка Bearer-токенов, Basic Auth и концепт OAuth2.",
            "Блок 7 (Python-разработка): Настройка окружения с Astral uv • Виртуальные среды • Синтаксис Python, типы данных, списки и словари.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Введение в дополненные LLM (Augmented LLMs) и базовый цикл рассуждений (Reasoning Loop).",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Линейные процессы (цепочки шагов) vs Автономные агенты (динамические циклы).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Концепция тестового стенда (Agent Harness) как операционной системы контроля ИИ."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): REST API Infrastructure — GET/POST/PUT/DELETE, Headers, Query/Body parameters in clients.",
            "Block 2 (AI Engineer / Automation): Status Codes & Rate Limiting — HTTP-status semantics (2xx, 3xx, 4xx, 5xx) and Retry-After headers.",
            "Block 3 (AI Engineer / Automation): JSON Data Formatting — nested objects, arrays, and JSON schema validation.",
            "Block 4 (AI Engineer / Automation): Event-Driven Webhooks — setting up webhook listeners and processing incoming POST payloads.",
            "Block 5 (AI Engineer / Automation): Practice: Public API Integration — building an E2E import pipeline from Weather/GitHub API.",
            "Block 6 (AI Engineer / Automation): Authentication & Security — Bearer tokens, Basic Auth, and OAuth2 concepts.",
            "Block 7 (Python Development): uv environment setup • Virtual envs • Python syntax, data types, lists, and dicts.",
            "Block 8 (AI Agent Builder / Agents & Harness): Intro to Augmented LLMs and the basic reasoning loop (Reasoning Loop).",
            "Block 9 (AI Agent Builder / Agents & Harness): Linear processes (chains) vs Autonomous agents (dynamic loop reasoning).",
            "Block 10 (AI Agent Builder / Agents & Harness): Understanding the Agent Harness as an Operating System."
        ]
    },
    2: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Эволюция от Prompt к Context Engineering — физика контекстных окон в 2026 году и управление токенами.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Системные инструкции (System Prompts) для жесткого управления форматом и структурой ответа.",
            "Блок 3 (ИИ-Инженер / Автоматизация): XML-теговый промптинг — шаблонизация промптов и разграничение контекста для защиты от инъекций.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Снижение уровня галлюцинаций LLM — методы верификации фактов и обработка неопределенности.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Сборщик JSON из сырого текста — написание промпта извлечения заказов из писем.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Безопасность контекста — проектирование защитных инструкций (Prompt Guard) против утечки промптов.",
            "Блок 7 (Python-разработка): Разработка Python-скрипта для чтения, валидации и фильтрации сырых JSON-файлов.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): 4 примитива контекст-инжиниринга: Write (запись), Select (выборка), Compress (сжатие), Isolate (изоляция).",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Few-shot промптинг с Example Selection • Chain of Thought (CoT) с тегами <thought>.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Концептуальный разбор и логика цикла рассуждений ReAct (Reason-Act)."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Prompt to Context Engineering — context windows in 2026 and token economics.",
            "Block 2 (AI Engineer / Automation): System Instructions (System Prompts) for strict formatting and response structure control.",
            "Block 3 (AI Engineer / Automation): XML Tag Prompting — prompt templates and context isolation for injection prevention.",
            "Block 4 (AI Engineer / Automation): Mitigating Hallucinations — verification methods and instructions for handling uncertainty.",
            "Block 5 (AI Engineer / Automation): Practice: JSON Lead Extractor — crafting prompts to extract orders from raw emails.",
            "Block 6 (AI Engineer / Automation): Context Security — designing protective instructions (Prompt Guard) against prompt leaks.",
            "Block 7 (Python Development): Developing Python scripts for reading, validating, and filtering raw JSON files.",
            "Block 8 (AI Agent Builder / Agents & Harness): The 4 Context Engineering Primitives: Write, Select, Compress, Isolate.",
            "Block 9 (AI Agent Builder / Agents & Harness): Few-shot prompting with dynamic Example Selection • Chain of Thought (CoT) with <thought> tags.",
            "Block 10 (AI Agent Builder / Agents & Harness): Conceptual breakdown and logical flow of the ReAct (Reason-Act) loop."
        ]
    },
    3: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Инфраструктура n8n — развертывание self-hosted n8n в Docker и подключение PostgreSQL как БД.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Холст и триггеры n8n — интерфейс платформы, типы триггеров (Manual, Webhook, Schedule) и экшены.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Передача данных и Expressions — синтаксис выражений n8n и работа со встроенными переменными.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Логическое ветвление — ноды IF, Switch и Merge (Wait, Pass-through, Combine).",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Автоматический приветственный пайплайн — сборка процесса отправки email-оповещений.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Авторизация внешних API в n8n — настройка Credentials, Bearer-токенов и интеграция OAuth2.",
            "Блок 7 (Python-разработка): Проектирование функций, аннотации типов и обработка системных ошибок через try-except-finally блоки.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование путей самовосстановления и обхода ошибок в визуальных воркфлоу n8n.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Архитектура переходов состояний (State Transitions) в визуальных графах автоматизации.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Линейные процессы vs циклические графы: пределы no-code оркестраторов."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): n8n Infrastructure — self-hosted n8n Docker deployment and PostgreSQL connection.",
            "Block 2 (AI Engineer / Automation): Canvas & n8n Triggers — UI, trigger types (Manual, Webhook, Schedule) and action nodes.",
            "Block 3 (AI Engineer / Automation): n8n Data & Expressions — n8n expression syntax and template variables.",
            "Block 4 (AI Engineer / Automation): Branching Logic — advanced IF, Switch, and Merge nodes (Wait, Pass-through, Combine modes).",
            "Block 5 (AI Engineer / Automation): Practice: Automated Welcome Pipeline — sending welcome emails and logging missing data.",
            "Block 6 (AI Engineer / Automation): API Authentication in n8n — setting up Credentials, Bearer tokens, and OAuth2.",
            "Block 7 (Python Development): Python functions, type hints, and error handling with try-except-finally blocks.",
            "Block 8 (AI Agent Builder / Agents & Harness): Designing self-healing paths and dynamic error recovery in n8n workflows.",
            "Block 9 (AI Agent Builder / Agents & Harness): State Transition architectures in visual automation graphs.",
            "Block 10 (AI Agent Builder / Agents & Harness): Linear workflows vs cyclic graphs: limits of no-code orchestrators."
        ]
    },
    4: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Интеграция ИИ-нод в n8n — подключение OpenAI/Anthropic, выбор оптимальных моделей под задачи.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Парсинг писем с помощью LLM — сборка ноды OpenAI для структурированного JSON-вывода.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Настройка Telegram Bot API — создание бота в BotFather, настройка вебхуков и отправка Markdown.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Практикум: Сборка умного Telegram-фильтра лидов — классификация писем и алерты в Telegram.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Интерактивная отладка n8n — дебаггинг активных выполнений, анализ логов и обработка сбоев API.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Экономика API-вызовов — оптимизация количества запросов к LLM при пиковых нагрузках в n8n.",
            "Блок 7 (Python-разработка): Асинхронное программирование в Python: создание неблокирующих API-запросов через httpx и asyncio.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Маршрутизация моделей (Cost-Performance Routing) — дешевые (Haiku) vs дорогие (Sonnet) модели.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование нод-заглушек (fallback) и ретраев с экспоненциальной задержкой (Backoff).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Сквозная логика рассуждений при квалификации лидов: от анализа до вердикта."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Ingesting AI Nodes in n8n — OpenAI/Anthropic nodes and model selection criteria.",
            "Block 2 (AI Engineer / Automation): Parsing Emails using LLMs — OpenAI node setup to extract structured JSON data.",
            "Block 3 (AI Engineer / Automation): Telegram Bot API Configuration — BotFather setup, webhooks, and Markdown format alerts.",
            "Block 4 (AI Engineer / Automation): Practice: Smart Telegram Lead Filter — E2E lead parsing, LLM routing, and alerts.",
            "Block 5 (AI Engineer / Automation): n8n Live Debugging — execution analysis, historical logs, and error tracing.",
            "Block 6 (AI Engineer / Automation): Token Economics — cost optimization strategies during high concurrent volume.",
            "Block 7 (Python Development): Async Python — non-blocking HTTP requests using httpx and asyncio.",
            "Block 8 (AI Agent Builder / Agents & Harness): Model Routing (Cost-Performance) — routing to cheap (Haiku) vs rich (Sonnet) models.",
            "Block 9 (AI Agent Builder / Agents & Harness): Designing fallback nodes and exponential backoff retry patterns.",
            "Block 10 (AI Agent Builder / Agents & Harness): E2E reasoning pipeline for lead qualification: from parse to routing decision."
        ]
    },
    5: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Концепция Item Lists в n8n — параллельная обработка списков элементов, циклы и итерации.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Итерация и циклы — разделение данных и порционная обработка через Split In Batches.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Модульная архитектура n8n — вызов дочерних процессов через Execute Workflow.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Изоляция данных — передача и сохранение переменных состояния между родительским и дочерним флоу.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Новости с циклом — RSS-лента, фильтр 5 новостей, дочерний воркфлоу суммаризации.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Масштабирование n8n — настройка self-hosted n8n в режиме Redis Queue Mode для воркеров.",
            "Блок 7 (Python-разработка): Сложные трансформации массивов данных в Python внутри ноды Code в n8n.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование событийно-ориентированных (Event-Driven) архитектур автоматизации.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Управление очередями задач при работе с лимитами сторонних API (Rate Limiting).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Распределенные состояния в low-code: защита данных при сбое на середине цикла."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): n8n Item Lists Concept — parallel executions, data loops, and item iteration.",
            "Block 2 (AI Engineer / Automation): Loops & Batches — processing item arrays through Split In Batches node.",
            "Block 3 (AI Engineer / Automation): Modular Workflows — executing sub-workflows using Execute Workflow node.",
            "Block 4 (AI Engineer / Automation): Variable Isolation — managing parent/child variables and scope persistence.",
            "Block 5 (AI Engineer / Automation): Practice: Loop News Digest — RSS trigger, top 5 items filter, sub-workflow summaries.",
            "Block 6 (AI Engineer / Automation): Scaling n8n — self-hosted n8n Redis Queue Mode configuration for worker nodes.",
            "Block 7 (Python Development): Writing Python scripts inside the n8n Code Node for complex data mappings.",
            "Block 8 (AI Agent Builder / Agents & Harness): Designing Event-Driven visual automation architectures.",
            "Block 9 (AI Agent Builder / Agents & Harness): Managing API task queues to prevent Rate Limit (429) lockouts.",
            "Block 10 (AI Agent Builder / Agents & Harness): Distributed state control: preventing data loss on crash."
        ]
    },
    6: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Архитектура ИИ-нод n8n — как под капотом собираются цепочки и агенты библиотеки LangChain.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Нода AI Agent в n8n — использование ИИ-агента в режиме Conversational Agent.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Продвинутые инструменты (Tools) — разработка кастомных инструментов через HTTP-запросы и JS.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Память чат-ботов — сохранение сессий диалогов: Window Buffer Memory vs внешняя БД pg/redis.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Импорт документов — загрузка документов (PDF, TXT, CSV) через Document Loaders для векторизации.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Стратегии разбивки текстов — работа с Text Splitters: заголовочный чанкинг, скользящее окно.",
            "Блок 7 (Python-разработка): Профессиональное использование официальных SDK OpenAI/Anthropic в Python • Управление таймаутами.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Описание инструментов (JSON-схемы) для агента: промптинг модели на выбор нужного тула.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Защита от prompt injection через параметры и аргументы инструментов агента.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Трассировка рассуждений агента при вызове цепочек инструментов."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): n8n AI Nodes Architecture — how LangChain structures chains and agents under the hood.",
            "Block 2 (AI Engineer / Automation): AI Agent Node in n8n — setting up n8n agents in Conversational Agent mode.",
            "Block 3 (AI Engineer / Automation): Advanced n8n Tools — creating custom tools via HTTP requests and JavaScript.",
            "Block 4 (AI Engineer / Automation): Bot Memory — chat session persistence: Window Buffer Memory vs external DBs.",
            "Block 5 (AI Engineer / Automation): Ingesting Documents — loading PDFs, CSVs, and TXT files via Document Loaders.",
            "Block 6 (AI Engineer / Automation): Text Splitting Strategies — chunking files via Text Splitters (header, character split).",
            "Block 7 (Python Development): Professional OpenAI/Anthropic Python SDK usage • dot-env and clients timeout.",
            "Block 8 (AI Agent Builder / Agents & Harness): Tool JSON schemas — prompt strategies for deterministic tool selection.",
            "Block 9 (AI Agent Builder / Agents & Harness): Prompt injection shields via strict tool schemas and input validation.",
            "Block 10 (AI Agent Builder / Agents & Harness): Tracing agent reasoning during multi-tool execution chains."
        ]
    },
    7: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Семантический поиск — векторные представления (embeddings) и косинусное сходство.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Развертывание векторных баз — настройка pgvector в Supabase, использование Pinecone и Qdrant.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Векторизация в n8n — сквозной пайплайн разбивки, эмбеддинга и загрузки документов в векторную БД.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Retriever в n8n — настройка ноды Vector Store Retriever для поиска контекста по запросу.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Справка по продукту — сборка чат-агента RAG, отвечающего по регламенту компании.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Cohere Rerank — интеграция API Cohere Rerank для фильтрации результатов векторного поиска.",
            "Блок 7 (Python-разработка): Программное создание векторных представлений текстов на чистом Python с использованием openai.embeddings.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Оценка качества RAG: ключевые метрики извлечения релевантного контекста.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Минимизация эффекта «Lost in the Middle» (потеря инфы в середине контекста).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование гибридного поиска (сочетание плотных векторов и разреженного BM25)."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Semantic Search — vector embeddings and cosine similarity concepts.",
            "Block 2 (AI Engineer / Automation): Deploying Vector DBs — Supabase pgvector configuration, Pinecone, and Qdrant setup.",
            "Block 3 (AI Engineer / Automation): Vector Pipelines in n8n — document splitting, embedding, and database ingestion.",
            "Block 4 (AI Engineer / Automation): Retriever in n8n — configuring Vector Store Retriever nodes for context searches.",
            "Block 5 (AI Engineer / Automation): Practice: Product Knowledge Base — RAG chatbot answering strictly from loaded documents.",
            "Block 6 (AI Engineer / Automation): Cohere Rerank — integrating Cohere Rerank API to optimize semantic vector search outputs.",
            "Block 7 (Python Development): Generating text embeddings programmatically using openai.embeddings in Python.",
            "Block 8 (AI Agent Builder / Agents & Harness): RAG Evals — metrics for assessing semantic context retrieval quality.",
            "Block 9 (AI Agent Builder / Agents & Harness): Overcoming 'Lost in the Middle' contextual degradation.",
            "Block 10 (AI Agent Builder / Agents & Harness): Designing Hybrid Search (dense vector embeddings + sparse BM25)."
        ]
    },
    8: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Скрейпинг лидов — сбор базы лидов с помощью скрейперов Apollo и Clay.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Обогащение данных — пайплайны обогащения B2B-контактов по социальным сетям и доменам.",
            "Блок 3 (ИИ-Инженер / Автоматизация): ИИ-персонализация — генерация писем-оупенеров на основе профилей LinkedIn лидов.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Интеграция CRM — автосоздание сделок и контактов в HubSpot / Pipedrive CRM через API.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Массовые рассылки — интеграция и запуск цепочек писем через Instantly/Smartlead.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Практикум: Сборка аутрич-машины — сквозной n8n-процесс холодного ИИ-аутрича.",
            "Блок 7 (Python-разработка): Фильтрация, очистка и нормализация сложных выгрузок CSV-данных на Python перед воронками.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Управление Tone-of-Voice при генерации писем ИИ-агентом.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Классификация ответов лидов по тональности (Заинтересован, Спам, Отписка).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Экономика токенов в массовых рассылках: расчет ROI ИИ-системы."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Lead Scraping — Apollo and Clay scraping setup.",
            "Block 2 (AI Engineer / Automation): Data Enrichment — B2B enrichment pipelines using websites and domains.",
            "Block 3 (AI Engineer / Automation): AI Personalization — personalized icebreakers from LinkedIn profiles.",
            "Block 4 (AI Engineer / Automation): CRM Sync — HubSpot/Pipedrive contact and deal sync via REST APIs.",
            "Block 5 (AI Engineer / Automation): Cold Inboxes — smart campaigns setup in Instantly/Smartlead.",
            "Block 6 (AI Engineer / Automation): Practice: Outreach Engine — complete outbound automation from lead to email draft.",
            "Block 7 (Python Development): CSV Parsing & Cleaning — cleaning and normalizing complex B2B data sheets.",
            "Block 8 (AI Agent Builder / Agents & Harness): Brand Tone-of-Voice control in autonomous copy generators.",
            "Block 9 (AI Agent Builder / Agents & Harness): Outbound reply intent classification (Positive vs Unsubscribe).",
            "Block 10 (AI Agent Builder / Agents & Harness): Token economics in scale outreach: pricing models and ROI."
        ]
    },
    9: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Динамический скрейпинг — Playwright и BeautifulSoup на Python для динамических веб-страниц.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Парсинг HTML в JSON — извлечение чистых структурированных JSON-данных из разметки.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Обход защит — программная обработка cookies, HTTP-headers and User-Agents.",
            "Блок 4 (ИИ-Инженер / Автоматизация): REST API без SDK — выполнение REST-запросов к внешним сервисам на чистом коде.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Практикум: Скрипт-анализатор погоды — получение погоды по API, парсинг JSON и запись лога.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Системная автоматизация — скрипты операций с локальной файловой системой и директориями.",
            "Блок 7 (Python-разработка): Concurrency в Python: asyncio.gather, семафоры (asyncio.Semaphore) для лимитов и очереди.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Перенос no-code сценариев n8n в высокооптимизированные Python-скрипты.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Программный мониторинг и логирование расходов токенов при параллельных вызовах.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Написание отказоустойчивых декораторов для ретраев API-запросов (exponential retry)."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Dynamic Scraping — Playwright and BeautifulSoup in Python for dynamic pages.",
            "Block 2 (AI Engineer / Automation): HTML parsing to JSON — extracting clean structured JSON records from raw markup.",
            "Block 3 (AI Engineer / Automation): WAF Bypass — custom HTTP headers, cookies, and dynamic User-Agent rotation.",
            "Block 4 (AI Engineer / Automation): Native REST API — sending direct HTTP requests to APIs without wrapper SDKs.",
            "Block 5 (AI Engineer / Automation): Practice: Weather Alert Script — API fetching, JSON extraction, and alert generation.",
            "Block 6 (AI Engineer / Automation): Operating System automation — programmatic file and directory management.",
            "Block 7 (Python Development): Concurrency in Python: asyncio.gather, asyncio.Semaphore limits, and async queues.",
            "Block 8 (AI Agent Builder / Agents & Harness): Migrating visual n8n workflows into high-performance Python scripts.",
            "Block 9 (AI Agent Builder / Agents & Harness): Token spending trackers and cost logging in programmatic script runs.",
            "Block 10 (AI Agent Builder / Agents & Harness): Creating robust retry decorators with exponential backoff configurations."
        ]
    },
    10: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): REST JSON-схемы — проектирование схем данных для интеграции внешних систем.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Валидация структур данных — валидация многоуровневых вложенных JSON-схем.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Обработка ошибок API — отлов сетевых исключений и заголовков лимитов (Rate Limit).",
            "Блок 4 (ИИ-Инженер / Автоматизация): Конфигурация SDK — проектирование системных инструкций для OpenAI/Anthropic SDK.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Параметры генерации — программное управление temperature, top_p, max_tokens.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Восстановление после лимитов — стратегии самовосстановления приложений после 429 ошибок.",
            "Блок 7 (Python-разработка): Использование Pydantic V2 для Structured Outputs • Кастомная валидация: @field_validator и @model_validator.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Цикл самовосстановления JSON (Self-healing loop): отлов ошибок Pydantic и исправление моделью.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Программное сохранение и типизация истории рассуждений агента в классах.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Версионирование схем и миграции данных в боевых ИИ-агентах."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): REST JSON Schema — designing robust data models for API payloads.",
            "Block 2 (AI Engineer / Automation): Structured Data Validation — parsing and validating multi-layered JSON payloads.",
            "Block 3 (AI Engineer / Automation): Handling API Exceptions — capturing network failures and rate limits headers.",
            "Block 4 (AI Engineer / Automation): SDK Configurations — system instructions design for OpenAI/Anthropic Python clients.",
            "Block 5 (AI Engineer / Automation): Generation Parameters — managing temperature, top_p, and token ceilings.",
            "Block 6 (AI Engineer / Automation): Rate Limit Resiliency — recovery configurations for API limits (429 errors).",
            "Block 7 (Python Development): Pydantic V2 for Structured Outputs • Custom validators: @field_validator and @model_validator.",
            "Block 8 (AI Agent Builder / Agents & Harness): Self-healing JSON loops — capturing Pydantic errors and query retries.",
            "Block 9 (AI Agent Builder / Agents & Harness): Session trace typings and saving reasoning logs inside Python classes.",
            "Block 10 (AI Agent Builder / Agents & Harness): Schema versioning and data migration strategies in production agents."
        ]
    },
    11: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Реестр инструментов — архитектура Tool Registry для кастомного агента.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Поисковые инструменты — подключение Tavily API / SerpAPI в качестве инструментов.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Файловые инструменты — безопасное чтение, запись и редактирование файлов на диске.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Инструменты как REST API — обертка локальных Python-инструментов в эндпоинты FastAPI.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Продвинутые схемы — разработка кастомных декораторов @tool для автогенерации схем функций на основе сигнатуры.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Изоляция окружения — управление зависимостями при вызове скриптов инструментами.",
            "Блок 7 (Python-разработка): Разработка кастомных декораторов @tool для автогенерации схем функций на основе сигнатуры.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Логика канонического цикла рассуждений ReAct (Think -> Act -> Observe).",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Парсинг структуры вызовов инструментов (tool_calls) и возврат результатов в историю.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Ограничение шагов итераций для защиты агента от бесконечного зацикливания."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Tool Registry — architecture of tool registries for custom agents.",
            "Block 2 (AI Engineer / Automation): Search APIs Tools — Tavily and SerpAPI integration as agent search tools.",
            "Block 3 (AI Engineer / Automation): File Actions Tools — reading, writing, and editing files inside safe directory bounds.",
            "Block 4 (AI Engineer / Automation): Tools as REST APIs — exposing Python tools via FastAPI micro-endpoints.",
            "Block 5 (AI Engineer / Automation): Dynamic JSON Schemas — dynamic schema generation from Python functions docstrings.",
            "Block 6 (AI Engineer / Automation): Runtime Isolation — handling dependencies and isolated runtimes for custom tools.",
            "Block 7 (Python Development): Coding custom @tool decorators with automatic JSON schema generation from docstrings.",
            "Block 8 (AI Agent Builder / Agents & Harness): Canonical ReAct loop logic (Think -> Act -> Observe) in Python.",
            "Block 9 (AI Agent Builder / Agents & Harness): Capturing tool_calls payloads and feeding execution returns back to model.",
            "Block 10 (AI Agent Builder / Agents & Harness): Safety caps: infinite loop prevention by capping execution runs."
        ]
    },
    12: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Интегрированный CLI-инструментарий — скрейперы, утилиты и поисковые API в едином наборе.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Сессионное хранение — сохранение истории диалога и запросов пользователя.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Логирование выполнения — красивое форматирование шагов работы агента для отладки.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Мониторинг директорий — написание фоновых скриптов для отслеживания изменений в файлах.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Автодокументирование — генерация отчетов по результатам решенных задач.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Практикум: Сборка CLI-агента — локальный ассистент с поиском и файловыми инструментами.",
            "Блок 7 (Python-разработка): Использование библиотеки Rich для премиального CLI-оформления терминала.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Скрытие внутренних размышлений (<thought>) от конечного пользователя в CLI.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Алгоритмы сжатия и очистки контекстного окна (Context Compaction) при лимитах токенов.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Сохранение, загрузка сессий и восстановление состояния CLI-помощника."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Unified CLI Toolkit — scrapers, utility files, and search APIs in one belt.",
            "Block 2 (AI Engineer / Automation): Session Logging — managing raw history storage and user configurations.",
            "Block 3 (AI Engineer / Automation): Step Trace Logs — beautiful programmatic logging of agent actions.",
            "Block 4 (AI Engineer / Automation): Directory Listeners — background watchers checking local file changes.",
            "Block 5 (AI Engineer / Automation): Auto-Documentation — automatic reporting of task outputs and resolutions.",
            "Block 6 (AI Engineer / Automation): Practice: CLI Agent — local assistant using Tavily search and file systems.",
            "Block 7 (Python Development): rich terminal printing library integration for premium visual console layouts.",
            "Block 8 (AI Agent Builder / Agents & Harness): Hiding model's internal reasoning (<thought> logs) in user CLI.",
            "Block 9 (AI Agent Builder / Agents & Harness): Context Compaction algorithms: summarizing older blocks to free window.",
            "Block 10 (AI Agent Builder / Agents & Harness): CLI Session recovery: loading and restoring state on restart."
        ]
    },
    13: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Концепция мультиагентов — разделение ролей, ответственности и наборов инструментов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Запуск по вебхуку — триггеры запуска CrewAI-скриптов по вебхукам.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Интерфейсы для CrewAI — передача результатов выполнения сложных задач на дашборды.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Форматирование обмена — подготовка структурированных данных для передачи между агентами.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Асинхронные вебхуки — разработка слушателей для параллельного запуска команд.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Облачный CrewAI — деплой локальных CrewAI-команд на облачные хостинги.",
            "Блок 7 (Python-разработка): Создание структуры CrewAI: определение агентов (Agent), задач (Task) и сборка команды (Crew).",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Паттерны мультиагентной координации в производственной среде.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Последовательный vs Иерархический процессы управления с кастомным Supervisor Pattern.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Архитектура общей памяти (Shared Memory) между независимыми агентами."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Multi-agent Primitives — role delegation, task breakdown, and tooling boundaries.",
            "Block 2 (AI Engineer / Automation): Webhook Triggers — running CrewAI scripts via visual webhook calls.",
            "Block 3 (AI Engineer / Automation): Dashboards for Crews — sending execution statuses and outputs to UI.",
            "Block 4 (AI Engineer / Automation): Payload Mappings — normalizing output structures for inter-agent communications.",
            "Block 5 (AI Engineer / Automation): Async Webhook Receivers — dynamic workers handling concurrent task triggers.",
            "Block 6 (AI Engineer / Automation): Cloud CrewAI — deploying local python crews to Railway/Render instances.",
            "Block 7 (Python Development): CrewAI Python classes setup — initializing Agents, Tasks, and Crews structures.",
            "Block 8 (AI Agent Builder / Agents & Harness): Multi-agent coordination patterns in enterprise pipelines.",
            "Block 9 (AI Agent Builder / Agents & Harness): Sequential vs Hierarchical routing containing custom Supervisor configurations.",
            "Block 10 (AI Agent Builder / Agents & Harness): Shared Memory systems for data retention across agent groups."
        ]
    },
    14: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Инструменты доступа к БД — обертка аналитических запросов к БД в инструменты агентов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): CRM-инструменты — API-интеграции для работы мультиагентных команд с CRM-системами.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Продвинутый обмен данными — подготовка промежуточных данных для обмена.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Защита API от блокировок — управление одновременной нагрузкой от нескольких агентов.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Экономика CrewAI — анализ затрат и оптимизация стоимости одного запуска сложной команды.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Экспорт отчетов — экспорт результатов выполнения команды в PDF и Markdown.",
            "Блок 7 (Python-разработка): Сохранение состояний мультиагентных систем с использованием внешних баз данных PostgreSQL/SQLite.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Разрешение логических противоречий и конфликтов между выводами разных агентов.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Цепочки контроля качества: автор (Writer) -> верификатор (Verifier) -> редактор (Editor).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Системы метрик и автоматическая оценка качества работы сложных мультиагентных групп."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): DB Tooling — wrapping complex SQL lookups as agent tools safely.",
            "Block 2 (AI Engineer / Automation): CRM Integrations — API tool hooks for multi-agent connections with HubSpot.",
            "Block 3 (AI Engineer / Automation): Context Passing — managing clean interim variables mapping.",
            "Block 4 (AI Engineer / Automation): API Capping — rate limit managers preventing concurrent request bans.",
            "Block 5 (AI Engineer / Automation): Crew Economics — tracking and optimizing token fees per run.",
            "Block 6 (AI Engineer / Automation): Visual Exports — compiling multi-agent outputs into markdown and PDF.",
            "Block 7 (Python Development): Multi-agent State persistence utilizing PostgreSQL backends.",
            "Block 8 (AI Agent Builder / Agents & Harness): Resolving conflicts and contradictions in competing agent outputs.",
            "Block 9 (AI Agent Builder / Agents & Harness): QA loops in Crews: Writer agent -> Verifier agent -> Editor reviews.",
            "Block 10 (AI Agent Builder / Agents & Harness): Metrics and automated evaluations for complex crew completions."
        ]
    },
    15: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Почему графы вместо цепочек — ограничения линейных пайплайнов, необходимость циклов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Проектирование графов — описание бизнес-логики в виде графа состояний.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Визуализация LangGraph — визуализация и чтение компилированных графов состояний.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Развертывание графов — запуск LangGraph в продакшн в виде микросервисов.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Инициализация графа — управление вводом и начальным состоянием графа.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Надежность путей графа — контроль переходов при нетипичном выводе LLM.",
            "Блок 7 (Python-разработка): Разработка структуры StateGraph: описание схемы состояния графа, узлов (Nodes) и переходов (Edges).",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Когнитивные архитектуры на основе графов состояний.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Настройка условных переходов (Conditional Edges) на основе валидации промежуточного состояния.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Обеспечение неизменяемости (immutability) состояния графа на шагах выполнения."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Cyclic Graphs over Chains — limitations of linear flows, why loops matter.",
            "Block 2 (AI Engineer / Automation): Designing Graphs — mapping complex business logic to graph formats.",
            "Block 3 (AI Engineer / Automation): Visualizing States — compiling and rendering LangGraph structures.",
            "Block 4 (AI Engineer / Automation): Deploying Graphs — packaging graph architectures as production services.",
            "Block 5 (AI Engineer / Automation): Input States — initializing state variables dynamically.",
            "Block 6 (AI Engineer / Automation): Graph Resilience — handling non-deterministic transitions from LLM outputs.",
            "Block 7 (Python Development): StateGraph setups — writing schemas, functional nodes, and edges.",
            "Block 8 (AI Agent Builder / Agents & Harness): Cognitive architectures built on graph paradigms.",
            "Block 9 (AI Agent Builder / Agents & Harness): Conditional Edges and dynamic routing using state variables validation.",
            "Block 10 (AI Agent Builder / Agents & Harness): State immutability rules inside node executions."
        ]
    },
    16: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Чекпоинты графа — подключение Postgres и SQLite для долговременного сохранения чекпоинтов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Роутинг сессий — идентификация сессий и роутинг пользователей при работе с графом.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Мониторинг графа — создание панелей отслеживания истории переходов и состояний.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Обогащение контекста — интеграция с внешними базами знаний для обогащения состояния.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Безопасность сессий — сохранение учетных данных пользователей в многопользовательском режиме.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Практикум: Чат-агент RAG с HITL — сборка графа поддержки, требующего аппрува человека в Telegram.",
            "Блок 7 (Python-разработка): Настройка динамического управления долгосрочной памятью (user-scoped vs thread-scoped) с Mem0/Letta.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Использование Checkpointers (PostgresSaver) для автоматического сохранения состояний.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Time Travel (путешествие во времени): отладка графа путем отката состояния и перезаписи.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Внедрение концепции Human-in-the-loop (HITL): прерывания (interrupt_before, interrupt_after)."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Persistence Backends — SQLiteSaver and PostgresSaver database checkpointers.",
            "Block 2 (AI Engineer / Automation): Session Routing — routing unique thread IDs through active graph states.",
            "Block 3 (AI Engineer / Automation): Graph Observability — monitoring node transitions and live state variables.",
            "Block 4 (AI Engineer / Automation): Context Injections — integrating external databases inside graph steps.",
            "Block 5 (AI Engineer / Automation): Secure Contexts — isolating user variables in multi-tenant environments.",
            "Block 6 (AI Engineer / Automation): Practice: RAG Agent with HITL — telegram integration requiring human check before replies.",
            "Block 7 (Python Development): Long-term Memory — integrating cross-session memory with Mem0 or Letta.",
            "Block 8 (AI Agent Builder / Agents & Harness): SQLite/Postgres Checkpointing for transaction recovery.",
            "Block 9 (AI Agent Builder / Agents & Harness): Time Travel debugging — rewinding execution to past state blocks.",
            "Block 10 (AI Agent Builder / Agents & Harness): HITL Breakpoints — setting interrupt_before and interrupt_after hooks."
        ]
    },
    17: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Умный чанкинг — продвинутые стратегии нарезки текстов на чанки с умным перекрытием.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Parent-Document Retriever — сохранение широкого контекста при точечном извлечении чанков.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Переранжирование — интеграция API Cohere Rerank для фильтрации результатов векторного поиска.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Query Translation — генерация субзапросов и переписывание пользовательских запросов.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Парсинг таблиц и схем — разбор сложных неструктурированных документов со встроенными таблицами.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Векторное масштабирование — масштабирование индексов векторных баз данных под высокой нагрузкой.",
            "Блок 7 (Python-разработка): Реализация логики Self-RAG (Corrective RAG - CRAG) на Python для автооценки релевантности документов.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Архитектура Оценщик-Оптимизатор (Evaluator-Optimizer) для контроля качества генерации.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование сценариев 'заглушек' при отсутствии релевантных документов в векторной БД.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Расчет ключевых RAG-метрик: Recall (полнота), Precision (точность) и Hit Rate."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Advanced Chunking — recursive split and semantic chunks overlaps.",
            "Block 2 (AI Engineer / Automation): Parent-Document Retrieval — storing broad context with precise retrievals.",
            "Block 3 (AI Engineer / Automation): Reranking — integrating Cohere Rerank API with vector store returns.",
            "Block 4 (AI Engineer / Automation): Query Translation — query rewriting and sub-queries generation.",
            "Block 5 (AI Engineer / Automation): Tabular Ingestions — parsing documents containing complex structural tables.",
            "Block 6 (AI Engineer / Automation): Vector Scaling — optimizing index lookups under high request volume.",
            "Block 7 (Python Development): Writing Self-RAG (Corrective RAG - CRAG) pipelines programmatically in Python.",
            "Block 8 (AI Agent Builder / Agents & Harness): Evaluator-Optimizer pattern in context retrieval loops.",
            "Block 9 (AI Agent Builder / Agents & Harness): Graceful fallbacks for empty retriever search results.",
            "Block 10 (AI Agent Builder / Agents & Harness): Evaluating RAG systems: tracking Recall, Precision, and Hit Rate."
        ]
    },
    18: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Трейсинг OpenTelemetry — развертывание систем трассировки и логирования ИИ-приложений.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Экспорт логов n8n — настройка экспорта логов выполнения воркфлоу n8n во внешние системы.",
            "Блок 3 (ИИ-Инженер / Автоматизация): LangSmith / Langfuse — интеграция платформ трассировки для анализа шагов генерации.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Финансовый мониторинг — мониторинг затрат на API-вызовы и детальное логирование расхода токенов.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Мониторинг задержек — измерение времени отклика (latency) и задержки генерации первого токена (TTFT).",
            "Блок 6 (ИИ-Инженер / Автоматизация): Лимиты и оповещения — настройка алертов в Slack/Telegram при превышении бюджетов или задержек.",
            "Блок 7 (Python-разработка): Интеграция SDK LangSmith/Langfuse в Python-приложения для трассировки холодных стартов.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 1: Сильные модели не означают надежного исполнения.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 2: Что такое тестовый стенд (Harness): изоляция, симуляция ввода.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 3: Код-репозиторий как источник правды • Лекция 4: Разделение промптов."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): OpenTelemetry Tracing — deploying trace servers and logs in AI apps.",
            "Block 2 (AI Engineer / Automation): Exporting n8n Execution Logs — routing visual run statistics.",
            "Block 3 (AI Engineer / Automation): LangSmith & Langfuse — integrating API tracers for execution trees.",
            "Block 4 (AI Engineer / Automation): Cost Tracking — auditing token consumption fees in raw logs.",
            "Block 5 (AI Engineer / Automation): Latency Watchers — tracking response speeds and Time-To-First-Token (TTFT).",
            "Block 6 (AI Engineer / Automation): Budget Alerting — Slack/Telegram notifications for high latency or cost runs.",
            "Block 7 (Python Development): Programmatic trace hooks setup using LangSmith/Langfuse Python SDKs.",
            "Block 8 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 1: Strong models != reliable execution.",
            "Block 9 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 2: Test Harness structures (isolation, input simulation).",
            "Block 10 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 3: Code Repository as Single Source of Truth • Lecture 4: Prompt file division."
        ]
    },
    19: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Датасеты из продакшна — сбор и разметка логов продакшна для формирования тестовых датасетов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Золотые датасеты (Golden Datasets) — создание эталонных выборок для непрерывной интеграции (CI/CD).",
            "Блок 3 (ИИ-Инженер / Автоматизация): Регрессионные тесты промптов — автоматический запуск тестов оценки качества при обновлении промптов.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Мультимодельные бенчмарки — бенчмаркинг работы агентов на различных языковых моделях.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Оптимизация стоимости/качества — оценка зависимости стоимости запроса от качества ответов.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Дашборды регрессии — построение автоматических дашбордов тестирования качества.",
            "Блок 7 (Python-разработка): Промышленное Е2Е-тестирование логики ИИ-агентов с помощью Playwright (автоматическая симуляция UI действий).",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 7: Четкие границы задач (как ограничить зону ответственности агента).",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 8: Ограничение нежелательного поведения через Feature Lists.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 9: Предотвращение преждевременного завершения • Лекция 10: Сквозное Е2Е тесты."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Production Datasets — harvesting production logs to create eval tests.",
            "Block 2 (AI Engineer / Automation): Golden Datasets — building master test sheets for continuous integration (CI/CD).",
            "Block 3 (AI Engineer / Automation): Prompt Regression Checks — automated test triggers on prompt updates.",
            "Block 4 (AI Engineer / Automation): Multi-model Performance Benchmarks — comparing cost/quality curves.",
            "Block 5 (AI Engineer / Automation): Cost-Quality Curves — optimizing budgets against factual accuracies.",
            "Block 6 (AI Engineer / Automation): Regression Visuals — building automated charts for dashboard evals.",
            "Block 7 (Python Development): Automated E2E agent UI checks using Playwright script runners.",
            "Block 8 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 7: Strict Task Boundaries (restricting agent scope).",
            "Block 9 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 8: Controlling behavior via dynamic Feature Lists.",
            "Block 10 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 9: Self-checks against premature completion • Lecture 10: E2E Playwright."
        ]
    },
    20: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Очистка ресурсов — разработка пайплайнов автоматической очистки временных файлов и кэшей в БД.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Таблицы состояний — проектирование таблиц долгосрочных состояний сессий в реляционных БД.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Алерты о зависших процессах — системы мониторинга зависших процессов и незавершенных сессий.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Автоматический сброс кэшей — применение триггеров БД для очистки кэшей при разрыве соединений.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Бэкап состояний — архитектура резервного копирования и быстрого восстановления состояний.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Жизненный цикл сессий — управление жизненным циклом сессионных переменных и распределенных кэшей.",
            "Блок 7 (Python-разработка): Создание кастомных менеджеров контекста на Python для безопасной очистки системных ресурсов.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 5: Сохранение контекста между сессиями (сериализация и восстановление).",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 6: Правильная инициализация проекта ИИ-агентом при старте.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Harness Engineering. Лекция 11: Мониторинг рассуждений • Лекция 12: Чистая передача сессии (Session Handover)."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Resource Cleanup — automatic file and database cache purge routines.",
            "Block 2 (AI Engineer / Automation): State Tables Design — transactional database architectures for session logs.",
            "Block 3 (AI Engineer / Automation): Stuck Process Monitors — alerting setups for unresponsive or hung runs.",
            "Block 4 (AI Engineer / Automation): DB-triggered Purges — auto-deleting temp cache files on network dropouts.",
            "Block 5 (AI Engineer / Automation): State Backup Schemas — continuous database checkpoints backups.",
            "Block 6 (AI Engineer / Automation): Session Lifetime Control — caching variables expiration settings.",
            "Block 7 (Python Development): Coding custom Python context managers for safe cleanup on crashes.",
            "Block 8 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 5: Context persistence between runs (serialization).",
            "Block 9 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 6: Proper project initialization routines by agents.",
            "Block 10 (AI Agent Builder / Agents & Harness): Harness Engineering Lecture 11: Reasoning observability • Lecture 12: Clean Handover (5 conditions)."
        ]
    },
    21: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Концептуальная безопасность LLM — систематизация уязвимостей больших языковых моделей.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Санитаризация вебхуков — фильтрация и санитаризация входящих данных в вебхуках от инъекций.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Защита от System Prompt Leakage — проектирование защитных механизмов против утечки промптов.",
            "Блок 4 (ИИ-Инженер / Автоматизация): OWASP Top 10 для LLM — практическое применение стандартов безопасности.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Настройка Guardrails — конфигурирование входных и выходных фильтров (NeMo Guardrails, Llama Guard).",
            "Блок 6 (ИИ-Инженер / Автоматизация): Разграничение прав к БД — проектирование систем разграничения прав доступа ИИ-агентов к базам данных.",
            "Блок 7 (Python-разработка): Безопасный запуск генерируемого моделью кода в изолированных песочницах E2B Sandbox или Daytona SDK.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование архитектуры безопасного взаимодействия агентов с ОС хоста.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Контроль и ограничение сетевых политик безопасности внутри песочниц.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Реализация обязательных шагов подтверждения человеком (HITL) перед критическими действиями."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Conceptual LLM Security — categorizing major large language models vulnerabilities.",
            "Block 2 (AI Engineer / Automation): Webhooks Sanitization — input filters checking webhook payloads for malicious content.",
            "Block 3 (AI Engineer / Automation): System Prompt Protections — prompt architecture guards against system leakage.",
            "Block 4 (AI Engineer / Automation): OWASP Top 10 for LLMs — practical implementation of safety standards.",
            "Block 5 (AI Engineer / Automation): Setting up Guardrails — configuring Llama Guard and NeMo input/output rails.",
            "Block 6 (AI Engineer / Automation): Database Permission Capping — isolating agent access to tables and API keys.",
            "Block 7 (Python Development): Executing dynamically generated Python code inside E2B Sandbox or Daytona SDK.",
            "Block 8 (AI Agent Builder / Agents & Harness): Security-first agentic operating system interaction paradigms.",
            "Block 9 (AI Agent Builder / Agents & Harness): Custom network policies and sandbox isolation boundaries.",
            "Block 10 (AI Agent Builder / Agents & Harness): Obligatory Human-in-the-loop triggers before file deletions or transactions."
        ]
    },
    22: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Docker в ИИ-разработке — создание оптимизированных Docker-файлов для упаковки систем.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Docker Compose — конфигурирование Docker Compose сетей для взаимодействия ИИ-сервисов.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Облачный деплой — развертывание контейнеров на Railway, Render, AWS, GCP.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Автоскейлинг — настройка систем горизонтального автоскейлинга под нагрузкой.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Балансировка и кэш — развертывание балансировщиков нагрузки и кэширования запросов к LLM.",
            "Блок 6 (ИИ-Инженер / Автоматизация): High Availability — проектирование архитектуры высокой доступности для корпоративных ИИ-решений.",
            "Блок 7 (Python-разработка): Разработка высокопроизводительных асинхронных веб-сервисов для ИИ-приложений на FastAPI.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Концепция надежного выполнения долгоживущих процессов (Durable Execution) при сбоях.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Интеграция систем автоматического оркестрирования шагов выполнения (Temporal / Inngest SDK).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Обеспечение идемпотентности шагов графа рассуждений агента при аварийных перезапусках."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Docker for AI Engineers — creating optimal Dockerfiles for multi-agent suites.",
            "Block 2 (AI Engineer / Automation): Docker Compose — configuring multi-container network routing.",
            "Block 3 (AI Engineer / Automation): Cloud Deployments — launching agent containers on Railway, Render, AWS, GCP.",
            "Block 4 (AI Engineer / Automation): Autoscaling Rules — horizontal and vertical scaling setup under load spikes.",
            "Block 5 (AI Engineer / Automation): Load Balancing & Cache — deploying routing gates and prompt cache layers.",
            "Block 6 (AI Engineer / Automation): High Availability — architecting resilient enterprise-grade production servers.",
            "Block 7 (Python Development): Building async Python backends for agent executions using FastAPI.",
            "Block 8 (AI Agent Builder / Agents & Harness): Durable Execution principles: keeping agents alive across hardware crashes.",
            "Block 9 (AI Agent Builder / Agents & Harness): Orchestrating long-running graphs using Temporal or Inngest SDK.",
            "Block 10 (AI Agent Builder / Agents & Harness): Idempotency laws: ensuring safe state replays in dynamic graphs."
        ]
    },
    23: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Инфраструктура медиа-стриминга — потоковая передача голоса и обработка аудиосигналов.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Телефония с ИИ — настройка телефонии (Twilio) для входящих и исходящих голосовых ассистентов.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Голосовые сценарии — динамическая маршрутизация хода телефонного вызова на основе ответов.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Комнаты LiveKit — конфигурирование комнат реального времени на платформе LiveKit.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Трансляция звука — подключение и обработка медиа-сокетов для трансляции звуковых потоков.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Сервисы STT/TTS — интеграция облачных и локальных сервисов распознавания и синтеза речи.",
            "Блок 7 (Python-разработка): Разработка высокопроизводительных скриптов реального времени на базе LiveKit Agent SDK.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Реализация голосового общения с суб-100мс задержкой через OpenAI Realtime API.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Оптимизация задержек передачи звука по WebSockets и управление аудиобуферами.",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Динамическая обработка перебиваний (Interruption Handling) со стороны пользователя."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Streaming Media Infrastructure — audio processing and WebSockets streaming.",
            "Block 2 (AI Engineer / Automation): Voice Bots telephony — connecting Twilio triggers for inbound and outbound calls.",
            "Block 3 (AI Engineer / Automation): Dynamic IVR — real-time routing based on verbal user responses.",
            "Block 4 (AI Engineer / Automation): LiveKit Rooms — configuring low-latency audio/video rooms in LiveKit.",
            "Block 5 (AI Engineer / Automation): WebSocket Audio — dynamic byte buffer streaming via media sockets.",
            "Block 6 (AI Engineer / Automation): Speech-to-Text & Text-to-Speech — integrating Cloud STT/TTS engines.",
            "Block 7 (Python Development): Writing real-time voice assistants scripts on LiveKit Agent Python SDK.",
            "Block 8 (AI Agent Builder / Agents & Harness): Sub-100ms Voice Loops using OpenAI Realtime API.",
            "Block 9 (AI Agent Builder / Agents & Harness): WebSocket latency optimizations and streaming audio buffers.",
            "Block 10 (AI Agent Builder / Agents & Harness): Dynamic voice interruption detection and execution cancel patterns."
        ]
    },
    24: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Упаковка услуг — позиционирование и упаковка услуг автоматизации бизнеса • Value-based pricing.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Фриланс-старт — составление профессиональных откликов и коммерческих предложений.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Loom-портфолио — запись эффективных Loom-видеодемонстраций созданных ИИ-решений.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Аудит процессов — разработка чек-листов аудита бизнес-процессов клиентов для автоматизации.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Договоры автоматизации — разработка юридических договоров на внедрение ИИ-систем в компании.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Запуск агентства — стратегия запуска собственного фриланс-агентства.",
            "Блок 7 (Python-разработка): Разработка комплексной программной архитектуры выпускного проекта на чистом Python с asyncio.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование ИИ-отдела компании: оркестрация нескольких LangGraph-графов.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Оптимизация бюджетов за счет агрессивного кэширования промптов (Prompt Caching).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Нагрузочное стресс-тестирование, предотвращение бесконечных циклов рассуждений."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Services Packaging — B2B value-based pricing and retainer models.",
            "Block 2 (AI Engineer / Automation): Freelancing Launch — writing premium Upwork proposals and client outreach templates.",
            "Block 3 (AI Engineer / Automation): Loom Demos — recording high-converting 3-minute project walkthroughs.",
            "Block 4 (AI Engineer / Automation): Process Audits — drafting operational checklists to find automation gaps.",
            "Block 5 (AI Engineer / Automation): Service Agreements — legal contracts designs for AI integrations retainers.",
            "Block 6 (AI Engineer / Automation): Agency Strategy — operational models for boutique AI automation agencies.",
            "Block 7 (Python Development): Developing the E2E async Python code engine for the Capstone multi-agent team.",
            "Block 8 (AI Agent Builder / Agents & Harness): Designing Agent Departments: orchestrating coordinating LangGraph runtimes.",
            "Block 9 (AI Agent Builder / Agents & Harness): Caching Optimizations — dynamic Prompt Caching rules to slash token fees.",
            "Block 10 (AI Agent Builder / Agents & Harness): Infinite loop breakers, performance stress tests, and Capstone delivery."
        ]
    },
    25: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Упаковка услуг — позиционирование и упаковка услуг автоматизации бизнеса • Value-based pricing.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Фриланс-старт — составление профессиональных откликов и коммерческих предложений.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Loom-портфолио — запись эффективных Loom-видеодемонстраций созданных ИИ-решений.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Аудит процессов — разработка чек-листов аудита бизнес-процессов клиентов для автоматизации.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Договоры автоматизации — разработка юридических договоров на внедрение ИИ-систем в компании.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Запуск агентства — стратегия запуска собственного фриланс-агентства.",
            "Блок 7 (Python-разработка): Разработка комплексной программной архитектуры выпускного проекта на чистом Python с asyncio.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование ИИ-отдела компании: оркестрация нескольких LangGraph-графов.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Оптимизация бюджетов за счет агрессивного кэширования промптов (Prompt Caching).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Нагрузочное стресс-тестирование, предотвращение бесконечных циклов рассуждений."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Services Packaging — B2B value-based pricing and retainer models.",
            "Block 2 (AI Engineer / Automation): Freelancing Launch — writing premium Upwork proposals and client outreach templates.",
            "Block 3 (AI Engineer / Automation): Loom Demos — recording high-converting 3-minute project walkthroughs.",
            "Block 4 (AI Engineer / Automation): Process Audits — drafting operational checklists to find automation gaps.",
            "Block 5 (AI Engineer / Automation): Service Agreements — legal contracts designs for AI integrations retainers.",
            "Block 6 (AI Engineer / Automation): Agency Strategy — operational models for boutique AI automation agencies.",
            "Block 7 (Python Development): Developing the E2E async Python code engine for the Capstone multi-agent team.",
            "Block 8 (AI Agent Builder / Agents & Harness): Designing Agent Departments: orchestrating coordinating LangGraph runtimes.",
            "Block 9 (AI Agent Builder / Agents & Harness): Caching Optimizations — dynamic Prompt Caching rules to slash token fees.",
            "Block 10 (AI Agent Builder / Agents & Harness): Infinite loop breakers, performance stress tests, and Capstone delivery."
        ]
    },
    26: {
        "ru": [
            "Блок 1 (ИИ-Инженер / Автоматизация): Упаковка услуг — позиционирование и упаковка услуг автоматизации бизнеса • Value-based pricing.",
            "Блок 2 (ИИ-Инженер / Автоматизация): Фриланс-старт — составление профессиональных откликов и коммерческих предложений.",
            "Блок 3 (ИИ-Инженер / Автоматизация): Loom-портфолио — запись эффективных Loom-видеодемонстраций созданных ИИ-решений.",
            "Блок 4 (ИИ-Инженер / Автоматизация): Аудит процессов — разработка чек-листов аудита бизнес-процессов клиентов для автоматизации.",
            "Блок 5 (ИИ-Инженер / Автоматизация): Договоры автоматизации — разработка юридических договоров на внедрение ИИ-систем в компании.",
            "Блок 6 (ИИ-Инженер / Автоматизация): Запуск агентства — стратегия запуска собственного фриланс-агентства.",
            "Блок 7 (Python-разработка): Разработка комплексной программной архитектуры выпускного проекта на чистом Python с asyncio.",
            "Блок 8 (Создатель ИИ-Агентов / Агенты & Harness): Проектирование ИИ-отдела компании: оркестрация нескольких LangGraph-графов.",
            "Блок 9 (Создатель ИИ-Агентов / Агенты & Harness): Оптимизация бюджетов за счет агрессивного кэширования промптов (Prompt Caching).",
            "Блок 10 (Создатель ИИ-Агентов / Агенты & Harness): Нагрузочное стресс-тестирование, предотвращение бесконечных циклов рассуждений."
        ],
        "en": [
            "Block 1 (AI Engineer / Automation): Services Packaging — B2B value-based pricing and retainer models.",
            "Block 2 (AI Engineer / Automation): Freelancing Launch — writing premium Upwork proposals and client outreach templates.",
            "Block 3 (AI Engineer / Automation): Loom Demos — recording high-converting 3-minute project walkthroughs.",
            "Block 4 (AI Engineer / Automation): Process Audits — drafting operational checklists to find automation gaps.",
            "Block 5 (AI Engineer / Automation): Service Agreements — legal contracts designs for AI integrations retainers.",
            "Block 6 (AI Engineer / Automation): Agency Strategy — operational models for boutique AI automation agencies.",
            "Block 7 (Python Development): Developing the E2E async Python code engine for the Capstone multi-agent team.",
            "Block 8 (AI Agent Builder / Agents & Harness): Designing Agent Departments: orchestrating coordinating LangGraph runtimes.",
            "Block 9 (AI Agent Builder / Agents & Harness): Caching Optimizations — dynamic Prompt Caching rules to slash token fees.",
            "Block 10 (AI Agent Builder / Agents & Harness): Infinite loop breakers, performance stress tests, and Capstone delivery."
        ]
    }
}

# Read existing curriculum.ts
with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Split into RU and EN sections deterministically using unique boundary
split_parts = content.split('\n  en: {\n    common: {\n')
if len(split_parts) != 2:
    print(f"CRITICAL ERROR: Failed to split curriculum.ts at split boundary. Length is {len(split_parts)}")
    exit(1)

ru_section, en_section = split_parts[0], split_parts[1]

# Put back unique split string prefix inside the second part so we reconstruct it correctly
en_section = "    common: {\n" + en_section

def replace_week_topics(section, week_num, new_topics):
    week_key = f'"week-{week_num}":'
    idx = section.find(week_key)
    if idx == -1:
        print(f"Error: week_key {week_key} not found!")
        return section
        
    topics_start_str = 'topics: ['
    topics_idx = section.find(topics_start_str, idx)
    if topics_idx == -1:
        print(f"Error: 'topics: [' not found after {week_key}!")
        return section
        
    end_bracket_idx = section.find(']', topics_idx)
    if end_bracket_idx == -1:
        print(f"Error: ']' not found after 'topics: ['!")
        return section
        
    # Construct new topics array content
    formatted_topics = "topics: [\n"
    for topic in new_topics:
        safe_topic = topic.replace('"', '\\"')
        formatted_topics += f'          "{safe_topic}",\n'
    formatted_topics = formatted_topics.rstrip(",\n") + "\n        ]"
    
    # Do replacement in section
    return section[:topics_idx] + formatted_topics + section[end_bracket_idx + 1:]

# Process RU and EN sections
for week_num, languages_data in WEEKLY_BLOCKS.items():
    ru_section = replace_week_topics(ru_section, week_num, languages_data["ru"])
    en_section = replace_week_topics(en_section, week_num, languages_data["en"])

# Combine back and write
updated_content = ru_section + '\n  en: {\n' + en_section
with open(CURRICULUM_PATH, "w", encoding="utf-8") as f:
    f.write(updated_content)

print("SUCCESS: Full curriculum.ts database successfully refactored with the new 10-block high-density structures for RU and EN!")
