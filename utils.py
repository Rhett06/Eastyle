import os

def getViolationType(violation: dict) -> str:
    return violation["source"].split(".")[-1][:-5]
