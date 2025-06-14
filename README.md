# VectorDB API

## Features

- **Document Management**

  - Create, read, update, and delete documents.
  - Persistence in memory.
  - Lock memory allocation strategy.
  - Organize documents in libraries.
  - Support for document metadata.
  - Efficient document chunking.

- **Vector Search**

  - Multiple indexing algorithms:
    - Brute Force (exact search).
    - KD-Tree (approximate nearest neighbors).
  - Support for metadata filtering.
  - Configurable search parameters.

- **Library Management**
  - Create and manage document libraries.
  - Index libraries for efficient search.
  - Support for library metadata.
  - Persistence in memory.
  - Lock memory allocation strategy.

## Technical Decisions

### Indexing Algorithms

#### Brute Force Index

The `BruteForceIndex` class implements exact nearest neighbor search using euclidean distance.

**Key Features:**

- Exact search results.
- Euclidian distance for vector comparison.
- Support for metadata filtering.
- Simple implementation with O(n) query time.

**Implementation Details:**

- Uses a heap to maintain top-k results.
- Computes euclidian distance between query vector and all indexed vectors.
- Applies filters before similarity computation.
- Returns results sorted by euclidian distance.

#### KD-Tree Index

The `KDTreeIndex` class implements approximate nearest neighbor search using a KD-Tree data structure.

**Key Features:**

- Efficient approximate nearest neighbor search.
- Balanced tree structure for logarithmic search time.
- Support for metadata filtering.
- Optimized for high-dimensional vector spaces.

**Implementation Details:**

- Builds a balanced KD-Tree by recursively splitting points along alternating dimensions.
- Uses iterative traversal for nearest neighbor search.
- Maintains a max-heap for top-k results.
- Applies pruning based on axis-aligned bounding boxes.
- Supports cosine similarity for vector comparison.

**Tree Structure:**

```python
{
    "point_idx": int,      # Index of the point in the chunks list
    "point": List[float],  # The actual vector
    "axis": int,          # The splitting dimension
    "left": dict,       # Left subtree
    "right": dict       # Right subtree
}
```

**Search Process:**

1. Start at root node
2. Compare query point with current node along splitting axis.
3. Iteratively search the "near" subtree first.
4. If necessary, search the "far" subtree.
5. Maintain a heap of k nearest neighbors.

**Algorithm Selection:**

- Brute Force is used when:
  - Dataset size is small (< 1000 vectors)
  - Exact results are required
  - Memory usage is not a concern
- KD-Tree is used when:
  - Dataset size is large
  - Approximate results are acceptable
  - Memory efficiency is important
  - High-dimensional vectors are present

**Performance Considerations:**

- Brute Force:
  - Time Complexity: O(n) for each query
  - Space Complexity: O(n)
  - Best for small datasets
  - Guarantees exact results
- KD-Tree:
  - Time Complexity: O(log n) average case
  - Space Complexity: O(n)
  - Best for large datasets
  - Provides approximate results
  - Performance degrades in high dimensions

## Installation

1. Clone the repository:

```bash
git clone https://github.com/chamo1116/VectorDBAPI.git
cd VectorDBAPI
```

2. Build the image:

```bash
docker compose build --no-cache
```

3. Run container:

```bash
docker compose up -d
```

2. Run tests:

```bash
docker compose exec app uv run pytest
```

## API Documentation

Once the server is running, you can access:

- Swagger UI: http://localhost:8000/docs

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

## Future Improvements

### Architecture Improvements

1. **Microservices Architecture**

   - Split the monolithic application into microservices:
     - Indexing Service: Handle vector indexing and search.
     - API Gateway: Manage authentication and request routing.
     - Metadata Service: Handle metadata storage and filtering.
     - Vector Service: Manage vector operations and transformations.

2. **Message Queue Integration**

   - Implement RabbitMQ or Kafka for:
     - Asynchronous indexing operations.
     - Event-driven updates.
     - Better handling of bulk operations.
     - Improved scalability for write operations.

3. **Caching Layer**
   - Add Redis for:
     - Caching frequent queries.
     - Storing temporary search results.
     - Managing rate limiting.

### Scalability Enhancements

1. **Horizontal Scaling**

   - Implement sharding for vector data.
   - Add load balancing for API endpoints.
   - Support for distributed indexing.
   - Implement consistent hashing for data distribution.

2. **Database Improvements**

   - Add support for multiple database backends:
     - SQLlite, if the idea is continue saving the data in memory (not scalable).
     - PostgreSQL with pgvector.
     - Milvus.
     - Weaviate.
     - Qdrant.
   - Implement database abstraction layer.
   - Add support for hybrid search (vector + keyword).

3. **Performance Optimizations**
   - Implement batch processing for indexing.
   - Add support for more ANN algorithms:
     - HNSW (Hierarchical Navigable Small World).
     - IVF (Inverted File Index).
     - Product Quantization.
   - Implement vector compression techniques.

### Feature Enhancements

1. **Search Capabilities**

   - Add support for:
     - Multi-vector search.
     - Hybrid search (vector + keyword).
     - Semantic search.
     - Range queries.
     - Faceted search.

2. **Indexing Algorithms**

   - Implement additional algorithms:
     - Ball Tree.
     - LSH (Locality-Sensitive Hashing).
     - Annoy.
     - FAISS.
   - Implement automatic algorithm selection based on data characteristics.

3. **Monitoring and Observability**
   - Add comprehensive metrics:
     - Query latency.
     - Index size.
     - Memory usage.
     - Cache hit rates.
   - Implement distributed tracing.
   - Add health checks and alerts.

### Security Improvements

1. **Data Security**
   - Add encryption at rest.
   - Add data masking for sensitive information.
   - Implement audit logging.
   - Add support for data retention policies.

### Developer Experience

1. **Testing**

   - Add load testing scenarios.
   - Create integration tests for all supported databases.

2. **Development Tools**
   - Add CLI tool for management.
   - Create development containers.
   - Improve documentation.

### Deployment Improvements

1. **Containerization**

   - Add Kubernetes support.
   - Create deployment templates.

2. **CI/CD**
   - Add GitHub Actions workflows.
   - Implement automated testing.
   - Add automated deployment.
   - Add version management.

### Data Management

1. **Backup and Recovery**

   - Implement automated backups.
   - Add point-in-time recovery.

2. **Data Versioning**
   - Add support for vector versioning.
   - Implement metadata versioning.
   - Create rollback capabilities.
   - Add data lineage tracking.
