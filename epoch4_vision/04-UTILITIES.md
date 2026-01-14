# 04 UTILITIES

External interfaces. The only way out.

---

## What is a Utility

- Interface to external world
- Stateless from agent perspective
- Swappable implementation
- Not an agent (no reasoning, just interface)

---

## Core Utilities

```
time        # What moment is it
```

[TODO: Define domain-specific utilities separately]

---

## Utility vs Agent

If it requires reasoning → agent (skill).

If it's pure interface → utility.

```
Search API call         → utility
Interpreting search results → agent
```

---

## Utility Contract

```
INPUT:
  - Request file (what is being asked)

OUTPUT:
  - Response file (what was returned)
  - Includes: timestamp, latency, raw response, errors if any

PROPERTIES:
  - Stateless
  - Deterministic (same input → same output, external world permitting)
  - No side effects beyond the call itself
```

---

## Swapping Implementations

Utilities are interfaces. Implementations vary.

```
utility:
  name: market
  implementation: yfinance | polygon | alpha_vantage
  config:
    api_key: [if needed]
    cache_ttl: [seconds]
```

[TODO: Define interface contracts per utility type]

---

## Caching

Some utilities are cacheable (market data for a given day).

Some are not (time).

Cache rules defined per utility.
