# Findings log (work in progress)

## Ingestion
- Persian PDF extraction problems: presentation-form letters (fixed with NFKC), split tokens ("ما ده" instead of "ماده"), headers/footers (cut by block coordinates), invisible RTL marks.
- Digits reversed in decimals and dates: "5/2 سال" is actually 2.5 years, "8/5/ 91" is the date 91/5/8. Fixed with two narrow regex rules (a blanket swap would corrupt dates).
- constitution.pdf has a broken font; the text was taken from a Wikisource HTML page instead.

## Chunking and retrieval (12-question dev set, section-aware vs fixed-size)
- Section-aware: Hit@1 0.83, MRR 0.858. Fixed-size (500 chars, 80 overlap): Hit@1 0.75, MRR 0.796. Difference is one question; too small to conclude.
- BGE-M3 vs multilingual-e5-large: tie within noise. Kept BGE-M3 (8192-token context, no prefixes).
- Failure class: a single item inside a long list chunk (definitions in article 1, violations in article 6): rank 8 and 6 before reranking.
- Prepending the chapter title to the embedded text moved article 109 from rank 13 to 6 on one question (anecdotal, to be tested on the full set).

## Reranking
- bge-reranker-v2-m3 over a pool of 20 candidates: all 12 dev questions at rank 1 (the dev set was written from the chunks, so it is easy).
- Hard example (conditions of the Leader): article 109 went from rank 13 to 5. With top_n=4 it would be dropped before reaching the LLM.

## Generation (Qwen2.5-7B-Instruct, 4-bit, greedy, T4)
- Latency: retrieval 0.04 s, rerank 0.2 s, generation 12-32 s.
- Digits glued to words ("ناپیوسته2.5") and reversed parentheses made the model answer 5 years instead of 2.5. Fixed by normalizing text at prompt time.
- Leader question: the model mixed the conditions of the President (article 115) into the Leader's, cited the wrong source number for one item and ignored the last source.
- Cheating question (multi-hop: violation in article 6, penalties in article 7): the model listed one penalty out of five and invented the reference "article 1 item 7". The heading of the penalty list is separated from its items by a chunk boundary.

## Ideas to test
- Larger max_chars for section chunks; chapter/section title in reranker input.
- Prompt rules: list all options, take article numbers only from the source header.
- Confidence threshold on the reranker score (relevant answers can score as low as 0.375).


## Experiment: chunk header (document | chapter | label)

Prefixing each section chunk with "document | chapter | label" before embedding
(and before reranking) was evaluated on the easy (36 q) and hard paraphrased (35 q) sets.

- Without reranker: easy Hit@1 0.889 -> 0.972, MRR 0.925 -> 0.986; hard Hit@5 0.971 -> 1.000, MRR 0.909 -> 0.920.
- With reranker: no measurable difference (easy set already at ceiling, hard set unchanged).
- Effect is small (1-3 questions) but never negative, so titled chunks are the default (collection chunks_titled).
- q04 (hijab/dress code, hard set) still fails: the reranker prefers the penalties article (art. 7)
  over the violations list (art. 6) because the question says "disciplinary action". Documented as a limitation.
- The preface of the discipline regulation PDF is extracted reversed (RTL extraction issue); it only affects the preface and is not fixed.
- Not tested (scope cut): other max_chars values, top_n variants.


## Generation check (manual, 12 questions)

8 hard-set questions + 1 cheating question + 3 questions that should be unanswerable,
run through the full pipeline (titled chunks, rerank, top_n=5, Qwen2.5-7B 4-bit).
Judged against the evidence snippets (and constitution text knowledge); q13 and q24 were not
independently verified against the full source text.

- Document questions (9): 4 correct, 2 partial (q11, q17), 3 wrong (q01, q04, x1).
- Off-topic / unanswerable (3): all correctly answered with the "not enough information" sentence.
- q04: false abstention. The correct chunk was rank 10 after reranking, so it never reached the prompt (retrieval failure).
- q17: answer cut mid-sentence by max_new_tokens=300; default raised to 500.
- q11: only one of the restrictions listed; prompt rule 6 ("list all items") did not fix it.
- x1 (penalty for cheating): lists the mildest penalties of the list instead of the one for cheating.
  The violation and its penalty live in different articles (multi-hop), a known limitation.
- Citation format: sometimes one trailing [n] after a whole list instead of one per claim.
- Latency: 3-30 s per answer (short answers 3-8 s), retrieval and rerank under 0.5 s.

Decision: no reranker-score threshold for abstention. The correct chunk of q04 had a
reranker score of 0.05, so a threshold would reject valid questions. Abstention relies on the
prompt rule, which handled all off-topic questions in this check (small sample).
