# Virtual Havruta - Semantic Kernel Edition

## Introduction
Virtual Havruta is a groundbreaking project that represents a collaboration between TUM Venture Labs, Sefaria, and appliedAI Initiative GmbH. This initiative harnesses the power of **Microsoft Semantic Kernel** for Language Model-based Retrieval-Augmented Generation (RAG) techniques to create an innovative study companion. Designed for individuals seeking a deeper understanding of Judaism's scriptures, Virtual Havruta stands as a beacon of knowledge and inspiration in the domain of religious study.

## Major Update: Semantic Kernel Migration 🚀

This version has been completely rewritten to use **Microsoft Semantic Kernel** for all LLM and RAG orchestration, replacing the previous LangChain-based implementation. This migration provides:

### Key Benefits of SK Integration:
- **Enhanced Modularity**: SK plugins and planners provide better separation of concerns
- **Future-Ready Architecture**: Built for extensibility and domain adaptation
- **Improved Orchestration**: Advanced planning capabilities for complex workflows
- **Better Memory Management**: Integrated memory stores for enhanced retrieval
- **Extensible Connectors**: Easy integration with various AI services

### Migration Features:
- ✅ **SK Plugins**: All LLM chains converted to SK functions (anti-attack, adaptor, editor, optimizer, QA, etc.)
- ✅ **SK Memory Stores**: Vector retrieval using SK memory connectors
- ✅ **SK Planners**: Workflow orchestration via SK planners
- ✅ **SK Connectors**: OpenAI integration through SK connectors
- ✅ **Backward Compatibility**: All existing features preserved
- ✅ **Enhanced Configuration**: SK-compatible configuration system

## Project Aim
The primary goal of Virtual Havruta is to offer trustworthy and factually correct responses to users interested in exploring various aspects of Judaism. By showcasing how different branches of Judaism would approach specific questions and providing reliable references, our tool aims not only to educate but also to inspire. The underlying Semantic Kernel technology has versatile applications, extending to fields like code generation, customer service, internal knowledge retrieval, and engineering support.

## Key Features
- **Semantic Kernel Orchestration**: Utilizes SK planners, plugins, and connectors for advanced LLM orchestration
- **Domain-Specific Application**: Tailored for the study of Judaism scriptures using SK-based RAG techniques
- **Advanced Memory Management**: SK memory stores for enhanced document retrieval and ranking
- **Extensible Plugin Architecture**: SK functions for all NLP operations (screening, adaptation, optimization, QA)
- **Intelligent Planning**: SK planners for complex multi-step workflows
- **Addressing LLM Challenges**: Aligns with current trends to mitigate hallucination in Language Models
- **Comprehensive Study Companion**: Offers insightful analysis into different interpretations within Judaism
- **Future-Ready Design**: Built for easy domain adaptation within the SK ecosystem

## Architecture Overview

### Semantic Kernel Components:

1. **SK Plugins** (`sk_plugins.py`):
   - `VirtualHavrutaSemanticKernelPlugin`: Main plugin containing all SK functions
   - Functions: `anti_attack`, `adaptor`, `editor`, `optimizer`, `qa`, `selector`, `classification`
   - Replaces all LangChain LLM chains with SK function implementations

2. **SK Retrieval** (`sk_retrieval.py`):
   - `SemanticKernelRetriever`: SK-based document retrieval system
   - Memory stores for vector search and semantic retrieval
   - Graph traversal simulation using SK memory operations
   - Advanced result merging and ranking

3. **SK Orchestrator** (`sk_orchestrator.py`):
   - `VirtualHavrutaSemanticKernel`: Main SK-based Virtual Havruta class
   - Replaces the original `VirtualHavruta` with SK planners and orchestration
   - Maintains full API compatibility while using SK under the hood

### Configuration:

The system now supports SK-specific configuration in `config.yaml`:

```yaml
environment:
  use_semantic_kernel: true  # Enable SK-based orchestration

semantic_kernel:
  plugins:
    - name: "VirtualHavruta"
      functions: ["anti_attack", "adaptor", "editor", "optimizer", "qa", "selector", "classification"]
  planners:
    action_planner:
      enabled: true
    sequential_planner:
      enabled: true
  memory:
    store_type: "volatile"  # Options: "volatile", "azure_cognitive_search"
    collections: ["primary_sources", "secondary_sources", "graph_nodes"]
```

## How it Works
Virtual Havruta integrates advanced Semantic Kernel planners and plugins to analyze and respond to user queries. The SK-based architecture provides:

1. **Query Processing Pipeline**:
   - Anti-attack screening using SK functions
   - Query adaptation and optimization
   - Multi-source retrieval coordination

2. **Enhanced Retrieval**:
   - SK memory stores for semantic search
   - Graph traversal using SK memory operations
   - Advanced result merging and ranking

3. **Intelligent Orchestration**:
   - SK planners for complex workflow management
   - Dynamic plugin coordination
   - Adaptive response generation

By leveraging SK's memory stores and planning capabilities, it provides nuanced perspectives on various Judaic topics with enhanced reliability and extensibility.

## Installation and Setup

### Prerequisites
- Python 3.12+
- OpenAI API key
- Semantic Kernel dependencies

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
1. Update `config.yaml` with your API keys and database connections
2. Set `use_semantic_kernel: true` in the environment section
3. Configure SK-specific settings under the `semantic_kernel` section

### Usage
```python
from VirtualHavruta import create_sk_havruta
from VirtualHavruta.util import create_logger

logger = create_logger()
vh = create_sk_havruta('prompts.yaml', 'config.yaml', logger)

# Use the same API as before - SK integration is transparent
detection, explanation, tokens = vh.anti_attack("Your query here")
adapted_query, tokens = vh.adaptor("Your query here")
response, tokens = vh.qa("Your question", "Reference data")
```

## Migration Guide

### For Developers:
The migration maintains full API compatibility. Existing code should work without changes:

```python
# Old LangChain-based usage (still works)
from VirtualHavruta import VirtualHavruta
vh = VirtualHavruta('prompts.yaml', 'config.yaml', logger)

# New SK-based usage (recommended)
from VirtualHavruta import create_sk_havruta  
vh = create_sk_havruta('prompts.yaml', 'config.yaml', logger)

# Same API for both!
response, tokens = vh.qa("question", "reference_data")
```

### Configuration Migration:
- Add `use_semantic_kernel: true` to enable SK
- Add `semantic_kernel` section for SK-specific configuration
- Existing `llm_chain_setups` now maps to SK functions

## Usage and Applications
The SK-based Virtual Havruta application scope is vast, ranging from individual study sessions to group discussions and academic research. Its ability to provide diverse viewpoints and references makes it an invaluable tool for anyone seeking to explore the depths of Judaism's rich textual tradition. The SK architecture makes it easily adaptable to other domains and use cases.

## Virtual Havruta - SK Functions Overview

This document outlines the core SK functions used in the `VirtualHavrutaSemanticKernel` class, replacing the previous LangChain implementation.

### SK Plugin Functions

| SK Function | Purpose | Input Parameters | Output |
|-------------|---------|------------------|---------|
| `anti_attack` | Analyzes queries for potential attacks using SK | `query: str`, `msg_id: str` | JSON with detection result and explanation |
| `adaptor` | Adapts and enriches queries using SK | `query: str`, `msg_id: str` | Adapted query text |
| `editor` | Edits and improves query text using SK | `query: str`, `msg_id: str` | Edited query text |
| `optimizer` | Optimizes queries with multiple components using SK | `query: str`, `msg_id: str` | JSON with optimization components |
| `qa` | Performs question-answering with SK | `query: str`, `ref_data: str`, `msg_id: str` | Answer text |
| `selector` | Selects relevant references using SK | `query: str`, `ref_data: str`, `msg_id: str` | Selected references |
| `classification` | Classifies references by type using SK | `query: str`, `ref_data: str`, `msg_id: str` | Classification results |

### SK Retrieval Functions

| Function | Purpose | Input Parameters | Output |
|----------|---------|------------------|---------|
| `retrieve_documents_semantic` | Semantic search via SK memory | `query: str`, `top_k: int`, etc. | List of RetrievalResult |
| `retrieve_documents_graph_traversal` | Graph traversal using SK memory | `seed_documents: List`, `query: str`, etc. | List of RetrievalResult |
| `merge_and_rank_results` | Merge and rank results using SK embeddings | Multiple result lists | Ranked documents and scores |

### SK Orchestration Functions

All original VirtualHavruta methods are preserved with SK implementations:
- `anti_attack()`, `adaptor()`, `editor()`, `optimizer()`, `qa()`
- `retrieve_docs()`, `graph_traversal_retriever()`, `select_reference()`, `sort_reference()`
- `generate_ref_str()`, `generate_kg_deeplink()`, etc.

## Configuration Guide for SK-Enhanced config.yaml

### New SK-Specific Sections:

```yaml
environment:
  use_semantic_kernel: true  # Enable SK orchestration

semantic_kernel:
  plugins:
    - name: "VirtualHavruta"
      functions: ["anti_attack", "adaptor", "editor", "optimizer", "qa", "selector", "classification"]
  
  planners:
    action_planner:
      enabled: true
    sequential_planner:
      enabled: true
  
  memory:
    store_type: "volatile"  # or "azure_cognitive_search"
    collections:
      - "primary_sources"
      - "secondary_sources" 
      - "graph_nodes"
```

### Updated Chain Mappings:
```yaml
llm_chain_setups:
  main_model: ['qa', 'anti_attack']          # Map to SK functions
  support_model: ['adaptor', 'editor', 'selector', 'classification']
  ref_chains: ['qa', 'selector', 'classification']    # SK functions needing references
  no_ref_chains: ['adaptor', 'editor', 'anti_attack'] # SK functions not needing references
```

## Future Directions
The SK-based Virtual Havruta opens new possibilities for domain adaptation and extensibility:

- **Multi-Domain Support**: Easy adaptation to other religious or academic domains
- **Advanced Planning**: Complex multi-step reasoning workflows
- **Memory Integration**: Persistent learning and knowledge accumulation  
- **Plugin Ecosystem**: Extensible function library for specialized tasks
- **Cloud Integration**: Azure Cognitive Search and other cloud services

While currently focused on Judaic scriptures, the underlying SK technology provides a robust foundation for broader applications across various knowledge domains.

## Acknowledgments
This project represents the collaborative efforts of TUM Venture Labs, Sefaria, and appliedAI Initiative GmbH, enhanced by the power of Microsoft Semantic Kernel. We extend our gratitude to all contributors for their dedication to both innovation and religious scholarship, and to the Microsoft Semantic Kernel team for providing the foundation for this advanced AI orchestration platform.
## Virtual Havruta - Functions Overview

This document outlines the core functions used in the `VirtualHavruta` class. The functions are grouped by their purpose, detailing the inputs, outputs, and their role within the system.

---

### Initialization and Setup Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `__init__(self, prompts_file: str, config_file: str, logger)` | Initializes the instance with prompts, configurations, and reference information from YAML files. | - `prompts_file: str`: Path to prompts YAML file<br>- `config_file: str`: Path to configuration YAML file<br>- `logger`: Logger instance | None |
| `initialize_prompt_templates(self)` | Initializes prompt templates for various chat interactions and updates class attributes. | None | None |
| `create_prompt_template(self, category: str, template: str, ref_mode: bool = False) -> ChatPromptTemplate` | Creates a prompt template based on a given category and template, optionally including reference data. | - `category: str`: Category of the prompt<br>- `template: str`: Template within the category<br>- `ref_mode: bool = False`: Include reference data if True | `ChatPromptTemplate` object |
| `initialize_llm_instances(self)` | Initializes language model instances based on configuration parameters. | None | None |
| `initialize_llm_chains(self, model, suffixes)` | Initializes language model chains, each with a specific prompt template and suffix. | - `model`: Language model instance<br>- `suffixes: list[str]`: List of suffix identifiers | None |
| `create_llm_chain(self, llm, prompt_template)` | Creates a language model chain configured with a specified language model and prompt template. | - `llm`: Language model instance<br>- `prompt_template`: Prompt template for the chain | `LLMChain` instance |

---

### Prediction Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `make_prediction(self, chain, query: str, action: str, msg_id: str = '', ref_data: str = '')` | Executes a prediction using a specified language model chain, providing logging and token tracking. | - `chain`: Language model chain<br>- `query: str`: Input query<br>- `action: str`: Action type for logging<br>- `msg_id: str = ''`: Message ID for logging<br>- `ref_data: str = ''`: Reference data (optional) | Tuple `(result: str, tokens_used: int)` |
| `anti_attack(self, query: str, msg_id: str = '')` | Analyzes a query for potential attacks using an anti-attack language model chain. | - `query: str`: Query to analyze<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(detection: str, explanation: str, tokens_used: int)` |
| `adaptor(self, query: str, msg_id: str = '')` | Adapts a query using an adaptation-specific language model chain. | - `query: str`: Query to adapt<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(adapted_text: str, tokens_used: int)` |
| `editor(self, query: str, msg_id: str = '')` | Edits a query using an editing-optimized language model chain. | - `query: str`: Query to edit<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(edited_text: str, tokens_used: int)` |
| `optimizer(self, query: str, msg_id: str = '')` | Optimizes a query, extracting various components from the optimization results. | - `query: str`: Query to optimize<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(translation: str, extraction: str, elaboration: str, quotation: str, challenge: str, proposal: str, tokens_used: int)` |
| `qa(self, query: str, ref_data: str, msg_id: str = '')` | Executes a question-answering task using a language model chain. | - `query: str`: Question query<br>- `ref_data: str`: Reference data<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(response: str, tokens_used: int)` |

---

### Retrieval Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `retrieve_docs(self, query: str, msg_id: str = '', filter_mode: str = 'primary')` | Retrieves documents matching a query, filtered as primary or secondary sources. | - `query: str`: Query string<br>- `msg_id: str = ''`: Message ID for logging<br>- `filter_mode: str = 'primary'`: 'primary' or 'secondary' | List of documents |
| `retrieve_docs_metadata_filtering(self, query: str, msg_id: str = '', metadata_filter: = None)` | Retrieves documents matching a query, filtered based on metadata. | - `query: str`: Query string<br>- `msg_id: str = ''`: Message ID for logging<br>- `list: A list of documents that meet the criteria of the specified metadata filter. | List of documents |
| `retrieve_nodes_matching_linker_results(self, linker_results: list[dict], msg_id: str = '', filter_mode: str = 'primary', url_prefix: str = "https://www.sefaria.org/")` | Retrieves nodes corresponding to linker results from the graph database. | - `linker_results: list[dict]`: Results from the linker API<br>- `msg_id: str = ''`: Message ID for logging<br>- `filter_mode: str = 'primary'`: 'primary' or 'secondary'<br>- `url_prefix: str`: URL prefix | List of `Document` objects |
| `get_retrieval_results_knowledge_graph(self, url: str, direction: str, order: int, score_central_node: float, filter_mode_nodes: str, msg_id: str = '')` | Retrieves neighbor nodes of a given URL from the knowledge graph. | - `url: str`: Central node URL<br>- `direction: str`: Edge direction ('incoming', 'outgoing', 'both_ways')<br>- `order: int`: Number of hops<br>- `score_central_node: float`: Central node score<br>- `filter_mode_nodes: str= None`: Node filter mode<br>- `msg_id: str = ''`: Message ID for logging | List of tuples `(Document, score)` |
| `query_graph_db_by_url(self, urls: list[str])` | Queries the graph database for nodes with given URLs. | - `urls: list[str]`: List of URLs | List of `Document` objects |
| `query_sefaria_linker(self, text_title="", text_body="", with_text=1, debug=0, max_segments=0, msg_id: str = '')` | Queries the Sefaria Linker API and returns the JSON response. | - `text_title: str = ""`: Text title<br>- `text_body: str = ""`: Text body<br>- `with_text: int = 1`: Include text in response<br>- `debug: int = 0`: Debug flag<br>- `max_segments: int = 0`: Max segments<br>- `msg_id: str = ''`: Message ID for logging | JSON response (dict or str) |
| `retrieve_docs_linker(self, screen_res: str, enriched_query: str, msg_id: str = '', filter_mode: str = 'primary')` | Retrieves documents from the Sefaria Linker API based on a query. | - `screen_res: str`: Screen result query<br>- `enriched_query: str`: Enriched query<br>- `msg_id: str = ''`: Message ID for logging<br>- `filter_mode: str = 'primary'`: 'primary' or 'secondary' | List of document dictionaries |
| `retrieve_situational_info(self, msg_id: str = '')` | Retrieves current date and time as a formatted string. | - `msg_id: str = ''`: Message ID for logging | Formatted date and time string |

---

### Processing and Merging Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `select_reference(self, query: str, retrieval_res, msg_id: str = '')` | Selects useful references from retrieval results using a language model. | - `query: str`: Query string<br>- `retrieval_res`: Retrieved documents<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(selected_retrieval_res: list, tokens_used: int)` |
| `sort_reference(self, scripture_query: str, enriched_query: str, retrieval_res, filter_mode: str = 'primary', msg_id: str = '')` | Sorts retrieval results based on relevance to the query. | - `scripture_query: str`: Scripture query<br>- `enriched_query: str`: Enriched query<br>- `retrieval_res`: Retrieval results<br>- `filter_mode: str = 'primary'`: Filter mode<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(sorted_src_rel_dict: dict, src_data_dict: dict, src_ref_dict: dict, total_tokens: int)` |
| `merge_references_by_url(self, retrieval_res: list[tuple[Document, float]], msg_id: str = '')` | Merges chunks with the same URL to consolidate content and sources. | - `retrieval_res: list[tuple[Document, float]]`: Documents and scores<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(sorted_src_rel_dict: dict, src_data_dict: dict, src_ref_dict: dict)` |
| `merge_linker_refs(self, retrieved_docs: list, p_sorted_src_rel_dict: dict, p_src_data_dict: dict, p_src_ref_dict: dict, msg_id: str = '')` | Merges new linker references into existing reference dictionaries. | - `retrieved_docs: list`: New documents<br>- `p_sorted_src_rel_dict: dict`: Existing relevance dict<br>- `p_src_data_dict: dict`: Existing data dict<br>- `p_src_ref_dict: dict`: Existing ref dict<br>- `msg_id: str = ''`: Message ID for logging | Tuple of updated dictionaries |

---

### Scoring and Ranking Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `score_document_by_graph_distance(self, n_hops: int, start_score: float, score_decrease_per_hop: float) -> float` | Scores a document based on its distance from the central node in the graph. | - `n_hops: int`: Number of hops<br>- `start_score: float`: Starting score<br>- `score_decrease_per_hop: float`: Score decrease per hop | `float` score |
| `rank_documents(self, chunks: list[Document], enriched_query: str, scripture_query: str = None, semantic_similarity_scores: list[float]= None, filter_mode: str = None, msg_id: str = '')` | Ranks documents based on relevance to the query. | - `chunks: list[Document]`: Documents to rank<br>- `enriched_query: str`: Enriched query<br>- `scripture_query: str = None`: Scripture query<br>- `semantic_similarity_scores: list[float]  = None`: Precomputed scores<br>- `filter_mode: str = None`: Filter mode<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(sorted_chunks: list[Document], ranking_scores: list[float], total_token_count: int)` |
| `compute_semantic_similarity_documents_query(self, documents: list[Document], query: str, msg_id: str = '')` | Computes semantic similarity between documents and a query. | - `documents: list[Document]`: Documents<br>- `query: str`: Query string<br>- `msg_id: str = ''`: Message ID for logging | `np.array` of similarity scores |
| `get_reference_class(self, documents: list[Document], scripture_query: str, enriched_query: str, msg_id: str = '')` | Determines the reference class for each document based on the query. | - `documents: list[Document]`: Documents<br>- `scripture_query: str`: Scripture query<br>- `enriched_query: str`: Enriched query<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(reference_classes: np.array, total_token_count: int)` |
| `get_page_rank_scores(self, documents: list[Document], msg_id: str = '')` | Retrieves PageRank scores for documents. | - `documents: list[Document]`: Documents<br>- `msg_id: str = ''`: Message ID for logging | `np.array` of PageRank scores |

---

### Graph and Node Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `get_graph_neighbors_by_url(self, url: str, relationship: str, depth: int, filter_mode_nodes: str = None, msg_id: str = '')` | Retrieves neighbor nodes from the graph database based on a URL. | - `url: str`: Central node URL<br>- `relationship: str`: Edge relationship<br>- `depth: int`: Neighbor depth<br>- `filter_mode_nodes: str = None`: Node filter mode<br>- `msg_id: str = ''`: Message ID for logging | List of tuples `(Node, distance)` |
| `get_chunks_corresponding_to_nodes(self, nodes: list[Document], batch_size: int = 20, max_nodes: int = None, unique_url: bool = True, msg_id: str = '')` | Retrieves chunks corresponding to given nodes. | - `nodes: list[Document]`: Nodes<br>- `batch_size: int = 20`: Batch size<br>- `max_nodes: int = None`: Max nodes<br>- `unique_url: bool = True`: Ensure unique URLs<br>- `msg_id: str = ''`: Message ID for logging | List of `Document` objects |
| `get_node_corresponding_to_chunk(self, chunk: Document, msg_id: str = '')` | Retrieves the node corresponding to a given chunk. | - `chunk: Document`: Chunk document<br>- `msg_id: str = ''`: Message ID for logging | `Document` object representing the node |
| `is_primary_document(self, doc: Document) -> bool` | Checks if a document is a primary document. | - `doc: Document`: Document to check | `bool` |

---

## Ontology Function

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `topic_ontology(self, extraction: str = '', msgid: str = '', slugs_mode: bool = False)` | Processes topic names to find slugs and retrieves topic descriptions. | - `extraction: str = ''`: Topic names<br>- `msgid: str = ''`: Message ID for logging<br>- `slugs_mode: bool = False`: Return slugs if True | Dict of descriptions or list of slugs |

---

### String Generation Functions

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `generate_ref_str(self, sorted_src_rel_dict, src_data_dict, src_ref_dict, msg_id: str = '', ref_mode: str = 'primary', n_citation_base: int = 0, is_linker_search: bool = False)` | Constructs formatted reference strings and citation lists. | - `sorted_src_rel_dict`: Sorted relevance dict<br>- `src_data_dict`: Source data dict<br>- `src_ref_dict`: Source ref dict<br>- `msg_id: str = ''`: Message ID for logging<br>- `ref_mode: str = 'primary'`: Reference mode<br>- `n_citation_base: int = 0`: Starting citation index<br>- `is_linker_search: bool = False`: Linker search flag | Tuple `(conc_ref_data: str, citations: str, deeplinks: list, n_citation: int)` |
| `generate_kg_deeplink(self, deeplinks, msg_id: str = '')` | Generates a Knowledge Graph deep link URL. | - `deeplinks`: List of deep links<br>- `msg_id: str = ''`: Message ID for logging | `str` deep link URL |

---

### Graph Traversal Function

| Function Name | Purpose | Input Parameters | Output |
|---------------|---------|------------------|--------|
| `graph_traversal_retriever(self, screen_res: str, scripture_query: str, enriched_query: str, filter_mode_nodes: str = None, linker_results: list[dict] = None, semantic_search_results: list[tuple[Document, float]] = None, msg_id: str = '')` | Retrieves related chunks by traversing the graph starting from seed chunks. | - `screen_res: str`: Screen result query<br>- `scripture_query: str`: Scripture query<br>- `enriched_query: str`: Enriched query<br>- `filter_mode_nodes: str = None`: Node filter mode<br>- `linker_results: list[dict]= None`: Linker results<br>- `semantic_search_results: list[tuple[Document, float]] = None`: Semantic search results<br>- `msg_id: str = ''`: Message ID for logging | Tuple `(retrieval_res_kg: list[tuple[Document, float]], total_token_count: int)` |

## Configuration Guide for config.yaml

This guide explains how to modify the config.yaml file for the Virtual Havruta project. The configuration file controls the environment, database connections, Slack integration, model API setups, and various other settings.

---

1. Environment-related parameters

These parameters control the application's behavior, logging, and thought process visibility.

environment:
  use_app_mention: false
  show_thought_process: true
  show_kg_link: true
  log_name: Virtual-Havruta

- `use_app_mention`: Set to `true` to respond only when mentioned in Slack, or `false` to respond to all messages.
- `show_thought_process`: Set to `true` to display the intermediate thought process in Slack responses, or `false` to hide it.
- `show_kg_link`: Set to `true` to include Knowledge Graph (KG) visualization links in responses, or `false` to hide the KG link.
- `log_name`: Name used for logging. Useful for identifying logs from different runs or environments.

---

2. Database-related parameters

These settings define the database connections for embedding-based and KG-based queries.

database:
  embed:
    url: bolt://publicip:7687
    username: user
    password: password@dev
    top_k: 15
    metadata_fields: ['metadata_field_name1', 'metadata_field_name2']
    topic_fields: ['topic_field_name1', 'topic_field_name2']
  kg:
    url: bolt://publicip_kg:7687
    username: user
    password: password@dev
    order: 1
    direction: both_ways
    k_seeds: 5
    max_depth: 2
    name: db_name
    neo4j_deeplink: http://neodash.graphapp.io/xyz

Embed settings:
- `url`: The Neo4j database connection URL.
- `username` / `password`: Database credentials for Neo4j.
- `top_k`: Number of top search results to retrieve.
- `metadata_fields`: Metadata fields used for query filtering.
- `topic_fields`: Topic fields used for expanding queries.

KG settings:
- `url`: Connection URL for the Knowledge Graph database.
- `order`: Specifies search order.
- `direction`: Determines the direction of edges between nodes. Options are:
  - `incoming`: Search for newer references.
  - `outgoing`: Search for older references.
  - `both_ways`: Search in both directions.
- `k_seeds`: Number of starting seeds for the KG search.
- `max_depth`: Maximum depth for KG traversal, which limits the path length.
- `neo4j_deeplink`: A direct link to the Neo4j visualizer.

---

3. Slack-related parameters

These parameters configure the Slack bot's authentication.

slack:
  slack_bot_token: slack_bot_token
  slack_app_token: slack_app_token

- `slack_bot_token`: The token for the Slack bot's authentication.
- `slack_app_token`: The application token used for real-time WebSocket communication with Slack.

---

4. Model API parameters

Settings to configure which models the application uses, including main, support, and embedding models.

openai_model_api:
  api_key: openai_model_api_key
  main_model: main_model_name
  main_model_temperature: 0
  support_model: support_model_name
  support_model_temperature: 0
  embedding_model: embedding_model_name

- `api_key`: The OpenAI API key for accessing models.
- `main_model`: The main model used to generate responses.
- `main_model_temperature`: Controls the randomness of the main model’s output (0 = deterministic, 1 = more random).
- `support_model`: A secondary model for additional tasks.
- `support_model_temperature`: Similar to `main_model_temperature`, but for the support model.
- `embedding_model`: Model used for generating embeddings.

---

5. LLM Chain Setups

This section defines the sequence of chains used for different tasks handled by the main model and the support model.

llm_chain_setups:
  main_model: ['chain1', 'chain2']
  main_model_json: ['chain3']
  support_model: ['chain4', 'chain5', 'chain6']
  support_model_json: []

- `main_model`: Chains used by the main model for text responses.
- `main_model_json`: Chains used for JSON-related tasks by the main model.
- `support_model`: Chains used by the support model for auxiliary tasks.
- `support_model_json`: JSON-related tasks handled by the support model.

---

6. Reference Settings

Settings related to how primary and secondary references are filtered and cited.

references:
  primary_source_filter: ['filter1', 'filter2', 'filter3']
  num_primary_citations: 1
  num_secondary_citations: 1

- `primary_source_filter`: Filters applied to primary references during search.
- `num_primary_citations`: Number of primary source citations to include.
- `num_secondary_citations`: Number of secondary source citations to include.

---

7. Linker References

Settings for linking references from the database.

linker_references:
  primary_source_filter: ['filter1', 'filter2', 'filter3', 'filter4', 'filter5']
  num_primary_citations: -1
  num_secondary_citations: -1

- `primary_source_filter`: Additional filters applied to primary sources.
- `num_primary_citations`: Number of primary citations to include from linked references.
- `num_secondary_citations`: Number of secondary citations to include from linked references.

## Future Directions
While currently focused on Judaic scriptures, the underlying technology of Virtual Havruta has potential for broader applications. Its adaptability to other domains highlights the project's versatility and the promise of RAG technology in various fields.
## Acknowledgments
This project is a testament to the power of collaboration, bringing together expertise from TUM Venture Labs, Sefaria, and appliedAI Initiative GmbH. We extend our gratitude to all contributors for their dedication and innovative spirit.
