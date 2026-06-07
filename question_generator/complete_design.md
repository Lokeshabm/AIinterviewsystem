# Engineering Question Bank Generator — Complete Design

## Overview
This document finalizes the remaining design work for the Engineering Question Bank Generator.
It covers:
- API design and admin workflow
- Difficulty scoring and recommendation
- Tagging and metadata strategy
- Uniqueness/deduplication rules
- Operational scaling, indexing, search optimization
- Deliverables and next steps

---

## API Design
### Core endpoints
- `POST /api/generate`
  - Payload: `{ template_id, branch, subject, topic, difficulty, count, params, output_formats }`
  - Response: `{ job_id, status, requested_count, generated_count }`
- `GET /api/generate/{job_id}`
  - Response: `{ job_id, status, created_at, completed_at, generated_count, errors }`
- `GET /api/questions`
  - Filters: `branch`, `subject`, `topic`, `qtype`, `difficulty`, `tags`, `search`, `approved`, `created_after`
  - Pagination: `page`, `size`
  - Response: `{ items, total, page, size, facets }`
- `GET /api/questions/{question_uid}`
  - Response: full question document
- `POST /api/questions/{question_uid}/approve`
  - Payload: `{ reviewer_id, comments, approved }`
- `POST /api/questions/{question_uid}/flag`
  - Payload: `{ user_id, reason, metadata }`
- `GET /api/export`
  - Query: `format=sql|json|csv|mongo`, filters, fields
  - Response: download URL or streamed export

### Admin endpoints
- `GET /api/admin/approval-queue`
- `POST /api/admin/question/{question_uid}/edit`
- `GET /api/admin/templates`
- `POST /api/admin/templates`
- `GET /api/admin/metrics`

### Security
- OAuth 2.0 / JWT authentication
- RBAC roles: `admin`, `reviewer`, `generator`, `auditor`
- Audit logs for approve/reject/edit actions

---

## Admin Panel Structure
### Pages
- Dashboard: generation volume, approval status, tag coverage
- Template Manager: create/edit parameterized templates
- Approval Queue: review new questions, accept/reject, add tags
- Taxonomy Manager: branch/subject/topic hierarchy
- Search & QA: search questions and preview metadata
- Export Manager: generate SQL/JSON/CSV/Mongo exports
- Usage Analytics: difficulty distribution, usage, top tags

### Workflow
1. Question generation job creates draft questions.
2. Auto-validation checks run.
3. Questions in `pending_review` appear in approval queue.
4. Reviewer accepts or rejects with comments.
5. Approved questions are indexed and become searchable.
6. Feedback loops update template difficulty and tagging.

### Approval states
- `draft`
- `auto_validated`
- `pending_review`
- `approved`
- `rejected`
- `needs_revision`

---

## Difficulty Scoring Algorithm
### Scoring factors
- Base difficulty from template metadata
- Question type weight:
  - MCQ: baseline +0.5
  - TF: baseline -0.5
  - NUM: baseline +0.5
  - CODE: baseline +1.0
  - SA/LA: baseline +0.8
- Complexity features:
  - multi-step reasoning
  - numeric derivation
  - theoretical depth
  - practical/application focus

### Adaptive difficulty
- Track answer success rate, time spent, and revision count
- Recalculate difficulty score periodically using:
  - `difficulty_score = template_base + behavior_adjustment`
  - `behavior_adjustment = f(correct_rate, avg_time, wrong_rate)`
- Map float score into bins: Easy / Medium / Hard / Expert

---

## Tagging and Recommendation
### Tagging strategy
- Tags are assigned from:
  - template metadata
  - topic and subject taxonomy
  - keyword extraction from statements/explanations
  - manual reviewer input
- Example tags: `graph-theory`, `operating-systems`, `electronics`, `numerical-analysis`
- Leverage canonical tags and aliases to avoid fragmentation.

### Recommendation system
- Content-based: match user interests and studied topics
- Difficulty-aware: surface questions at the right level
- Sequence recommendations by curriculum progression
- Use tag vectors and usage signals for collaborative filtering
- Support `recommended_next` questions, `similar` questions, and `practice sets`

---

## Uniqueness and Deduplication Rules
### Deduplication pipeline
1. Exact text match
2. Normalized text match
3. Template-based signature match
4. Semantic similarity check using embeddings

### Canonical normalization
- Normalize whitespace and case
- Optionally mask numeric values only for semantic similarity
- Remove stop words for hash generation

### Duplicate policy
- Reject exact duplicate questions
- Allow variants that differ in parameter values or branches
- Track variant families using `question_variants`
- Prevent repeated options and repeated distractors

---

## Indexing and Search Optimization
### Search storage
- Primary search index: OpenSearch/Elasticsearch
- Document fields:
  - `branch`, `subject`, `topic`, `subtopic`, `qtype`, `difficulty`, `tags`, `keywords`, `statement`, `explanation`
- Use `keyword` sub-fields for filtering
- Use n-gram / edge-ngram analyzers for autocomplete
- Use vector search for semantic query expansion

### Index strategy
- Compose compound indexes for common filters
- Use aliasing for zero-downtime reindexing
- Periodic refresh after bulk imports
- Cache top queries in Redis

---

## Operational Scaling
### Generation at scale
- Batch workers that process template jobs in parallel
- Queue system for job orchestration: Kafka/RabbitMQ
- Template repository versioned in Git/DB
- Deduplication service in front of storage

### Storage and partitioning
- PostgreSQL with partitioned `questions` by branch or date
- MongoDB for denormalized question documents
- OpenSearch for fast retrieval and semantic search
- Use S3 or object storage for exports and snapshots

### Monitoring
- Track generation throughput, approval latency, duplicate rate
- Monitor indexing lag, query latency, and storage growth
- Use Prometheus, Grafana, ELK stack

---

## Deliverables
- Reference generator scripts: `generator.py`, `bulk_generate.py`
- Core schema: `schema.sql`, `mongo_schema.json`
- Sample exports: CSV/JSON/SQL/Mongo files
- API skeleton and admin workflow design
- Difficulty scoring and dedupe reference code
- Operational scaling and deployment notes

---

## Next Steps
1. Add a real template library for all 18 branches and 30+ question types.
2. Build a production-grade generation service with worker queue and monitoring.
3. Implement the API and admin UI using FastAPI/React or Django.
4. Add semantic deduplication with embeddings and quality scoring.
5. Integrate a recommendation engine and adaptive difficulty recalibration.
