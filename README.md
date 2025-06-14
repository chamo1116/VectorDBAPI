# VectorDB API

A FastAPI-based REST API for vector document storage and search.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/vectordb.git
cd vectordb
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode:

```bash
pip install -e ".[dev]"
```

## Development

1. Install development dependencies:

```bash
pip install -e ".[dev]"
```

2. Run tests:

```bash
pytest
```

3. Run linting:

```bash
flake8
black .
isort .
mypy .
```

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## HTTP Requests

### Libraries

#### Create Library

```bash
curl -X POST "http://localhost:8000/libraries" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Library", "metadata": {"type": "test"}}'
```

#### Get Library

```bash
curl "http://localhost:8000/libraries/{library_id}"
```

#### Update Library

```bash
curl -X PUT "http://localhost:8000/libraries/{library_id}" \
     -H "Content-Type: application/json" \
     -d '{"name": "Updated Library", "metadata": {"type": "updated"}}'
```

#### Delete Library

```bash
curl -X DELETE "http://localhost:8000/libraries/{library_id}"
```

#### List Libraries

```bash
curl "http://localhost:8000/libraries"
```

### Documents

#### Create Document

```bash
curl -X POST "http://localhost:8000/libraries/{library_id}/documents" \
     -H "Content-Type: application/json" \
     -d '{"name": "My Document", "metadata": {"type": "test"}}'
```

#### Get Document

```bash
curl "http://localhost:8000/libraries/{library_id}/documents/{document_id}"
```

#### Update Document

```bash
curl -X PUT "http://localhost:8000/libraries/{library_id}/documents/{document_id}" \
     -H "Content-Type: application/json" \
     -d '{"name": "Updated Document", "metadata": {"type": "updated"}}'
```

#### Delete Document

```bash
curl -X DELETE "http://localhost:8000/libraries/{library_id}/documents/{document_id}"
```

#### List Documents

```bash
curl "http://localhost:8000/libraries/{library_id}/documents"
```

### Chunks

#### Create Chunk

```bash
curl -X POST "http://localhost:8000/libraries/{library_id}/documents/{document_id}/chunks" \
     -H "Content-Type: application/json" \
     -d '{"content": "Chunk content", "metadata": {"type": "test"}}'
```

#### Get Chunk

```bash
curl "http://localhost:8000/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}"
```

#### Update Chunk

```bash
curl -X PUT "http://localhost:8000/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}" \
     -H "Content-Type: application/json" \
     -d '{"content": "Updated content", "metadata": {"type": "updated"}}'
```

#### Delete Chunk

```bash
curl -X DELETE "http://localhost:8000/libraries/{library_id}/documents/{document_id}/chunks/{chunk_id}"
```

#### List Chunks

```bash
curl "http://localhost:8000/libraries/{library_id}/documents/{document_id}/chunks"
```

#### Search Chunks

```bash
curl -X POST "http://localhost:8000/libraries/{library_id}/chunks/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "search query", "limit": 10}'
```
