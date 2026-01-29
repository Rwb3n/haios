---
template: observations
work_id: WORK-031
captured_session: '258'
generated: '2026-01-29'
last_updated: '2026-01-29T19:44:26'
---
# Observations: WORK-031

## What surprised you?

**The critique-agent found real bugs.** The critique phase (E2-072) caught two substantive issues that would have passed tests but failed in production:
- **A3:** fnmatch does NOT support `**` recursive glob patterns. The exclusion pattern `**/archive/**` would have silently failed, including archived files in the corpus. Fix: Use `PurePath.match()` instead which properly handles `**` for recursive patterns.
- **A5:** The `extract()` method in `requirement_extractor.py` line 320 uses `str(self.corpus_path)`. When CorpusLoader is used, `corpus_path=None`, so `source_corpus` would be set to the literal string `"None"`. Fix: Check `if self.loader:` and use `loader._parsed.name` instead.

Both issues would have been difficult to debug after the fact. The critique-agent justified its existence in this single work item.

## What's missing?

**Corpus schema validation:** CorpusLoader silently skips sources with missing `path` field via `logger.warning()` at line 99 of `corpus_loader.py`. Should there be explicit schema validation that fails loudly on malformed configs? Current behavior is graceful degradation, but could hide configuration errors.

**CLI help text:** The new `corpus-list` and `--corpus` options in `cli.py` don't have documented help. Running `cli.py` without arguments shows usage, but there's no `--help` flag to enumerate available commands.

## What should we remember?

**Duck-typing for backward compatibility:** Using `hasattr(corpus, 'discover')` instead of `isinstance(corpus, CorpusLoader)` at `requirement_extractor.py` line 307 avoids circular imports and allows any object with a `discover()` method. This pattern should be reused for similar interface extensions where backward compatibility matters.

**Critique-agent is worth the cost:** Despite adding ~5 minutes to planning phase, critique-agent caught bugs that would have taken longer to debug in CHECK phase. The REVISE verdict with operator confirmation workflow worked well.

**TRDParser path matching:** Tests failed initially because TRDParser checks for 'specs' or 'trd' in the path string (`requirement_extractor.py` line 163). Test fixtures must use paths that trigger the correct parser - using `tmp_path / "docs" / "spec.md"` won't match TRDParser because 'specs' != 'spec'.

## What drift did you notice?

**18 pre-existing test failures:** The full test suite shows 18 failures unrelated to WORK-031 (checkpoint_cycle_verify, hooks, lib_migration, etc.). These represent accumulated drift that should be triaged. Ref: `pytest tests/ -v` output shows 871 passed, 18 failed.

**Version assertion hardcoding:** `tests/test_requirement_extractor.py` line 166 had hardcoded `VERSION == "1.0.0"` assertion. When bumping versions in source code, tests must be updated. This coupling is fragile and could be avoided by testing `VERSION` format rather than exact value.
