# Azure AI Search

## Introduction

Azure AI Search is a cloud-based search service that lets you build powerful search and discovery features into your apps or websites — but with AI capabilities built in.
It’s like giving your data Google-like search — where users can search text, phrases, or even questions — and get relevant, ranked, and AI-enriched results.


## Architecture

Azure AI Search follows a pipeline architecture made up of four main stages:

A. Data Ingestion 
    You connect your data source to Azure AI Search.
    Supported data sources:
        - Azure Blob Storage (PDFs, JSON, text, Office docs)
        - Azure SQL Database
        - Azure Cosmos DB
        - SharePoint Online
        - Custom data (via API push)
    You can either:
        - Push data manually using the Search SDK/API, or
        - Pull data automatically using indexers (scheduled crawlers).
B. Data Enrichment (Optional AI Step)
    Before indexing, you can apply Cognitive Skills or AI enrichments, such as:
    - OCR (extract text from images/PDFs)
    - Entity recognition (e.g., company names, dates)
    - Key phrase extraction
    - Language detection
    - Custom ML models
    - Vector embedding generation (for semantic/vector search)

    💡 If you enable vector search, embeddings (numerical representations of text meaning) are generated for each record or document chunk.
C. Indexing
    Azure creates an inverted index, similar to how a search engine works:
    - Each document becomes a record.
    - Each word or token is mapped to its document and position.
    - Fields can be searchable, filterable, sortable, or facetable.

    For vector search, embeddings are stored in a vector index, enabling nearest-neighbor search (ANN) using techniques like HNSW (Hierarchical Navigable Small World graphs).
D. Querying
    When a user performs a search:
        1. The query hits your search index endpoint.
        2. The engine parses it and finds matches:
            - Text search: term-based, fuzzy matching, relevance ranking.
            - Vector search: semantic similarity search (find “conceptually similar” results).
            - Hybrid: combines keyword + vector + semantic ranking.
        3. The top results are ranked by relevance score and returned as JSON.

You can also combine with Azure OpenAI for:
- Natural language questions.
- RAG (Retrieval-Augmented Generation): where GPT uses Azure AI Search results as context.


Overall:

```pgsql

Azure Blob Storage  →  AI Enrichment Skillset  →  AI Search Index  →  Query API
       ↑                                                   ↓
   PDFs, Docs, JSON                              Web App / Chatbot / Dashboard

```


## Indexing in Azure AI Search
In Azure AI Search, indexing is the process of preparing your data so that it can be searched efficiently.
It’s similar to how a search engine like Google works — it creates a structured representation (an index) of your content.

How it works
- You define an index schema — the list of fields you want to make searchable (for example, title, content, category, date).
- Azure AI Search processes each document and breaks it into searchable tokens (words or phrases).
- It stores mappings between these tokens and the documents that contain them — this is called an inverted index.
- When you run a query, the service searches this index instead of scanning every document, which makes searches much faster.


Let’s say you index these three documents:
```
1. "Azure is a cloud platform."
2. "Cloud computing is powerful."
3. "Azure AI Search supports vector search."
```
The inverted index might look like:
```
"azure" → [1, 3]
"cloud" → [1, 2]
"search" → [3]

```

When you search for “cloud”, Azure returns documents 1 and 2 immediately — no need to read every file again.

Important terms
- Searchable field: A text field that’s analyzed for full-text search.
- Filterable field: A field that can be used in filters or conditions (like category eq 'Finance').
- Facetable field: A field used to group or summarize results.
- Sortable field: A field you can order results by.

### What is incremental indexing
Incremental indexing in Azure AI Search means updating only the new or changed data in your search index instead of rebuilding the entire index from scratch.

If you have large datasets (millions of documents, GBs of data), reindexing everything each time a small change happens would be:
- Time-consuming
- Expensive
- Disruptive (it can temporarily affect search availability)

Incremental indexing solves this by syncing only the delta — what’s new, modified, or deleted since the last run.

How it works
1. Your data source (e.g., Azure SQL, Blob Storage, Cosmos DB) contains some form of change tracking, such as:
- A LastModified timestamp column.
- Metadata like Last-Modified in blob properties.
2. The indexer (a built-in Azure AI Search component) keeps track of when it last ran successfully.
3. On the next run, the indexer:
    - Checks which records or files were added, updated, or deleted after that timestamp.
    - Updates only those in the index.
4. The rest of the data remains untouched.


Example

Assume you have 1 million product records in Azure SQL, each with a last_updated field.

First run:
- The indexer scans all 1M records.
- Index is built completely.

Second run (incremental):
- The indexer queries only rows where last_updated > [last run time].
- Suppose only 500 rows changed — only those 500 are reindexed.

Result: faster, cheaper, and up-to-date index.


#### What do we mean when we say on the next run?
So, “on the next run” means:

The next time the indexer job executes — either based on a schedule (like every hour/day) or because you triggered it manually — it will perform the indexing operation again (possibly incremental if enabled).

Azure AI Search is not real-time by default.

Here’s how it works:
- Data ingestion (indexing) happens through an indexer, which pulls data from a source (like Azure SQL, Cosmos DB, or Blob Storage).
- The indexer runs on a schedule — for example, every 5 minutes, hourly, or daily — depending on what you configure.
- Each run picks up new or modified data (if incremental indexing is enabled).

So, yes — it’s near real-time at best, not continuous streaming. You can configure the interval based on how fresh you need the data to be.

If you truly need real-time updates, you’d need to:

- Push data directly into the search index using the Azure Search SDK or REST API, instead of waiting for the indexer.
- This is sometimes called push-based indexing, and it gives you more control over when data appears in the search results.

### Can i push data directly into Azure AI without sitting on top of any DB (such as MySQL)
Yes — you absolutely can push data directly into Azure AI Search without using any data source like MySQL, Blob Storage, or Cosmos DB.

That’s a completely valid and common approach, especially for applications that generate or modify data dynamically.

Here’s how that works:

#### Direct (Push-Based) Approach

You can treat Azure AI Search as a standalone search engine.
- You create your index (like defining a schema in a database).
- Then you push documents directly into that index using:
    - Azure SDKs (for Python, Node.js, Java, .NET, etc.)
    - or the REST API.


Example:
```http
POST https://<service-name>.search.windows.net/indexes/products/docs/index?api-version=2023-07-01-Preview
Content-Type: application/json
api-key: <admin-key>

{
  "value": [
    {
      "@search.action": "upload",
      "id": "P001",
      "name": "Wireless Mouse",
      "category": "Electronics",
      "price": 25.99,
      "description": "A lightweight ergonomic mouse."
    }
  ]
}

```

That’s it — no MySQL, no Blob Storage, no indexer.
Your data is immediately searchable once uploaded.


How it works:
1. You define the index schema 
    ```json
    {
        "name": "products",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": true},
            {"name": "name", "type": "Edm.String", "searchable": true},
            {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
            {"name": "price", "type": "Edm.Double", "sortable": true},
            {"name": "description", "type": "Edm.String", "searchable": true}
        ]
    }

    ```
2. You push (upload) documents — via API or SDK.
3. Azure Search indexes them immediately, so users can query them right away.
4. You can update, merge, or delete specific documents anytime.


## Partition in Azure AI Search
A partition determines how your index data is physically stored and distributed across Azure infrastructure.

Each partition:

- Stores a subset of your documents.
- Handles both indexing (write) and query (read) operations for its portion of data.

When your dataset grows, you can add more partitions to:
- Increase the total storage capacity of your search index.
- Improve indexing throughput (because data is split across more servers).

Example

If you have 100 million documents and each partition can store 25 million, you’d need 4 partitions to hold them all.
Azure automatically splits your data across these partitions.

Partition vs Replica:

| Concept       | Purpose                  | Effect                                    |
| ------------- | ------------------------ | ----------------------------------------- |
| **Partition** | Splits data horizontally | Increases capacity & write speed          |
| **Replica**   | Duplicates the same data | Increases query throughput & availability |






## Best Practices while using Azure AI search

### Data Ingestion

- Use incremental indexing (change detection) rather than reindexing everything.
- Break large documents into smaller chunks (e.g., 500–1000 words) to improve search precision.
- Pre-clean data (remove boilerplate, fix encodings) before indexing.

### Index Design

- Choose fields carefully:
    - searchable for full-text.
    - filterable and sortable for metadata.
    - facetable for grouping.
- Avoid making every field searchable — it increases index size and latency.
- Use semantic fields (like title, content, summary) for ranking boosts.


### Vector Search Optimization

- Use smaller embedding models (like text-embedding-3-small) for speed if high accuracy isn’t critical.
- Set appropriate vector dimensions (usually 1,536 for OpenAI embeddings).
- Use hybrid search → keyword + vector → more accurate and faster.
- Keep vector fields separate from text fields to simplify reindexing.


### Scaling and Performance

- Start with 1–2 replicas and partitions, then scale based on:
    - High query load → increase replicas.
    - Large dataset or slow indexing → increase partitions.
- Use batch indexing (up to 1000 docs per request) for efficiency.
- Cache frequent queries in your app to reduce calls.

### AI Enrichment

- Use skillsets for structured extraction — for example:
- Extract entities → enrich with metadata → index enriched text.
- Chain multiple skills (like OCR → entity recognition → key phrase extraction).
- Log enrichment results to a storage container for debugging.

### Security

- Always use Managed Identity or API keys securely.
- Use Private Endpoints for sensitive data.
- Control query access with Azure Role-Based Access Control (RBAC).



