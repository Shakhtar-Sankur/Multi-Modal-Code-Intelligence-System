"""Parsing: the part that has a right answer.

Both defects the README records are pinned here — a regex comment stripper that
ate `#` inside strings, and definition collection that only looked at top-level
children and so missed every method — plus the ordinary cases either one would
have to get right.
"""

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from src.preprocess import load_parser, preprocess_code


SAMPLE = '''
# a leading comment
import os


def top_level(a, b):
    """A docstring is not a comment."""
    return a + b  # trailing comment


class Thing:
    def method_one(self):
        return "#not-a-comment"

    def method_two(self):
        url = "http://example.com/#anchor"
        return url


def another():
    pass
'''


@pytest.fixture(scope="module")
def result():
    return preprocess_code(SAMPLE)


def test_functions_and_methods_are_told_apart(result):
    assert set(result["metadata"]["functions"]) == {"top_level", "another"}
    assert set(result["metadata"]["methods"]) == {"method_one", "method_two"}, \
        "methods live inside a class body; walking only the top level misses them"
    assert result["metadata"]["classes"] == ["Thing"]


def test_comments_are_removed(result):
    assert "a leading comment" not in result["code"]
    assert "trailing comment" not in result["code"]


def test_a_hash_inside_a_string_survives(result):
    """The regex version stripped from `#` to end of line, strings included."""
    assert '"#not-a-comment"' in result["code"]
    assert "http://example.com/#anchor" in result["code"]


def test_the_stripped_code_still_parses(result):
    """Whatever comes out must still be valid Python."""
    compile(result["code"], "<stripped>", "exec")


def test_a_docstring_is_not_treated_as_a_comment(result):
    assert "A docstring is not a comment." in result["code"]


def test_nested_definitions_are_found():
    code = """
def outer():
    def inner():
        return 1
    return inner


class A:
    class B:
        def deep(self):
            return 2
"""
    meta = preprocess_code(code)["metadata"]
    assert "outer" in meta["functions"]
    assert "inner" in meta["functions"], "a function nested in a function is still a function"
    assert set(meta["classes"]) == {"A", "B"}
    assert "deep" in meta["methods"]


def test_empty_and_comment_only_input():
    assert preprocess_code("")["metadata"]["functions"] == []
    only_comments = preprocess_code("# one\n# two\n")
    assert only_comments["code"].strip() == ""


def test_syntactically_broken_code_does_not_raise():
    """tree-sitter is error-tolerant; the caller should not have to guard."""
    out = preprocess_code("def broken(:\n    pass\n")
    assert isinstance(out["code"], str)


def test_the_parser_is_cached():
    assert load_parser("python") is load_parser("python")


def test_an_unknown_language_says_what_to_do():
    with pytest.raises(ValueError) as exc:
        preprocess_code("int main(){}", language="c")
    message = str(exc.value)
    assert "c" in message and "python" in message
    assert "tree-sitter-" in message, "the error should name the fix"
