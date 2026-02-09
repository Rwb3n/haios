---
name: {ceremony-name}
description: "{description}"
category: {category}
input_contract:
  - field: {field_name}
    type: string
    required: true
    description: "{field_description}"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether ceremony completed successfully"
side_effects:
  - "{side_effect_description}"
generated: {date}
last_updated: "{date}"
---
# {Ceremony Display Name} Ceremony

{Purpose description}

## When to Use

- {trigger_condition}

**Invocation:** `Skill(skill="{ceremony-name}")`

---

## Input Contract

| Field | Required | Description |
|-------|----------|-------------|
| `{field_name}` | MUST | {field_description} |

---

## Ceremony Steps

1. {step_1}
2. {step_2}
3. Log ceremony event
4. Report result to operator

---

## Output Contract

| Field | Guaranteed | Description |
|-------|------------|-------------|
| `success` | Always | Whether ceremony completed successfully |

---

## Side Effects

- {side_effect_description}

---

## References

- {chapter_reference}
- {requirement_reference}
