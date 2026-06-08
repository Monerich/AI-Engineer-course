# Презентация: Vector Databases and RAG in Automations

📊 Slide 1. Semantic Search
**Visual Layout Concept:** Dark mode (HSL: 220, 15%, 15%). Use the `Network` and `Brain` Lucide icons. Include a 3D scatter plot graphic representing vector space.
* Text embeddings act as a universal encoding, compressing text of arbitrary length into a fixed-size mathematical vector.
* Similar semantic concepts (like "dog" and "wolf") are grouped close to each other in this multi-dimensional space, while unrelated concepts are farther apart.
* When a user queries the database, the system calculates the cosine similarity (the distance between vectors) to fetch semantically relevant answers even if exact keywords are missing.

---

📊 Slide 2. Deploying Vector DBs
**Visual Layout Concept:** Light mode (HSL: 210, 20%, 98%). Use the `Database` and `Server` Lucide icons. Display a split schema of a NoSQL vector index vs. a relational Postgres table.
* Dedicated vector databases like Pinecone and Qdrant allow you to create serverless indexes with specific dimensions, such as 1536 for OpenAI's `text-embedding-3-small`.
* Alternatively, Supabase uses Postgres with the `pgvector` extension, allowing you to store documents, metadata, and high-dimensional vectors within standard relational tables.
* Namespaces (in Pinecone) or specific tables (in Supabase) must be configured to compartmentalize different types of enterprise data.

---

📊 Slide 3. Vector Pipelines in n8n
**Visual Layout Concept:** Dark mode (HSL: 200, 50%, 15%). Use the `FileText`, `Scissors`, and `ArrowRight` Lucide icons. Show a visual flow of a document being sliced into chunks.
* Data ingestion requires a pipeline that extracts binary data (e.g., from Google Drive) and normalizes it.
* A Recursive Character Text Splitter breaks large documents into smaller, digestible chunks (e.g., 500 characters with a 20-character overlap) to maintain semantic context.
* These chunks are then processed by an embeddings model and upserted into the vector database alongside metadata for future filtering.

---

📊 Slide 4. Retriever in n8n
**Visual Layout Concept:** Light mode (HSL: 0, 0%, 100%). Use the `Search` and `DatabaseZap` Lucide icons. Show the n8n Vector Store tool connecting to an agent node.
* To search the knowledge base, the user's query is vectorized using the exact same embedding model used during the ingestion phase.
* The n8n Vector Store node acts as a retriever, performing an approximate nearest neighbor search to pull the most relevant chunks.
* Engineers can configure relevance thresholds (e.g., setting a score > 0.4) to drop low-quality matches and prevent garbage data from entering the LLM's context.

---

📊 Slide 5. Practice: Product Knowledge Base
**Visual Layout Concept:** Split screen. Left: User email. Right: AI Agent fetching from Pinecone. Use the `MessageSquare` and `ShieldCheck` Lucide icons.
* Retrieval-Augmented Generation (RAG) grounds the LLM in factual, private data, drastically reducing hallucinations.
* By equipping an AI agent with a Vector Store tool pointed at an "FAQ" namespace, the agent autonomously searches company policies to answer customer emails.
* Strict system instructions are critical here: "You must only answer using relevant knowledge provided to you; don't make anything up".

---

📊 Slide 6. Cohere Rerank
**Visual Layout Concept:** Dark mode (HSL: 220, 10%, 10%). Use the `ListOrdered` and `TrendingUp` Lucide icons. Visualize a list of documents being re-sorted based on precision.
* Standard vector searches are incredibly fast but approximate, which means they often return dozens of results that are semantically close but contextually irrelevant.
* A Reranker acts as a sophisticated secondary scoring system.
* It takes the initial Top-K results and cross-evaluates them against the user's specific query, re-ranking them to ensure the absolute best answers are pushed to the top of the context window.

---

📊 Slide 7. Generating Embeddings Programmatically
**Visual Layout Concept:** Code editor aesthetic (Dark theme, syntax highlighting). Use the `Terminal` and `Cpu` Lucide icons.
* Visual low-code tools can hit memory limits when processing tens of thousands of corporate documents; programmatic Python scripts handle scale.
* Using the `openai.embeddings` API requires writing explicit logic for text sanitization, chunking, and batch processing.
* Production-grade scripts must include `try/except` loops and exponential backoff to handle API rate limits (HTTP 429) seamlessly during massive ingestion runs.

---

📊 Slide 8. RAG Evals
**Visual Layout Concept:** Light mode (HSL: 210, 20%, 98%). Use the `BarChart` and `Target` Lucide icons. Display a dashboard with precision and recall metrics.
* You cannot optimize a RAG system without evaluating it. Evals measure the exact performance and accuracy of your retrieval and generation layers.
* Metrics focus on two core areas: did the retriever fetch the right chunks, and did the model generate a factually accurate answer without hallucinating?
* Using platforms like LangSmith allows you to run automated LLM-as-a-judge evaluators over a golden dataset to catch regressions before deploying to production.

---

📊 Slide 9. Overcoming 'Lost in the Middle'
**Visual Layout Concept:** Dark mode (HSL: 0, 0%, 15%). Use the `Minimize2` and `AlertTriangle` Lucide icons. Show a massive block of text compressing into a high-signal summary.
* Feeding an LLM too many raw retrieved chunks triggers the "Lost in the Middle" phenomenon, causing it to ignore facts buried in the center of the prompt.
* Passing 20,000 tokens of raw RAG output causes "Instruction Bloat", where the model loses track of its core objective.
* The solution is Context Compression: deploying sub-agents to read isolated batches of chunks, extracting only the relevant facts, and passing a highly compressed summary to the final orchestrator.

---

📊 Slide 10. Designing Hybrid Search
**Visual Layout Concept:** Light mode (HSL: 0, 0%, 100%). Use the `Layers` and `SearchCheck` Lucide icons. Visual: Parallel arrows for semantic and lexical search merging into one context.
* Dense vector embeddings excel at understanding semantic intent but fail at finding exact keyword matches, such as specific error codes or UUIDs.
* Sparse retrieval (like BM25) uses term frequency to find exact lexical matches without semantic understanding.
* Hybrid search executes both retrieval methods in parallel, fusing the results using Reciprocal Rank Fusion (RRF) to provide the agent with both semantic richness and exact precision.

Are you ready to dive into the technical implementation of Week 8, or would you like to explore any of these RAG concepts further?