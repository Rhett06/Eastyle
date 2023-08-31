from itertools import takewhile
from .utils import locate_token, next_nl, get_indent_type

def fixCommentsIndentation (violation: dict, tokens: list, whitespace: list, **kwargs) -> list:
    msg = violation["message"]
    #print(msg)
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
        new_ws = get_indent_type(whitespace) if whitespace[indent_id][2] == "None" else whitespace[indent_id][2]
        #print(new_ws)
        whitespace[indent_id] = (whitespace[indent_id][0],
                                 whitespace[indent_id][1] + indent_diff, new_ws)

        new_ws = get_indent_type(whitespace) if whitespace[next_indent_id][2] == "None" else whitespace[next_indent_id][2]
        #print(new_ws)
        if next_indent_id:
            whitespace[next_indent_id] = (whitespace[next_indent_id][0],
                                          whitespace[next_indent_id][1] - indent_diff, new_ws)

    else:  # TODO: find indent manually
        pass

    return whitespace
