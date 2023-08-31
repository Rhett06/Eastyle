import os
import json
import shutil
import checkstyle
from utils import get_violation_type, load_file, save_file
import tqdm

dataDir = "../data-by-rule-21"
outputDir = "./temp/data-by-rule-21"
is_multiple = True

violationRules = ["CommentsIndentation", "EmptyForIteratorPad", "EmptyLineSeparator", "FileTabCharacter", "GenericWhitespace", "Indentation", 
            "LeftCurly", "LineLength", "MethodParamPad", "NoLineWrap", "NoWhitespaceAfter", "NoWhitespaceBefore", "OneStatementPerLine",
            "OperatorWrap", "ParenPad", 
            "Regexp", "RegexpMultiline", "RegexpSingleline", "RegexpSinglelineJava",
            "RightCurly", "SeparatorWrap",
            "SingleSpaceSeparator", "TrailingComment", "WhitespaceAfter", "WhitespaceAround", "NewlineAtEndOfFile", "AnnotationLocation", 
            "AnnotationOnSameLine", "EmptyForInitializerPad", "TypecastParenPad"]
exclude_set = {"JavadocPackage", "PackageDeclaration"}
fix_rules = violationRules

if is_multiple:
    fix_rules = ["Multiple"]
num_errs = {}
type_count = {}

for rule in fix_rules:
    in_dataset = os.path.join(dataDir, rule)
    out_dataset = os.path.join(outputDir, rule)
    dataset = os.listdir(in_dataset)
    dataset = sorted(dataset)
    for idx in tqdm.tqdm(range(len(dataset))):
        in_dir = os.path.join(in_dataset, dataset[idx])
        out_dir = os.path.join(out_dataset, str(idx))
    # dataset = [(os.path.join(in_dataset, i), os.path.join(out_dataset, i)) for i in dataset]
    # for in_dir, out_dir in tqdm.tqdm(dataset):
        checkstyleFile = os.path.join(in_dir, "checkstyle.xml")
        infoFile = os.path.join(in_dir, "info.json")
        with open(infoFile, "r") as f:
            info = json.load(f)

        checkstyleJar = info["checkstyle_jar"]
        checkstyleJar = os.path.join("jars", checkstyleJar)

        codeFile = os.path.join(out_dir, info["filename"])
        remaining = checkstyle.check(codeFile, checkstyleFile, checkstyleJar)
        # print(remaining, codeFile, checkstyleFile, checkstyleJar)
        remaining = [get_violation_type(i) for i in remaining]
        remaining = [i for i in remaining if i not in exclude_set]

        if len(remaining) not in num_errs:
            num_errs[len(remaining)] = 0
        num_errs[len(remaining)] += 1
        # remaining = {get_violation_type(i) for i in remaining}
        for new_rule in remaining:
            if new_rule not in type_count:
                type_count[new_rule] = 0
            type_count[new_rule] += 1

print(num_errs)
print(type_count)