import argparse
import os
import sys
from bs4 import BeautifulSoup  # parse xml
import json
import javalang
import checkstyle
import tqdm
from typing import Tuple, Union
import copy
import time
import pickle as pkl

from tokenizer.tokenizer import tokenize_file, tokenize_violation, tokenize_with_white_space, de_tokenize, reformat
from utils import get_violation_type, load_file, save_file

from violationFixes import (
    fixNewlineAtEndOfFile, fixNoLineWrap, fixEmptyForIteratorPad, fixLeftCurly,
    fixOneStatementPerLine, fixCommentsIndentation, fixNoWhitespaceAfter,
    fixNoWhitespaceBefore,fixWhitespaceAfter, fixFileTabCharacter, fixGenericWhitespace,
    fixEmptyLineSeparator, fixIndentation, fixLineLength, fixMethodParamPad,
    fixOperatorWrap, fixParenPad, fixRightCurly, fixSeparatorWrap, 
    fixSingleSpaceSeparator, fixTrailingComment, fixWhitespaceAround,
    fixAnnotationLocation, fixTypecastParenPad, fixAnnotationOnSameLine
)

violationRules = {"CommentsIndentation", "EmptyForIteratorPad", "EmptyLineSeparator", "FileTabCharacter", "GenericWhitespace", "Indentation", 
            "LeftCurly", "LineLength", "MethodParamPad", "NoLineWrap", "NoWhitespaceAfter", "NoWhitespaceBefore", "OneStatementPerLine",
            "OperatorWrap", "ParenPad",
                 # "Regexp", "RegexpMultiline", "RegexpSingleline", "RegexpSinglelineJava",
                  "RightCurly", "SeparatorWrap", "SingleSpaceSeparator", "TrailingComment", "WhitespaceAfter", "WhitespaceAround", "NewlineAtEndOfFile", "AnnotationLocation",
            "AnnotationOnSameLine", "EmptyForInitializerPad", "TypecastParenPad"}
tempDir = "temp"


# return a list of fixes
def fix_violations_step(code: str, violations: list, checkstyleData: BeautifulSoup) -> str:
    codeLines = code.split("\n")
    whitespace, tokens, whitespace_str = tokenize_with_white_space(code)
    violating_whitespace = copy.deepcopy(whitespace)
    # for i in range(30):
    #    print(tokens[i].value, len(tokens[i].value), whitespace[i], f"*{whitespace_str[i]}*")
    for violation in violations:
        # print(violation)
        # print(type(tokens[0]))
        violation_type = get_violation_type(violation)
        args = {"violation": violation, "tokens": tokens, "whitespace": whitespace, "checkstyleData": checkstyleData}
        if violation_type not in violationRules:
            continue
        whitespace = globals()["fix"+violation_type](**args)
    # print(type(violation))
    # print(whitespace)

    # code = de_tokenize(code, whitespace)
    code = reformat(whitespace, violating_whitespace, tokens, whitespace_str)
    # print(whitespace)
    # print(code)
    return code


def fix_violations(code: str, violations: list, checkstyleData: BeautifulSoup, steps: int = 3,
                   tempCodeFile = None, checkstyleJar: str = None, checkstyleConfigFile: str=None) -> Tuple[Union[str, None], list]:
    # TODO: expose an interface to users
    if not tempCodeFile:
        tempCodeFile = os.path.join(tempDir, info["filename"])  # TODO: generate an output path
    discarded = []
    pos = 0
    try:
        for iter in range(steps):
            # print(steps, len(violations), pos)
            if pos >= len(violations):
                break
            violation = violations[pos]
            fixed = fix_violations_step(code, violations[pos:pos+1], checkstyleData)
            with open(tempCodeFile, "w") as f:
                f.write(fixed)
            save_file(fixed, tempCodeFile)
            remaining = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
            # print(newViolations)
            # remaining = [i for i in newViolations if get_violation_type(i) == rule]

            if violation in remaining:
                discarded.append(violation)
                pos += 1
            else:
                code = fixed
                violations = remaining
        
        return code, remaining
    except Exception:
        return None, []

# def fix_violations2(code: str, violations: list, checkstyleData: BeautifulSoup, steps: int = 3) -> Tuple[Union[str, None], list]:
#     tempCodeFile = os.path.join(tempDir, info["filename"]) # TODO: generate an output path
#     with open(tempCodeFile, "w") as f:
#         f.write(code)
#     remaining = checkstyle.check(tempCodeFile, checkstyleConfigFile, checkstyleJar)
#     return code, remaining

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', help='the dataset directory')
    parser.add_argument('--rule', help='the tested rule')
    parser.add_argument('--checkpoint', help='checkpoint file')
    args = parser.parse_args()
    dataPath = args.data
    dataset_name = os.path.basename(os.path.normpath(dataPath))
    fixing_rules = list(violationRules)
    if args.rule is not None:
        fixing_rules = [args.rule]
    fixing_rules = sorted(fixing_rules)

    result = {}

    if args.checkpoint and os.path.exists(args.checkpoint):
        result_file = open("./result.txt", "w+")
        with open(args.checkpoint, "rb") as f:
            result, fix_time = pkl.load(f)
    else:
        # args.checkpoint = "checkpoint.pkl"
        result_file = open("./result.txt", "w")
        fix_time = {}
        for rule in fixing_rules:
            result[rule] = {"success": 0, "same": 0, "new": 0, "same+new": 0, "error": 0, "total": 0}
            fix_time[rule] = []


    for rule in fixing_rules:
        print(f"running with rule {rule}...")
        rulePath = os.path.join(dataPath, rule)
        dataset = os.listdir(rulePath)
        dataset = sorted(dataset)
        # import random
        # random.shuffle(dataset)
        # dataset = dataset[:1]
        # print(dataset)
        # dataset = ["../data-by-rule/FileTabCharacter/218"]  # 174 173  142 80 74 143

        start_id = result[rule]["total"]
        for idx in tqdm.tqdm(range(start_id, len(dataset))):
            data = os.path.join(rulePath, dataset[idx])
            checkstyleConfigFile = os.path.join(data, "checkstyle.xml")
            infoFile = os.path.join(data, "info.json")
            violationFile = os.path.join(data, "violations.json")
            if not os.path.exists(checkstyleConfigFile):
                result[rule]["total"] += 1
                continue
            
            with open(checkstyleConfigFile, "r") as f:
                checkstyleData = f.read()
                checkstyleData = BeautifulSoup(checkstyleData, "xml")  # xml -> java
            try:
                with open(violationFile, "r") as f:
                    violations = json.load(f)
            except Exception:
                continue
            with open(infoFile, "r") as f:
                info = json.load(f)

            codeFile = os.path.join(data, info["filename"])

            output_dir = os.path.join(tempDir, dataset_name, rule, dataset[idx])
            os.makedirs(output_dir, exist_ok=True)
            output_dir = os.path.join(output_dir, info["filename"])

            code = load_file(codeFile)
            if code is None:
                print("error on input file: ", data, file=sys.stderr)
                result[rule]["error"] += 1
                continue

            checkstyleJar = info["checkstyle_jar"]
            # print(checkstyleJar)
            checkstyleJar = os.path.join("jars", checkstyleJar)
            init_code = code
            init_violations = violations

            start_time = time.time()
            new_code, remaining = fix_violations(code, violations, checkstyleData, 10 * len(violations), output_dir,
                                                checkstyleJar=checkstyleJar, checkstyleConfigFile=checkstyleConfigFile)
            end_time = time.time()

            # print(remaining)
            exclude_set = {"JavadocPackage", "PackageDeclaration"}
            remaining = [i for i in remaining if get_violation_type(i) not in exclude_set]
            # print(remaining)
            
            remaining_same = len([i for i in remaining if get_violation_type(i) == rule])
            remaining_new = len([i for i in remaining if get_violation_type(i) != rule])
            if any([get_violation_type(i) == "Checker" for i in remaining]):
                print("result code cannot compile for datapoint: ", data, file=sys.stderr)
                result[rule]["error"] += 1
            elif new_code is None or remaining is None:
                print("error on data point: ", data, file=sys.stderr)
                result[rule]["error"] += 1
            elif len(remaining) == 0:
                fix_time[rule].append((idx, end_time - start_time))
                result[rule]["success"] += 1
            else:
                print(data, [get_violation_type(i) for i in remaining], file=sys.stderr)
                # print(remaining)
                if remaining_same > 0 and remaining_new > 0:
                    result[rule]["same+new"] += 1
                elif remaining_same > 0:
                    result[rule]["same"] += 1
                elif remaining_new > 0:
                    result[rule]["new"] += 1

            result[rule]["total"] += 1

            if args.checkpoint and idx % 100 == 99:
                with open(args.checkpoint, "wb") as f:
                    pkl.dump([result, fix_time], f)

                t = [j for i, j in fix_time[rule]]
                if len(t) > 0:
                    print(f"saved {idx}, ", result[rule], min(t), max(t), sum(t) / len(t))

        if args.checkpoint:
            with open(args.checkpoint, "wb") as f:
                pkl.dump([result, fix_time], f)
        print(rule, result[rule], file=result_file)
        t = [j for i,j in fix_time[rule]]
        if len(t) > 0:
            print(min(t), max(t), sum(t)/len(t))
    print(result)
