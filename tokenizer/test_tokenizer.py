from tokenizer import tokenize
import pytest

testdata = []
# TODO: design test data
for i in range(10):
    testdata.append((str(i), "")) # tuple (input, output)

@pytest.mark.parametrize("code, tokens", testdata)
def test_tokenizer(code, tokens):
    assert tokenize(code) == tokens

