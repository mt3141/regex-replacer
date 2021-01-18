# 010620210228


# ==============================================================================
# convert
# ------------------------------------------------------------------------------
# find all match regex in file, convert them to target regex
# ==============================================================================

import re
import in_place


def removeDotCharacters(s):
    return s.replace("[.]", ".")


def replacementPairs(regToFind, regToReplace, line):
    matchRegs = re.findall(regToFind, line)
    
    regToFind = removeDotCharacters(regToFind)
    regToReplace = removeDotCharacters(regToReplace)

    find = re.split("[.][*]", regToFind)
    replace = re.split("[.][*]", regToReplace)

    replacementDic = {}

    for matchReg in matchRegs:
        pos = 0
        value = matchReg
        #  need
        for r in tuple(zip(find, replace)):
            index = value.find(r[0], pos)
            value = value[0:index:] + r[1] + value[index + len(r[0])::]
            pos = index - len(r[0]) + len(r[1])
        replacementDic[matchReg] = value

    return replacementDic


def replaceRegexInLine(line, regToFind, regToReplace):
    replacementDic = replacementPairs(regToFind, regToReplace, line)

    for rep in replacementDic.items():
        line = line.replace(rep[0], rep[1])

    return line


def main(regToFind, regToReplace, file):
    with in_place.InPlace(file) as file:
        for line in file:
            line = replaceRegexInLine(line, regToFind, regToReplace)
            file.write(line)
