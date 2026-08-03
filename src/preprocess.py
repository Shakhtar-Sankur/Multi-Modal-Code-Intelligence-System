"""Parse source code with tree-sitter and pull out its structure.

The parser used to be built from `build/my-languages.so` via the pre-0.22
tree-sitter API. That shared object was never in this repository and there was no
script to produce it, so parsing failed on a fresh clone. The grammar now comes
from the `tree-sitter-python` wheel, which ships the compiled grammar and needs
no build step.
"""
import logging

from tree_sitter import Language, Parser
import tree_sitter_python

logger = logging.getLogger(__name__)

_PARSERS = {}

#: Grammars available without a build step. Add a wheel, add a line.
LANGUAGE_MODULES = {
    'python': tree_sitter_python,
}


def load_parser(language='python'):
    """Return a cached parser for `language`."""
    if language in _PARSERS:
        return _PARSERS[language]

    module = LANGUAGE_MODULES.get(language)
    if module is None:
        raise ValueError(
            f"No grammar registered for {language!r}. "
            f"Available: {', '.join(sorted(LANGUAGE_MODULES))}. "
            f"Install the matching tree-sitter-<language> wheel and add it to "
            f"LANGUAGE_MODULES."
        )

    parser = Parser(Language(module.language()))
    _PARSERS[language] = parser
    return parser


def _walk(node):
    """Yield every node in the tree, not just the top level."""
    yield node
    for child in node.children:
        yield from _walk(child)


def _name_of(node):
    """The identifier a definition node binds, if it has one."""
    for child in node.children:
        if child.type == 'identifier':
            return child.text.decode('utf8')
    return None


def preprocess_code(code, language='python'):
    """Parse `code` and return it alongside the definitions it contains.

    Comments are dropped using the parse tree rather than a regular expression.
    The previous version ran `re.sub(r'#.*?\\n', ...)` over the raw text, which
    also stripped every `#` inside a string literal and could leave the source
    unparseable.

    Definitions are collected by walking the whole tree. Iterating only
    `root_node.children`, as this used to, sees top-level functions but misses
    every method, because methods live inside a class body.
    """
    parser = load_parser(language)
    tree = parser.parse(bytes(code, 'utf8'))

    metadata = {'functions': [], 'classes': [], 'methods': []}
    comment_spans = []

    for node in _walk(tree.root_node):
        if node.type == 'comment':
            comment_spans.append((node.start_byte, node.end_byte))
        elif node.type == 'function_definition':
            name = _name_of(node)
            if name is None:
                continue
            parent = node.parent
            inside_class = False
            while parent is not None:
                if parent.type == 'class_definition':
                    inside_class = True
                    break
                parent = parent.parent
            (metadata['methods'] if inside_class else metadata['functions']).append(name)
        elif node.type == 'class_definition':
            name = _name_of(node)
            if name is not None:
                metadata['classes'].append(name)

    raw = bytes(code, 'utf8')
    for start, end in sorted(comment_spans, reverse=True):
        raw = raw[:start] + raw[end:]
    stripped = raw.decode('utf8')

    logger.info(
        "Preprocessed %d chars: %d functions, %d classes, %d methods",
        len(stripped), len(metadata['functions']),
        len(metadata['classes']), len(metadata['methods']),
    )
    return {'code': stripped, 'metadata': metadata}
