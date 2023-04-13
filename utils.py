import os


def get_violation_type(violation: dict) -> str:
    return violation["source"].split(".")[-1][:-5]
