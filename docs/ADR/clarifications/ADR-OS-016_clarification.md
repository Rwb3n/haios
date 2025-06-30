# ADR Clarification Record: {{ADR-ID}} - {{QUESTION_ID}}

## 1. Question

Q1: What JSON event schema fields are mandatory for every status entry?
Q2: How will multi-agent concurrent updates coordinate append offsets safely on network file systems?
Q3: Will there be a gRPC or WebSocket stream to subscribe to status updates instead of file polling?
Q4: What archival strategy compresses rotated status files to save space?
Q5: How are status events reconciled after partition healing to ensure correct ordering?
