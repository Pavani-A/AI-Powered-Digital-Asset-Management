# AI-DAM Architecture

## 1. System Overview

AI-DAM is a local AI-powered Digital Asset Management system designed to index and semantically search mixed-media assets.

The system consists of five primary layers:

```text
┌──────────────────────────────────────────────┐
│                React Frontend                │
│          Search • Preview • Status           │
└──────────────────────┬───────────────────────┘
                       │ HTTP
                       ▼
┌──────────────────────────────────────────────┐
│                 FastAPI Backend              │
│     API • Scanning • Indexing • Search       │
└───────────┬──────────────┬───────────────────┘
            │              │
            ▼              ▼
┌──────────────────┐  ┌──────────────────────┐
│   PostgreSQL     │  │       Qdrant         │
│                  │  │                      │
│ Asset metadata   │  │ Vector embeddings    │
│ Job information  │  │ Semantic similarity  │
│ Processing state  │  │ Search payloads      │
└──────────────────┘  └──────────────────────┘
            ▲              ▲
            │              │
            └──────┬───────┘
                   │
                   ▼
          ┌──────────────────┐
          │      Ollama      │
          │                  │
          │    Moondream     │
          │  EmbeddingGemma  │
          └──────────────────┘
```

---

## 2. Major Components

### 2.1 Frontend

The frontend is implemented using React and Vite.

Responsibilities:

* Provide the search interface
* Display ranked search results
* Display relevance scores
* Filter results by file type
* Display image previews
* Play video previews
* Display PDF previews
* Display asset metadata
* Display AI-generated search context
* Provide access to the original asset
* Display indexing progress and status

The frontend communicates with the FastAPI backend using HTTP APIs.

---

### 2.2 FastAPI Backend

The backend provides the main application logic.

Responsibilities:

* Expose REST API endpoints
* Scan the local media library
* Start and manage indexing jobs
* Process individual assets
* Generate searchable content
* Generate embeddings
* Perform semantic search
* Retrieve asset metadata
* Serve original local files
* Track processing status and failures

The backend coordinates communication between PostgreSQL, Qdrant, Ollama, and the local filesystem.

---

### 2.3 PostgreSQL

PostgreSQL provides persistent relational storage.

It stores information such as:

* Asset IDs
* Filenames
* File paths
* File types
* File sizes
* File hashes
* Processing status
* AI/search context
* Indexing jobs
* Job progress
* Processing results and failures

PostgreSQL acts as the primary source of truth for asset metadata and indexing state.

---

### 2.4 Qdrant

Qdrant is used as the vector database.

It stores semantic embeddings generated from the searchable representation of each asset.

The application uses the:

```text
asset_embeddings
```

collection.

The vector size used by the application is:

```text
768
```

Qdrant enables similarity-based retrieval for natural-language queries.

---

### 2.5 Ollama

Ollama provides local AI model inference.

The project uses:

```text
Moondream
EmbeddingGemma
```

Moondream is used for visual content understanding.

EmbeddingGemma is used to convert searchable text/context into vector embeddings.

Running these models locally allows the application to process the dataset without requiring a cloud AI service.

---

## 3. Service Layer

The backend separates processing responsibilities into services.

```text
backend/app/services/

├── embedding_service.py
├── indexing_service.py
├── media_service.py
├── ollama_service.py
├── pdf_service.py
├── qdrant_service.py
├── scanner_service.py
├── search_service.py
└── video_service.py
```

### Scanner Service

Responsible for:

* Recursive library scanning
* Supported file detection
* Metadata extraction
* SHA-256 hashing
* Duplicate detection
* Incremental scan behavior

---

### Indexing Service

Coordinates the complete indexing pipeline.

It:

1. Retrieves pending assets.
2. Determines the appropriate processing pipeline.
3. Generates searchable content.
4. Generates embeddings.
5. Stores vectors in Qdrant.
6. Updates PostgreSQL status.
7. Updates job progress.
8. Records processing failures.

---

### Media Service

Handles image/media-related processing and preparation before AI analysis.

---

### Ollama Service

Provides communication with the locally running Ollama server.

It handles requests to the configured AI models and returns model-generated content.

---

### PDF Service

Processes PDF documents using PyMuPDF.

Its primary responsibility is extracting text that can be used as searchable content.

---

### Video Service

Handles video processing and representative frame extraction.

The system does not process every frame of a video. Instead, representative frames are sampled to reduce processing cost.

---

### Embedding Service

Converts searchable text into vector embeddings using the configured embedding model.

The resulting vectors are passed to Qdrant.

---

### Qdrant Service

Handles vector database operations such as:

* Creating/accessing the collection
* Storing embeddings
* Querying similar vectors
* Applying search filters

---

### Search Service

Coordinates semantic search.

The search flow is:

```text
User Query
    │
    ▼
Search Service
    │
    ▼
Embedding Model
    │
    ▼
Query Embedding
    │
    ▼
Qdrant
    │
    ▼
Similar Asset IDs
    │
    ▼
PostgreSQL
    │
    ▼
Asset Metadata
    │
    ▼
Ranked Results
```

Only assets with an indexed status are returned by normal semantic search.

---

## 4. Asset Indexing Architecture

The indexing architecture separates scanning from AI processing.

```text
                Local Dataset
                     │
                     ▼
              Scanner Service
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    File Metadata          SHA-256 Hash
          │                     │
          └──────────┬──────────┘
                     ▼
                PostgreSQL
                     │
                     ▼
              Indexing Job
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
       Image       Video       PDF
          │          │          │
          ▼          ▼          ▼
     Moondream   Frame       PyMuPDF
                 Sampling
          │          │          │
          └──────────┼──────────┘
                     ▼
             Searchable Context
                     │
                     ▼
               EmbeddingGemma
                     │
                     ▼
                  Qdrant
                     │
                     ▼
             Indexed Asset
```

---

## 5. Image Processing Flow

For an image asset:

```text
Image File
    │
    ▼
Image Preparation
    │
    ▼
Moondream
    │
    ▼
AI-generated Description
    │
    ▼
EmbeddingGemma
    │
    ▼
Vector Embedding
    │
    ▼
Qdrant
```

The generated description provides semantic information about the visual content.

For example, an image containing a yellow flower can become searchable using:

```text
yellow flower
```

even if those words are not present in the filename.

---

## 6. Video Processing Flow

Videos are processed using representative frame sampling.

```text
Video File
    │
    ▼
Video Metadata
    │
    ▼
Representative Frame Sampling
    │
    ▼
Sampled Frames
    │
    ▼
Moondream
    │
    ▼
Video Context
    │
    ▼
EmbeddingGemma
    │
    ▼
Qdrant
```

### Why frame sampling?

Processing every frame of a long video would significantly increase AI inference cost and processing time.

Sampling representative frames provides a practical compromise for local indexing while still allowing the system to understand the general visual content of a video.

---

## 7. PDF Processing Flow

PDF processing uses PyMuPDF.

```text
PDF
 │
 ▼
PyMuPDF
 │
 ▼
Text Extraction
 │
 ▼
Searchable Context
 │
 ▼
EmbeddingGemma
 │
 ▼
Qdrant
```

Text-based PDFs can therefore participate in semantic search.

PDFs that are encrypted, corrupted, or contain no extractable text may fail processing.

OCR for scanned/image-only PDFs is not currently implemented.

---

## 8. Search Architecture

The search system uses semantic vector similarity rather than filename-only matching.

```text
                User
                 │
                 ▼
          Natural Language
               Query
                 │
                 ▼
        GET /search?q=...
                 │
                 ▼
          Search Service
                 │
                 ▼
          EmbeddingGemma
                 │
                 ▼
           Query Vector
                 │
                 ▼
              Qdrant
                 │
                 ▼
       Similarity-ranked Assets
                 │
                 ▼
            PostgreSQL
                 │
                 ▼
        Asset Metadata
                 │
                 ▼
          FastAPI Response
                 │
                 ▼
             React UI
```

The search endpoint also supports an optional file-type filter.

---

## 9. Incremental Indexing

The system is designed to avoid unnecessary reprocessing.

During scanning, the application records information such as:

* File path
* File size
* Modification information
* SHA-256 hash
* Processing status

Previously indexed and unchanged assets can therefore remain indexed.

New or changed assets can be processed during subsequent indexing runs.

This is particularly useful for a large local media library.

---

## 10. Duplicate Handling

SHA-256 hashes are generated during scanning.

The hash provides a content-based identifier that can be used to detect duplicate files.

Duplicate detection prevents identical content from being treated as completely unrelated assets solely because the files have different names.

---

## 11. Indexing Job Architecture

Indexing jobs are persisted in PostgreSQL.

A job tracks information such as:

```text
Total files
Processed files
Successful files
Failed files
Job status
```

The frontend can use this information to display indexing progress.

The general flow is:

```text
Start Indexing
      │
      ▼
Create Job
      │
      ▼
Select Pending Assets
      │
      ▼
Process Assets
      │
      ├───────────────┐
      │               │
      ▼               ▼
   Success          Failure
      │               │
      └───────┬───────┘
              ▼
       Update Job Progress
              │
              ▼
        Complete Job
```

---

## 12. Failure Isolation

Each asset is processed independently.

For example:

```text
Asset 1 → Success
Asset 2 → Failed
Asset 3 → Success
Asset 4 → Success
```

A failure in Asset 2 does not stop the processing of the remaining assets.

Failure information is recorded so that problematic files can be identified later.

Possible failures include:

* Corrupted media
* Encrypted PDFs
* PDFs without extractable text
* Unsupported files
* AI model failures
* Media processing failures

---

## 13. Asset State

Assets have processing states that allow the application to distinguish between different conditions.

Conceptually:

```text
Discovered
    │
    ▼
Pending
    │
    ├──────────────┐
    ▼              ▼
Indexed          Failed
    │
    ▼
Searchable
```

Assets can also be marked as:

```text
Excluded
```

Excluded assets remain in the database but are omitted from normal semantic search.

---

## 14. Data Persistence

The system uses two persistent stores for different purposes.

```text
                AI-DAM
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   PostgreSQL            Qdrant
        │                   │
        │                   │
   Structured data      Vector data
        │                   │
   Asset metadata       Embeddings
   Job status           Similarity search
   Processing state     Search payloads
```

This separation allows relational application state and vector search data to be managed independently.

---

## 15. Local Infrastructure

Docker Compose provides the local infrastructure services:

```text
Docker Compose
     │
     ├── PostgreSQL
     │
     └── Qdrant
```

Ollama runs locally outside the Docker Compose services and provides AI inference.

The FastAPI backend communicates with all required services through their configured local endpoints.

---

## 16. API Layer

The main API endpoints are:

| Method | Endpoint                     | Responsibility             |
| ------ | ---------------------------- | -------------------------- |
| GET    | `/health`                    | API health                 |
| GET    | `/health/database`           | Database health            |
| GET    | `/health/qdrant`             | Vector database health     |
| POST   | `/index/scan`                | Scan local library         |
| POST   | `/index/start`               | Start indexing             |
| GET    | `/index/jobs/{job_id}`       | Retrieve indexing progress |
| POST   | `/assets/{asset_id}/analyze` | Analyze an asset           |
| GET    | `/search`                    | Semantic search            |
| GET    | `/assets/{asset_id}/file`    | Access original file       |

---

## 17. Frontend-to-Backend Flow

```text
React UI
   │
   ├── Search ───────────────► GET /search
   │
   ├── Start Scan ───────────► POST /index/scan
   │
   ├── Start Indexing ───────► POST /index/start
   │
   ├── Job Status ────────────► GET /index/jobs/{job_id}
   │
   └── Original File ────────► GET /assets/{asset_id}/file
```

The frontend does not directly communicate with PostgreSQL or Qdrant.

All application operations go through the FastAPI backend.

---

## 18. Security and Configuration

The application is intended for local single-user use.

Configuration is provided through environment variables:

```text
DATABASE_URL
QDRANT_URL
OLLAMA_BASE_URL
OLLAMA_VISION_MODEL
AI_REQUEST_TIMEOUT_SECONDS
VISION_MAX_IMAGE_SIZE
VISION_JPEG_QUALITY
FFPROBE_PATH
FFMPEG_PATH
```

The `.env` file contains machine-specific configuration and should not be committed.

`.env.example` provides a safe configuration template for setup.

---

## 19. Current Limitations

The current architecture has several known limitations:

* OCR for scanned PDFs is not implemented.
* Video processing uses sampled frames rather than every frame.
* Broad semantic queries can produce some false positives.
* Local AI inference can be computationally expensive.
* Large libraries may need to be processed in batches.
* The system does not currently provide authentication.
* The system is designed for a single local user.
* AI processing depends on locally available Ollama models.

---

## 20. Future Architecture Improvements

Potential production improvements include:

### Background Workers

Move long-running AI processing into dedicated worker processes or a task queue.

```text
FastAPI
   │
   ▼
Job Queue
   │
   ├── Worker 1
   ├── Worker 2
   └── Worker 3
```

This would allow indexing to scale independently from API requests.

### OCR Pipeline

Add OCR for image-only and scanned PDFs.

```text
PDF
 │
 ├── Text available → PyMuPDF
 │
 └── No text → OCR
```

### Improved Multimodal Search

Use a multimodal embedding model that represents images and text in a shared vector space.

This could reduce dependence on generated textual descriptions.

### Better Search Ranking

Combine multiple signals:

```text
Semantic Similarity
        +
File Type
        +
Metadata
        +
Keyword Match
```

to improve ranking for specific queries.

### Production Storage

For a production deployment, the local filesystem could be replaced or extended with object storage while PostgreSQL and Qdrant continue to store metadata and vector representations.

---

## 21. End-to-End Architecture Summary

```text
┌──────────────────────────────────────────────────────────┐
│                    Local Asset Library                   │
│              Images • Videos • PDFs                      │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Scanner Service │
                   └────────┬────────┘
                            │
                 Metadata + Hash + Status
                            │
                            ▼
                   ┌─────────────────┐
                   │   PostgreSQL    │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │ Indexing Service│
                   └────────┬────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
          Images          Videos          PDFs
             │              │              │
             ▼              ▼              ▼
        Moondream       Frame Sampling   PyMuPDF
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                   Searchable Context
                            │
                            ▼
                   ┌─────────────────┐
                   │ EmbeddingGemma  │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │     Qdrant      │
                   └────────┬────────┘
                            │
                     Semantic Search
                            │
                            ▼
                   ┌─────────────────┐
                   │   FastAPI API   │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   React UI      │
                   └─────────────────┘
```

This architecture separates file ingestion, persistent metadata, AI processing, vector search, and presentation while keeping the complete system locally deployable.
