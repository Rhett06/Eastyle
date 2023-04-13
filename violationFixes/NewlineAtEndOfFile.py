def fixNewlineAtEndOfFile(whitespace: list, **kwargs) -> list:
    indent = -sum([i[1] for i in whitespace[:-1] if i[0]>0])
    whitespace[-1] = (1, indent, whitespace[-1][2])
    return whitespace