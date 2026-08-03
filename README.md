# Multi-Modal Code Intelligence System

**A transformer-based system for analysing source code — parsing it structurally as well
as reading it as text.**

"Multi-modal" here means the code is treated as two things at once: a token sequence a
language model can read, and a syntax tree that carries structure the tokens alone lose.
`tree-sitter` provides the parse; the transformer provides the semantics.

## What's here

```
src/
  preprocess.py   tree-sitter parsing: comment removal and definition extraction
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
python main.py --code_file path/to/file.py     # CLI
python api.py                                   # HTTP API
```

The Python grammar arrives with the `tree-sitter-python` wheel, so there is no build step.
Adding another language means installing its wheel and adding one line to
`LANGUAGE_MODULES` in `src/preprocess.py`.

`config.yaml` defaults to `device: auto`, which uses CUDA when it is present and CPU
otherwise.

Parsing a file returns the definitions it contains:

```
functions: ['top_level']
methods  : ['method_one', 'method_two']
classes  : ['Widget']
```

## Status

Working skeleton: parsing, model definition, training loop, inference and API are present
and wired together. It is a compact implementation — around 240 lines of Python — not a
finished product.

### Notes from a correctness pass

Four defects fixed:

- **The parser could not load.** `load_parser` built a `Language` from
  `build/my-languages.so` using the pre-0.22 tree-sitter API. That file was never in the
  repository and nothing generated it, so `preprocess_code` failed on every clone. The
  grammar now comes from a wheel.
- **Comment stripping corrupted code.** `re.sub(r'#.*?
', ...)` cuts at any `#`, including
  one inside a string. A line like `url = "http://example.com/#anchor"` became
  `url = "http://example.com/` — an unterminated literal, and the file no longer parsed.
  Comments are now removed by their parse-tree spans.
- **Every method was invisible.** Definitions were read from `root_node.children`, which
  only reaches the top level; methods live inside a class body. The walk now covers the
  whole tree and reports functions and methods separately.
- **The default config could not run on a CPU machine.** `config.yaml` set `device: cuda`
  while the model chose its own device, so the model sat on CPU and the inputs went to
  CUDA. Device is resolved once and shared. The analyzer also forwarded `token_type_ids`
  into a `forward()` that takes only `input_ids` and `attention_mask`.

## Licence

All rights reserved. Published for reading, not for reuse.
