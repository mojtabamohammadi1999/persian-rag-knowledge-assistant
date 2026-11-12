# Data

## Source documents (`data/raw/`)

| File | Document | Source |
|---|---|---|
| `discipline_regulation.pdf` | Student discipline regulation (آیین‌نامه انضباطی دانشجویان) | https://vsca.tums.ac.ir/uploads/322/2024/%D8%A2%DB%8C%DB%8C%D9%86%20%D9%86%D8%A7%D9%85%D9%87%20%D9%87%D8%A7/4692452.pdf |
| `education_regulation.pdf` | Undergraduate education regulation (آیین‌نامه آموزشی دوره کارشناسی) | https://new.meybod.ac.ir/documents/39687/184874/academic_research_14.pdf |
| `constitution.html` | Constitution of the Islamic Republic of Iran (قانون اساسی جمهوری اسلامی ایران) | Persian Wikisource (saved HTML page) |

These are public legal and regulatory texts, included only so the demo and the experiments can be reproduced.
They belong to their original publishers; the Wikisource text follows Wikisource's own license terms.
`data/raw/constitution.pdf` is not used by the pipeline and is not committed.

## Generated data (not committed)

`scripts/build_index.py` creates `data/processed/` (cleaned documents, chunks, embeddings) and the `qdrant_storage/` index from the raw files.

## Evaluation data (`data/eval/`)

- `eval_questions.json`: 36 questions written from the chunks (easy set).
- `eval_questions_hard.json`: 35 paraphrased versions of the same questions that avoid the keywords of the text (hard set).

Each item has the question, the id of the gold chunk, and an `evidence` string. A retrieved passage counts as relevant if it contains the evidence string.
