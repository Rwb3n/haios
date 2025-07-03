# Legacy Components

This directory contains the original adapter implementations for reference. These components are **NOT** compliant with the current security architecture and should **NOT** be used directly.

## Why These Are Legacy

1. **No Security Controls**: Direct external access without sandboxing
2. **No Evidence Chain**: Missing cryptographic verification
3. **No Separation of Duties**: Monolithic design
4. **No Trace Propagation**: Cannot track distributed operations

## Migration Path

To use the arxiv integration logic:

1. Extract the core API interaction patterns
2. Wrap in `ResearchBuilderAgent` class
3. Add evidence generation at each step
4. Execute within security sandbox
5. Pass to separate `ResearchValidatorAgent`

## Files

- `adapters/poll_arxiv_new.py` - Original arxiv polling logic
- `adapters/extract_arxiv.py` - Original PDF extraction logic

These serve as reference for the arxiv API patterns but must be reimplemented within the secure architecture defined in the parent directory.