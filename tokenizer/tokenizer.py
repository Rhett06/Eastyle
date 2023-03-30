
from typing import Tuple
from .token_utils import get_line_indent,get_token_value,get_space_value
from javalang import tokenizer as javalang_tokenizer

def getViolationType(violation: dict) -> str:
    return violation["source"].split(".")[-1][:-5]


def tokenize_with_white_space(code: str) -> Tuple[list, list]:
    """
    Tokenize the java source code
    :param file_content: the java source code
    :return: (whitespace, tokens)
    """
    indentation_last_line = 1
    file_content_lines = code.split('\n')
    javalang_tokens = javalang_tokenizer.tokenize(code, parse_comments=True)
    tokens = []
    count = 0
    try:
        for t in javalang_tokens:
            count += 1
            if count > 1000000:
                break
            tokens.append(t)
            pass
    except Exception as err:
        print('Something wrong happened while tokenizing the following content: ' + code)
        return None, None
    whitespace = list()
    for index in range(0, len(tokens)-1):
        tokens_position = tokens[index].position
        next_token_position = tokens[index+1].position
        end_of_token = (tokens_position[0], tokens_position[1] + len(tokens[index].value))
        if end_of_token == next_token_position:
            whitespace.append((0,0,'None'))
        else:
            if end_of_token[0] == next_token_position[0]:
                # same line
                if file_content_lines[tokens_position[0]-1] is not '':
                    if len(file_content_lines[tokens_position[0]-1]) > end_of_token[1] and file_content_lines[tokens_position[0]-1][end_of_token[1]] == '\t':
                        space_type = 'TB'
                    else:
                        space_type = 'SP'
                else:
                    space_type = 'None'
                whitespace.append(( 0, next_token_position[1] - end_of_token[1], space_type))
            else:
                # new line
                new_line = file_content_lines[next_token_position[0]-1]
                if new_line is not '':
                    if new_line[get_line_indent(new_line) - 1] == '\t':
                        space_type = 'TB'
                    else:
                        space_type = 'SP'
                else:
                    space_type = 'None'
                if True: # relative
                    spaces = next_token_position[1] - indentation_last_line
                    whitespace.append((next_token_position[0] - end_of_token[0] - tokens[index].value.count('\n'), spaces, space_type))
                    indentation_last_line = next_token_position[1]
                else:
                    whitespace.append((next_token_position[0] - end_of_token[0] - tokens[index].value.count('\n'), next_token_position[1] - 1, space_type))
    
    count_line_break = 0
    for index in range(len(code)-1, 0, -1):
        if code[index] == '\n':
            count_line_break += 1
        elif code[index] != ' ' and code[index] != '\t':
            break

    whitespace.append((count_line_break, 0, 'None'))

    return whitespace, tokens




def tokenize_violation(code: str, violation: dict) -> Tuple[list, dict]:
    spaces, tokens = tokenize_with_white_space(code)
    violation["type"] = getViolationType(violation)

    info = {}

    n_lines = 6

    token_started = False
    token_line_start = -1
    token_line_end = -1
    count = 0

    tokens_violating = []

    context_beginning_token = len(tokens)
    context_end_token = 0

    violation_beginning_token = 0
    violation_end_token = 0

    for token, space in zip(tokens, spaces):
        if token.position[0] >= int(violation['line']) - n_lines and token.position[0] <= int(violation['line']) + n_lines:
            context_beginning_token = min(count, context_beginning_token)
            context_end_token = max(count, context_end_token)
        if not token_started and int(violation['line']) == token.position[0]:
            token_started = True
            token_line_start = count
        if token_started and int(violation['line']) < token.position[0]:
            token_started = False
            token_line_end = count
        count += 1
    context_beginning_token = max(0, context_beginning_token - 1)
    context_end_token = min(len(tokens), context_end_token + 1)
    if token_line_end == -1:
        token_line_end = token_line_start

    # print(violation)

    violating_token_index = -1
    if 'column' in violation:
        around = 1
        column = int(violation['column'])

        if column <= tokens[token_line_start].position[1]:
            violating_token_index = token_line_start
        elif column >= tokens[token_line_end - 1].position[1]:
            violating_token_index = token_line_end - 1
        else:
            index = token_line_start
            for token in tokens[token_line_start:token_line_end]:
                if token.position[1] <= column:
                    violating_token_index = index
                index += 1

        violation_beginning_token = max(0, violating_token_index - around)
        violation_end_token = min(len(tokens), violating_token_index + around)
    else:
        around = 1
        around_after = 1
        if token_line_start != -1:
            violation_beginning_token = max(context_beginning_token, token_line_start - around)
            violation_end_token = min(context_end_token, token_line_end + around_after)
        else:
            for token, index in zip(tokens,range(len(tokens))):
                if token.position[0] < int(violation['line']):
                    violating_token_index = index
            violation_beginning_token = max(0, violating_token_index - around)
            violation_end_token = min(len(tokens), violating_token_index + around_after)
    

    tokens_violating_in_tag = []
    for token, space in zip(tokens[violation_beginning_token:violation_end_token], spaces[violation_beginning_token:violation_end_token]):
        tokens_violating_in_tag.append(get_token_value(token))
        tokens_violating_in_tag.append(get_space_value(space))


    for token, space in zip(tokens[context_beginning_token:violation_beginning_token], spaces[context_beginning_token:violation_beginning_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))
    tokens_violating.append(f'<{violation["type"]}>')
    for token, space in zip(tokens[violation_beginning_token:violation_end_token], spaces[violation_beginning_token:violation_end_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))
    tokens_violating.append(f'</{violation["type"]}>')
    for token, space in zip(tokens[violation_end_token:context_end_token], spaces[violation_end_token:context_end_token]):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))


    info['violation_beginning_token'] = violation_beginning_token
    info['violation_end_token'] = violation_end_token
    info['context_beginning_token'] = context_beginning_token
    info['context_end_token'] = context_end_token
    info['violation'] = violation
    info['tokens_violating_in_tag'] = tokens_violating_in_tag

    return tokens_violating, info




# TODO: tokenize
def tokenize_file(code: str) -> list:
    spaces, tokens = tokenize_with_white_space(code)

    tokens_violating = []


    for token, space in zip(tokens, spaces):
        tokens_violating.append(get_token_value(token))
        tokens_violating.append(get_space_value(space))


    return tokens_violating

