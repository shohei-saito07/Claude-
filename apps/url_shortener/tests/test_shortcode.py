import re

from url_shortener.shortcode import generate


def test_generate_returns_string_of_default_length():
    code = generate()
    assert isinstance(code, str)
    assert len(code) == 7


def test_generate_respects_length():
    code = generate(length=10)
    assert len(code) == 10


def test_generate_uses_only_alphanumeric():
    for _ in range(50):
        code = generate()
        assert re.fullmatch(r"[A-Za-z0-9]+", code)


def test_generate_produces_varied_output():
    seen = {generate() for _ in range(100)}
    assert len(seen) > 90  # collisions on 7-char codes are extremely unlikely
