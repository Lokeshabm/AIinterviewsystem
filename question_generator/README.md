Reference Question Generator

This folder contains a simple, runnable reference generator that demonstrates:
- Parameterized template-based question generation
- Deduplication using canonical hashing
- Export to SQL INSERTs, JSON, CSV, and MongoDB document formats

Requirements:
- Python 3.8+

Quick run:

```bash
python generator.py --count 100 --outdir ./output
```

Files:
- `generator.py`: reference generator script
- `templates.json`: a few example templates
- `schema.sql`: PostgreSQL schema for core tables
- `mongo_schema.json`: example Mongo document schema
- `sample_question.json/csv/sql`: single-question samples

Notes:
- This is a minimal reference and not production-ready. For scale, wire it to the full template repository, queue workers, and the deduplication/index services described earlier.
