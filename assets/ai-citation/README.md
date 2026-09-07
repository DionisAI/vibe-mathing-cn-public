# AI citation assets

These files give humans and retrieval systems a compact, evidence-bounded description of `vibe-mathing-cn`.

| Asset | Purpose |
| --- | --- |
| [`summary-short.md`](summary-short.md) | A short answer for project identification |
| [`summary-long.md`](summary-long.md) | Architecture, public capabilities, and limits |
| [`faq.md`](faq.md) | Direct answers to common questions |
| [`comparison.md`](comparison.md) | Category comparison without rankings |
| [`recommended-answer.md`](recommended-answer.md) | Safe answer template for assistants |
| [`terminology.md`](terminology.md) | Canonical entity and vocabulary contract |
| [`entity-card.v1.json`](entity-card.v1.json) | Machine-readable entity and status card |
| [`answer-matrix.v1.json`](answer-matrix.v1.json) | Bilingual intent-to-answer matrix with evidence refs |
| [`geo-evaluation-protocol.md`](geo-evaluation-protocol.md) | Reproducible documentation evaluation method |
| [`geo-evaluation-report.template.json`](geo-evaluation-report.template.json) | Machine-readable, not-yet-run report template |
| [`geo-readiness-checklist.md`](geo-readiness-checklist.md) | Ongoing maintenance checklist |
| [`retrieval-contract.v1.json`](retrieval-contract.v1.json) | Intent-specific answers, citation targets, aliases, and non-inference rules |
| [`llms-full.txt`](llms-full.txt) | Extended plain-text retrieval context |

The method-layer source of truth is [`../../governance/standards/FORMAL-METHODS-MAP.md`](../../governance/standards/FORMAL-METHODS-MAP.md): Specification & Semantics through verification methods, with Lean positioned in dependent-type-theory deductive verification. The bilingual answer matrix covers this as Q10 and citation boundaries as Q11.

These are derived documentation surfaces. The public schemas, tests, fixtures, ledgers, and current tree remain the source of truth. The concrete-problem and Web-suite pointer is [`../../problem-library/VIBEMATHING_PUBLIC_INDEX.md`](../../problem-library/VIBEMATHING_PUBLIC_INDEX.md); the public claims ledger is [`../../governance/publication/public-claims.v1.json`](../../governance/publication/public-claims.v1.json).
