# AI-DAM — AI-Powered Digital Asset Management

AI-DAM is a local AI-powered Digital Asset Management system for indexing, understanding, searching, and previewing mixed digital assets.

The system supports images, videos, and PDF documents stored in a local library. It extracts file metadata, uses AI to understand visual content, generates semantic embeddings, and enables natural-language search over the indexed assets.

The application is designed to work completely locally using PostgreSQL, Qdrant, Ollama, and a React frontend.

---

## 1. Project Overview

Traditional file browsing requires users to remember filenames, folders, or exact keywords.

AI-DAM provides semantic search over a local media library. Instead of searching only by filename, users can search using natural-language descriptions such as:

* `yellow flower`
* `cartoon rabbit`
* `mountain landscape`
* `outdoor scene`
* `document with text`
* `people`
* `animal`

The system processes each supported asset and creates a searchable representation containing:

* File metadata
* AI-generated content understanding
* Extracted PDF text where available
* Semantic embeddings
* File type information
* Original local file location

Search results are ranked according to semantic similarity.

---

## 2. Key Features

### Asset Ingestion

* Recursive scanning of a configured local data directory
* Image ingestion
* Video ingestion
* PDF ingestion
* File metadata extraction
* SHA-256 hashing for duplicate detection
* Incremental indexing
* Detection of unchanged files
* Per-file processing status

### AI-Powered Understanding

* AI-based image understanding using Ollama and Moondream
* Video understanding through sampled video frames
* PDF text extraction using PyMuPDF
* AI/search context stored for indexed assets
* Semantic embeddings generated for searchable content

### Semantic Search

* Natural-language search
* Vector similarity search using Qdrant
* Relevance-ranked results
* Relevance scores displayed in the UI
* File-type filtering
* Search across mixed media types

### Asset Preview

* Image preview
* Video playback
* PDF preview and page navigation
* Asset metadata display
* AI-generated search context display
* Access to the original local file

### Reliability

* Persistent indexing jobs
* Indexing progress tracking
* Successful/failed processing counts
* Per-file failure handling
* Unsupported/corrupted asset handling
* Duplicate detection
* Incremental indexing
* Failed assets do not prevent successfully processed assets from remaining searchable

---

## 3. Supported File Types

### Images

* JPG / JPEG
* PNG
* WEBP
* BMP
* GIF
* TIFF

### Videos

* MP4
* MOV
* AVI
* MKV
* WEBM
* MPEG / MPG

### Documents

* PDF

---

## 4. Technology Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

### AI and Search

* Ollama
* Moondream
* EmbeddingGemma
* Qdrant

### Media Processing

* Pillow
* OpenCV
* FFmpeg
* FFprobe
* PyMuPDF

### Frontend

* React
* Vite

### Testing

* Pytest
* FastAPI TestClient
* Manual UI test cases

### Infrastructure

* Docker Compose
* Git

---

## 5. Project Structure

```text
AI-DAM/
├── backend/
│   └── app/
│       ├── api/
│       ├── db/
│       ├── models/
│       └── services/
├── frontend/
│   ├── public/
│   └── src/
├── data/
│   ├── images/
│   ├── pdfs/
│   └── videos/
├── db/
├── testcases/
│   ├── test_api.py
│   ├── test_ui_manual.md
│   └── search_evaluation.md
├── docker-compose.yml
├── .env
├── .env.example
└── README.md
```

Generated/development directories such as `.venv`, `node_modules`, `dist`, and `__pycache__` are not part of the application source structure.

---

## 6. System Architecture

AI-DAM uses separate components for metadata storage, vector search, AI processing, and the user interface.

```text
                    ┌─────────────────────┐
                    │    React Frontend   │
                    │      + Vite         │
                    └──────────┬──────────┘
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │                     │
                    │ Search / Indexing   │
                    │ Asset Access        │
                    └───────┬─────┬───────┘
                            │     │
                 ┌──────────┘     └─────────────┐
                 ▼                              ▼
        ┌─────────────────┐             ┌─────────────────┐
        │   PostgreSQL    │             │     Qdrant      │
        │                 │             │                 │
        │ Asset metadata  │             │ Vector          │
        │ Indexing jobs   │             │ embeddings      │
        │ Status          │             │ similarity      │
        └─────────────────┘             └─────────────────┘
                 ▲                              ▲
                 │                              │
                 └──────────────┬───────────────┘
                                │
                       ┌────────▼────────┐
                       │     Ollama      │
                       │                 │
                       │   Moondream     │
                       │ EmbeddingGemma  │
                       └─────────────────┘
```

---

## 7. Data Flow

### Indexing Flow

```text
Local Data Folder
       │
       ▼
Library Scanner
       │
       ├── File metadata
       ├── SHA-256 hash
       └── File type detection
       │
       ▼
PostgreSQL
       │
       ▼
Indexing Job
       │
       ├── Image → Moondream
       │
       ├── Video → frame sampling → Moondream
       │
       └── PDF → PyMuPDF text extraction
       │
       ▼
Searchable Text / AI Context
       │
       ▼
EmbeddingGemma
       │
       ▼
Qdrant
       │
       ▼
Asset becomes searchable
```

### Search Flow

```text
User Query
    │
    ▼
FastAPI Search Endpoint
    │
    ▼
EmbeddingGemma
    │
    ▼
Query Vector
    │
    ▼
Qdrant Similarity Search
    │
    ▼
Matching Asset IDs
    │
    ▼
PostgreSQL Metadata
    │
    ▼
Ranked Search Results
    │
    ▼
React UI
```

---

## 8. Storage Design

### PostgreSQL

PostgreSQL stores persistent application data including:

* Asset records
* File metadata
* File paths
* File type
* File size
* SHA-256 hash
* Processing status
* AI/search context
* Indexing jobs
* Job progress and processing results

PostgreSQL is the source of truth for asset metadata and processing state.

### Qdrant

Qdrant stores vector embeddings used for semantic similarity search.

The application uses the `asset_embeddings` collection.

The embedding vector size used by the application is 768.

Qdrant payloads associate vectors with the corresponding asset records.

---

## 9. Indexing Pipeline

The indexing pipeline processes assets individually.

For each asset:

1. Identify the asset in PostgreSQL.
2. Determine the file type.
3. Run the appropriate processing pipeline.
4. Generate AI/search context.
5. Generate an embedding.
6. Store the embedding in Qdrant.
7. Update the asset status in PostgreSQL.
8. Update indexing job progress.

If processing fails, the asset is marked as failed and the error is recorded. Other assets can continue to be processed.

This prevents a single problematic asset from stopping the complete indexing workflow.

---

## 10. Image Processing

Images are processed using the Ollama vision model.

The image is prepared for the vision model and passed to Moondream to generate a textual description of the visual content.

The resulting context is then converted into a semantic embedding using EmbeddingGemma.

Example:

```text
Image
  ↓
Moondream
  ↓
AI-generated description
  ↓
EmbeddingGemma
  ↓
Qdrant
```

This allows queries such as:

```text
yellow flower
mountain landscape
cartoon rabbit
people
animal
```

to retrieve visually relevant images even when the search terms are not present in the filename.

---

## 11. Video Processing

Videos are not processed frame-by-frame for their entire duration.

Instead, the application samples representative frames from the video and uses the vision model to understand the sampled content.

This approach reduces processing cost while still providing useful semantic information about the video.

```text
Video
  ↓
Representative frame sampling
  ↓
Vision model
  ↓
Combined video context
  ↓
Embedding
  ↓
Qdrant
```

This is a practical trade-off for local processing, particularly for longer videos.

---

## 12. PDF Processing

PDF files are processed using PyMuPDF.

The application attempts to extract text from the document and uses the extracted content as searchable context.

Text-based PDFs can therefore be searched using queries such as:

```text
document with text
```

Some PDFs may contain images, encrypted content, or content that does not expose extractable text.

Such files can fail processing without stopping the overall indexing job.

OCR for scanned/image-only PDFs is currently not implemented.

---

## 13. Incremental Indexing

The scanner uses file metadata and SHA-256 hashes to identify assets.

The system avoids unnecessarily reprocessing files that have already been indexed and have not changed.

This allows subsequent indexing runs to focus on:

* New files
* Modified files
* Previously failed/pending files

This is important for large local libraries because the entire collection does not need to be processed again after every change.

---

## 14. Duplicate Detection

Files are hashed using SHA-256 during scanning.

The hash can be used to identify duplicate content even when duplicate files have different filenames or locations.

Duplicate assets are recorded during scanning rather than silently overwriting the existing asset record.

---

## 15. Failed and Unsupported Assets

The system is designed to handle problematic files without crashing the application.

Examples include:

* Corrupted files
* Encrypted/password-protected PDFs
* PDFs without extractable text
* Unsupported formats
* AI/model processing failures
* Media processing failures

Each asset has a processing status.

A failed asset does not prevent other assets from being indexed.

This allows indexing jobs to complete while preserving information about files that require investigation or additional processing support.

---

## 16. Excluded Assets

Assets can also be marked as `excluded`.

Excluded assets remain in the local dataset and database but are not returned by normal semantic search.

This allows problematic or intentionally excluded assets to remain available for record keeping without affecting normal search results.

---

## 17. API Endpoints

The FastAPI backend currently provides the following endpoints.

| Method | Endpoint                     | Purpose                                  |
| ------ | ---------------------------- | ---------------------------------------- |
| GET    | `/health`                    | Check API health                         |
| GET    | `/health/database`           | Check PostgreSQL connectivity            |
| GET    | `/health/qdrant`             | Check Qdrant connectivity and collection |
| POST   | `/index/scan`                | Scan the configured library              |
| POST   | `/index/start`               | Start an indexing job                    |
| GET    | `/index/jobs/{job_id}`       | Check indexing job progress              |
| POST   | `/assets/{asset_id}/analyze` | Analyze an individual asset              |
| GET    | `/search`                    | Perform semantic search                  |
| GET    | `/assets/{asset_id}/file`    | Access the original asset                |

Interactive API documentation is available through FastAPI Swagger UI.

---

## 18. Running the Application

### Prerequisites

Install the following:

* Python
* Node.js and npm
* Docker Desktop
* Ollama
* FFmpeg / FFprobe

The required Ollama models are:

```text
moondream:latest
embeddinggemma:latest
```

The local environment configuration is documented in `.env.example`.

### Start Infrastructure

From the project root:

```powershell
docker compose up -d
```

This starts:

* PostgreSQL
* Qdrant

### Verify Ollama Models

Make sure Ollama is running locally and the required models are available.

```powershell
ollama list
```

Expected models include:

```text
moondream:latest
embeddinggemma:latest
```

### Start the Backend

Activate the Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn backend.app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Frontend

Open a second terminal:

```powershell
cd frontend
```

Install dependencies if required:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Open the URL shown by Vite in the terminal.

---

## 19. Indexing the Library

The application scans the configured local data directory.

The sample project uses:

```text
data/
├── images/
├── pdfs/
└── videos/
```

The indexing process is split into scanning and processing.

### Step 1 — Scan

The scanner identifies supported files and registers their metadata.

### Step 2 — Index

The indexing job processes pending assets using the appropriate AI/media pipeline.

The UI displays indexing progress and processing results.

---

## 20. Search

The search interface accepts natural-language queries.

Examples:

```text
yellow flower
forest
flowers
people
animal
nature
document with text
car
outdoor scene
mountain landscape
```

Results are ranked according to semantic similarity.

Users can also filter results by file type:

* Images
* Videos
* PDFs

---

## 21. Dataset

The project uses a locally stored mixed-media dataset containing:

* Images
* Videos
* PDFs

The dataset is stored under:

```text
data/
├── images/
├── pdfs/
└── videos/
```

The initial library scan contained approximately **2,063 supported files**.

Because AI processing is computationally expensive on a local machine, the full dataset is not necessarily AI-indexed in a single run. The application supports incremental and batch processing so that indexing can be performed safely on available hardware.

The dataset includes both normal assets and intentionally problematic files used to validate failure handling.

Examples of tested failure cases include:

* Encrypted/password-protected PDFs
* PDFs without extractable text
* Assets that cause vision-model processing failures

---

## 22. Search Evaluation

Semantic search was evaluated using 10 natural-language queries.

| Query                | Expected Result                   | Observation                                           |
| -------------------- | --------------------------------- | ----------------------------------------------------- |
| `yellow flower`      | Yellow flowers / sunflower images | Relevant sunflower assets appeared near the top       |
| `forest`             | Forest and wooded scenes          | Relevant forest images were retrieved                 |
| `flowers`            | Flower images                     | Multiple flower-related assets were retrieved         |
| `people`             | Images containing people          | A family/people image appeared near the top           |
| `animal`             | Animal images                     | Multiple animal images were retrieved                 |
| `nature`             | Natural landscapes/scenes         | Relevant outdoor and natural scenes were retrieved    |
| `document with text` | Text-based PDFs                   | PDF documents dominated the top results               |
| `car`                | Car images                        | Relevant car images appeared near the top             |
| `outdoor scene`      | Outdoor environments              | Multiple outdoor images were highly ranked            |
| `mountain landscape` | Mountain images                   | Mountain images received the highest relevance scores |

### Observed Limitations

The evaluation also identified some false positives.

For broader queries such as:

```text
forest
people
animal
nature
```

some PDFs appeared among the top results even when they were not visually relevant.

This is a current limitation of the semantic representation and mixed-media embedding approach.

More specialized metadata, modality-aware ranking, and improved multimodal embeddings could improve this behavior.

---

## 23. Testing

### Automated API Tests

Automated tests are located at:

```text
testcases/test_api.py
```

The test suite covers:

* API health
* PostgreSQL health
* Qdrant health
* Semantic search
* File-type filtering

Run:

```powershell
pytest
```

The current API test suite contains 5 tests.

### Manual UI Tests

Manual UI test cases are documented in:

```text
testcases/test_ui_manual.md
```

The manual tests cover:

* Natural-language search
* Image preview
* Video preview
* PDF preview
* File-type filtering
* Library indexing
* Original file access
* AI search context
* Failed asset handling
* Excluded asset handling

### Search Evaluation

Search evaluation results are documented in:

```text
testcases/search_evaluation.md
```

---

## 24. Reliability and Failure Handling

The system was designed with long-running indexing operations in mind.

### Per-file failure isolation

Each asset is processed independently.

```text
Asset A → Success
Asset B → Failed
Asset C → Success
```

The failure of Asset B does not prevent Asset C from being processed.

### Persistent job status

Indexing jobs maintain:

* Total files
* Processed files
* Successful files
* Failed files
* Current status

This allows the frontend to display progress while the indexing operation is running.

### Incremental processing

Previously indexed and unchanged files can be skipped rather than processed repeatedly.

---

## 25. Configuration

Copy the example environment file:

```text
.env.example
```

to:

```text
.env
```

The environment file contains configuration for:

* PostgreSQL
* Qdrant
* Ollama
* Vision model
* AI request timeout
* Image processing limits
* FFmpeg / FFprobe

Machine-specific paths such as FFmpeg locations should be configured in the local `.env`.

The actual `.env` file should not be committed to the repository.

---

## 26. Limitations

Current limitations include:

* OCR for scanned/image-only PDFs is not implemented.
* Video understanding is based on sampled frames rather than complete frame-by-frame analysis.
* Semantic search can return false positives, particularly for broad queries.
* Local AI inference can be computationally expensive.
* Processing very large libraries may require batching.
* The current system is designed for a local single-user environment.
* There is no authentication or multi-user access control.
* AI model availability is dependent on the local Ollama installation.

---

## 27. Possible Production Improvements

Future improvements could include:

* OCR support for scanned PDFs
* More advanced multimodal embeddings
* Modality-aware search ranking
* Better video scene sampling
* Thumbnail generation and caching
* Background worker queues
* Retry policies for temporary AI failures
* Improved duplicate management
* More detailed search filters
* Full-text search alongside vector search
* Authentication and authorization
* Multi-user support
* Cloud/object-storage integration
* Distributed indexing workers
* Monitoring and structured logging
* Production database migrations
* Improved model evaluation and relevance tuning

---

## 28. Assignment Coverage

| Requirement               | Implementation                     |
| ------------------------- | ---------------------------------- |
| Local mixed-media library | Images, videos, PDFs under `data/` |
| File metadata             | PostgreSQL asset records           |
| AI content understanding  | Ollama + Moondream                 |
| PDF text extraction       | PyMuPDF                            |
| Video processing          | Representative frame sampling      |
| Semantic search           | EmbeddingGemma + Qdrant            |
| Ranked results            | Vector similarity scores           |
| Image preview             | Frontend asset preview             |
| Video preview             | Frontend video playback            |
| PDF preview               | Frontend PDF viewer                |
| Filters                   | File-type filtering                |
| Progress/status           | Persistent indexing jobs           |
| Failed files              | Per-file failure status            |
| Duplicate handling        | SHA-256 hashing                    |
| Incremental indexing      | Existing asset/status checks       |
| Persistent storage        | PostgreSQL + Qdrant                |
| Search evaluation         | 10-query evaluation                |
| Automated testing         | Pytest API tests                   |
| Manual UI testing         | `test_ui_manual.md`                |

---

## 29. Repository Contents

```text
backend/
    FastAPI backend and application services

frontend/
    React/Vite user interface

data/
    Local mixed-media dataset

db/
    Database initialization files

testcases/
    Automated tests, manual UI tests, and search evaluation

docker-compose.yml
    PostgreSQL and Qdrant infrastructure

.env.example
    Example environment configuration

README.md
    Project documentation
```

---

## 30. Summary

AI-DAM provides an end-to-end local workflow for:

```text
Local Files
    ↓
Scan
    ↓
Metadata + Duplicate Detection
    ↓
AI / Document Processing
    ↓
Searchable Context
    ↓
Embeddings
    ↓
Qdrant
    ↓
Natural-Language Search
    ↓
Ranked Results
    ↓
Preview + Original File Access
```

The system combines traditional metadata storage with AI-based semantic understanding to make a mixed-media local library searchable using natural language.
