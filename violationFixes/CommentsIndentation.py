from itertools import takewhile
from .utils import locate_token, next_nl

def fixCommentsIndentation (violation: dict, tokens: list, whitespace: list, **kwargs) -> list:
    msg = violation["message"]
    line = int(violation["line"])
    comment_id = locate_token(tokens, line)

    indent_prefix = "incorrect indentation level "
    new_indent_prefix = "expected is "
    pos_indent = msg.find(indent_prefix)
    pos_new_indent = msg.find(new_indent_prefix)
    indent_id = comment_id - 1
    next_indent_id = next_nl(whitespace, indent_id + 1)

    def next_int(s: str) -> int:
        return int(''.join(takewhile(str.isdigit, s)))

    if pos_indent >= 0 and pos_new_indent >= 0:  # find correct indent from checkstyle message
        pos_indent += len(indent_prefix)
        pos_new_indent += len(new_indent_prefix)
        indent = next_int(msg[pos_indent:])
        new_indent = next_int(msg[pos_new_indent:])
        indent_diff = new_indent - indent
        whitespace[indent_id] = (whitespace[indent_id][0],
                                 whitespace[indent_id][1] + indent_diff, whitespace[indent_id][2])
        if next_indent_id:
            whitespace[next_indent_id] = (whitespace[next_indent_id][0],
                                          whitespace[next_indent_id][1] - indent_diff, whitespace[next_indent_id][2])

    else:  # TODO: find indent manually
        pass

    return whitespace
