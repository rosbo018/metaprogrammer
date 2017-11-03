#!/usr/bin/python3
###############################################################################
#                               meta programmer                               #
# lisenced under the GPL gentoo penguin lisence      
#
# currently very primative, would like to add more functionality if I can
# think of anything. 
#
#example input file
# you have to use '#variable', '#code' and '#end'
#          #variables
#          ~a = [A...D]
#          ~y = [1...3]
#          ~z = [a...d]
#          ~b = {nice, meme}
#          #end
#          #code
#          for (int i = 0; i < 10; i++){
#          	~a+= ~;
#          	~y;
#          	function~b(~b);
#          	
#          
#          }
#          #end
###############################################################################
# univeral syntax
# _$'xxx' variables eg _$a, _$ABED
#sections determined by #variables and #code
import re
import sys
def sectionLocationParse(rawLines): #gets the location of variable and code blocks
    error = ""
    lineNum = 0
    variableMode = False
    codeMode = False
    variableStart = "nan"
    variableEnd = "nan"
    codeStart = "nan"
    codeEnd = "nan"
    for i in rawLines:
#        print(i)
        if (i == "#variables\n"):
            if (codeMode):
                error = "Incorrect formatting: start of new statement before end"
                break;
            variableMode = True
            variableStart = lineNum
        if (i == "#code\n"):
            if (codeMode):
                error = "Incorrect formatting: start of new statement before end"
                break;
            codeMode = True
            codeStart = lineNum
        if (i == "#end\n" or i == "#end"):
            if(variableMode):
                variableEnd = lineNum
                variableMode = False
            elif(codeMode):
                codeEnd = lineNum
                codeMode = False
            else:
                error = "end of statement before beginning of statement"
        lineNum +=1

    #print(str( variableStart )+ " "+ str( variableEnd )+ " "+ str( codeStart )+ " "+ str( codeEnd )+ " ")
    lst = [variableStart, variableEnd, codeStart, codeEnd]
    return lst

def defineVariables(lines, varStart, varEnd): #gets variable name and ranges, use other
    #function to evaluate ranges
    
    rawVariables = []
    variableNames = []
    variableEval = []
    #print("#######################")
    varStart+=1
    while (varStart < varEnd):
        rawVariables.append(lines[varStart])
        varStart +=1
    #print (rawVariables)
    for i in rawVariables:
        variableNames.append(re.search("\~[a-zA-Z]+", i).group(0))
    for i in rawVariables:
        variableEval.append(re.search("\=.+", i).group(0))
    vars = [ variableNames ,  evaluateRanges( variableEval ) ]
    return vars

# this function delegats to evaluate ranges
# if the input is [A...D], the function will return a list [A, B, C, D]
# if same with a..d=[a, b, c, d], and 1..5 = [1, 2, 3, 4, 5]
# if the input is {"one", "two", "three"}, that will be the range

def evaluateRanges(ranges):
    evaluatedRanges = []
    for range in ranges:
        if "..." in range:
            evaluatedRanges.append(evaluateArithmeticRanges(range))
        elif "{" in range and "}":
            evaluatedRanges.append(evaulatedStaticRanges(range))
    return evaluatedRanges
            
            
###############################################################################
#             creates the arithmetic ranges and returns the range             #
###############################################################################
def evaluateArithmeticRanges(arithString):
    arithString = re.search("\[.+\]", arithString)[0]
    arithString = arithString[1:-1]
    digitRange = not arithString[0].isalpha()
    range = []
        
    if (not digitRange):
        print("alpha\n")
        v = re.search("([a-zA-z][a-zA-z\d]*)\.+([a-zA-z][a-zA-z\d]*)", arithString)
        start = v.group(1)
        end = v.group(2)
        iterCharStart = (start[-1:]) #last character
        iterCharEnd = (end[-1:])
        iterCharStartNum = ord(iterCharStart)
        itercharEndNum = ord(iterCharEnd)
        # adda ... addd = [adda, addb, addc, addd]
        #ad1...ad5 = [ad1, 1d2, ad3, ad4, ad5]
        while (iterCharStartNum <= itercharEndNum):
            range.append(start[:-1] + str( chr(iterCharStartNum) ))
            iterCharStartNum +=1

    if (digitRange):
        print("numeric\n")
        v = re.search("(\d+)\.+(\d+)", arithString)
        start = int( v.group(1) )
        end = int( v.group(2) )
        while(start <= end):
            range.append(str(start))
            start +=1
    return range

def evaulatedStaticRanges (rangeString):
    staticRange = re.search("{.+}", rangeString)[0]
    staticRange = staticRange[1:-1]
    range = re.split("\s*\,\s*", staticRange)
    return range

def getNumIterations(listOfRanges):
    numElems = []
    for i in listOfRanges:
        numElems.append(len(i))
    return min(numElems)
        
def writePermutations(fileInLines, fileOut, varList, numPermutations, codeStart, codeEnd):
     i = 0
     baseFile = ( ''.join( fileInLines[codeStart+1:codeEnd] ) )
     print(baseFile);
     numVars = len(varList[0])
     while(i < numPermutations):
        changeFile = baseFile
        j = 0
        while (j < numVars):
        # j is the variable number
        # i  is the iteration number
            var = (varList[0][j])
            rep = varList[1][j][i]
            changeFile = changeFile.replace(var, rep)#varList[1][j][i]
            j+=1
        print (changeFile)
        fileOut.write(changeFile)
        i+=1
            
        

def main(argv):

    print(len(argv))
    if (len(argv ) <= 1):
        print("use --help to see options")
        return
    if(argv[1] == "--help" or argv[1] == "-h"):
        printHelp()
        return
    input = argv[1]
    output = input+".mout" #incase there isn't an output file specified
    if(len(argv) >= 3):
        output = argv[2]
    fMeta = open(input, "r") #change "test' to variable input"
    fOut = open(output, "a")
    fOut.seek(0)
    fOut.truncate()
    lines = fMeta.readlines();
    loc = sectionLocationParse(lines)
    vars = defineVariables(lines, loc[0], loc[1])
    iterations = getNumIterations(vars[1])
    print(vars)
    print(iterations)
    writePermutations(lines, fOut, vars, iterations, loc[2], loc[3])
    fMeta.close()
    fOut.close()

main(sys.argv)

