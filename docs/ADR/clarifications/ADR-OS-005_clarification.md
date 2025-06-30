# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Questions

Q1: What versioning strategy is defined for haios.config.json to support breaking schema changes?
Q2: How should the OS react to extra, unrecognized keys in the config file—ignore or fail fast?
Q3: Is there a CLI bootstrap command to regenerate a default directory scaffold if the config is missing?
Q4: What guardrails prevent user-supplied paths from escaping the repository root (path traversal)?
Q5: How will multi-repository or mono-repo setups override or extend the single config paradigm?
