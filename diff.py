import os
import json
import shutil
import checkstyle
import pickle as pkl
import subprocess
from utils import get_violation_type, load_file, save_file
import tqdm

dataDir = "../Dataset3"
outputDir = "./temp/Dataset3"
save_pkl = "./dataset3_length_exe.pkl"
# result_pkl = "./checkpoint.pkl"
# with open(result_pkl, "rb") as f:
#     _, success_result = pkl.load(f)
# print(success_result)
is_multiple = False

def diff_dp(in_code, out_code):
    in_code = load_file(in_code).split("\n")
    out_code = load_file(out_code).split("\n")
    # inf = len(in_code) + len(out_code) + 1
    dp = [[0 for i in range(len(out_code)+1)] for j in range(len(in_code)+1)]
    dp[0][0] = 0
    for i in range(len(out_code)+1):
        dp[0][i] = i
    for i in range(len(in_code)+1):
        dp[i][0] = i
    for i in range(len(in_code)):
        for j in range(len(out_code)):
            dp[i+1][j+1] = min([dp[i][j]+1, dp[i+1][j]+1, dp[i][j+1]+1])
            if in_code[i] == out_code[j]:
                dp[i+1][j+1] = min(dp[i+1][j+1], dp[i][j])

    return dp[-1][-1]
    # for line in in_code:
    #     for idx in range(len(out_code)-1, 0, -1):
    #         if line == out_code[idx]:
    #             dp[idx] = max(dp[idx], dp[idx-1] + 1)
    #     if line == out_code[0]:
    #         dp[0] = 1
    #     for idx in range(len(out_code)-1):
    #         dp[idx+1] = max(dp[idx], dp[idx+1])
    #
    # return len(in_code) + len(out_code) - max(dp) * 2

violationRules = ["CommentsIndentation", "EmptyForIteratorPad", "EmptyLineSeparator", "GenericWhitespace", "Indentation",
            "LeftCurly", "LineLength", "MethodParamPad", "NoLineWrap", "NoWhitespaceAfter", "NoWhitespaceBefore", "OneStatementPerLine",
            "OperatorWrap", "ParenPad", 
            #"Regexp", "RegexpMultiline", "RegexpSingleline", "RegexpSinglelineJava", "FileTabCharacter",
            "RightCurly", "SeparatorWrap",
            "SingleSpaceSeparator", "TrailingComment", "WhitespaceAfter", "WhitespaceAround", "NewlineAtEndOfFile", "AnnotationLocation", 
            "AnnotationOnSameLine", "EmptyForInitializerPad", "TypecastParenPad"]
exclude_set = {"JavadocPackage", "PackageDeclaration"}
fix_rules = violationRules

if is_multiple:
    fix_rules = ["Multiple"]
num_errs = {}
type_count = {}

size_over3 = {i: 0 for i in violationRules}
fix_size = []
# fix_rules = fix_rules[7:]
for rule in fix_rules:
    # rule = "FileTabCharacter"
    # success_rule = {k for k,v in success_result[rule]}
    in_dataset = os.path.join(dataDir, rule)
    out_dataset = os.path.join(outputDir, rule)
    dataset = os.listdir(in_dataset)
    dataset = sorted(dataset)
    for idx in tqdm.tqdm(range(len(dataset))):
        in_dir = os.path.join(in_dataset, dataset[idx])
        out_dir = os.path.join(out_dataset, dataset[idx])
        # dataset = [(os.path.join(in_dataset, i), os.path.join(out_dataset, i)) for i in dataset]
        # for in_dir, out_dir in tqdm.tqdm(dataset):
        checkstyleFile = os.path.join(in_dir, "checkstyle.xml")
        infoFile = os.path.join(in_dir, "info.json")
        if not os.path.exists(infoFile):
            continue
        with open(infoFile, "r") as f:
            info = json.load(f)

        checkstyleJar = info["checkstyle_jar"]
        checkstyleJar = os.path.join("jars", checkstyleJar)

        input_code = os.path.join(in_dir, info["filename"])
        output_code = os.path.join(out_dir, info["filename"])
        if not (os.path.exists(input_code) and os.path.exists(output_code)):
            continue

        remaining = checkstyle.check(output_code, checkstyleFile, checkstyleJar)
        # print(remaining, codeFile, checkstyleFile, checkstyleJar)
        remaining = [get_violation_type(i) for i in remaining]
        remaining = [i for i in remaining if i not in exclude_set]
        if len(remaining) > 0:
            continue

        # method1
        # cmd = ["git", "diff",  "--numstat", "--minimal", input_code, output_code]
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # diff = process.communicate()[0]
        # diff = diff.decode().split("\t")
        # if diff[0] == '-':
        #     diff[0] = 0
        # if diff[1] == '-':
        #     diff[1] = 0
        # diff1 = int(diff[0]) + int(diff[1])
        #
        #
        # # method 2
        # cmd = ["comm", "-3", input_code, output_code]
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # diff = process.communicate()[0].decode()
        # diff = diff.split("\n")
        # diff2 = len(diff)
        #
        # method 3
        diff = diff_dp(input_code, output_code)
        # #
        # print(diff1, diff2, diff, input_code)
        fix_size.append(diff)
        if diff > 3:
            size_over3[rule]+=1

        # if idx > 100:
        #     break
        # print(dataset[idx], diff)


with open(save_pkl, "wb") as f:
    pkl.dump(fix_size, f)
print(f"total files: {len(fix_size)}, avg fix length: {sum(fix_size) / len(fix_size)}")
print(size_over3)