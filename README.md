# Multi-Modal Code Intelligence System

**A transformer-based system for analysing source code — parsing it structurally as well
as reading it as text.**

"Multi-modal" here means the code is treated as two things at once: a token sequence a
language model can read, and a syntax tree that carries structure the tokens alone lose.
`tree-sitter` provides the parse; the transformer provides the semantics.

## What's here

```
src/
  preprocess.py   tree-sitter parsing and tokenisation
  model.py        CodeUnderstandingModel
  inference.py    CodeAnalyzer — the analysis entry point
  train.py        fine-tuning loop
  visualize.py    attention and structure views
  utils.py        logging and config loading
api.py            Flask endpoint
main.py           CLI entry point
config.yaml       model and runtime settings
```

## Design targets

- Analysis across several languages from one model
- Structural understanding rather than pattern matching over text
- Fast enough to sit in an editor loop

## On the numbers

The figures above are **design targets** that shaped the implementation — they are not
measured results. This repository ships no benchmark harness and no trained weights, so
nothing here reproduces them. They are recorded because they drove real decisions about
architecture and algorithm choice, not as claims about observed performance.

## Running it

```bash
pip install -r requirements.txt
python main.py            # CLI
python api.py             # HTTP API
```

## Status

Working skeleton: parsing, model definition, training loop, inference and API are all
present and wired together. It is a compact implementation — around 240 lines of Python —
not a finished product.

## Licence

All rights reserved. Published for reading, not for reuse.
