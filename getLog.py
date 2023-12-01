import subprocess
import os
import os.path
from os import path

HOME = "/home/autofz"
OUT = "output"
PATH = os.getcwd()
MAB = "mab" # if log file name is not mab, it must change.
MABPATH = path.join(PATH, MAB)
TARGET = [
    'exiv2',
    'ffmpeg',
    'imginfo',
    'infotocap',
    'lame',
    'mp42aac',
    'mujs',
    'nm',
    'objdump',
    'pdftotext',
    'tcpdump',
    'tiffsplit',
    'freetype2',
    'harfbuzz',
    'libarchive',
    'libjpeg',
    'boringssl',
    # 'openthread-2018-02-27-radio',
    'woff2',
    'wpantund',
    # 'boringssl-2016-02-12',
    'c-ares',
    'guetzli',
    # 'json-2017-02-12',
    'lcms',
    'libpng',
    're2',
    'sqlite',
    # 'vorbis-2017-12-11'
]

# Get docker container name in command "docker ps"
def getContainerName():
    nlist = [] # Name List

    psString = subprocess.check_output("docker ps --format \"{{.Names}}\"", shell=True).decode("utf-8")
    for name in psString.splitlines():
        nlist.append(name)
    return nlist

# Get output directory name in docker container with name entered as a parameter
def getLogPath(containerName, isMAB):

    """ Get home directory's files """
    """ return string list """
    def getHomeFiles(container):
        # Get home directory's files
        homeDirectoryFiles = [] # Home directory List
        lsString = subprocess.check_output("docker exec -ti " 
                                            + container 
                                            + " sh -c \"ls ~\"", shell=True).decode("utf-8")
        for files in lsString.split():
            homeDirectoryFiles.append(files)

        return homeDirectoryFiles

    """ Get output directory's name """
    """ return string list """
    def getOutputDirectoryNames(homeDirectory):
        outputDirectoryNames = []
        if isMAB == False:
            for files in homeDirectory:
                if files.find(OUT) != -1:
                    outputDirectoryNames.append(files)
                else:
                    print("A file \'" + files + "\' is not output directory.")
                continue
        else:
            for files in homeDirectory:
                if files.find(MAB) != -1:
                    outputDirectoryNames.append(files)
                else:
                    print("A file \'" + files + "\' is not mab directory")

        return outputDirectoryNames


    """ Get output directory's log file """
    """ return string """
    def getLogFile(container, outputDirectoryName):
        outputDirectoryFiles = [] # output directory List
        lsString = subprocess.check_output("docker exec -ti " 
                                            + container
                                            + " sh -c \"ls ~/" 
                                            + outputDirectoryName
                                            + "\"", shell=True).decode("utf-8")
        for files in lsString.split():
            outputDirectoryFiles.append(files)

        # Get log file's name
        logFileName = '' # default log file name
        for files in outputDirectoryFiles:
            if files.find('.json') != -1:
                logFileName = files
            else:
                continue
        if logFileName == '':
            print("There is no log file in " + outputDirectoryName + "!")

        return logFileName

    outputDirectories = getOutputDirectoryNames(getHomeFiles(containerName))
    
    logPaths = []
    for directory in outputDirectories:
        logPath = HOME + "/" + directory + "/" + getLogFile(containerName, directory)
        logPaths.append(logPath)

    return logPaths

# It modify a log for making focus_one to autofz_mab
def modifyFocusOneMAB(file):
    temp_line = []
    
    # Modify the line 1
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\"focus_one\": null', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": afl', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": aflfast', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": mopt', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": angora', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": qsym', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": fairfuzz', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": lafintel', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": learnafl', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": libfuzze', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": radamsa', '\"focus_one\": autofz_mab')
            line = line.replace('\"focus_one\": redqueen', '\"focus_one\": autofz_mab')
            temp_line.append(line)
    # Rewrite
    with open(file, 'w') as f:
        f.writelines(temp_line)



def main():
    # Get container name
    containerList = getContainerName()
    
    os.system("mkdir autofz")
    print("========== Get autofz Logs ==========")
    # Get autofz logs
    for containerName in containerList:
        print("In " + containerName)
        logPaths = getLogPath(containerName, False)
        for logPath in logPaths:
            # If there is no log file -> continue
            if logPath.find(".json") == -1:
                continue
            
            # Set a target directory as a target program
            targetDirectory = PATH
            for target in TARGET:
                if logPath.find(target) != -1:
                    if not path.exists(target):
                        inDirectory = path.join(PATH, "autofz")
                        os.makedirs(inDirectory + "/" + target, exist_ok=True)
                    targetDirectory = path.join(PATH, "autofz/" + target)
            
            subprocess.call("docker cp " + containerName + ":" + logPath + " " + targetDirectory, shell=True)
    
    
    print("\n========== Get autofz_mab Logs ==========")
    # Get autofz_mab logs
    os.system("mkdir " + MAB)
    for containerName in containerList:
        print("In " + containerName)

        # Get logPaths which have prefix MAB
        logPaths = getLogPath(containerName, True)

        for logPath in logPaths:
            # If there is no log file -> continue
            if logPath.find(".json") == -1:
                continue

            # Set a target directory as a target program
            targetDirectory = PATH
            for target in TARGET:
                if logPath.find(target) != -1:
                    if not path.exists(target):
                        inDirectory = path.join(PATH, MAB)
                        os.makedirs(inDirectory + "/" + target, exist_ok=True)
                    targetDirectory = path.join(PATH, MAB + "/" + target)
            
            # Copy a log file
            subprocess.call("docker cp " + containerName + ":" + logPath + " " + targetDirectory, shell=True)
    

    # If there are autofz_mab logs, it change focus_one for autofz-draw
    if path.exists(MAB):
        # Get a list of MAB directory
        dirList = os.listdir(MAB)
        for directory in dirList:
            mabLogList = os.listdir(MAB + "/" + directory)
            for log in mabLogList:
                print(MAB + "/" + directory + "/" + log)
                modifyFocusOneMAB("./" + MAB + "/" + directory + "/" + log)

if __name__ == "__main__":
    main()
