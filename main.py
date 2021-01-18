# 122520200014 010620210228


# ==============================================================================
# main script
# ------------------------------------------------------------------------------
# get options and arguments from command line
# get backup from files if specified in options
# find all match regex in file, convert them to target regex using convert.py
# ==============================================================================

import re
import convert

from optparse import OptionParser
from os.path import isfile, isdir, splitext, join
from os import walk, getcwd, makedirs
from shutil import copy2
from uuid import uuid1


# feel free to add supported files
SUPPORT_TYPES = ['txt', 'html', 'css', 'js']


# if BACKUP_DIRECTION = None, current directory will be use for get backup
BACKUP_DIRECTION = None


# log file name for using log (it's possible to use this file to restore changes)
LOG_FILE = 'log.txt'


# ==============================================================================
# validate_regex function
# ------------------------------------------------------------------------------
# compile entered regex and check is support?
# ==============================================================================

def validate_regex(reg):
    try:
        re.compile(reg)
        return True
    except:
        return False


# ==============================================================================
# get_file_extension function
# ------------------------------------------------------------------------------
# return extension of given file.
# ==============================================================================

def get_file_extension(file):
    return splitext(file)[1][1:]


# ==============================================================================
# handle_command_errors function
# ------------------------------------------------------------------------------
# handles error(s) in command.
# ==============================================================================

def handle_command_errors(parser, OPTIONS, ARGS):

    # 3 argument need
    if len(ARGS) != 3:
        parser.error("Wrong number of arguments.")

    # is first argument a valid file or directory?
    elif (not isfile(ARGS[0]) and not isdir(ARGS[0])):
        parser.error("Enter a valid file or directory!")
    
    # validate regex: second and third arguments
    elif (not validate_regex(ARGS[1]) or not validate_regex(ARGS[2])):
        parser.error("Enter a valid Regex!")

    # if a directory and type option entered: are all entered types supporte?
    elif (isdir(ARGS[0]) and not set(OPTIONS.TYPE).issubset(set(SUPPORT_TYPES))):
        parser.error(
            f"Not support type! Supported types: {', ' .join(OPTIONS.TYPE)}!")

    # if a file entered: is entered file extension supported?
    elif (isfile(ARGS[0]) and not get_file_extension(ARGS[0]) in SUPPORT_TYPES):
        parser.error(
            f"Not support type! Supported types: {', ' .join(OPTIONS.TYPE)}!")


# ==============================================================================
# commandParser function
# ------------------------------------------------------------------------------
# define and pars command-line options.
# ==============================================================================

def command_parser():

    # -h, --help: show usage
    parser = OptionParser(usage="usage: %prog [options] <filename or directory path> <regex to find> <target regex>",
                          version="%prog 0.0.1")

    # backup option
    parser.add_option("-b", "--backup",
                      action="store_true",
                      dest="BACKUP",
                      default=False,
                      help="Create backup file before changing content of file!")

    # recursive search in directory (only if a diectory itered)
    parser.add_option("-r", "--recursive",
                      action="store_true",
                      dest="RECURSIVE",
                      default=False,
                      help="Search directories recursively (if directory entered).",)

    # specifies which type should change
    parser.add_option("-t", "--type",
                      action="store",
                      dest="TYPE",
                      default="",
                      help="Change file if it is specific type (if directory entered). ex: txt or txt,html",)

    #  specifies files that contain a phrase should change
    parser.add_option("-c", "--contain",
                      action="store",
                      dest="CONTAIN",
                      default="",
                      help="Change file if its name contains specific phrase (if directory entered).",)

    (OPTIONS, ARGS) = parser.parse_args()

    # convert TYPE option to list or set default list
    if (OPTIONS.TYPE):
        OPTIONS.TYPE = OPTIONS.TYPE.split(',')
    else:
        OPTIONS.TYPE = SUPPORT_TYPES

    handle_command_errors(parser, OPTIONS, ARGS)

    return OPTIONS, ARGS


# ==============================================================================
# file_contain function
# ------------------------------------------------------------------------------
# check existance of specific string in file's name.
# ==============================================================================

def file_contain(filename, contain):

    return True if contain.lower() in filename.lower() else False


# ==============================================================================
# create_file_list function
# ------------------------------------------------------------------------------
# create a list of files that should change.
# ==============================================================================

def create_file_list(path, OPTIONS):

    files = []
    if (isfile(path)):
        files.append(path)
    # is direction
    else:
        # append files that theri type
        for (dirpath, dirnames, filenames) in walk(path):
            for filename in filenames:
                #just supported files
                if (get_file_extension(filename) in OPTIONS.TYPE and file_contain(filename, OPTIONS.CONTAIN)):
                    files.append(join(dirpath, filename))
            
            # if recursive == false breaks and does not search in inside directions
            if(not OPTIONS.RECURSIVE):
                break

    return files


# ==============================================================================
# create_files_dic function
# ------------------------------------------------------------------------------
# create a dictionary that its key is primitive file path
# and its value is a uniqe valid name for backup file 
# ==============================================================================

def create_files_dic(files):

    files_dic = {}
    # remove not valid characters for file name
    for file in files:
        file = file.replace('\\', '/')
        files_dic[file] = str(uuid1()) + '_' + file.replace('/', '_').replace(':', '_')

    return files_dic


# ==============================================================================
# create_file_in function
# ------------------------------------------------------------------------------
# create a file in given directory, if not exist.
# ==============================================================================

def create_file_in(file, direcory):
    if (not isdir(direcory)):
        makedirs(direcory)
    
    # in this case there is no need to if condition
    # if ile exist this function will not called
    if (not isfile(f"{direcory}/{file}")):
       file = open(f"{direcory}/{file}", 'w')
       file.close()


# ==============================================================================
# create_log function
# ------------------------------------------------------------------------------
# create a log file. it's possible to use this file to restore changes.
# ==============================================================================

def create_log(files_dic, back_dir):

    # create log file if not exist
    if (not isfile(f"{back_dir}/{LOG_FILE}")):
        create_file_in(LOG_FILE, back_dir)

        with open(f"{back_dir}/{LOG_FILE}", "w") as log:
            log.write("LOG FILE: this file contain information for restoring changes done by script!!!\n")
            log.write("===============================================================================\n")
    
    with open(f"{back_dir}/{LOG_FILE}", "a") as log:
        for key, value in files_dic.items():
            log.write(f"{key}: {value}.bak\n")
        log.write("===============================================================================\n")


# ==============================================================================
# backup function
# ------------------------------------------------------------------------------
# backup files befoe change them in BACKUP_DIRECTION or working directory.
# ==============================================================================

def backup(files):
    if(BACKUP_DIRECTION and isdir(BACKUP_DIRECTION)):
        back_dir = BACKUP_DIRECTION
    else:
        back_dir = f'{getcwd()}/bak'.replace('\\', '/')
    
    # create a dictioanry of files and its backup names (in uniform shape)
    files_dic = create_files_dic(files)
    
    # create log, for restore changes
    create_log(files_dic, back_dir)
    
    for file_pair in files_dic.items():
        copy2(file_pair[0], f'{back_dir}/{file_pair[1]}.bak')


# ==============================================================================
# main function
# ------------------------------------------------------------------------------
# Initialize command-line argument parser, loggers, searchs input files.
# ==============================================================================

def main():

    # parse command
    OPTIONS, ARGS = command_parser()

    # ARGS[0] is file or directory path.
    # Lets create a list of all files that should change
    files = create_file_list(ARGS[0], OPTIONS)

    # if backup need so get a backup from file(s)
    if (OPTIONS.BACKUP):
        backup(files)

    # replace all matched regex to target regex 
    for file in files:
        convert.main(ARGS[1], ARGS[2], file)


# ==============================================================================
# Application code
# ------------------------------------------------------------------------------
# Calls main function.
# ==============================================================================
if __name__ == "__main__":
    main()
