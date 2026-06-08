# Week 10: OpenAI & Anthropic SDKs: Structured Outputs

## Block 1: REST JSON Schema — designing robust data models for API payloads.

Welcome to Week 10: *OpenAI & Anthropic SDKs: Structured Outputs*. Throughout Week 9, you engineered high-performance, asynchronous Python scripts capable of parallelizing hundreds of tasks, bypassing Web Application Firewalls, and scraping the dynamic web. You have constructed a massively scalable execution layer. However, raw execution speed is entirely useless if the data traversing your pipeline is corrupt. 

In the realm of Enterprise AI Architecture, Large Language Models (LLMs) are inherently probabilistic, yet our software systems—our databases, our CRMs, and our REST APIs—are strictly deterministic. If an LLM outputs `"age": "thirty"` instead of `"age": 30`, or forgets a closing bracket, the entire pipeline crashes. As emphasized in the foundational materials, "you don't know JavaScript object notation you are going to have to learn some things like types and objects and what variables are and stuff like that". 

To bridge the gap between stochastic neural networks and deterministic software, we must enforce rigid boundaries. In this exhaustive, voluminous deep-dive, we will master **REST JSON Schemas**. We will explore how to architect robust data models that force LLMs to output clean, perfectly typed API payloads, transitioning your skill set from generating "chat responses" to generating actionable, production-grade microservice data.

---

### Deep Theoretical Analysis: The Physics of Structured Outputs and JSON Schemas

Before writing execution code, an AI Architect must understand the linguistic and structural physics of JSON inside an LLM's context window. 

#### 1. The Universality of JSON in LLM Training
JSON (JavaScript Object Notation) is not just a data format; it is a universal language deeply embedded in the weights of modern models. "Pretty much every single large language model or like chat gbt cloud 3.5 they're all trained on JSON and they all understand it so well because it's universal". When you instruct an LLM to output JSON, you are tapping into highly optimized pathways within the neural network. This allows the model to map conceptual relationships into "literally just key value pairs". 

#### 2. The Power of JSON Schemas for Input and Output
A JSON Schema is a declarative contract that defines the expected structure, data types, and required fields of a JSON object. While most developers think of schemas only for validating outputs, they are equally powerful for structuring inputs. "A JSON Schema defines the expected structure and data types of your JSON input. By providing a schema, you give the LLM a clear blueprint of the data it should expect, helping it focus its attention on the relevant information and reducing the risk of misinterpreting the input". 

By defining exact field names, types, and descriptions, you guide the model's reasoning process. "Schema definitions guide the model. Field names, types, and descriptions specify exactly what format the output should adhere to". This is essentially a form of highly structured prompt engineering.

#### 3. The "Verification Gap" and Deterministic Control
In *Lecture 01. Сильные модели не означают надёжного исполнения* (Strong models do not mean reliable execution), the concept of the "Verification Gap" is introduced. This is the chasm between the model's confidence in its output and the actual correctness of that output. When an agent generates free-form text, verifying its correctness programmatically is nearly impossible. By constraining the agent to a JSON Schema, we close the Verification Gap. If the schema demands a `boolean` for the field `"is_compliant"`, and the model returns a string, the system can instantly flag the error. "Once you have structure to your data you can obviously um you know forward that over to some software platform parse out the keys add the values to to other variables".

#### 4. The Token Economy of Structured Data
While JSON is powerful, it introduces financial and performance overhead. "The structured nature of JSON, while beneficial for parsing and use in applications, requires significantly more tokens than plain text, leading to increased processing time and higher costs. Furthermore, JSON's verbosity can easily consume the entire output window...". Every curly brace `{}`, bracket `[]`, and quotation mark `"` consumes tokens. An architect must balance the need for deep structure against the unit economics of the API call, ensuring schemas are comprehensive but not unnecessarily bloated.

---

### ASCII Architecture Schema: The Deterministic Payload Pipeline

The following Directed Acyclic Graph (DAG) illustrates how a JSON Schema acts as a cognitive mold, forcing the unstructured reasoning of an LLM into a strict REST API payload.

```ascii
=============================================================================================
 ENTERPRISE REST JSON SCHEMA HARNESS
=============================================================================================

[ 1. UNSTRUCTURED INPUT ] -> Raw PDF text, scraped HTML, or messy user email.
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. SCHEMA DEFINITION LAYER (The Contract) |
| - Defines "type": "object" |
| - Defines strict "properties": {"first_name": {"type": "string"},...} |
| - Maps "descriptions" as localized prompt instructions. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. LLM EXECUTION ENGINE (OpenAI / Anthropic SDK) |
| - Injects the Unstructured Input. |
| - Injects the JSON Schema into the `response_format` or system prompt. |
| - LLM aligns probabilistic generation with deterministic constraints. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. PAYLOAD VERIFICATION & REPAIR |
| - Checks for truncation or missing brackets (json-repair). |
| - Validates data types against the schema. |
+-----------------------------------------------------------------------------------------+
 / (Validation SUCCESS) \ (Validation FAILED / TRUNCATED)
 v v
[ 6. REST API DISPATCH ] +--------------------------------------------------+
- Executes `requests.post()` | 5. FALLBACK / SELF-HEALING LOOP |
- Clean JSON payload delivered. | - Uses `json-repair` to fix brackets. |
- 200 OK Response from Server. | - Re-prompts LLM if data types are corrupt. |
 +--------------------------------------------------+
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will now engineer a production-grade Python script that defines a strict JSON Schema and uses the OpenAI SDK to enforce this schema on unstructured data. We will simulate extracting e-commerce product data to populate a REST API payload.

#### Step 1: Architecting the JSON Schema
A schema must be explicit. Notice how the `description` fields act as micro-prompts for the LLM.

```python
import json
import logging
from openai import OpenAI
import os

# Initialize observability
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [JSON_SCHEMA_HARNESS] - %(message)s')

# Instantiate the client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Step 1: Define the strict JSON Schema for the REST API Payload
# Based on Snippet 5 from "Prompt Engineering" 
PRODUCT_EXTRACTION_SCHEMA = {
 "name": "ecommerce_product_extraction",
 "description": "Extracts structured product attributes from unstructured marketing copy.",
 "schema": {
 "type": "object",
 "properties": {
 "name": {
 "type": "string", 
 "description": "The exact product name."
 },
 "category": {
 "type": "string", 
 "description": "Product category. Must map to the closest standard retail category."
 },
 "price": {
 "type": "number", 
 "description": "Product price in USD, strictly as a float. E.g. 19.99"
 },
 "features": {
 "type": "array",
 "items": {"type": "string"},
 "description": "A list of 3 to 5 key features or selling points of the product."
 },
 "release_date": {
 "type": "string", 
 "description": "Date the product was released. Must be formatted strictly as YYYY-MM-DD."
 }
 },
 "required": ["name", "category", "price", "features"] # release_date is optional
 }
}
```

#### Step 2: The LLM Execution Function
We will use the `response_format` parameter introduced by OpenAI to mathematically guarantee that the output matches our schema perfectly. As advised in the documentation, "Ensure JSON data emitted from a model conforms to a JSON schema".

```python
def extract_structured_product(unstructured_text: str) -> dict:
 """
 Executes the LLM call, forcing the output to bind entirely to the defined JSON Schema.
 """
 logging.info("Initiating strict JSON Schema extraction pipeline...")
 
 system_instruction = (
 "You are an elite data extraction agent. "
 "Your sole task is to extract information from the user's text and format it "
 "STRICTLY according to the provided JSON Schema. Do not include markdown formatting or conversational filler."
 )
 
 try:
 response = client.chat.completions.create(
 model="gpt-4o",
 temperature=0.0, # Zero temperature is critical for deterministic schema adherence
 messages=[
 {"role": "system", "content": system_instruction},
 {"role": "user", "content": unstructured_text}
 ],
 # Here we enforce the Structured Output constraint
 response_format={
 "type": "json_schema",
 "json_schema": PRODUCT_EXTRACTION_SCHEMA
 }
 )
 
 # The model is forced by the API to return valid JSON matching the schema
 raw_json_string = response.choices.message.content
 logging.info("LLM successfully generated schema-compliant JSON.")
 
 # Parse into a native Python dictionary for REST dispatch
 payload = json.loads(raw_json_string)
 return payload

 except json.JSONDecodeError as je:
 logging.error(f"JSON Parsing Failed: {str(je)}")
 raise
 except Exception as e:
 logging.error(f"Execution Error: {str(e)}")
 raise

# ==========================================
# Execution Environment
# ==========================================
if __name__ == "__main__":
 messy_marketing_copy = """
 Introducing the all-new AeroGlide Wireless Headphones! Dropping on November 15th, 2026, 
 these bad boys are going to revolutionize your commute. They feature active noise cancellation, 
 a 40-hour battery life, and ultra-plush memory foam earcups. Grab yours for just $149.50.
 """
 
 extracted_data = extract_structured_product(messy_marketing_copy)
 
 print("\n=== FINAL REST API PAYLOAD ===")
 print(json.dumps(extracted_data, indent=4))
 
 # In a real system, you would now dispatch this payload:
 # response = requests.post("[Ссылка](https://api.inventory.com/v1/products"), json=extracted_data)
```

By defining the schema externally and injecting it into the `response_format`, we guarantee that the output contains the exact keys our REST API endpoint expects. "By preprocessing your data and instead of providing full documents only providing both the schema and the data, you give the LLM a clear understanding of the product's attributes... making it much more likely to generate an accurate and relevant description".

---

### Realistic Business Applications & Unit Economics

Understanding and deploying JSON Schemas separates hobbyist prompting from highly lucrative B2B software engineering. 

**1. Scalable Lead Enrichment & Personalization**
Imagine building an automated outbound sales engine. You scrape a target's LinkedIn profile and company website. If you ask an LLM to "summarize this person," you receive unpredictable paragraphs. You cannot build a system on paragraphs. Instead, you define a JSON Schema with fields like `{"decision_maker_status": "boolean", "recent_company_news": "string", "personalized_icebreaker": "string"}`. 
As Nick Saraev outlines in his practical application: "you are asked to parse that out turn that into the above object... go deep into detail for website contexts write at least two paragraphs for person context... use all the website and information about the provided person to create three interesting points". When the LLM outputs this exact JSON structure, your pipeline can easily inject the `personalized_icebreaker` directly into your email sending software via a REST API webhook. "This is exactly what a real functional system that you guys can charge money for looks like".

**2. Legal and Medical Document Parsing**
In industries with high compliance requirements, free-form AI text is a liability. A LegalTech company analyzing NDA contracts must extract specific entities (Party A, Party B, Jurisdiction, Expiration Date). By crafting a rigid JSON schema, the AI Architect forces the model to extract *only* these points. The resulting JSON object can then be safely ingested into a PostgreSQL database or a React frontend dashboard. The schema acts as an unyielding filter, ensuring no hallucinated legal advice makes it into the final product output.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Implementing JSON Schemas is powerful, but it introduces unique edge cases associated with context limits and strict validation.

> [!CAUTION] 
> **Token Truncation and the Malformed JSON Trap** 
> **The Problem:** If you request a massive JSON object (e.g., extracting 50 separate fields from a 100-page document), the LLM may hit its `max_tokens` output limit before it finishes writing the JSON. "JSON's verbosity can easily consume the entire output window, becoming especially problematic when the generation is abruptly cut off due to token limits. This truncation often results in invalid JSON, missing crucial closing braces or brackets, rendering the output unusable". 
> **Harness Mitigation:** You must implement defensive parsing. Instead of immediately failing, utilize tools like the `json-repair` library in Python. "This library intelligently attempts to automatically fix incomplete or malformed JSON objects, making it a crucial ally when working with LLM-generated JSON, especially when dealing with potential truncation issues". 

> [!WARNING] 
> **Schema Rigidity and Hallucinated Defaults** 
> **The Error:** You define a schema field: `"contract_end_date": {"type": "string"}` and mark it in the `required` array. However, the document provided to the LLM *does not contain* an end date. Because the schema forces the LLM to output that field, the LLM will often hallucinate a fake date just to satisfy the schema contract. 
> **Diagnostic Loop:** Never back an LLM into a corner. If a field is required, update your schema description to explicitly permit null or default values: `"description": "The contract end date. If absolutely no date is found in the text, output 'NOT_FOUND'."` Additionally, you can utilize the `Optional` typing or remove the field from the `required` array entirely, allowing the model to simply omit keys it cannot factually populate.

> [!NOTE] 
> **The Instruction Bloat Conundrum** 
> **The Problem:** Adding massive JSON Schemas with exhaustive descriptions inside the system prompt consumes thousands of input tokens. If you are processing 10,000 documents a day, passing that massive schema repeatedly will drain your financial budget. 
> **Solution:** Leverage **Prompt Caching** (supported by both Anthropic and OpenAI). By placing the heavy JSON Schema at the very beginning of the system prompt and marking it as a cacheable block, the API provider will store the schema in memory. Subsequent API calls utilizing the exact same schema will see their input token costs slashed by up to 90%, preserving both your schema integrity and your profit margins.

By mastering REST JSON Schemas, you establish total dominance over the stochastic nature of artificial intelligence. You dictate the exact terms of engagement, forcing the model to bend to the architectural needs of your software environment. You no longer build chatbots; you build deterministic, highly reliable cognitive microservices.

This sets the foundation for Week 10. In our next blocks, we will explore how to integrate these concepts seamlessly into Pydantic V2 for even deeper Python-native type checking and runtime validation. Are you ready to proceed?

---

## Block 2: Structured Data Validation — parsing and validating multi-layered JSON payloads.

Welcome to Block 2 of Week 10. In the previous block, we explored the theoretical and structural necessity of designing REST JSON schemas to act as cognitive molds for our Large Language Models (LLMs). We learned how to constrain a stochastic model into generating a deterministic payload. However, generating the payload is only half the battle. As mandated in the *AI Engineer roadmap* curriculum, an AI Automation Builder must master writing a "clear system prompt that returns stable structured output". But what happens when that "stable" output is a deeply nested, multi-layered JSON object spanning hundreds of lines, and the model subtly hallucinates a data type deep within layer four?

If you blindly pass an unvalidated, multi-layered JSON response directly into your database or a downstream client API, your system will inevitably experience catastrophic runtime crashes. To understand why, we must turn to *Lecture 01. Сильные модели не означают надёжного исполнения* (Strong models do not mean reliable execution). This lecture introduces the fundamental concept of the "Verification Gap: разрыв между уверенностью агента в своей работе и реальной корректностью" (Verification Gap: the chasm between the agent's confidence in its work and the actual correctness). 

In this exhaustive, production-grade deep-dive, we will close this Verification Gap. Before we introduce heavy third-party frameworks like Pydantic in Block 7, an elite AI Architect must first understand how to natively parse, traverse, and strictly validate multi-layered JSON payloads using pure Python. We will engineer a robust validation middleware that structurally guarantees the integrity of every nested dictionary, array, and primitive type before it ever touches your core business logic.

---

### Deep Theoretical Analysis: The Anatomy of Multi-Layered Validation

To build enterprise-grade cognitive architectures, we must shift our perspective. LLMs are not traditional APIs; they do not have guaranteed return types. They are probabilistic text engines. When dealing with multi-layered data—such as a generated financial report containing lists of transactions, which in turn contain nested dictionaries of line items—the probability of a structural hallucination increases exponentially with depth.

#### 1. The Multi-Layered Hallucination Problem
When an LLM is tasked with generating nested JSON, it must maintain a massive internal state of bracket balancing and type adherence. Common structural hallucinations include:
* **Type Coercion Failures:** The schema demands a nested `integer` for `"user_id"`, but the model generates a `string` `"12345"`.
* **Array Flattening:** The schema demands a list of dictionaries `[{"role": "admin"}]`, but the model hallucinates a single dictionary `{"role": "admin"}`.
* **Phantom Keys:** The model invents highly plausible, but schema-violating keys deep within a nested object (e.g., adding `"middle_name"` inside a `"user_profile"` object that only accepts `"first_name"` and `"last_name"`).

#### 2. Verification via End-to-End Testing
As stated in *Lecture 10. Только сквозное тестирование — настоящая верификация* (Only end-to-end testing is true verification), we cannot trust the model's output just because the top-level keys look correct. A robust Harness must explicitly verify every leaf node of the JSON tree. "Without observability, agents make decisions in uncertainty... retries turn into blind wandering". Your validation logic *is* that observability mechanism. It provides the exact stack trace of *where* the LLM deviated from the schema.

#### 3. Context Compaction and Nested Payloads
When working with "deep agent research analysts", you will frequently spawn sub-agents with isolated contexts. These sub-agents return "compressed summaries to the parent". This handoff is almost always executed via a multi-layered JSON payload. If the orchestrator agent lacks strict validation logic to parse the sub-agent's nested arrays of research citations, the entire orchestration pipeline breaks down. The validation layer acts as a strictly typed border control checkpoint between autonomous agents.

---

### ASCII Architecture Schema: Multi-Layered Payload Validator

The following Directed Acyclic Graph (DAG) illustrates the lifecycle of a multi-layered JSON payload as it moves from the LLM, through our strict Python validation middleware, and into the clean execution state.

```ascii
=============================================================================================
 ENTERPRISE MULTI-LAYERED JSON VALIDATION HARNESS
=============================================================================================

[ 1. RAW LLM OUTPUT ] 
`{"company": {"name": "Acme", "employees": [{"id": "1A", "role": "CEO"}]}}`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. NATIVE PARSING LAYER |
| - `json.loads(raw_output)` |
| - Traps `json.JSONDecodeError` (e.g., missing closing brackets). |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. RECURSIVE SCHEMA VALIDATOR (The Middleware) |
| -> LEVEL 1: Root Object Check (Is it a dictionary?) |
| -> LEVEL 2: Key Existence Check (Does `"company"` exist?) |
| -> LEVEL 3: Nested Array Check (Is `"employees"` a list?) |
| -> LEVEL 4: Leaf Node Type Check (Is `"id"` an integer? Fails if string!) |
+-----------------------------------------------------------------------------------------+
 | (If ANY level fails) | (If ALL levels pass)
 v v
[ 4A. EXCEPTION GENERATION ] +----------------------------------------+
- Raises custom `SchemaValidationError`. | 4B. CLEAN STATE HANDOFF |
- Captures exact path of failure: | - Payload is cryptographically trusted.|
 `"company -> employees -> -> id"` | - Dispatched to Database / REST API. |
- Routes to Diagnostic Loop. +----------------------------------------+
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready recursive validation harness in Python. This code does not rely on external libraries. It demonstrates a deep understanding of recursive traversal, type checking, and detailed error tracking—essential skills for an AI Automation Architect.

#### Step 1: Defining the Blueprint Schema
We must define our target schema structurally. This blueprint dictates the exact expected layout of our multi-layered payload.

```python
import json
import logging
from typing import Any, Dict, List

# Lecture 11: Make the agent runtime observable
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VALIDATION_HARNESS] - %(message)s')

# A complex, multi-layered blueprint describing the expected data types
EXPECTED_ENTERPRISE_BLUEPRINT = {
 "project_name": str,
 "budget_usd": float,
 "team": list, # Expecting an array
 "milestones": { # Nested dictionary
 "planning": str,
 "execution": str,
 "completed": bool
 }
}

# We also need to define the structure INSIDE the arrays
EXPECTED_TEAM_MEMBER_BLUEPRINT = {
 "emp_id": int,
 "name": str,
 "role": str
}
```

#### Step 2: Engineering the Recursive Validator
The following Python class parses the raw LLM string and recursively digs through the layers, comparing the payload against our blueprint. It traps type mismatches and missing keys, generating precise error messages indicating the exact layer where the hallucination occurred.

```python
class SchemaValidationError(Exception):
 """Custom exception raised when the LLM payload violates structural boundaries."""
 pass

class MultiLayerValidator:
 """
 Enterprise middleware for validating deep, multi-layered JSON outputs natively.
 Ensures absolute data integrity before downstream execution.
 """
 
 @staticmethod
 def _validate_layer(payload: Any, blueprint: Any, path: str = "root") -> None:
 """
 Recursively checks payload structures against the defined blueprint.
 """
 # 1. Dictionary Validation
 if isinstance(blueprint, dict):
 if not isinstance(payload, dict):
 raise SchemaValidationError(f"Type mismatch at '{path}': Expected dict, got {type(payload).__name__}")
 
 for key, expected_type in blueprint.items():
 if key not in payload:
 raise SchemaValidationError(f"Missing required key at '{path}': '{key}'")
 
 # Recursive call for nested layers
 MultiLayerValidator._validate_layer(payload[key], expected_type, f"{path}.{key}")
 
 # 2. List Validation (Validating items inside the array)
 elif blueprint is list:
 if not isinstance(payload, list):
 raise SchemaValidationError(f"Type mismatch at '{path}': Expected list, got {type(payload).__name__}")
 
 # If it's the specific 'team' array, validate its internal dictionaries
 if path == "root.team":
 for index, item in enumerate(payload):
 MultiLayerValidator._validate_layer(item, EXPECTED_TEAM_MEMBER_BLUEPRINT, f"{path}[{index}]")
 
 # 3. Primitive Type Validation (Leaf nodes)
 elif isinstance(blueprint, type):
 if not isinstance(payload, blueprint):
 raise SchemaValidationError(f"Type mismatch at '{path}': Expected {blueprint.__name__}, got {type(payload).__name__} (Value: {payload})")
 
 else:
 raise SchemaValidationError(f"Invalid blueprint configuration at '{path}'")

 @classmethod
 def parse_and_verify(cls, raw_llm_string: str) -> Dict[str, Any]:
 """
 The main ingestion method. Traps malformed JSON and triggers deep validation.
 """
 logging.info("Ingesting raw LLM payload for structural verification...")
 
 try:
 # Step 1: Ensure it is actually valid JSON
 parsed_json = json.loads(raw_llm_string)
 except json.JSONDecodeError as e:
 logging.error("Catastrophic Syntax Failure: Payload is not valid JSON.")
 raise SchemaValidationError(f"JSON Syntax Error: {str(e)}")
 
 # Step 2: Traverse and validate the multi-layered structure
 cls._validate_layer(parsed_json, EXPECTED_ENTERPRISE_BLUEPRINT)
 
 logging.info("Verification complete. Payload perfectly matches the multi-layered schema.")
 return parsed_json

# ==========================================
# Execution Environment
# ==========================================
if __name__ == "__main__":
 # Simulating a slightly hallucinated LLM payload
 # Notice the subtle error: "emp_id" is a string "101" instead of an integer.
 hallucinated_llm_output = """
 {
 "project_name": "Project Alpha",
 "budget_usd": 150000.50,
 "team": [
 {
 "emp_id": "101", 
 "name": "Sarah Connor",
 "role": "Lead Architect"
 }
 ],
 "milestones": {
 "planning": "Q1 2026",
 "execution": "Q2 2026",
 "completed": false
 }
 }
 """
 
 try:
 # The Harness executes the verification
 clean_data = MultiLayerValidator.parse_and_verify(hallucinated_llm_output)
 except SchemaValidationError as critical_error:
 print(f"\n[BLOCKED BY HARNESS] Validation Gap Detected: {critical_error}")
 # Output: [BLOCKED BY HARNESS] Validation Gap Detected: Type mismatch at 'root.team.emp_id': Expected int, got str (Value: 101)
```

By engineering this `MultiLayerValidator`, we have achieved a critical architectural goal: we have isolated the failure. We did not wait for the database insertion script to crash with a cryptic SQL exception. We caught the exact variable `root.team.emp_id` that violated our architectural contract, fulfilling the mandate that "Only end-to-end testing is true verification".

---

### Realistic Business Applications & Unit Economics

Mastering multi-layered validation is what separates junior scripters from elite developers capable of charging $10k+ for robust automation solutions.

**1. Enterprise E-Commerce Data Ingestion**
A retail client tasks you with building an AI pipeline that reads competitor websites and extracts product catalogs into their backend. A product object is incredibly deep: `Product -> Variations[] -> Pricing{} -> Dimensions{}`. If you use standard prompt instructions without strict multi-layered validation, the LLM will eventually hallucinate. It might place the `Pricing` object *outside* of the `Variations` array. If your Python script blindly forwards this malformed payload to the client's Shopify API, you will overwrite the wrong prices and destroy the client's store. Your recursive validation middleware protects the client's inventory and your agency's reputation by strictly verifying the tree depth before any API dispatch occurs.

**2. Multi-Agent Orchestration (The "Orchestrator-Worker" Pattern)**
According to the principles of context engineering, scaling AI systems requires dividing tasks among sub-agents. You build a `Financial_Review_Agent` (Worker) that analyzes a 100-page earnings report and returns a complex array of JSON objects summarizing revenue risks to the `CEO_Agent` (Orchestrator). If the Worker agent hallucinates the structure of its return payload, the CEO agent's code will crash when attempting to iterate over the data. By injecting our `MultiLayerValidator` into the communication channel between the two agents, the system guarantees that agents only exchange mathematically sound data structures.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Validating stochastic output is inherently combative. You are forcing chaos into order, and the LLM will occasionally fight back.

> [!CAUTION] 
> **The Token Feeding Death Spiral** 
> **The Error:** In his essay "Как я перестал «кормить» нейросеть токенами" (How I stopped "feeding" the neural network tokens), Stepan Kozhevnikov details a fatal trap. If your `MultiLayerValidator` catches an error, and your script blindly loops a retry request 20 times saying "Fix this JSON", you will burn thousands of tokens and hundreds of dollars in minutes on a deeply flawed prompt that the LLM fundamentally cannot resolve. 
> **Harness Mitigation:** Never use infinite retry loops for validation failures. If the validation catches a structural hallucination, retry a maximum of 3 times. Crucially, when you retry, you must feed the specific error message generated by our validator (`"Type mismatch at 'root.team.emp_id'"`) back into the prompt so the model knows exactly *where* in the deep layer it made the mistake.

> [!WARNING] 
> **Boolean vs. String Coercion** 
> **The Problem:** LLMs are notorious for struggling with native JSON booleans. Instead of outputting the boolean `false`, they frequently output the string `"false"`, or even `"False"`. If your blueprint strictly checks for `bool`, it will crash unnecessarily on what is essentially a formatting quirk. 
> **Diagnostic Loop:** Your native Python validation layer should implement intelligent, safe coercion. In your `_validate_layer` method, if the blueprint expects a `bool` and receives a `str`, the code should safely check `if payload.lower() == "false": payload = False` before explicitly raising a `SchemaValidationError`.

> [!NOTE] 
> **The Null-Value Edge Case** 
> Often, an LLM correctly parses a nested structure but determines a specific value does not exist in the source text. It outputs `null` (which translates to `None` in Python). If your blueprint explicitly expects a `str`, your code will crash. Always explicitly support `Optional` typing by modifying your validation logic to accept `None` as a valid leaf node, preventing your pipeline from crashing due to legitimately missing data.

By implementing strict, multi-layered data validation natively in Python, you have established absolute control over the LLM's output. You have closed the Verification Gap. 

This deep understanding of nested parsing paves the way for Block 3, where we will move beyond validating the payload and focus on validating the network itself—mastering the art of trapping HTTP rate limits and executing graceful pipeline degradation.

---

## Block 3: Handling API Exceptions — capturing network failures and rate limits headers.

Welcome to Block 3 of Week 10. In the previous block, we engineered recursive validation middleware to ensure that the multi-layered JSON outputs from our Large Language Models (LLMs) perfectly match our deterministic schemas. You have successfully closed the semantic gap between probabilistic text generation and rigid database structures. However, your cognitive architecture must now face an entirely different class of chaos: the physical reality of the internet.

As an AI Automation Architect, you must internalize a brutal truth: APIs fail. Networks drop. Rate limits are aggressively enforced. As explicitly warned in the foundational principles of harness engineering, "Strong models do not mean reliable execution". If you write a flawless prompt and construct a perfect Pydantic schema, but fail to programmatically catch an `HTTP 429 Too Many Requests` or an `HTTP 502 Bad Gateway`, your Python script will trigger a fatal exception, your agent will die mid-thought, and your automated pipeline will collapse. 

In this voluminous, enterprise-grade deep-dive, we will master **API Exception Handling**. We will move beyond naive `try/except` blocks and learn to deeply inspect HTTP response status codes and HTTP headers. We will build systems that do not just "fail gracefully," but autonomously self-heal by reading rate limit headers, pausing execution, and intelligently retrying, effectively bringing the "self-annealing" resilience of advanced agent frameworks into your raw Python scripts.

---

### Deep Theoretical Analysis: The Physics of API Failures and Rate Limits

To build a resilient execution layer—what the roadmap defines as the core of "Tool dispatch... recovery, retries" —we must mathematically classify the types of failures our LLM SDKs will encounter. 

#### 1. The Taxonomy of HTTP Status Codes
When the OpenAI or Anthropic SDK makes a network request, it acts as an HTTP client. The server responds with standardized HTTP response status codes. An architect must differentiate between errors that can be retried and errors that are fatal:
* **Transient Errors (Server-Side 5xx & Network):** `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable`, `504 Gateway Timeout`. These mean the LLM provider's infrastructure is currently unstable. These *must* be caught and retried.
* **Rate Limits (429 Too Many Requests):** You have exceeded your tier's allowed tokens per minute (TPM) or requests per minute (RPM). This is a transient error, but retrying immediately will result in a longer ban.
* **Fatal Client Errors (4xx, excluding 429):** `400 Bad Request` (malformed JSON payload), `401 Unauthorized` (invalid API key), `404 Not Found`. Retrying these is a critical anti-pattern. If the API key is revoked, retrying 50 times simply burns CPU cycles. The script must crash immediately (fail-fast) and alert a human.

#### 2. The Superiority of Header-Driven Backoff
In Week 9, we built an Exponential Backoff decorator. While exponential backoff is the industry standard for generic network failures, it is technically sub-optimal for `429 Rate Limit` errors. Why guess how long to wait when the server explicitly tells you?
Modern REST APIs include specific HTTP Headers in their 429 error responses. These headers typically include:
* `x-ratelimit-remaining-tokens`: How much budget you have left.
* `x-ratelimit-reset-requests`: The exact timestamp or time delta (in seconds) until your ban is lifted.
By parsing the `x-ratelimit-reset` header, your Python script can execute an exact `time.sleep()` for the precise number of seconds required, maximizing throughput without violating the provider's constraints.

#### 3. Actionable Feedback and the Diagnostic Loop
When an API call within a custom agent tool fails, the worst thing you can do is let the Python script exit. According to the "Self-annealing" framework, an agent "will not crash it will instead pause, read the error message... and then hopefully it will fix it... then try again". 
Crucially, as outlined in *Lecture 09. Предотвращение преждевременных заявлений о завершении* and *Lecture 10. Только сквозное тестирование — настоящая верификация*, "error messages for agents must include instructions for fixing them". If your API call fails because of a context window overflow, catching the error and returning `"Error 400"` to the agent is useless. You must return actionable feedback: `"Error 400: Context length exceeded. You must summarize your previous observations to compress your context before retrying."`

---

### ASCII Architecture Schema: Header-Driven Resilience Harness

The following Directed Acyclic Graph (DAG) illustrates how our exception-handling middleware intercepts network failures, parses headers, and orchestrates the recovery loop.

```ascii
=============================================================================================
 ENTERPRISE API EXCEPTION & RATE LIMIT HARNESS
=============================================================================================

[ 1. AI ORCHESTRATOR ] -> Calls `client.chat.completions.create(...)`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. SDK EXECUTION LAYER (Network Request) |
+-----------------------------------------------------------------------------------------+
 | (HTTP 200 OK) | (HTTP 4xx / 5xx Exception)
 v v
[ 3. RETURN CLEAN DATA ] +---------------------------------------------------+
 | 4. EXCEPTION CLASSIFICATION ROUTER |
 | -> `except openai.RateLimitError:` |
 | -> `except openai.APIConnectionError:` |
 | -> `except openai.BadRequestError:` |
 +---------------------------------------------------+
 | |
 (Transient / 429) | | (Fatal / 401 / 400)
 v v
 +---------------------------------------+ [ 6. FATAL PROPAGATION ]
 | 5. HEADER PARSING & RECOVERY | - Alert Human Operator.
 | - Extract `x-ratelimit-reset` header. | - Route task to Dead Letter Queue.
 | - Log observability metric. | - Document in Runbook.
 | - Execute exact `asyncio.sleep()`. |
 | - Loop back to Step 2. |
 +---------------------------------------+
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-grade wrapper around the OpenAI SDK. This code demonstrates how to precisely catch SDK-specific exceptions, parse the raw HTTP response headers embedded within those exceptions, and format actionable error strings for agent diagnostic loops.

#### Step 1: The Resilient SDK Wrapper
This class acts as a protective proxy between your application logic and the OpenAI API. It implements header-driven waiting and actionable error formatting.

```python
import os
import time
import logging
from typing import Any, Dict
import openai
from openai import OpenAI

# Observability is mandatory (Lecture 11)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [API_HARNESS] - %(levelname)s: %(message)s')

class ResilientOpenAIClient:
 """
 An enterprise wrapper for the OpenAI SDK that captures network failures,
 parses rate limit headers, and prevents fatal pipeline crashes.
 """
 def __init__(self, max_retries: int = 3):
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 self.max_retries = max_retries

 def execute_chat_completion(self, model: str, messages: list, **kwargs: Any) -> str:
 """
 Executes a chat completion with deep exception trapping and header-driven backoff.
 """
 attempt = 0
 
 while attempt <= self.max_retries:
 try:
 # 1. Attempt the native API call
 response = self.client.chat.completions.create(
 model=model,
 messages=messages,
 **kwargs
 )
 return response.choices.message.content

 # 2. Trap Rate Limits (HTTP 429)
 except openai.RateLimitError as e:
 attempt += 1
 logging.warning(f"RateLimitError encountered on attempt {attempt}/{self.max_retries}.")
 
 if attempt > self.max_retries:
 raise Exception("Maximum rate limit retries exhausted. Pipeline halted.")
 
 # Extract exact reset time from HTTP headers (e.g., 'x-ratelimit-reset-requests')
 # Fallback to standard exponential backoff if header is missing
 headers = e.response.headers if e.response else {}
 reset_time_str = headers.get('x-ratelimit-reset-tokens', '5s') 
 
 # Parse the time string (e.g., "5s", "2m", "10ms")
 sleep_duration = self._parse_reset_header(reset_time_str)
 
 logging.info(f"Header parsed. Suspending execution for {sleep_duration} seconds to respect API limits.")
 time.sleep(sleep_duration)

 # 3. Trap Transient Network/Server Errors (HTTP 500, 502, 503)
 except (openai.APIConnectionError, openai.InternalServerError) as e:
 attempt += 1
 logging.error(f"Transient Server Error: {str(e)}. Retrying in {2 ** attempt} seconds...")
 time.sleep(2 ** attempt)

 # 4. Trap Fatal Client Errors (HTTP 400, 401)
 except openai.BadRequestError as e:
 # Implementing Lecture 10: Error messages must include fix instructions
 diagnostic_feedback = (
 f"Fatal BadRequestError: {str(e)}. "
 f"FIX INSTRUCTION: Check your input payload. Ensure the context length "
 f"does not exceed the model's maximum limit, and verify that the structured output schema is valid."
 )
 logging.critical(diagnostic_feedback)
 # We raise here immediately because retrying a 400 will never succeed.
 raise ValueError(diagnostic_feedback)
 
 except openai.AuthenticationError as e:
 logging.critical("API Key is invalid or revoked. Halting immediately.")
 raise

 def _parse_reset_header(self, reset_str: str) -> float:
 """
 Parses OpenAI's specific time-string format (e.g., '6s', '1m', '500ms') into seconds.
 """
 if not reset_str:
 return 5.0 # Safe default
 
 try:
 if reset_str.endswith('ms'):
 return float(reset_str[:-2]) / 1000.0
 elif reset_str.endswith('s'):
 return float(reset_str[:-1])
 elif reset_str.endswith('m'):
 return float(reset_str[:-1]) * 60.0
 else:
 return 5.0
 except ValueError:
 return 5.0
```

#### Step 2: Implementation in an Agentic Workflow
Observe how the consuming script is completely insulated from network chaos. The developer only worries about business logic.

```python
if __name__ == "__main__":
 harness_client = ResilientOpenAIClient(max_retries=3)
 
 agent_messages = [
 {"role": "system", "content": "You are a financial analysis bot."},
 {"role": "user", "content": "Summarize Q3 earnings for AAPL."}
 ]
 
 try:
 logging.info("Dispatching task to LLM...")
 result = harness_client.execute_chat_completion(
 model="gpt-4o", 
 messages=agent_messages,
 temperature=0.2
 )
 print("\n--- FINAL OUTPUT ---")
 print(result)
 
 except Exception as final_error:
 # In a real business environment, this goes to the Runbook / Incident management system
 print(f"\n[PIPELINE TERMINATED]: {final_error}")
```

---

### Realistic Business Applications & Unit Economics

Understanding the nuances of network exceptions separates prototype builders from engineers capable of managing production Service Level Agreements (SLAs).

**1. Mass Data Extraction & Auto-Scaling (The E-Commerce Scraper)**
An agency is contracted to extract and structure data from 50,000 competitor product pages using an LLM. At 50 concurrent requests per second, the pipeline will inevitably trigger OpenAI's TPM (Tokens Per Minute) limit within the first two minutes. If the script uses naive retries without header parsing, it will repeatedly hit the API, extending the rate limit lockout penalty. By reading the `x-ratelimit-reset-tokens` header natively, the script effectively "throttles itself" with surgical precision. It pauses for exactly 14.5 seconds when told to, and resumes instantly. 
* **Business Impact:** The pipeline operates at the absolute maximum speed the provider allows without ever dropping a payload, ensuring the 50,000 pages are processed reliably, avoiding the loss of expensive halfway-processed context data.

**2. Building Comprehensive Runbooks for Client Handoffs**
As highlighted in the *AI Engineer roadmap* curriculum under "Documentation and Client Handoff," an automation project worth $5,000+ requires a Runbook: "Ранбук: 5 самых вероятных типов сбоев и как их решить" (Runbook: 5 most likely failure types and how to solve them). 
When your Python wrapper catches an `AuthenticationError`, it can automatically trigger a webhook to a Slack channel with a pre-formatted Runbook entry: *"Alert: OpenAI API Key Revoked. Runbook Action: Go to platform.openai.com, generate a new key, and update the `.env` file in the staging server."* This dramatically reduces support tickets and positions you as an elite architect.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Handling exceptions requires intense architectural discipline to avoid silent failures and runaway costs.

> [!CAUTION] 
> **The Context-Length Exception Trap (Cost Blowouts)** 
> **The Problem:** Your agent progressively appends file text to its context window. Eventually, the `messages` array exceeds the model's 128k token limit. The API returns a `400 BadRequestError`. If you use a generic `except Exception:` block and blindly retry, you will repeatedly send a 130k token payload that fails instantly, but you may be billed for network egress or risk an account ban for API abuse. 
> **Harness Mitigation:** As demonstrated in our code, never retry a `400 BadRequestError`. Instead, implement a **Context Management / Compaction** layer. The diagnostic feedback must instruct the orchestrator: "Context exceeded. Triggering the summarization sub-agent to compress history before retrying."

> [!WARNING] 
> **Asynchronous Semaphore Desyncs** 
> **The Error:** In heavily parallelized asynchronous workflows (using `asyncio.gather`), catching a rate limit in one thread might cause all 50 threads to simultaneously sleep and wake up, creating a massive "Thundering Herd" that instantly triggers another 429 error. 
> **Diagnostic Loop:** If using async Python, your rate-limit exception handler should temporarily adjust the `asyncio.Semaphore` limit dynamically, slowing down the entire global queue, rather than just sleeping the individual thread.

> [!NOTE] 
> **Provider-Specific Header Variations** 
> OpenAI uses `x-ratelimit-reset-requests` and `x-ratelimit-reset-tokens`. Anthropic uses `anthropic-ratelimit-requests-reset` and `anthropic-ratelimit-tokens-reset`. If you are building a multi-model router that fails over from OpenAI to Anthropic, your exception classification router must be highly specific about which SDK headers it is parsing.

By mastering precise API exception handling, HTTP status code classification, and header-driven backoff logic, you have fortified your cognitive architecture. You have shifted your scripts from fragile, hopeful executions into resilient, self-healing enterprise microservices.

Does this structured approach to API exception handling and diagnostic feedback make sense as we prepare for Block 4?

---

## Block 4: SDK Configurations — system instructions design for OpenAI/Anthropic Python clients.

Welcome to Block 4 of Week 10. In the previous blocks, we mastered recursive data validation and network resilience, successfully bridging the gap between probabilistic intelligence and deterministic software APIs. However, the most robust pipeline in the world is useless if the agent driving it fundamentally misinterprets its role, loses focus, or forgets its instructions halfway through a complex task. 

In this exhaustive, production-grade deep-dive, we will master **SDK Configurations and System Instructions Design**. We will move far beyond amateur "prompt engineering" and delve into the architectural management of directives. You will learn how to structure Enterprise system prompts, implement the **DO Framework** (Directives, Orchestration, Execution), and engineer dynamic Python loaders that read markdown files (like ``) from disk to configure your OpenAI and Anthropic SDK clients at runtime. 

---

### Deep Theoretical Analysis: The Physics of Directives and System Prompts

To construct reliable cognitive architectures, an AI Automation Architect must decouple the "rules" of the agent from the Python execution loop. 

#### 1. The DO Framework (Directives, Orchestration, Execution)
In advanced agentic building, you must adopt an architecture that separates concerns to maximize reliability. "llms are probabilistic whereas most business logic is deterministic and thus requires consistency". The DO framework establishes a rigid three-layer architecture to solve this mismatch. "layer one directive what to do it's SOPs written in markdown that lives in directives". 

Your System Instructions are your **Directives**. They are not hardcoded Python strings; they are dynamic Standard Operating Procedures (SOPs). By "pushing the heavy lifting onto those deterministic Python scripts which is the execution and then keeping the instructions really clear in markdown which are directives we let the LLM do the one thing that it's actually really good at which is being a very intelligent router".

#### 2. The Danger of Instruction Rot and Context Bloat
Why do we separate instructions into modular files rather than dumping them into a single string? *Lecture 04. Разносите инструкции по файлам* (Separate instructions into files) provides a stark warning: "Создали и впихнули туда каждое правило... Через месяц файл раздулся до 300 строк... качество работы агента на самом деле падает" (You created and crammed every rule into it... After a month, the file bloated to 300 lines... the quality of the agent's work actually drops). 
When you build monolithic system prompts, critical rules are buried, and "три противоречащих друг другу правила стиля заставляют агента каждый раз случайно выбирать одно из них" (three contradictory style rules force the agent to randomly choose one of them each time). Therefore, the modern standard is modularity: reading multiple, highly targeted `.md` files dynamically.

#### 3. Transforming a Chatbot into an "Eager" Agent
System instructions for autonomous agents look fundamentally different than instructions for chatbots. The OpenAI Cookbook explicitly advises adding three specific reminders to GPT-4.1 system prompts:
1. **Persistence:** "You are an agent - please keep going until the user’s query is completely resolved".
2. **Deliberate Planning:** "You MUST plan extensively before each function call, and reflect extensively on the outcomes".
These instructions shift the behavior radically. "As a whole, we find that these three instructions transform the model from a chatbot-like state into a much more 'eager' agent, driving the interaction forward autonomously",.

---

### The 10-Element Architecture of Complex Prompts

When writing the actual text of your System Instruction (the markdown file), Anthropic's rigorous guidelines dictate a 10-element structure for optimal cognitive alignment. 

| Step | Prompt Element | Architectural Purpose | Example / Best Practice |
|:--- |:--- |:--- |:--- |
| **1** | `"User:"` formatting | Initiates the conversational API structure securely. | "This is mandatory! Prompts to Claude using CLAUDEMESSAGES() always need to begin with this." |
| **2** | Task Context | Defines the agent's absolute role and overarching boundaries. | "You will be acting as an AI career coach named Joe... It's best to put context early in the body". |
| **3** | Tone Context | Establishes brand safety and communication style. | "You should maintain a friendly customer service tone." |
| **4** | Detailed Rules | Explicit "out" conditions to prevent hallucinations. | "If you are unsure how to respond, say 'Sorry, I didn't understand that.'" |
| **5** | Few-Shot Examples | Closes the verification gap. "Giving Claude examples of how you want it to behave... is extremely effective for: Getting the right answer... Getting the answer in the right format". | "Examples are probably the single most effective tool in knowledge work... Make sure to give Claude examples of common edge cases." |
| **6** | Input Data | Securely wraps variable context using XML tags. | "XML is convenient to precisely wrap a section including start and end". |
| **7** | Immediate Task | Reminds the agent of the exact final goal before it generates. | "It's best to do this toward the end of a long prompt. This will yield better results than putting this at the beginning." |
| **8** | Precognition | Forces the LLM to map out its logic (Chain of Thought). | "For tasks with multiple steps, it's good to tell Claude to think step by step before giving an answer." |
| **9** | Output Formatting | Enforces JSON or specific XML structures for parsing. | "Put your response in `<response></response>` tags." |
| **10** | Prefilling | (Anthropic specific) Forces the model to start its generation with a specific bracket or tag. | "Assistant: [Joe] `<response>`". |

---

### ASCII Architecture Schema: Dynamic SDK Configuration

This Directed Acyclic Graph (DAG) demonstrates how the Harness uses Python to load external Markdown files, construct the OpenAI/Anthropic configuration, and execute the SDK call securely.

```ascii
=============================================================================================
 ENTERPRISE SDK CONFIGURATION HARNESS (DO FRAMEWORK)
=============================================================================================

[ 1. FILE SYSTEM (DIRECTIVES LAYER) ]
 ├── harness/
 │ ├── (Global conventions, DO Framework setup)
 │ ├── rules/
 │ │ ├── (Error recovery SOPs)
 │ │ └── (Brand safety SOPs)
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. PYTHON CONFIGURATOR (ORCHESTRATION LAYER) |
| - `glob.glob("harness/rules/*.md")` loads modular rules dynamically. |
| - Concatenates rules into a unified `SystemInstruction` string. |
| - Formats payload using Anthropic 10-Element principles. |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. SDK INGESTION & DISPATCH (EXECUTION LAYER) |
| `client.chat.completions.create(` |
| `model="gpt-4o",` |
| `messages=[{"role": "system", "content": concatenated_system_prompt},...]` |
| `)` |
+-----------------------------------------------------------------------------------------+
 |
 v
[ 4. EAGER AGENT RESPONSE ] -> Output strictly adheres to markdown rules.
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

According to the Phase 3 roadmap constraints for your custom harness, you must implement a system prompt loader. Specifically: "Загрузчик системногопромпта в стиле, читающий./harness/rules/*.md с path-glob matching" (A system prompt loader in the style of, reading `./harness/rules/*.md` with path-glob matching). 

Here is the robust, production-ready Python code to achieve this.

#### Step 1: The Directives (Markdown Files)
First, create your directory structure. 
`harness/`:
```markdown
You operate within a three-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. 
You are an autonomous Orchestrator agent. You MUST plan extensively before each function call, and reflect extensively on the outcomes.
```
*Note: This directly mirrors the self-annealing DO structure described by industry architects,.*

`harness/rules/`:
```markdown
You should self-anneal when things break: read the error message and stack trace, fix the parameters, and test it again. Update your mental model with what you learned.
```

#### Step 2: The Dynamic Python SDK Configurator
This script reads the filesystem, constructs the modular prompt, and configures the SDK call.

```python
import os
import glob
import logging
from openai import OpenAI
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SDK_CONFIG] - %(message)s')

class SDKConfigurator:
 """
 Implements dynamic loading of system instructions (DO Framework).
 Prevents Context Bloat and Instruction Rot by keeping rules modular.
 """
 def __init__(self, harness_dir: str = "harness"):
 self.harness_dir = harness_dir
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 
 def _load_claude_md(self) -> str:
 """Loads the foundational 'паттерн как системного промпта'."""
 path = os.path.join(self.harness_dir, "")
 if os.path.exists(path):
 with open(path, "r", encoding="utf-8") as f:
 return f.read().strip()
 return "You are a helpful AI assistant."

 def _load_modular_rules(self) -> str:
 """Reads./harness/rules/*.md with path-glob matching as per Phase 3 roadmap."""
 rules_content = []
 rule_paths = glob.glob(os.path.join(self.harness_dir, "rules", "*.md"))
 
 for path in rule_paths:
 rule_name = os.path.basename(path).replace('.md', '')
 with open(path, "r", encoding="utf-8") as f:
 # Wrap in XML as advised: "XML is convenient to precisely wrap a section" 
 rules_content.append(f"<rule name='{rule_name}'>\n{f.read().strip()}\n</rule>")
 
 return "\n".join(rules_content)

 def compile_system_instruction(self) -> str:
 """Assembles the 10-element complex prompt structure."""
 base_context = self._load_claude_md()
 modular_rules = self._load_modular_rules()
 
 # We enforce "Precognition (thinking step by step)" 
 precognition_instruction = (
 "\n<instruction>\n"
 "Think about your answer step-by-step before you respond. "
 "Please keep going until the user’s query is completely resolved, before ending.\n"
 "</instruction>"
 )
 
 compiled_prompt = f"{base_context}\n\nHere are your modular operating rules:\n{modular_rules}{precognition_instruction}"
 logging.info(f"System Prompt compiled successfully ({len(compiled_prompt)} characters).")
 return compiled_prompt

 def dispatch_agent_call(self, user_query: str) -> str:
 """Configures the OpenAI SDK with the dynamic directives."""
 system_prompt = self.compile_system_instruction()
 
 messages = [
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": user_query}
 ]
 
 try:
 response = self.client.chat.completions.create(
 model="gpt-4o",
 messages=messages,
 temperature=0.1 # Low temperature for agentic reliability
 )
 return response.choices.message.content
 except Exception as e:
 logging.error(f"SDK Dispatch failed: {str(e)}")
 raise

# ==========================================
# Execution
# ==========================================
if __name__ == "__main__":
 # Ensure your harness directories and markdown files exist before running!
 configurator = SDKConfigurator()
 
 # We pass the input data securely
 user_input = "Please analyze the logs and resolve the 500 Server Error on the backend."
 
 output = configurator.dispatch_agent_call(user_input)
 print("\n--- AGENT OUTPUT ---")
 print(output)
```

---

### Realistic Business Applications & Unit Economics

Understanding how to load files dynamically into SDK configurations separates entry-level prompting from true enterprise systems engineering.

**1. Scalable AI Proposal Systems (Agency Automation)**
In B2B scenarios, creating client-specific outputs rapidly is essential. "have an AI proposal system that creates professional customized proposals in real time during sales calls". If you build an AI proposal generator for a marketing agency, the brand guidelines, tone, and pricing rules change every quarter. If these rules are hardcoded into Python, a developer must commit code to update pricing. By utilizing the `glob` loading pattern mapped to `.md` files, a non-technical sales manager can simply edit `harness/rules/`. The Python script dynamically loads the new directive during the next SDK call, maintaining true separation of concerns and dropping software maintenance costs by thousands of dollars a year.

**2. Self-Healing Multi-Agent Pipelines**
When agents hit API errors or database timeouts, they often crash if not instructed properly. By dedicating a specific file (`harness/rules/`) that explicitly tells the SDK, "you should self-anneal when things break read error message and stack trace fix the script and test it again", the agent transforms. It reads the error via the tools we built in Block 1, looks at its `` directive, and autonomously attempts a second strategy. This "Eager Agent" behavior is what makes 24/7 autonomous background processing economically viable.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Configuring the SDK is an art of managing limitations. 

> [!CAUTION] 
> **The Context-Rot and Priority Dilemma** 
> **The Problem:** The LLM receives 10 separate markdown rule files via the `glob` loader. It successfully follows Rule 1 but entirely forgets Rule 9 (e.g., Output Formatting). This is a well-documented issue called "Lost in the Middle." 
> **Harness Mitigation:** As explicitly stated by Anthropic: "It generally doesn't hurt to reiterate to Claude its immediate task. It's best to do this toward the end of a long prompt. This will yield better results than putting this at the beginning". Your Python script must ensure that the most absolutely critical format instructions (e.g., "Output ONLY valid JSON") are injected at the very bottom of the system prompt, or directly alongside the user's query.

> [!WARNING] 
> **Premature Task Completion (Agent Laziness)** 
> **The Error:** The user asks the agent to refactor 5 files. The agent refactors 2 files and then outputs: "I have started the work. Please let me know if you want me to do the other 3." 
> **Diagnostic Loop:** You must enforce OpenAI's specific agentic reminder: "You are an agent - please keep going until the user’s query is completely resolved, before ending". If the agent still attempts to stop, the Orchestration layer (your Python loop) must catch the completion status, compare it to the initial request, and programmatically inject a system message: `"Task incomplete. You must process the remaining 3 files before concluding."`

> [!NOTE] 
> **Role Reversals in Conversational History** 
> When managing deep multi-agent pipelines, always ensure that your SDK configuration respects the strict `[{"role": "user", "content":...}, {"role": "assistant",...}]` format. If you accidentally format an Assistant's tool-use thought process as a "User" message, the SDK will reject the payload with an HTTP 400 Bad Request error. Maintain strict data typing for message histories.

By mastering dynamic SDK Configurations, the DO Framework, and the 10-element system prompt design, you guarantee that your underlying AI models operate strictly within defined cognitive boundaries.

Are you ready to proceed to Block 5, where we will dive into Generation Parameters to dynamically control Temperature, Top-P, and token economics programmatically?

---

## Block 5: Generation Parameters — managing temperature, top_p, and token ceilings.

Welcome to Block 5 of Week 10. In our previous architectural discussions, we focused heavily on the structural and contextual constraints of large language models (LLMs). We engineered dynamic system instructions using the DO Framework and built strict JSON validators to force compliance. However, an elite AI Automation Architect understands that controlling an LLM is not just about what you input into the prompt; it is also about fundamentally altering the mathematical physics of how the model predicts its next word.

When you interact with the OpenAI or Anthropic SDKs, you are interfacing with a probabilistic engine. By manipulating specific mathematical configuration parameters—namely `temperature`, `top_p` (nucleus sampling), `top_k`, and `max_tokens`—you dictate the engine's creativity, factual rigidity, and financial consumption. In this exhaustive, production-grade deep-dive, we will master Generation Parameters. We will dissect the mechanisms of greedy decoding, resolve the catastrophic "repetition loop bug", and build programmatic parameter routers that dynamically shift the LLM's neural behavior based on the specific business task at hand.

---

### Deep Theoretical Analysis: The Physics of Token Prediction

To build robust cognitive architectures, we must peer beneath the abstraction of the SDK and understand the statistical mechanics of token generation. LLMs do not output text; they output a probability distribution (logits) across their entire vocabulary for what the next token should be. Generation parameters are mathematical filters applied to this distribution *before* the final token is selected.

#### 1. Temperature and Greedy Decoding
"Temperature controls the degree of randomness in token selection". It acts as a scaling factor on the output logits before they are passed through the softmax function. 
* **Low Temperature (Deterministic):** Lower temperatures are good for prompts that expect a more deterministic response. When you set the temperature to exactly 0, you activate "greedy decoding." "A temperature of 0 (greedy decoding) is deterministic: the highest probability token is always selected". This is not just a preference; it is an architectural requirement for analytical tasks. "For CoT prompting, set the temperature to 0. Chain of thought prompting is based on greedy decoding, predicting the next word in a sequence based on the highest probability assigned by the language model... there’s likely one single correct answer".
* **High Temperature (Stochastic):** Higher temperatures flatten the probability distribution, giving lower-probability tokens a higher chance of being selected. This "can lead to more diverse or unexpected results". However, "With more freedom (higher temperature, top-K, top-P, and output tokens), the LLM might generate text that is less relevant".

#### 2. Top-K and Top-P (Nucleus Sampling)
While Temperature scales the probabilities, `top_k` and `top_p` physically truncate the pool of available tokens.
* **Top-K:** This parameter instructs the model to only consider the top *K* most likely next tokens. If `top_k=40`, the model completely discards the 41st most likely token and below, redistributing the probability mass among the remaining 40.
* **Top-P (Nucleus Sampling):** Instead of a fixed number of tokens, `top_p` considers the smallest set of tokens whose cumulative probability exceeds the probability *P*. If `top_p=0.9`, the model dynamically includes as many tokens as needed to reach a 90% probability mass. Note that in many SDK configurations, default values effectively disable these settings unless explicitly overwritten.

#### 3. Token Ceilings and Computational Budgets
Controlling length is an economic imperative. "To control the length of a generated LLM response, you can either set a max token limit in the configuration or explicitly request a specific length in your prompt". 
An AI Architect must remember that a token is a fragment of computation. "A token is not a word a token is about 0.7 words". Furthermore, models possess strict boundaries: "There's only a certain number of tokens that you can actually fit into one conversation... 200,000 to about a million". By programmatically enforcing `max_tokens` (or `max_completion_tokens` in recent OpenAI SDK updates), you physically prevent the agent from burning computational budget on endless, hallucinated rants.

---

### ASCII Architecture Schema: Dynamic Parameter Routing

In an enterprise application, you should never hardcode a single global `temperature` for all API calls. The following Directed Acyclic Graph (DAG) demonstrates a **Parameter Routing Middleware** that inspects the nature of the task and injects the mathematically optimal generation configurations.

```ascii
=============================================================================================
 ENTERPRISE PARAMETER ROUTING HARNESS
=============================================================================================

[ 1. ORCHESTRATOR / USER REQUEST ] -> e.g., "Extract JSON" OR "Write a creative blog."
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. TASK CLASSIFICATION MIDDLEWARE |
| Determines the cognitive requirements of the current execution step. |
+-----------------------------------------------------------------------------------------+
 / | \
 (Data Extraction/CoT) (Standard Chatbot) (Creative Copywriting)
 v v v
+-----------------------+ +-----------------------+ +-----------------------+
| 3A. GREEDY CONFIG | | 3B. BALANCED CONFIG | | 3C. STOCHASTIC CONFIG |
| - Temperature: 0.0 | | - Temperature: 0.5 | | - Temperature: 0.9 |
| - Top_P: 1.0 (Off) | | - Top_P: 0.9 | | - Top_P: 0.95 |
| - Max Tokens: 2000 | | - Max Tokens: 4000 | | - Max Tokens: 8000 |
+-----------------------+ +-----------------------+ +-----------------------+
 \ | /
 -------------------------+------------------------
 |
 v
+-----------------------------------------------------------------------------------------+
| 4. SDK DISPATCH (Execution Layer) |
| `client.chat.completions.create(..., temperature=dynamic_temp, top_p=dynamic_top_p)` |
+-----------------------------------------------------------------------------------------+
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a `GenerationConfigManager` in Python. This utility ensures that our AI pipeline mathematically aligns its probabilistic engine with the specific task it is attempting to solve, adhering strictly to the principle that different cognitive tasks require different statistical parameters.

#### Step 1: Architecting the Parameter Classes
We use `Pydantic` or standard Dataclasses to define our configurations. This guarantees that our scripts cannot accidentally pass invalid parameter types (like a string into the `temperature` argument) to the SDK.

```python
import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from openai import OpenAI

# Adhering to the mandate: "Сделайте рантайм агента наблюдаемым" (Make agent runtime observable)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [PARAM_ROUTER] - %(message)s')

@dataclass
class GenerationProfile:
 """Blueprint for mathematical generation parameters."""
 temperature: float
 top_p: float
 max_tokens: int
 presence_penalty: float = 0.0
 frequency_penalty: float = 0.0

class ParameterRouter:
 """
 Enterprise middleware to dynamically map business tasks to 
 their optimal probabilistic generation profiles.
 """
 def __init__(self):
 # 1. Greedy Decoding Profile (Data Extraction, Code Generation, Chain-of-Thought)
 # "For CoT prompting, set the temperature to 0... there’s likely one single correct answer" 
 self.analytical_profile = GenerationProfile(
 temperature=0.0,
 top_p=1.0, # Disable nucleus sampling to ensure absolute determinism
 max_tokens=2500
 )
 
 # 2. Balanced Profile (Standard QA, Customer Support)
 self.balanced_profile = GenerationProfile(
 temperature=0.4,
 top_p=0.9,
 max_tokens=4000
 )
 
 # 3. Stochastic Profile (Creative Writing, Brainstorming)
 self.creative_profile = GenerationProfile(
 temperature=0.85,
 top_p=0.95,
 max_tokens=8000,
 presence_penalty=0.5 # Encourages the model to talk about new concepts
 )

 def get_profile(self, task_type: str) -> GenerationProfile:
 """Routes the task to the correct mathematical configuration."""
 routing_map = {
 "extract_json": self.analytical_profile,
 "chain_of_thought": self.analytical_profile,
 "customer_support": self.balanced_profile,
 "creative_blog": self.creative_profile
 }
 selected = routing_map.get(task_type, self.balanced_profile)
 logging.info(f"Routed task '{task_type}' to profile with Temp: {selected.temperature}")
 return selected
```

#### Step 2: Executing the SDK with Dynamic Parameters
We will now inject these dynamic parameters directly into the OpenAI SDK execution block.

```python
class TaskExecutor:
 """Executes the LLM call using the routed generation parameters."""
 def __init__(self):
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 self.router = ParameterRouter()

 def run_task(self, task_type: str, user_prompt: str) -> str:
 profile = self.router.get_profile(task_type)
 
 messages = [
 {"role": "system", "content": "You are an enterprise AI worker."},
 {"role": "user", "content": user_prompt}
 ]
 
 try:
 response = self.client.chat.completions.create(
 model="gpt-4o",
 messages=messages,
 temperature=profile.temperature,
 top_p=profile.top_p,
 max_tokens=profile.max_tokens,
 presence_penalty=profile.presence_penalty,
 frequency_penalty=profile.frequency_penalty
 )
 return response.choices.message.content
 except Exception as e:
 logging.error(f"Generation failure: {str(e)}")
 raise

# ==========================================
# Execution Environment
# ==========================================
if __name__ == "__main__":
 executor = TaskExecutor()
 
 print("--- EXECUTING ANALYTICAL TASK ---")
 # Forces Temperature 0.0 (Greedy Decoding)
 analytical_result = executor.run_task(
 task_type="chain_of_thought", 
 user_prompt="Calculate the compound interest of $50,000 at 5% over 10 years. Think step by step."
 )
 
 print("\n--- EXECUTING CREATIVE TASK ---")
 # Forces Temperature 0.85 (Stochastic Decoding)
 creative_result = executor.run_task(
 task_type="creative_blog", 
 user_prompt="Brainstorm three highly unusual, futuristic business models for AI agents in 2030."
 )
```

By decoupling the generation configuration from the hardcoded execution script, we grant the Orchestrator the ability to tune the "creativity dial" of its sub-agents precisely as needed.

---

### Realistic Business Applications & Unit Economics

Understanding the unit economics of generation parameters is what separates amateur prompt engineers from enterprise cloud architects.

**1. Scalable JSON Extraction Pipelines**
Imagine a pipeline built to ingest 100,000 customer emails and extract `{"sentiment": "string", "intent_category": "string"}` for a CRM database. If a junior developer leaves the default SDK `temperature` at `0.7`, the LLM will occasionally attempt to be "creative" with the JSON keys, resulting in pipeline crashes and schema validation failures. By routing this task through our `ParameterRouter` and enforcing `temperature=0.0`, the architect guarantees mathematical determinism (greedy decoding). This eliminates schema hallucinations, saving the company from the immense compute costs associated with running massive diagnostic and self-healing retry loops.

**2. Multi-Agent Synthesis and Ideation**
In content production factories, you often utilize a multi-agent debate framework. "You can run multiple agents with the same prompt and then use their statistical spread in order to ideate and improve things". If you run 5 agents in parallel to brainstorm marketing hooks, but leave `temperature=0.0`, all 5 agents will output the exact same hook because greedy decoding is deterministic. By dynamically pushing `temperature=0.9` and `top_p=0.95`, you force the model to explore the outer edges of its latent space, generating 5 distinctly unique conceptual hooks.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Configuring mathematical parameters improperly can physically break the neural network's generation cycle.

> [!CAUTION] 
> **The Repetition Loop Bug (Infinite Filler)** 
> **The Error:** You receive a response from the API that looks like this: *"The data shows that the revenue is increasing increasing increasing increasing increasing increasing..."* 
> **Harness Mitigation:** This is a documented architectural failure. "Have you ever seen a response ending with a large amount of filler words? This is also known as the 'repetition loop bug'... where the model gets stuck in a cycle... exacerbated by inappropriate temperature and top-k/top-p settings",. This occurs at both extremes. At low temperatures, the model rigidly follows the highest probability path back into a loop. At high temperatures, random chance traps it. To fix this programmatically in your diagnostic loop, if you detect a repetition loop via regex, you must have the script automatically tweak the `presence_penalty` (e.g., increase to `0.5`) and retry, which algorithmically punishes the model for repeating the same tokens.

> [!WARNING] 
> **Max Tokens vs. Context Limit Confusion** 
> **The Problem:** Developers often confuse the `max_tokens` generation parameter with the total context window size. If you set `max_tokens=100000`, thinking you are giving the model a massive context, the API will reject your call because `max_tokens` refers *only* to the generated output ceiling, not the input size. 
> **Diagnostic Loop:** Always set `max_tokens` specifically to constrain the economic budget of the *response*. If you ask for a "tweet-length summary" but leave `max_tokens=4000`, a hallucinating model might write 4,000 words, charging you for every token. Setting `max_tokens=100` acts as a hard financial circuit breaker.

> [!NOTE] 
> **Simultaneous Top-P and Temperature Adjustments** 
> OpenAI's official documentation strongly advises against altering both `temperature` and `top_p` simultaneously. Because they both interact with the probability distribution (one scales it, the other truncates it), changing both makes debugging erratic behavior nearly impossible. As a best practice, if you adjust `temperature` (e.g., `0.2`), leave `top_p=1.0`. If you adjust `top_p` (e.g., `0.5`), leave `temperature=1.0`.

By mastering these mathematical parameters, you command total control over the probabilistic nature of your AI architecture. You can force an LLM to be a rigid, zero-hallucination data extractor, or unleash it as a highly stochastic creative engine, all orchestrated dynamically via Python.

Does this breakdown of probability distribution controls make sense? We can move on to Block 6 next to implement recovery strategies for when these models inevitably hit rate limits.

---

## Block 6: Rate Limit Resiliency — recovery configurations for API limits (429 errors).

Welcome to Block 6 of Week 10: *OpenAI & Anthropic SDKs: Structured Outputs*. In Block 5, we mastered the manipulation of Generation Parameters, learning to bend the probabilistic distribution of tokens to our will using Temperature and Top-P filtering. We have successfully aligned the cognitive engine. However, the most brilliantly engineered, perfectly constrained LLM architecture will shatter the moment it encounters the harsh physical reality of cloud infrastructure: the Rate Limit.

As an AI Automation Architect, you must internalize a fundamental truth: **APIs are hostile environments**. As established in the foundational principles of harness engineering, specifically *Lecture 01. Сильные модели не означают надёжного исполнения* (Strong models do not mean reliable execution), your architecture must treat network failures not as anomalies, but as guaranteed operational states. If you write a flawless script but fail to programmatically catch an `HTTP 429 Too Many Requests` error, your Python application will trigger a fatal exception, your agent's memory will be wiped, and your automated pipeline will collapse. 

In this exhaustive, production-grade deep-dive, we will master **Rate Limit Resiliency**. We will move beyond naive `try/except` blocks and build systems that do not just "fail gracefully," but autonomously self-heal by reading rate limit HTTP headers, pausing execution mathematically, and intelligently retrying. You will learn to implement the "Self-Annealing" resilience of advanced agent frameworks natively in your Python scripts.

---

### Deep Theoretical Analysis: The Physics of API Traffic and 429 Errors

To build a resilient execution layer, we must mathematically classify the types of throttling our LLM SDKs will encounter. An `HTTP 429` is not a server failure; it is the server successfully protecting itself from your code.

#### 1. The Taxonomy of Token Buckets
When you interact with the OpenAI or Anthropic SDKs, your usage is gated by two distinct limiters:
* **RPM (Requests Per Minute):** The sheer volume of individual HTTP POST requests you are firing. In multi-agent swarms, where 10 sub-agents might simultaneously query a model, you will hit RPM limits in seconds.
* **TPM (Tokens Per Minute):** The total volume of input context plus requested output tokens. As noted in the *AI Agent roadmap* Phase 5 guidelines, "Для мульти-агентных сценариев... ждите ~15× токенов, чем у одиночного чат-агента" (For multi-agent scenarios... expect ~15x more tokens than a single chat agent). This massive token consumption makes TPM limits the primary bottleneck in enterprise AI engineering.

#### 2. The Superiority of Header-Driven Backoff
When a 429 error occurs, junior developers typically implement a generic `time.sleep(10)`. This is a critical anti-pattern. Why guess how long to wait when the server explicitly tells you? Modern REST APIs include specific HTTP Headers in their 429 error responses, such as `x-ratelimit-reset-requests` or `x-ratelimit-reset-tokens`. 
By parsing the exact reset header, your Python script can execute an exact `asyncio.sleep()` for the precise number of milliseconds required, maximizing pipeline throughput without triggering a secondary ban.

#### 3. The "Self-Annealing" Framework and the Diagnostic Loop
What happens if the rate limit is not temporary, but an absolute hard cap (e.g., you hit your monthly billing limit)? If you loop blindly, you burn compute. As warned in Stepan Kozhevnikov's essay on Habr, "Как я перестал «кормить» нейросеть токенами" (How I stopped "feeding" the neural network tokens), blindly feeding retries into a broken loop is financially disastrous.
Instead, we must adopt the **Self-Annealing** concept. As leading architects explain, "if an error occurs in the agent a self annealing framework means it will not crash it will instead pause it will read the error message and then it will look at the code that caused the error... and then rewrite both the script... and then the directive". 
Crucially, as outlined in *Lecture 11. Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable), "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание" (Without observability, agents make decisions in uncertainty... retries turn into blind wandering). Your harness must return actionable feedback directly into the agent's context.

---

### ASCII Architecture Schema: Header-Driven Resilience Harness

The following Directed Acyclic Graph (DAG) illustrates how our exception-handling middleware intercepts `HTTP 429` network failures, parses the underlying headers, and orchestrates a deterministic recovery loop before returning control to the agent.

```ascii
=============================================================================================
 ENTERPRISE RATE LIMIT RESILIENCY HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR ] -> Calls `client.chat.completions.create(...)`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. SDK EXECUTION LAYER (Network Request) |
+-----------------------------------------------------------------------------------------+
 | (HTTP 200 OK) | (HTTP 429 Too Many Requests)
 v v
[ 3. RETURN CLEAN DATA ] +---------------------------------------------------+
 | 4. EXCEPTION CLASSIFICATION ROUTER |
 | -> `except openai.RateLimitError as e:` |
 +---------------------------------------------------+
 |
 v
 +-----------------------------------------------------------------------+
 | 5. HEADER PARSING & RECOVERY (The Self-Annealing Pause) |
 | - Extract `e.response.headers.get('x-ratelimit-reset-tokens')` |
 | - Log observability metric: "Paused for 14.2s to heal Rate Limit" |
 | - Execute exact `time.sleep(14.2)`. |
 | - Recursively attempt Step 2 up to MAX_RETRIES. |
 +-----------------------------------------------------------------------+
 |
 (If MAX_RETRIES exceeded / Hard Billing Cap Reached)
 v
 +---------------------------------------------------+
 | 6. DIAGNOSTIC OBSERVATION INJECTION |
 | Returns string to LLM: "CRITICAL 429 ERROR: |
 | Quota exceeded. Compress your context history |
 | and try a different analytical approach." |
 +---------------------------------------------------+
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-grade wrapper around the OpenAI SDK. This code demonstrates how to cleanly trap `RateLimitError` exceptions, extract the hidden HTTP response headers from the exception object, and format actionable error strings to maintain the integrity of your multi-agent workflows.

#### Step 1: Architecting the Rate Limit Parser
OpenAI and Anthropic return specific string formats in their reset headers (e.g., `"14s"`, `"500ms"`, `"2m"`). We must build a deterministic parser to convert these strings into Python floats for our `time.sleep()` function.

```python
import os
import time
import logging
import re
from typing import Any, Dict, Optional
import openai
from openai import OpenAI

# Lecture 11: Make the agent runtime observable
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RESILIENCY_HARNESS] - %(levelname)s: %(message)s')

def parse_rate_limit_header(reset_str: Optional[str]) -> float:
 """
 Parses complex time-string formats returned by API headers into seconds.
 Supports 'ms' (milliseconds), 's' (seconds), and 'm' (minutes).
 """
 if not reset_str:
 return 5.0 # Safe fallback if header is missing
 
 reset_str = reset_str.strip().lower()
 
 try:
 if reset_str.endswith('ms'):
 return float(reset_str.replace('ms', '')) / 1000.0
 elif reset_str.endswith('s'):
 return float(reset_str.replace('s', ''))
 elif reset_str.endswith('m'):
 return float(reset_str.replace('m', '')) * 60.0
 else:
 # Attempt raw float parsing if no unit is provided
 return float(reset_str)
 except ValueError:
 logging.warning(f"Failed to parse reset header '{reset_str}'. Defaulting to 5.0s.")
 return 5.0
```

#### Step 2: The Resilient SDK Wrapper
This class acts as a protective proxy between your application logic and the OpenAI API. It implements header-driven waiting and actionable error formatting. As dictated by *Lecture 10. Только сквозное тестирование — настоящая верификация* (Only end-to-end testing is true verification), "сообщения об ошибках для агентов должны включать инструкции по исправлению" (error messages for agents must include instructions for fixing them).

```python
class ResilientOpenAIClient:
 """
 An enterprise wrapper for the OpenAI SDK that captures 429 network failures,
 parses rate limit headers, and prevents fatal pipeline crashes via self-annealing pauses.
 """
 def __init__(self, max_retries: int = 4):
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 self.max_retries = max_retries

 def execute_chat_completion(self, model: str, messages: list, **kwargs: Any) -> str:
 """
 Executes a chat completion with deep exception trapping and header-driven backoff.
 """
 attempt = 0
 
 while attempt <= self.max_retries:
 try:
 # 1. Attempt the native API call
 response = self.client.chat.completions.create(
 model=model,
 messages=messages,
 **kwargs
 )
 return response.choices.message.content

 # 2. Trap Rate Limits (HTTP 429)
 except openai.RateLimitError as e:
 attempt += 1
 logging.warning(f"RateLimitError (429) encountered on attempt {attempt}/{self.max_retries}.")
 
 if attempt > self.max_retries:
 # If we exhaust retries, we DO NOT crash. We return an observation to the LLM.
 diagnostic_feedback = (
 f"SYSTEM ERROR: Maximum rate limit retries exhausted. "
 f"The API is currently overwhelmed. "
 f"FIX INSTRUCTION: You must summarize your current findings to save context space, "
 f"conclude the current sub-task, and yield control back to the orchestrator."
 )
 logging.critical("Max retries hit. Routing diagnostic feedback to LLM.")
 return diagnostic_feedback
 
 # Extract exact reset time from HTTP headers. 
 # OpenAI uses 'x-ratelimit-reset-tokens' and 'x-ratelimit-reset-requests'.
 headers = e.response.headers if e.response else {}
 
 # We check tokens first, as TPM is usually the bottleneck in agentic workflows
 reset_time_str = headers.get('x-ratelimit-reset-tokens') or headers.get('x-ratelimit-reset-requests', '10s')
 
 sleep_duration = parse_rate_limit_header(reset_time_str)
 
 # Add a 10% jitter buffer to prevent Thundering Herds when multiple agents wake up
 jitter = sleep_duration * 0.10
 final_sleep = sleep_duration + jitter
 
 logging.info(f"Header parsed. Self-Annealing Pause: Suspending execution for {final_sleep:.2f} seconds.")
 time.sleep(final_sleep)

 # 3. Trap Transient Server Errors (HTTP 500, 502, 503)
 except (openai.APIConnectionError, openai.InternalServerError) as e:
 attempt += 1
 logging.error(f"Transient Server Error: {str(e)}. Executing standard exponential backoff.")
 if attempt > self.max_retries:
 return f"SYSTEM ERROR: API provider is down. Cannot complete task. Details: {str(e)}"
 time.sleep(2 ** attempt)

 # 4. Trap Fatal Client Errors (HTTP 400 - e.g., Context Length Exceeded)
 except openai.BadRequestError as e:
 # We raise here immediately because retrying a 400 (bad JSON/too long) will never succeed.
 diagnostic_feedback = (
 f"Fatal BadRequestError: {str(e)}. "
 f"FIX INSTRUCTION: Check your input payload. Ensure the context length "
 f"does not exceed the model's maximum limit. Truncate files immediately."
 )
 logging.critical(diagnostic_feedback)
 return diagnostic_feedback
```

#### Step 3: Deployment in the ReAct Loop
By utilizing this resilient client, the underlying ReAct loop is completely insulated from network chaos. 

```python
# Execution Environment
if __name__ == "__main__":
 harness_client = ResilientOpenAIClient(max_retries=3)
 
 agent_messages = [
 {"role": "system", "content": "You are a robust data parsing sub-agent."},
 # Simulating a massive payload that might trigger TPM limits
 {"role": "user", "content": "Extract the key metrics from the following massive string: [...]"} 
 ]
 
 # The developer simply calls the execution method. The class handles the mathematical pauses autonomously.
 logging.info("Dispatching task to LLM...")
 result = harness_client.execute_chat_completion(
 model="gpt-4o", 
 messages=agent_messages,
 temperature=0.0 # Greedy decoding for data extraction (Block 5)
 )
 
 print("\n--- FINAL OUTPUT OR OBSERVATION ---")
 print(result)
```

---

### Realistic Business Applications & Unit Economics

Mastering 429 recovery configurations separates hobbyist scripts from enterprise Service Level Agreements (SLAs).

**1. Mass Data Extraction & Auto-Scaling (The Web Scraper Swarm)**
An agency is contracted to extract and structure data from 50,000 competitor product pages using an LLM swarm. At 50 concurrent requests per second, the pipeline will inevitably trigger the provider's TPM (Tokens Per Minute) limit within the first two minutes. If the script uses naive `time.sleep(60)` retries without header parsing, it will wait far too long, destroying pipeline throughput. 
By reading the `x-ratelimit-reset-tokens` header natively, the script effectively "throttles itself" with surgical precision. It pauses for exactly 14.5 seconds when told to, and resumes instantly. 
*Business Impact:* The pipeline operates at the absolute maximum speed the provider allows without ever dropping a payload, ensuring the 50,000 pages are processed reliably and avoiding the loss of expensive, halfway-processed context data.

**2. Building Comprehensive Runbooks for Client Handoffs**
As highlighted in the *AI Engineer roadmap* curriculum under "Документация и передача клиенту" (Documentation and client handoff), an automation project worth $5,000+ requires a "Ранбук: 5 самых вероятных типов сбоев и как их решить" (Runbook: 5 most likely failure types and how to solve them). 
When your Python wrapper catches an absolute failure that exhausts all retries, you document this exact scenario in the Runbook. You explain to the client that the system is designed to return a graceful `SYSTEM ERROR` observation, ensuring the AI logs the failure in its final report rather than crashing the client's internal server silently.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Handling exceptions requires intense architectural discipline to avoid silent failures and runaway cloud costs.

> [!CAUTION] 
> **The Context-Length Exception Trap (Cost Blowouts)** 
> **The Problem:** Your agent progressively appends file text to its context window using tools. Eventually, the `messages` array exceeds the model's 128k token limit. The API returns an `HTTP 400 BadRequestError`. If you use a generic `except Exception:` block and blindly retry, you will repeatedly send a 130k token payload that fails instantly, risking account bans for API abuse. 
> **Harness Mitigation:** As demonstrated in our code, **never retry a 400 BadRequestError**. Instead, implement a **Context Management / Compaction** layer. The diagnostic feedback must instruct the orchestrator: "Context exceeded. You MUST trigger your `summarize_memory` tool to compress history before proceeding."

> [!WARNING] 
> **Asynchronous Semaphore Desyncs (The Thundering Herd)** 
> **The Error:** In heavily parallelized asynchronous workflows (using `asyncio.gather`), catching a rate limit in one thread might cause all 50 threads to simultaneously sleep and wake up exactly 10 seconds later, creating a massive "Thundering Herd" that instantly triggers another 429 error. 
> **Diagnostic Loop:** Always add a mathematical `jitter` (a randomized percentage multiplier, e.g., 5-15%) to your parsed sleep duration. This ensures your concurrent threads wake up slightly staggered, smoothing out the traffic spike and allowing the provider's token bucket to refill gracefully.

> [!NOTE] 
> **Provider-Specific Header Variations** 
> OpenAI uses `x-ratelimit-reset-requests` and `x-ratelimit-reset-tokens`. Anthropic uses `anthropic-ratelimit-requests-reset` and `anthropic-ratelimit-tokens-reset`. If you are building a multi-model router that fails over from OpenAI to Anthropic, your exception classification router must be highly specific about which SDK headers it is parsing to avoid `KeyError` crashes.

By mastering precise API exception handling, HTTP status code classification, and header-driven backoff logic, you have fortified your cognitive architecture. You have shifted your scripts from fragile, hopeful executions into resilient, self-healing enterprise microservices capable of surviving the chaotic reality of live network traffic.

Does this robust approach to rate limit recovery and diagnostic feedback make sense? If so, we are ready to move forward.

---

## Block 7: Pydantic V2 for Structured Outputs • Custom validators: @field_validator and @model_validator.

Welcome to Block 7 of Week 10. Over the past chapters, we have explored generation parameters, rate limit resiliency, and the architectural scaffolding required to safely interface Large Language Models (LLMs) with the physical world. Yet, one fundamental challenge remains in the journey of an AI Automation Architect: bridging the semantic gap between the probabilistic output of an LLM and the deterministic requirements of business logic.

As outlined in the *AI Engineer roadmap* curriculum, true automation requires mastering "API, вебхуки и JSON (словарь, а не код)" (APIs, webhooks, and JSON - dictionaries, not code). An LLM fundamentally generates raw text strings. To pass that data into a PostgreSQL database, an n8n webhook, or a legacy CRM system, that text must be strictly validated against a predefined schema. Simply asking the model to "output JSON" and parsing it with the native `json.loads()` library is a fragile, amateur approach that will inevitably crash your pipeline in production.

In this exhaustive, production-grade deep-dive, we will master **Pydantic V2** as the ultimate boundary enforcement layer (Harness) for your AI agents. We will move beyond basic type hints and engineer advanced cryptographic-level data validation using custom `@field_validator` and `@model_validator` decorators. By the end of this block, you will possess the ability to algorithmically trap LLM hallucinations and dynamically route validation errors back into the agent's context for autonomous self-healing.

---

### Deep Theoretical Analysis: The Physics of Deterministic Boundaries

To build robust cognitive architectures, we must mathematically enforce rules on the LLM's outputs before they interact with our internal systems. 

#### 1. The Fallacy of "Strong Models"
As established in the foundational principles of harness engineering, specifically *Лекция 01. Сильные модели не означают надёжного исполнения* (Strong models do not mean reliable execution), you cannot simply trust a frontier model like GPT-4o or Claude 3.5 Sonnet to always respect your JSON constraints. Even with the best prompt engineering, models will occasionally hallucinate field names, return strings instead of integers, or invent data that violates your business rules. Pydantic serves as the physical "Harness" that catches these probabilistic anomalies before they poison your database.

#### 2. The Anatomy of Pydantic V2 Validators
Pydantic V2 is a data validation library written in Rust that enforces type hints at runtime. While standard `BaseModel` classes ensure a variable is an `int` or `str`, custom validators allow you to enforce deep semantic business logic:
* **`@field_validator` (Localized Boundary Checks):** This decorator runs validation logic on a *single* specific field immediately after it is parsed. For example, ensuring that an LLM-generated `confidence_score` is strictly between `0.0` and `1.0`, or verifying that an extracted `company_email` contains an `@` symbol.
* **`@model_validator` (Cross-Field Dependency Checks):** This decorator runs after all individual fields are parsed. It evaluates the entire dictionary to ensure holistic consistency. For example, if an agent is parsing a contract and sets `is_signed=True`, a `@model_validator` can enforce that the `signature_date` field must also be populated, rejecting the payload if it is not.

#### 3. The Diagnostic Loop: Turning Errors into Instructions
When Pydantic catches a hallucination and throws a `ValidationError`, you must not let the Python script crash. According to *Лекция 10. Только сквозное тестирование — настоящая верификация* (Only end-to-end testing is true verification), "сообщения об ошибках для агентов должны включать инструкции по исправлению" (error messages for agents must include instructions for fixing them). 
Furthermore, *Лекция 11. Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable) states: "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание" (Without observability, agents make decisions in uncertainty... retries turn into blind wandering). Your architecture must catch the `ValidationError`, parse its specific violation strings, and feed them back to the LLM as actionable context so the agent can fix its own mistake.

---

### ASCII Architecture Schema: The Deterministic Pydantic Harness

The following Directed Acyclic Graph (DAG) illustrates how the Orchestrator interacts with the Pydantic V2 layer, and how the self-healing Diagnostic Loop functions when the LLM hallucinates invalid data.

```ascii
=============================================================================================
 ENTERPRISE PYDANTIC V2 VALIDATION HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR / LLM ]
Output: `{"confidence_score": 1.5, "status": "active", "end_date": null}`
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. SDK STRUCTURED OUTPUT PARSER (JSON Parsing) |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. PYDANTIC V2 BASEMODEL (The Harness Layer) |
| |
| [ @field_validator('confidence_score') ] |
| - Checks if 0.0 <= score <= 1.0. |
| - FAILS: Score is 1.5. Raises ValueError. |
| |
| [ @model_validator(mode='after') ] |
| - Checks cross-field logic: if status == 'active', end_date must be None. |
+-----------------------------------------------------------------------------------------+
 | (Success) | (Validation Error Trapped)
 v v
[ 4A. DETERMINISTIC EXECUTION ] +------------------------------------------+
Pass sanitized Object to Database | 4B. DIAGNOSTIC OBSERVATION INJECTION |
or subsequent workflow nodes. | Transforms Error into string: |
 | "ValidationError: confidence_score must |
 | be between 0.0 and 1.0. Fix and retry." |
 +------------------------------------------+
 |
 v
 [ 5. AGENT SELF-HEALING LOOP ]
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready data pipeline using Pydantic V2 to validate a complex AI-generated output. In this scenario, the agent is tasked with parsing a highly complex legal analysis document into a strictly typed analytical report.

#### Step 1: Architecting the Pydantic V2 Models
We define our strict schema using `BaseModel`, incorporating `Field` descriptions for the LLM, and our custom validation decorators.

```python
import json
import logging
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationError

# "Сделайте рантайм агента наблюдаемым"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [VALIDATION_HARNESS] - %(message)s')

class LegalEntity(BaseModel):
 """Schema representing an extracted legal entity from a document."""
 entity_name: str = Field(..., description="The full legal name of the entity.")
 entity_type: str = Field(..., description="Must be 'Corporation', 'LLC', or 'Individual'.")

 @field_validator('entity_type')
 @classmethod
 def validate_entity_type(cls, value: str) -> str:
 """Localized check to prevent LLM hallucination of unapproved entity types."""
 allowed_types = ['Corporation', 'LLC', 'Individual']
 if value not in allowed_types:
 raise ValueError(f"Hallucinated entity_type: '{value}'. Must be one of {allowed_types}.")
 return value

class LegalAnalysisReport(BaseModel):
 """The master schema for the structured JSON output requested from the LLM."""
 contract_id: str = Field(..., description="Unique alphanumeric identifier of the contract.")
 is_signed: bool = Field(..., description="Boolean indicating if the contract has been fully executed.")
 signature_date: Optional[str] = Field(None, description="ISO 8601 date string if signed, else null.")
 parties_involved: List[LegalEntity] = Field(..., description="List of all entities in the contract.")
 confidence_score: float = Field(..., description="The AI's confidence in its extraction (0.0 to 1.0).")

 @field_validator('confidence_score')
 @classmethod
 def validate_confidence(cls, score: float) -> float:
 """Ensures the LLM understands probabilistic boundaries."""
 if not (0.0 <= score <= 1.0):
 raise ValueError(f"Confidence score {score} is mathematically invalid. Must be 0.0 - 1.0.")
 return score

 @model_validator(mode='after')
 def validate_signature_logic(self) -> 'LegalAnalysisReport':
 """
 Cross-field dependency check.
 If the LLM claims the contract is signed, it MUST provide a date.
 If it is not signed, it MUST NOT invent a date.
 """
 if self.is_signed and not self.signature_date:
 raise ValueError("Logical Error: 'is_signed' is True, but no 'signature_date' was provided.")
 if not self.is_signed and self.signature_date:
 raise ValueError("Logical Error: 'is_signed' is False, but a 'signature_date' was hallucinated.")
 
 # Simple Date format validation
 if self.signature_date:
 try:
 datetime.strptime(self.signature_date, "%Y-%m-%d")
 except ValueError:
 raise ValueError(f"Date format hallucination: '{self.signature_date}'. Must be YYYY-MM-DD.")
 
 return self
```

#### Step 2: Implementing the Self-Healing Dispatcher
This script wraps the OpenAI API call and implements the recursive diagnostic loop, turning Pydantic crashes into actionable feedback for the agent.

```python
import os
from openai import OpenAI

class StructuredOutputHarness:
 def __init__(self, max_retries: int = 3):
 self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
 self.max_retries = max_retries

 def parse_document(self, document_text: str) -> Optional[LegalAnalysisReport]:
 """Executes the LLM request and enforces Pydantic validation recursively."""
 
 system_prompt = (
 "You are an expert legal parsing agent. Analyze the text and output pure JSON "
 "matching the requested schema perfectly."
 )
 
 # We maintain the message history to allow for conversational correction
 messages = [
 {"role": "system", "content": system_prompt},
 {"role": "user", "content": f"Extract data from this text:\n\n{document_text}"}
 ]

 attempt = 0
 while attempt <= self.max_retries:
 logging.info(f"Dispatching to LLM (Attempt {attempt}/{self.max_retries})...")
 
 try:
 response = self.client.beta.chat.completions.parse(
 model="gpt-4o",
 messages=messages,
 # OpenAI's Beta Parse endpoint natively handles the base JSON schema, 
 # but Pydantic handles our deep semantic validation decorators.
 response_format=LegalAnalysisReport,
 temperature=0.0 # Greedy decoding for data extraction
 )
 
 # Extract the parsed object
 parsed_object = response.choices.message.parsed
 logging.info("Payload successfully validated through Pydantic V2.")
 return parsed_object

 except ValidationError as e:
 # TRAPPING THE HALLUCINATION
 attempt += 1
 logging.warning(f"Pydantic Validation Failed on Attempt {attempt}.")
 
 # Format the error into an actionable instruction (Lecture 10 principle)
 error_details = json.dumps([err['msg'] for err in e.errors()])
 diagnostic_feedback = (
 f"Pydantic Validation Error: Your previous JSON payload failed semantic validation. "
 f"Details: {error_details}. "
 f"FIX INSTRUCTION: Please review the strict rules for 'confidence_score', 'entity_type', "
 f"and the cross-field dependency between 'is_signed' and 'signature_date'. "
 f"Regenerate a corrected JSON object."
 )
 
 # Append the failure to the context window so the agent learns
 messages.append({"role": "assistant", "content": response.choices.message.content or "{}"})
 messages.append({"role": "user", "content": diagnostic_feedback})
 
 if attempt > self.max_retries:
 logging.critical("Max validation retries exhausted. Pipeline halting.")
 return None
 
 except Exception as generic_e:
 logging.error(f"Fatal System Error: {generic_e}")
 return None

# ==========================================
# Execution Environment
# ==========================================
if __name__ == "__main__":
 harness = StructuredOutputHarness()
 
 # A tricky piece of text designed to test the model's logic
 complex_text = (
 "Contract AX-992 involves Wayne Enterprises (Corporation) and John Doe (Individual). "
 "The contract is currently in the drafting phase and is not signed yet, though "
 "they expect to sign it on 2026-12-01."
 )
 
 result = harness.parse_document(complex_text)
 if result:
 print("\n--- DETERMINISTIC PAYLOAD SECURED ---")
 print(result.model_dump_json(indent=2))
```

---

### Realistic Business Applications & Unit Economics

Implementing deep Pydantic validation fundamentally alters the unit economics of AI pipelines, allowing them to scale to millions of requests without manual oversight.

**1. Reliable Data Engineering Pipelines (ETL)**
In modern B2B data architectures, companies often use LLMs to extract unstructured web data (e.g., scraping LinkedIn profiles) and load it into strict relational databases like PostgreSQL. If a pipeline processes 50,000 leads a day, a 1% hallucination rate means 500 corrupt database entries daily. As highlighted in *AI Engineer roadmap* regarding "API, вебхуки и JSON", you cannot afford database crashes. By injecting a Pydantic `@field_validator` that uses regex to strictly validate that `extracted_linkedin_url` actually starts with `[Ссылка](https://linkedin.com/`), the pipeline achieves 100% deterministic safety, completely eliminating the need for human QA teams.

**2. Intelligent Contract Auditing (Multi-Agent Swarms)**
In legal automation workflows, as discussed in the Phase 5 roadmap requirements for "мульти-агентных сценариев", the output of Agent A is often the input for Agent B. If Agent A (the Extractor) hallucinates that a contract is signed but provides no date, Agent B (the Risk Assessor) will crash trying to process a `None` type. By enforcing a `@model_validator` that holistically checks `is_signed` against `signature_date`, you create an absolute, impenetrable contract between agents, ensuring that complex swarms do not cascade into failure due to one bad token prediction.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Relying on Pydantic to discipline a neural network introduces unique edge cases that an architect must monitor.

> [!CAUTION] 
> **The Infinite Validation Loop (Doom Loop)** 
> **The Problem:** The LLM hallucinates an invalid status, Pydantic throws a `ValidationError`, the error is fed back to the LLM, but the LLM is mathematically incapable of generating the correct value due to poor prompt design. It tries the same bad value 10 times in a row, burning your API tokens and rate limits. 
> **Harness Mitigation:** The diagnostic feedback string *must* be highly specific. Do not just return `"Error in status field"`. You must algorithmically inject the acceptable enums into the feedback string: `"Error: status must be EXACTLY one of: ['active', 'pending']"`. Furthermore, you must cap your retry loop (e.g., `self.max_retries = 3`) to act as an economic circuit breaker, preventing runaway costs.

> [!WARNING] 
> **Silent Coercion Traps** 
> **The Error:** Pydantic V2 is highly efficient and will often attempt to silently coerce data types. If an LLM generates `{"age": "25"}` (a string), Pydantic will silently coerce it to the integer `25` if the schema dictates `age: int`. While convenient, this can mask the fact that your LLM is fundamentally misinterpreting its formatting instructions, which can lead to larger logic breakdowns later. 
> **Diagnostic Loop:** To enforce absolute strictness, AI Architects should instantiate models with strict mode enabled: `model_config = ConfigDict(strict=True)`. This forces Pydantic to reject `"25"`, triggering the self-healing loop and forcing the LLM to learn that its JSON generation must be typographically perfect.

> [!NOTE] 
> **Cost Overheads of Retry Logic** 
> Every time a `ValidationError` triggers the self-healing loop, the script must resend the entire message history (including the document text) back to the LLM. In our code example, a 10,000-token document that fails validation three times will cost 30,000 tokens to parse. This reinforces why precise system instructions (to minimize the initial error rate) and highly descriptive validation errors (to fix the error on the first retry) are the highest ROI skills for an AI Builder.

By mastering Pydantic V2 decorators and the self-healing diagnostic loop, you have transformed your AI application from a brittle text generator into a rugged, enterprise-grade software system capable of defending its own data boundaries.

Does this setup for deep semantic validation make sense? We can discuss how to deploy these validated models via standard webhooks to orchestrators like n8n next.

---

## Block 8: Self-healing JSON loops — capturing Pydantic errors and query retries.

Welcome to Block 8 of Week 10. In Chapter 7, we engineered our physical boundary layer using Pydantic V2. We established that Large Language Models (LLMs) are probabilistic engines, and to use them in enterprise automation, we must force their outputs into deterministic structures. We built `@field_validator` and `@model_validator` decorators to catch hallucinations, logical inconsistencies, and data type errors. 

However, simply catching an error is not enough. If your Python script crashes with a `ValidationError` every time the LLM hallucinates a string instead of an integer, your automation pipeline is fragile. In true enterprise AI architecture, the system must not crash; it must autonomously heal. 

As stated in the AI Builder curriculum, a core automation skill is managing errors natively, specifically implementing a "Повторный промпт к LLM при кривом JSON" (retry prompt to the LLM upon crooked JSON). In this exhaustive, production-grade deep dive, we will master **Self-Healing JSON Loops**. We will bridge the gap between static validation and dynamic cognitive correction, allowing our agents to read their own stack traces, understand their schema violations, and rewrite their payloads without human intervention.

---

### Deep Theoretical Analysis: The Physics of Autonomous Self-Correction

Before writing our recursive while-loops, an AI Architect must internalize the cognitive dynamics of how LLMs interpret failure.

#### 1. The Fallacy of the Silent Retry (Blind Wandering)
When junior developers first encounter a JSON schema failure, they often write a naive `try/except` block that simply resends the identical prompt to the API: `except Exception: return get_llm_response()`. This is a catastrophic anti-pattern. 
As mandated by the foundational principles of harness engineering in *Лекция 11. Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable): "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание" (Without observability, agents make decisions in uncertainty... retries turn into blind wandering). If the LLM does not know *why* its payload was rejected, it will generate the exact same hallucination again, burning your token budget.

#### 2. Actionable Diagnostic Feedback
To break the cycle of blind wandering, you must feed the specific error back into the agent's context window. But simply passing `ValidationError: status is invalid` is insufficient. 
According to *Лекция 10. Только сквозное тестирование — настоящая верификация*, the architectural rule is absolute: "сообщения об ошибках для агентов должны включать инструкции по исправлению" (error messages for agents must include instructions for fixing them). You must explicitly tell the agent what went wrong and provide a direct path to correct it (e.g., "The field 'status' received 'pending', but must be exactly one of: ['active', 'closed'].").

#### 3. The Self-Annealing Framework
This cycle of feedback and correction is formally known as "Self-Annealing." In advanced agentic architectures, "if an error occurs in the agent a self annealing framework means it will not crash it will instead pause it will read the error message and then it will look at the code that caused the error... and then rewrite". By returning the Pydantic error trace as a `user` message directly back to the LLM, the model updates its mental state, recognizes its failure against the schema, and generates a stronger, fully compliant JSON object on the next pass.

#### 4. "Strong Models Do Not Mean Reliable Execution"
Never assume that utilizing GPT-4o or Claude 3.5 Sonnet exempts you from building these loops. As *Лекция 01. Сильные модели не означают надёжного исполнения* dictates, the inherent stochastic nature of transformers means that even the most intelligent model will eventually skip a required JSON key or invent a nonexistent enum. True reliability is built in the Harness (the Python loop), not the neural network.

---

### ASCII Architecture Schema: The Self-Healing Diagnostic Loop

The following Directed Acyclic Graph (DAG) demonstrates the exact memory management and message appending sequence required to successfully execute a self-healing loop.

```ascii
=============================================================================================
 ENTERPRISE SELF-HEALING JSON HARNESS
=============================================================================================

[ 1. INITIAL LLM DISPATCH ]
 Messages: [{"role": "system", "content": "..."}, {"role": "user", "content": "Extract data"}]
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. PAYLOAD GENERATION & PARSING |
| Output: `{"email": "john.doe.com", "age": "twenty"}` |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. PYDANTIC V2 VALIDATION (The Harness Layer) |
| - Evaluates email against Regex. FAILS (Missing '@'). |
| - Evaluates age against Integer type. FAILS (String provided). |
| - Raises `ValidationError`. |
+-----------------------------------------------------------------------------------------+
 / (Success) \ (Validation Error)
 v v
[ 4A. RETURN OBJECT ] +------------------------------------------+
Exit Loop. Return clean data | 4B. DIAGNOSTIC OBSERVATION INJECTION |
to orchestrator. | - Catch Exception. |
 | - Format: "Error in 'email': missing @." |
 | - Append invalid JSON as 'assistant'. |
 | - Append Error as 'user'. |
 +------------------------------------------+
 |
 v
 [ 5. RETRY DISPATCH (Max Retries: 3) ]
 LLM reads its mistake, reflects, and 
 outputs corrected JSON. 
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready Python class that enforces self-healing. This system will dynamically catch Pydantic errors, format them into actionable prompts, append them to the conversation history, and loop until the LLM yields or the maximum retry limit is hit.

#### Step 1: Defining the Strict Pydantic Schema
First, we establish our rigorous data contract. We use strict typing to prevent the LLM from relying on silent coercions.

```python
import json
import logging
import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
from openai import OpenAI

# Lecture 11: Make the runtime observable
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SELF_HEAL_LOOP] - %(message)s')

class CustomerRecord(BaseModel):
 """Schema for extracting highly structured customer CRM data."""
 customer_id: str = Field(..., description="The alphanumeric ID of the customer.")
 email: str = Field(..., description="The official contact email.")
 account_tier: str = Field(..., description="Must be exactly one of: 'Free', 'Pro', 'Enterprise'.")

 @field_validator('email')
 @classmethod
 def validate_email_format(cls, v: str) -> str:
 """Regex validation to ensure the LLM didn't hallucinate a broken email."""
 if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v):
 raise ValueError(f"The generated email '{v}' is invalid. It must contain an '@' symbol and domain.")
 return v

 @field_validator('account_tier')
 @classmethod
 def validate_tier(cls, v: str) -> str:
 allowed = ['Free', 'Pro', 'Enterprise']
 if v not in allowed:
 raise ValueError(f"Hallucinated tier '{v}'. You must select EXACTLY from: {allowed}")
 return v
```

#### Step 2: Architecting the Self-Healing Retry Loop
This is the core of the Agent Builder pattern. We utilize a `while` loop that manages its own conversation history to ensure the LLM understands *contextually* what it did wrong on the previous turn.

```python
class ResilientDataExtractor:
 """
 Implements a Self-Annealing JSON loop to dynamically capture 
 and resolve Pydantic validation errors through LLM reflection.
 """
 def __init__(self, max_retries: int = 3):
 self.client = OpenAI() # Assumes OPENAI_API_KEY is in environment
 self.max_retries = max_retries

 def extract_with_healing(self, raw_text: str) -> Optional[CustomerRecord]:
 system_instructions = (
 "You are an elite data extraction agent. "
 "Analyze the unstructured text and output a JSON object matching the exact schema."
 )
 
 # We must maintain history so the agent remembers its past mistakes
 messages = [
 {"role": "system", "content": system_instructions},
 {"role": "user", "content": f"Extract the customer record from this text:\n\n{raw_text}"}
 ]

 attempt = 0
 while attempt <= self.max_retries:
 logging.info(f"Initiating generation (Attempt {attempt + 1}/{self.max_retries + 1})...")
 
 try:
 # Using OpenAI's structured outputs feature alongside our Pydantic Harness
 response = self.client.beta.chat.completions.parse(
 model="gpt-4o",
 messages=messages,
 response_format=CustomerRecord,
 temperature=0.0 # Greedy decoding for maximum determinism
 )
 
 # If this succeeds, Pydantic has validated every field and decorator
 valid_data = response.choices.message.parsed
 logging.info("Payload successfully validated! Loop resolved.")
 return valid_data

 except ValidationError as e:
 attempt += 1
 logging.warning(f"Pydantic Trapped a Hallucination! Initiating Self-Healing Phase.")
 
 if attempt > self.max_retries:
 logging.critical("Maximum self-healing retries exhausted. Aborting to prevent infinite loops.")
 return None

 # 1. Capture the exact invalid JSON output to show the LLM its mistake
 invalid_json_string = response.choices.message.content if response else "{}"
 messages.append({"role": "assistant", "content": invalid_json_string})
 
 # 2. Extract specific Pydantic errors
 error_list = [f"Field '{err['loc']}': {err['msg']}" for err in e.errors()]
 formatted_errors = "\n".join(error_list)
 
 # 3. Construct Actionable Feedback (Lecture 10 Principle)
 diagnostic_feedback = (
 f"SYSTEM VALIDATION ERROR:\n"
 f"Your previous JSON response failed strict validation rules.\n"
 f"Errors detected:\n{formatted_errors}\n\n"
 f"FIX INSTRUCTION: Please deeply reflect on the errors above. "
 f"Ensure 'email' contains an '@' and 'account_tier' matches the allowed enums perfectly. "
 f"Generate a new, fully compliant JSON object."
 )
 
 logging.info(f"Injecting Diagnostic Feedback:\n{diagnostic_feedback}")
 messages.append({"role": "user", "content": diagnostic_feedback})

 except Exception as generic_e:
 logging.error(f"Fatal API or Network Error: {generic_e}")
 return None

# ==========================================
# Execution Environment
# ==========================================
if __name__ == "__main__":
 extractor = ResilientDataExtractor(max_retries=3)
 
 # Intentionally messy text designed to trigger LLM hallucinations
 tricky_input = (
 "Client ID: CX-9901. Reach out to them at CX9901-at-domain.com. "
 "They are currently on the 'Basic' plan but want to upgrade."
 )
 
 # 1. On Attempt 1, the LLM will likely output email="CX9901-at-domain.com" and account_tier="Basic".
 # 2. Pydantic will throw TWO errors (No '@' symbol, and 'Basic' is not 'Free', 'Pro', or 'Enterprise').
 # 3. The loop will catch the error, format the instruction, and ask the LLM to try again.
 # 4. On Attempt 2, the LLM reads its mistake, reflects, and corrects the payload.
 
 final_record = extractor.extract_with_healing(tricky_input)
 
 if final_record:
 print("\n--- FINAL DETERMINISTIC JSON PAYLOAD ---")
 print(final_record.model_dump_json(indent=2))
```

---

### Realistic Business Applications & Unit Economics

Implementing a closed-loop self-healing mechanism fundamentally changes the financial viability of automation systems.

**1. Scraping and CRM Data Enrichment (No-Code Integration)**
In modern automated sales pipelines, tools like n8n are heavily used to trigger webhooks that pass scraped website data into a Python API for structured extraction. If a client is paying you $5,000 to build a lead-generation system, that system cannot require daily human intervention. As referenced in the *AI Engineer roadmap* curriculum, an automation builder must configure a "Повторный промпт к LLM при кривом JSON". 
If an LLM parses a LinkedIn profile and outputs `"company_size": "10-50 employees"` but your CRM strictly requires an integer (`50`), the webhook will fail. By wrapping your Python API endpoint in a `ResilientDataExtractor` loop, the agent catches the string violation, corrects it to `50`, and returns HTTP 200 OK back to n8n. The client never sees the error, saving hundreds of hours of manual database cleanup.

**2. Handling Financial Document OCR (Receipts/Invoices)**
When processing massive volumes of raw OCR (Optical Character Recognition) text from scanned invoices, the OCR often misreads characters (e.g., mistaking an `S` for a `$`). An LLM trying to format this into `{"total_amount": float}` will crash if it generates `{"total_amount": "$1,00S.00"}`. A self-annealing framework catches the Pydantic type error, instructs the LLM: *"Remove all currency symbols and letters, output pure float,"* and the LLM seamlessly extracts `1005.00` on the retry. This self-correction loop allows the pipeline to process 100,000 invoices overnight without halting on single-document failures.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Building `while` loops around paid API calls is inherently dangerous. An AI Architect must implement strict circuit breakers to protect the infrastructure.

> [!CAUTION] 
> **The Context Window Explosion (Token Bloat)** 
> **The Problem:** Every time your loop fails, you append the failed JSON (Assistant) and the error message (User) back into the `messages` array. If the agent fails 4 times on a massive 15,000-token payload, your `messages` array grows exponentially, quickly exceeding token limits and causing API costs to skyrocket. As noted in Habr articles on optimization, "Как я перестал «кормить» нейросеть токенами" (How I stopped feeding the neural network tokens), unchecked loops drain budgets instantly. 
> **Harness Mitigation:** You must enforce a strict `max_retries` counter (e.g., 3). If the model cannot fix its schema violation in 3 attempts, the input data is likely hopelessly malformed. The loop must break, log a `CRITICAL` error to the human observer, and gracefully reject the payload rather than looping into financial ruin.

> [!WARNING] 
> **The "Blind Wandering" Doom Loop** 
> **The Error:** You catch a `ValidationError`, but your diagnostic feedback simply says: `"System Error: Invalid JSON. Try again."` The LLM does not know *what* was invalid. It guesses, changes a correct field, keeps the wrong field, and fails again, creating an infinite Doom Loop. 
> **Diagnostic Loop:** You must leverage Pydantic's `e.errors()` object. You must programmatically extract the exact `loc` (field location) and `msg` (the reason it failed) and map it into the prompt. The LLM is a reasoning engine; if you give it the specific stack trace of its mistake, it will solve it. 

> [!NOTE] 
> **Irrecoverable Logic Errors vs. Typographical Errors** 
> Self-healing loops are incredible for fixing formatting issues (e.g., removing a stray comma, correcting an enum casing from `pro` to `Pro`). However, if the source text fundamentally *lacks* the required data (e.g., the invoice simply has no date), the LLM cannot magically invent it. Your Pydantic schema must utilize `Optional[str]` for fields that might genuinely be missing, otherwise, the loop will infinitely demand data that does not exist until it exhausts its retries.

By mastering the integration of Pydantic validation with dynamic conversation history appending, you have created a true cognitive architecture. Your scripts are no longer passive pipelines; they are active, self-correcting agents capable of wrestling probabilistic hallucinations into deterministic, enterprise-grade business value. 

Are you ready to advance to Block 9, where we will move beyond single-agent architectures and explore the "Orchestrator-Worker" pattern for handling complex, multi-step routing tasks?

---

## Block 9: Session trace typings and saving reasoning logs inside Python classes.

Welcome to Block 9 of Week 10. In previous blocks, we mastered the physical boundaries of Large Language Models (LLMs) using Pydantic V2 and engineered autonomous self-healing loops that catch schema violations. We transformed fragile text generators into robust, deterministic systems. However, an enterprise AI pipeline is not simply about producing the final output; it is about guaranteeing absolute transparency, reproducibility, and auditability throughout the entire cognitive process.

When a standard script fails, a developer reads the stack trace. When an autonomous AI agent fails—or worse, succeeds using flawed logic—a standard stack trace is useless, because the "logic" occurred entirely within the probabilistic weights of a neural network. As strictly mandated by the foundational principles of harness engineering in *Lecture 11: Сделайте рантайм агента наблюдаемым* (Make the agent runtime observable), you cannot manage what you cannot see. Furthermore, the roadmap warns that "Без наблюдаемости агенты принимают решения в условиях неопределённости... ретраи превращаются в слепое блуждание" (Without observability, agents make decisions in uncertainty... retries turn into blind wandering).

In this exhaustive, production-grade deep dive, we will master **Session Tracing and Reasoning Logs**. We will utilize Pydantic to strictly type the agent's internal monologue (the ReAct trajectory) and engineer Python classes to persist this state. By implementing what the AI Engineer Roadmap calls "Durable resume: persist истории сообщений и состояния в SQLite после каждого шага" (Durable resume: persist message history and state in SQLite after each step), we will transform our agents from opaque black boxes into fully auditable, observable cognitive architectures.

---

### Deep Theoretical Analysis: The Physics of Agent Observability

To engineer a true enterprise harness, an AI Architect must discard the concept of "print statements" and embrace structured, deterministic telemetry.

#### 1. The ReAct Trajectory as a Data Structure
A ReAct (Reasoning and Acting) agent does not execute in a single forward pass. It operates in a cyclical trajectory: **Thought** -> **Action** -> **Observation**. 
If you only save the final JSON output of the agent, you lose the trajectory. You do not know if the agent arrived at the correct answer efficiently on the first try, or if it spent 45 iterations hallucinating API calls before finally guessing the right parameters. To evaluate and optimize an agent, you must capture the entire trace. As outlined in the Phase 4 testing guidelines, an architect must perform a "trajectory eval: спланировал ли агент, заспавнил ли >=2 суб-агента, процитировал ли источники, уложился ли в бюджет?" (trajectory eval: did the agent plan, spawn >=2 sub-agents, cite sources, stay within budget?). You cannot evaluate a trajectory if you do not rigorously type and save it in real-time.

#### 2. OpenTelemetry and The Tracing Standard
In modern MLOps (or GenAIOps), tracing agent executions requires standardized schemas. The AI Engineer roadmap explicitly requires "OpenTelemetry-трейсинг через opentelemetry-sdk в LangSmith или Phoenix" (OpenTelemetry tracing via opentelemetry-sdk in LangSmith or Phoenix). OpenTelemetry (OTEL) treats each LLM call, tool execution, and self-reflection step as a "Span." Multiple spans combine to form a "Trace." By typing our reasoning logs properly in Python, our custom harness becomes fully compatible with these massive, enterprise-grade observability platforms, allowing us to visualize the agent's brain in real-time.

#### 3. Durable Execution and the Resumable State
A severe vulnerability in amateur agent design is in-memory volatility. If an agent is tasked with a 2-hour deep research workflow and the Python process crashes at minute 119 due to a network timeout, the entire session—and all API costs incurred—are permanently destroyed. 
To achieve production hardening, we must implement "Durable resume." By saving the strictly typed session trace to a persistent SQLite database *after every single step*, the harness achieves true statefulness. If the container crashes, the orchestrator simply boots back up, queries the database for the last `run_id`, re-injects the reasoning trace into the LLM's context, and resumes execution seamlessly. 

#### 4. Context Bloat and Filesystem Offload
As we log observations from tools (like a web scraper returning a 5MB HTML document), we cannot simply append massive strings into our trace logs blindly. The AI Engineer roadmap dictates the "Filesystem offload: любой результат инструмента >20K токенов пишется в./workspace/<id>.txt, в контексте остается путь и preview из 10 строк" (Filesystem offload: any tool result >20K tokens is written to./workspace/<id>.txt, the context retains the path and a 10-line preview). Our tracing class must actively monitor string sizes and redirect payload storage to prevent blowing out both the database and the LLM's context window.

---

### ASCII Architecture Schema: Durable Tracing Harness

The following Directed Acyclic Graph (DAG) illustrates how the Pydantic-typed reasoning objects interact with the SQLite Persistence Layer and external observability platforms to guarantee a durable, auditable session.

```ascii
=============================================================================================
 ENTERPRISE SESSION TRACING & DURABLE RESUME HARNESS
=============================================================================================

[ 1. ReAct ORCHESTRATOR LOOP ]
 |
 |-> (A) THOUGHT: "I need to search the database for user 992."
 |-> (B) ACTION: `search_db({"user_id": 992})`
 |-> (C) OBSERVATION: "User 992 found. Status: Active."
 v
+-----------------------------------------------------------------------------------------+
| 2. PYDANTIC TRACE TYPINGS (Structured Memory) |
| Validates the step elements into a strict `TraceStep` object. |
| { |
| "step_id": "uuid-1234", |
| "timestamp": "2026-06-01T12:00:00Z", |
| "thought": "I need to search...", |
| "action": {"tool": "search_db", "args": {"user_id": 992}}, |
| "observation": "User 992 found...", |
| "token_usage": {"prompt": 150, "completion": 45} |
| } |
+-----------------------------------------------------------------------------------------+
 | |
 v v
+------------------------------------+ +-------------------------------------------+
| 3A. SQLITE DURABLE STATE (Local) | | 3B. OPENTELEMETRY EXPORTER (Cloud) |
| - Commits `TraceStep` to DB. | | - Translates Pydantic to OTEL Spans. |
| - Enables instant resume if the | | - Flushes to LangSmith / Phoenix. |
| Python process is killed. | | - Enables UI visual trajectory analysis. |
+------------------------------------+ +-------------------------------------------+
 |
 v
[ 4. CONTEXT INJECTION FOR NEXT CYCLE ]
The agent reads the persisted trace to plan its next move.
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a production-ready system utilizing Pydantic V2 to define the immutable structure of a ReAct trace, followed by a Python manager class that handles SQLite database transactions for durable persistence.

#### Step 1: Architecting the Pydantic Trace Typings
We define rigorous models for every component of the agent's cognitive cycle. This ensures that logs are universally parsable by external dashboards or evaluation scripts.

```python
import uuid
import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Lecture 11: Make the runtime observable
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [TRACE_HARNESS] - %(message)s')

class AgentAction(BaseModel):
 """Represents a specific tool invocation requested by the LLM."""
 tool_name: str = Field(..., description="The name of the executed tool.")
 arguments: Dict[str, Any] = Field(..., description="The JSON arguments passed to the tool.")

class TokenUsage(BaseModel):
 """Tracks the economic cost of a single execution step."""
 prompt_tokens: int = Field(default=0)
 completion_tokens: int = Field(default=0)
 total_tokens: int = Field(default=0)

class TraceStep(BaseModel):
 """
 A single, complete ReAct cycle (Thought -> Action -> Observation).
 This is the atomic unit of agentic memory.
 """
 step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
 timestamp: datetime = Field(default_factory=datetime.utcnow)
 
 thought: str = Field(..., description="The internal reasoning of the agent.")
 action: Optional[AgentAction] = Field(None, description="The tool called, if any.")
 observation: Optional[str] = Field(None, description="The result of the tool execution.")
 
 usage: TokenUsage = Field(default_factory=TokenUsage)

class SessionTrace(BaseModel):
 """
 The complete trajectory of an agent's session, enabling Durable Resume 
 and Trajectory Evals.
 """
 session_id: str = Field(..., description="Unique ID for the overall task.")
 task_directive: str = Field(..., description="The original prompt/goal given to the agent.")
 status: str = Field(default="running", description="Status: running, completed, or failed.")
 steps: List[TraceStep] = Field(default_factory=list)
```

#### Step 2: Engineering the SQLite Durable Trace Manager
This class takes the Pydantic models and physically persists them to the local disk. If the script crashes, we can re-instantiate this class with the same `session_id` and pick up exactly where we left off.

```python
class DurableTraceManager:
 """
 Enterprise manager for persisting Pydantic-typed agent traces to SQLite.
 Fulfills the 'Durable resume' requirement of the AI Engineer Roadmap.
 """
 def __init__(self, db_path: str = "agent_traces.db"):
 self.db_path = db_path
 self._initialize_db()

 def _initialize_db(self):
 """Creates the relational schema for tracking sessions and steps."""
 with sqlite3.connect(self.db_path) as conn:
 cursor = conn.cursor()
 # Table for overarching sessions
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS sessions (
 session_id TEXT PRIMARY KEY,
 task_directive TEXT,
 status TEXT,
 created_at TIMESTAMP
 )
 """)
 # Table for atomic ReAct steps
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS trace_steps (
 step_id TEXT PRIMARY KEY,
 session_id TEXT,
 timestamp TIMESTAMP,
 step_data JSON,
 FOREIGN KEY(session_id) REFERENCES sessions(session_id)
 )
 """)
 conn.commit()
 logging.info("SQLite Trace Database initialized securely.")

 def create_or_resume_session(self, session_id: str, task_directive: str) -> SessionTrace:
 """
 Implements Durable Resume. If the session exists, loads the history.
 If it is new, initializes a fresh SessionTrace.
 """
 with sqlite3.connect(self.db_path) as conn:
 cursor = conn.cursor()
 cursor.execute("SELECT task_directive, status FROM sessions WHERE session_id =?", (session_id,))
 row = cursor.fetchone()
 
 if row:
 logging.info(f"Resuming existing session: {session_id}")
 # Load existing steps
 cursor.execute("SELECT step_data FROM trace_steps WHERE session_id =? ORDER BY timestamp ASC", (session_id,))
 steps_data = [json.loads(r) for r in cursor.fetchall()]
 
 # Reconstruct the Pydantic object entirely from DB state
 return SessionTrace(
 session_id=session_id,
 task_directive=row,
 status=row,
 steps=[TraceStep(**step) for step in steps_data]
 )
 else:
 logging.info(f"Initializing new session: {session_id}")
 cursor.execute(
 "INSERT INTO sessions (session_id, task_directive, status, created_at) VALUES (?,?,?,?)",
 (session_id, task_directive, "running", datetime.utcnow())
 )
 conn.commit()
 return SessionTrace(session_id=session_id, task_directive=task_directive)

 def append_step(self, session_id: str, step: TraceStep):
 """
 Commits a newly executed ReAct step to the database immediately.
 """
 # Truncate massive observations to prevent database bloat (Filesystem Offload Principle)
 if step.observation and len(step.observation) > 5000:
 file_id = step.step_id
 offload_path = f"./workspace/{file_id}.txt"
 with open(offload_path, "w", encoding="utf-8") as f:
 f.write(step.observation)
 
 # Replace observation with a pointer to the filesystem
 step.observation = (
 f"[SYSTEM ALERT: Observation exceeded 5000 chars. "
 f"Full payload offloaded to {offload_path}. "
 f"Preview: {step.observation[:500]}...]"
 )
 logging.warning(f"Filesystem Offload triggered for step {step.step_id}")

 step_json = step.model_dump_json()
 
 with sqlite3.connect(self.db_path) as conn:
 cursor = conn.cursor()
 cursor.execute(
 "INSERT INTO trace_steps (step_id, session_id, timestamp, step_data) VALUES (?,?,?,?)",
 (step.step_id, session_id, step.timestamp, step_json)
 )
 conn.commit()
 logging.info(f"Trace step {step.step_id} durably persisted to SQLite.")
```

#### Step 3: Integrating Tracing into the Execution Loop
We now demonstrate how an AI Architect uses these classes during an active generation loop to guarantee observability.

```python
if __name__ == "__main__":
 # 1. Initialize our Persistent Telemetry Logger
 tracer = DurableTraceManager()
 
 # 2. We define a unique ID for a long-running background job
 current_job_id = "job-aws-migration-analysis-001"
 goal = "Analyze the AWS billing CSV and determine optimization strategies."
 
 # 3. Create or Resume State (If script crashed yesterday, it restores history)
 active_session = tracer.create_or_resume_session(current_job_id, goal)
 
 # --- SIMULATED AGENT LOOP EXECUTION ---
 print(f"\n--- EXECUTING SESSION: {active_session.session_id} ---")
 print(f"Prior Steps in Memory: {len(active_session.steps)}")
 
 # Simulated output from the LLM via SDK
 simulated_llm_thought = "I need to read the billing CSV first to understand the data structure."
 simulated_tool_call = AgentAction(tool_name="read_filesystem", arguments={"path": "billing.csv"})
 
 # Simulated execution result
 simulated_observation = "id,cost,service\n1,$500,EC2\n2,$1000,RDS"
 
 # 4. Pack the iteration into the strict Pydantic Model
 new_step = TraceStep(
 thought=simulated_llm_thought,
 action=simulated_tool_call,
 observation=simulated_observation,
 usage=TokenUsage(prompt_tokens=450, completion_tokens=85, total_tokens=535)
 )
 
 # 5. Persist the step durably
 tracer.append_step(active_session.session_id, new_step)
 active_session.steps.append(new_step)
 
 print("\n--- NEW STEP PERSISTED ---")
 print(new_step.model_dump_json(indent=2))
```

---

### Realistic Business Applications & Unit Economics

Understanding structured session tracing is the defining characteristic of a Senior AI Engineer managing production environments.

**1. "Trajectory Evals" in CI/CD Pipelines**
As outlined in Phase 4 of the roadmap, you must run automated evaluations on your agents using tools like *Inspect*. Consider a corporate compliance bot. If you update the LLM's system prompt, you need to know if the agent's behavior degraded. Because every session is strictly typed in Pydantic and saved to SQLite, you can write a deterministic CI/CD Python script that loops through the database traces. The script checks: `if "search_compliance_database" not in [step.action.tool_name for step in session.steps]: fail_eval()`. 
You are no longer guessing if the agent is behaving correctly based on its final text output; you are programmatically verifying its exact cognitive path.

**2. Asynchronous Fleet Management and Resiliency**
In enterprise architectures, you might have 500 agents running simultaneously processing insurance claims. These agents might take 15 minutes each. Cloud platforms (like AWS Lambda or Kubernetes pods) frequently preempt or kill long-running processes to manage node health. Without durable tracing, a pod restart wipes out 14 minutes of LLM context, requiring you to start over and pay for those tokens twice. By implementing the `create_or_resume_session` logic, a restarted pod simply fetches the trace from SQLite, loads the Pydantic objects back into the `messages` array, and resumes at minute 14 without burning duplicate computational budget.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Implementing telemetry introduces significant systems engineering challenges regarding state size and data privacy.

> [!CAUTION] 
> **PII (Personally Identifiable Information) Data Leakage** 
> **The Problem:** Your agent processes medical records. The ReAct trace captures the `observation`, which includes raw patient names, and persists it to a centralized, accessible SQLite database or pushes it to LangSmith. This is a severe HIPAA/GDPR violation. 
> **Harness Mitigation:** Your `append_step` method in the `DurableTraceManager` must include a PII obfuscation middleware. Before executing `conn.cursor().execute(...)`, you must pipe the Pydantic object's string fields through a regex scrubber or a local, lightweight NER (Named Entity Recognition) model to replace sensitive data with `<REDACTED>` tags, ensuring compliance while maintaining structural observability.

> [!WARNING] 
> **The Disk I/O Blocking Spiral** 
> **The Error:** In a heavily asynchronous multi-agent swarm, writing 50 massive JSON traces to a single SQLite file every second using synchronous `conn.commit()` calls will cause SQLite locking (`sqlite3.OperationalError: database is locked`). This blocks the main event loop, causing agents to timeout. 
> **Diagnostic Loop:** For high-throughput environments, you must decouple the execution loop from the telemetry loop. Do not write to SQLite synchronously. Instead, append the `TraceStep` Pydantic objects to an in-memory `asyncio.Queue`. A separate, dedicated background worker task should consume the queue and perform batched `INSERT` commits to the database, ensuring your cognitive loops run at maximum network speed.

> [!NOTE] 
> **Structured Output Coercion on Trace Loading** 
> When performing a "Durable resume" and loading old JSON traces from the database back into Pydantic models, be aware of versioning updates. If you update your `TraceStep` schema to require a new field (e.g., `latency_ms: float`), loading yesterday's database traces will trigger a `ValidationError` and crash the resume process. You must either provide `default` values in your Pydantic schema or write database migration scripts to backfill legacy trace rows to maintain backward compatibility.

By strictly typing the cognitive steps of your ReAct agent and persisting them durably, you have achieved absolute observability. Your architecture is no longer a fragile text generator; it is a stateful, auditable, enterprise-grade software system capable of surviving infrastructure failures and providing perfect historical transparency.

Does this breakdown of Pydantic trace typings and durable SQLite persistence make sense? If you are ready, we will transition into Phase 4 testing concepts, utilizing these very traces to run automated evaluations.

---

## Block 10: Schema versioning and data migration strategies in production agents.

Welcome to Block 10 of Week 10. In Chapter 9, we achieved absolute runtime observability. We engineered a durable SQLite persistence layer that records perfectly typed Pydantic traces of the agent's internal monologue and tool executions. If the Python process crashes, our agent utilizes "durable resume" to instantly recover its context. 

However, we must now confront the reality of long-term software maintenance. In traditional engineering, data schemas evolve. A business requirement changes, a new feature is requested, and suddenly your database structure must be updated. In AI engineering, this evolution introduces a catastrophic friction point. As established in the foundational curriculum, building integrations requires mastering "API, webhooks, and JSON (a dictionary, not code)". If you update your Pydantic V2 definitions in your Python code from `V1` to `V2`, but your SQLite database is full of legacy `V1` JSON traces, your durable resume pipeline will instantly crash with a fatal `ValidationError` the moment you attempt to load historical data.

In this exhaustive, production-grade deep-dive, we will master **Schema Versioning and Data Migration Strategies**. We will address the profound challenges of "backward and forward compatibility" in generative architectures. You will learn to engineer deterministic migration layers that dynamically upgrade legacy AI memory payloads, ensuring that your long-running cognitive architectures survive inevitable codebase mutations without losing a single token of historical context.

---

### Deep Theoretical Analysis: The Physics of Evolving Cognitive Architectures

To build AI systems that scale seamlessly across months and years, an AI Automation Architect must bridge the gap between static database records and dynamic neural execution.

#### 1. The Forward and Backward Compatibility Bottleneck
As highlighted by leading industry architects regarding productionizing LLM applications, managing "backward and forward compatibility" is a critical hurdle. When an LLM outputs a structured JSON payload, that structure represents a snapshot in time of your application's Agent-Computer Interface (ACI). 
If tomorrow your business logic requires adding a `confidence_score: float` to all customer profiles, your new `@tool` decorator schema will demand it. But what happens to the 10,000 customer profiles the agent extracted yesterday? If the agent attempts to recall that memory, Pydantic will reject the historical JSON. The agent effectively develops "schema-induced amnesia," permanently severing its access to its own past.

#### 2. ACID Principles in Agentic State Management
The 12 Harness Engineering Lectures mandate that we must evaluate project state management using ACID principles: "Atomicity... Consistency... Isolation... Durability". 
* **Consistency** is the primary victim of schema drift. If your database contains a mix of V1 and V2 traces, your orchestrator cannot rely on a uniform state. 
* To restore consistency, we cannot rely on the LLM to "guess" how to read old data. The Harness (your Python code) must implement an explicit, deterministic translation layer that coerces V1 data into V2 structures *before* it is ever injected back into the LLM's context window.

#### 3. The Amnesiac Engineer and Handoff Integrity
A fundamental principle of agent design states: "treat the agent as a brilliant engineer with amnesia". Before the agent finishes a cycle, it must write its critical information so the next "shift" can pick it up seamlessly. 
If a codebase deployment occurs between "shifts" (changing the schema), the new agent wakes up to a handoff file it mathematically cannot parse. This violates the directive that "Every session must leave a clean state". A clean state means the data must be readable by the *current* runtime, necessitating a Just-In-Time (JIT) migration pipeline.

---

### ASCII Architecture Schema: Just-In-Time (JIT) Schema Migration Harness

The following Directed Acyclic Graph (DAG) illustrates how the orchestrator intercepts legacy data during a Durable Resume operation, dynamically migrating it through Python logic, and optionally triggering a "Cognitive Backfill" if the LLM needs to synthesize new fields.

```ascii
=============================================================================================
 ENTERPRISE SCHEMA MIGRATION & VERSIONING HARNESS
=============================================================================================

[ 1. DURABLE RESUME TRIGGERED ]
Orchestrator requests historical session data from SQLite.
 |
 v
+-----------------------------------------------------------------------------------------+
| 2. DATABASE READ LAYER |
| Retrieves raw JSON: `{"schema_version": "v1", "user_id": 99, "name": "John"}` |
+-----------------------------------------------------------------------------------------+
 |
 v
+-----------------------------------------------------------------------------------------+
| 3. MIGRATION ROUTER (The Interceptor) |
| Checks `schema_version`. Detects discrepancy with active application (V2). |
+-----------------------------------------------------------------------------------------+
 |
 (If purely deterministic mapping is possible)
 v
+---------------------------------------------------+
| 4A. DETERMINISTIC PYTHON MIGRATOR |
| - Maps `user_id` -> `client_identifier`. |
| - Assigns default: `confidence_score = 1.0`. |
| - Upgrades tag: `"schema_version": "v2"`. |
+---------------------------------------------------+
 |
 (If LLM reasoning is required to synthesize missing data)
 v
+---------------------------------------------------+
| 4B. COGNITIVE BACKFILL AGENT (Self-Healing) |
| - Dispatches V1 payload + original source |
| text back to a lightweight LLM. |
| - Prompt: "Extract missing 'confidence_score' |
| from the source text for this record." |
+---------------------------------------------------+
 |
 v
[ 5. PYDANTIC V2 VALIDATION ]
Ensures the migrated payload perfectly matches the current runtime requirements.
 |
 v
[ 6. INJECT CLEAN V2 CONTEXT INTO RE-ACT LOOP ]
Agent resumes work with perfectly consistent memory.
=============================================================================================
```

---

### Detailed Step-by-Step Practical Guide & Production Code

We will engineer a highly resilient `SchemaMigrationManager`. This codebase demonstrates how to load unversioned or legacy JSON, route it through specific upgrade functions, and use Pydantic's `model_validate` to enforce absolute correctness before yielding the data to the agent.

#### Step 1: Defining the Versioned Models
We define both the legacy structure (for reference) and the new current structure. Notice the inclusion of the explicit `schema_version` literal, which acts as our routing flag.

```python
import json
import logging
from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, ValidationError

# "Make the agent runtime observable"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MIGRATION_HARNESS] - %(message)s')

class CustomerRecordV1(BaseModel):
 """Legacy schema representing data extracted during previous application versions."""
 schema_version: Literal["v1"] = "v1"
 name: str = Field(...)
 contact_info: str = Field(..., description="A mixed string of email and/or phone.")

class CustomerRecordV2(BaseModel):
 """
 Current production schema.
 Changes:
 - 'name' split into 'first_name' and 'last_name'.
 - 'contact_info' strictly separated into typed 'email' and 'phone'.
 - Added 'is_active' boolean flag.
 """
 schema_version: Literal["v2"] = "v2"
 first_name: str = Field(...)
 last_name: str = Field(...)
 email: Optional[str] = Field(None)
 phone: Optional[str] = Field(None)
 is_active: bool = Field(default=True)
```

#### Step 2: Architecting the Deterministic Migration Layer
When the SQLite database yields a V1 payload, we must not pass it to Pydantic V2 directly, as it will crash. We intercept it as a raw dictionary and execute deterministic Python transformations.

```python
class SchemaMigrationError(Exception):
 """Raised when data cannot be mathematically upgraded."""
 pass

class MigrationManager:
 """
 Enterprise harness layer for upgrading historical agent memory structures
 into current Pydantic models. Fulfills the ACID Consistency requirement.
 """
 
 @staticmethod
 def _migrate_v1_to_v2(raw_data: Dict[str, Any]) -> Dict[str, Any]:
 """Deterministically transforms V1 dictionary into V2 dictionary."""
 logging.info("Executing deterministic V1 -> V2 migration.")
 
 migrated = {"schema_version": "v2"}
 
 # 1. Handle Name Splitting
 full_name = raw_data.get("name", "Unknown Unknown").strip()
 name_parts = full_name.split(" ", 1)
 migrated["first_name"] = name_parts
 migrated["last_name"] = name_parts if len(name_parts) > 1 else ""
 
 # 2. Handle Contact Info Parsing (Regex Extraction)
 contact = raw_data.get("contact_info", "")
 import re
 
 # Extract email if present
 email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", contact)
 migrated["email"] = email_match.group(0) if email_match else None
 
 # Extract basic phone digits if present
 phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", contact)
 migrated["phone"] = phone_match.group(0) if phone_match else None
 
 # 3. Apply New Defaults
 migrated["is_active"] = True 
 
 return migrated

 @classmethod
 def load_and_upgrade(cls, raw_db_json: str) -> CustomerRecordV2:
 """
 The entrypoint for the durable resume layer. Safely loads raw strings,
 determines their version, routes them through migrators, and validates.
 """
 try:
 data = json.loads(raw_db_json)
 except json.JSONDecodeError:
 raise SchemaMigrationError("Corrupted database payload. Not valid JSON.")

 # Identify the version of the incoming data
 current_version = data.get("schema_version", "v1") # Default to v1 if untagged
 
 if current_version == "v1":
 # Upgrade data through the pipeline
 data = cls._migrate_v1_to_v2(data)
 current_version = "v2"
 
 if current_version == "v2":
 try:
 # Finally, perform strict validation against the current active schema
 validated_record = CustomerRecordV2.model_validate(data)
 logging.info("Schema migration successful. Record passes V2 validation.")
 return validated_record
 except ValidationError as e:
 logging.error(f"Migration produced invalid V2 data: {e.errors()}")
 raise SchemaMigrationError("V2 Validation Failed post-migration.")
 else:
 raise SchemaMigrationError(f"Unknown schema version: {current_version}")
```

#### Step 3: Execution and Context Injection
By utilizing this manager, the ReAct orchestrator is completely shielded from historical breaking changes.

```python
if __name__ == "__main__":
 # Simulating a legacy payload retrieved from our SQLite 'trace_steps' table
 legacy_sqlite_payload = json.dumps({
 "schema_version": "v1",
 "name": "Jane Doe",
 "contact_info": "Reach me at jane.doe@enterprise.com or 555-019-8832."
 })
 
 print("--- RAW LEGACY DB PAYLOAD ---")
 print(legacy_sqlite_payload)
 
 try:
 # The Orchestrator calls the migration manager during 'Durable Resume'
 active_memory_object = MigrationManager.load_and_upgrade(legacy_sqlite_payload)
 
 print("\n--- MIGRATED V2 RUNTIME OBJECT ---")
 print(active_memory_object.model_dump_json(indent=2))
 
 except SchemaMigrationError as e:
 print(f"CRITICAL PIPELINE HALT: {e}")
```

---

### Realistic Business Applications & Unit Economics

Implementing a robust schema migration strategy shifts your AI pipelines from experimental prototypes to durable enterprise assets.

**1. Sustaining Long-Running Research Swarms**
In multi-agent architectures (like Anthropic's research systems, which experience a "~15x token multiplier" compared to single agents ), workflows can run asynchronously for days to generate comprehensive reports. If your backend engineering team deploys a new version of the application on Tuesday that changes the `ResearchFinding` Pydantic schema, the agents running since Monday will crash upon waking up to write their next step. By implementing JIT migration, the agents seamlessly convert Monday's V1 thoughts into Tuesday's V2 structures, preserving thousands of dollars of API compute that would otherwise be discarded.

**2. Seamless Client Handoffs and Runbook Integrity**
As dictated in the curriculum's deployment guidelines, projects require comprehensive documentation and client handoffs: "Runbook: 5 most likely failure types and how to solve them". Schema drift is a primary failure mode when clients inevitably request changes (e.g., "Can the AI also extract the client's LinkedIn URL?"). If you manually update the prompt without a migration script, the client's dashboard will break when loading historical leads. By architecting versioned migrations natively in the Python backend, you fulfill the SLA (Service Level Agreement), ensuring zero downtime and eliminating urgent support tickets regarding corrupted historical views.

---

### Edge-Cases, Common Errors, Rate Limits, and Debugging Loops

Altering the cognitive memory of an autonomous system requires intense architectural discipline to prevent cascading hallucinations.

> [!CAUTION] 
> **Silent Data Loss (The Truncation Trap)** 
> **The Problem:** In V1, the agent extracted a 500-word `executive_summary`. In V2, the business decides they only want a 50-word `brief_overview`. If your migration script simply maps `v2["brief_overview"] = v1["executive_summary"][:50]`, you forcefully truncate the LLM's historical memory. The agent, reading this truncated string in its next ReAct loop, loses the deep context it gathered, leading to degraded decision-making. 
> **Harness Mitigation:** Migrations involving data compression must utilize the **Cognitive Backfill Agent** pattern. Instead of a dumb Python string slice, you pass the 500-word V1 summary back to a fast, cheap model (e.g., Haiku 4.5 ) via an asynchronous background job with the prompt: *"Condense this into a 50-word precise brief."* This ensures semantic integrity is maintained across schema versions.

> [!WARNING] 
> **Validation Doom Loops on Legacy Resumes** 
> **The Error:** An agent resumes a session, pulls a V1 payload, fails the migration, and triggers a Pydantic `ValidationError`. If this error is blindly fed back into the standard Self-Healing JSON Loop (Block 8), the agent will see an error for a JSON structure it generated *three days ago* on a schema it no longer understands. It will attempt to fix the past, looping infinitely and burning tokens. 
> **Diagnostic Loop:** Historical payload loading must occur *outside* the agent's primary ReAct loop. If `load_and_upgrade()` raises an exception, it must trigger a hard system failure (HTTP 500) rather than a prompt retry. You cannot ask an LLM to self-heal a database state corruption; that requires human engineering intervention.

> [!NOTE] 
> **Token Bloat via Backward Compatibility Instructions** 
> Amateur prompt engineers often try to solve schema versioning purely in the prompt: *"Output V2 schema, but if you are reading V1 schema in the history, ignore the missing fields."* This violates the rule to "Enforce invariants, don't micromanage implementation". Stuffing your prompt with complex versioning rules bloats your context window and confuses the model. Keep the prompt perfectly clean and focused *only* on V2. Let your Python Migration Manager handle the dirty work of upgrading the past.

By mastering schema versioning and deterministic data migrations, you have achieved true durability. You have constructed a cognitive architecture capable of evolving alongside your business requirements, ensuring that your agents remain consistent, observable, and reliably functional across their entire operational lifecycle. 

Are you ready to finalize this module and move into Phase 4, where we will build the rigorous automated evaluation gates (Evals) needed to measure these resilient systems?
