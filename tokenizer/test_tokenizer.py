from .tokenizer import tokenize_file, tokenize_violation
import pytest
import json
import os

with open(os.path.join(os.path.dirname(__file__), "./test.json")) as f:
    testDataset = json.load(f)


@pytest.mark.parametrize("data", testDataset)
def test_tokenizer(data):
    code = data["code"]
    violation = data["violation"]
    tokens = data["tokens"]
    info = data["info"]
    if violation is None: # global
        assert tokenize_file(code) == tokens
    else: # select a violation content
        tokensGenerated, infoGenerated = tokenize_violation(code, violation)
        assert tokens == tokensGenerated
        # infoGenerated = {}
        assert "violation_beginning_token" in infoGenerated
        assert "violation_end_token" in infoGenerated
        assert "context_beginning_token" in infoGenerated
        assert "context_end_token" in infoGenerated
