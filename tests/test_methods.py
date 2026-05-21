from data_anonymizer.core.methods import ANONYMIZED_PLACEHOLDER, AnonymizeMethod, apply_method


def test_redact():
    assert apply_method(AnonymizeMethod.REDACT, "secret") == ANONYMIZED_PLACEHOLDER


def test_mask():
    assert apply_method(AnonymizeMethod.MASK, "555-1234", visible=4) == "****1234"


def test_hash_deterministic():
    a = apply_method(AnonymizeMethod.HASH, "hello", salt="s")
    b = apply_method(AnonymizeMethod.HASH, "hello", salt="s")
    assert a == b
    assert a != apply_method(AnonymizeMethod.HASH, "hello", salt="other")


def test_pseudonym():
    assert apply_method(AnonymizeMethod.PSEUDONYM, "Jane", salt="x").startswith("anon_")


def test_partial():
    assert apply_method(AnonymizeMethod.PARTIAL, "Kendrick Lamar", keep_start=1, keep_end=0) == "K*************"


def test_constant():
    assert apply_method(AnonymizeMethod.CONSTANT, "x", replacement="N/A") == "N/A"


def test_shuffle_token_preserves_word_count():
    out = apply_method(AnonymizeMethod.SHUFFLE_TOKEN, "Stray Kids", salt="s")
    assert len(out.split()) == 2
