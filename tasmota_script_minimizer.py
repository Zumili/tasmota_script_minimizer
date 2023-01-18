#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# tasmota-script-minimizer minimizes tasmota scripts
"""The tool tasmota-script-minimizer minimizes tasmota scripts.

It does this by replacing variable names with shorter names
and removing spaces where possible.

Example
    Minimize script with aggressivity=1 and write to minimized.txt::

        $ python tasmota_script_minimizer.py testscript.txt -o minimized.txt -a 1

Todo:
    * Find regex for string variable name replacement only before quotation

.. _Tasmota Script Minimizer
   https://github.com/Zumili/tasmota_script_minimizer

"""

__author__ = "Thomas Messmer"
__contact__ = "https://github.com/Zumili/tasmota_script_minimizer"
__copyright__ = "Copyright 2023, TWM"
__credits__ = ["Thomas Messmer"]
__date__ = "2023/01/15"
__license__ = "The MIT License"
__version__ = "0.1.0"
__maintainer__ = "Thomas Messmer"
__status__ = "Development"
__username__ = "Zumili"
__description__ = "The tool tasmota_script_minimizer.py minimizes tasmota scripts"
__example1__ = "$ python tasmota_script_minimizer.py testscript.txt"
__example2__ = "$ python tasmota_script_minimizer.py testscript.txt -o minimized.txt -a 3"


import os
import sys
import re
import itertools
import argparse

# import regex

from datetime import datetime
from string import ascii_lowercase


# A list of system/special variables and function names
# which are already predefined. Will not be used in
# replacement dictionary.
EXCLUDE_LIST = [
    "abs",
    "acos",
    "acp",
    "adc",
    "af",
    "asc",
    "boot",
    "bt",
    "bu",
    "c2ps",
    "cbs",
    "chg",
    "core",
    "cos",
    "day",
    "dvnm",
    "enrg",
    "epoch",
    "epoffs",
    "eres",
    "freq",
    "frnm",
    "ghum",
    "gjp",
    "gprs",
    "gtmp",
    "gtopic",
    "gwr",
    "hd",
    "heap",
    "hf",
    "hn",
    "hours",
    "http",
    "hx",
    "ia",
    "ins",
    "int",
    "ir",
    "is",
    "is1",
    "knx",
    "lip",
    "loglvl",
    "luip",
    "med",
    "micros",
    "millis",
    "mins",
    "month",
    "mpt",
    "mqttc",
    "mqttd",
    "mqtts",
    "npwr",
    "pc",
    "pd",
    "pheap",
    "pin",
    "pl",
    "pn",
    "pow",
    "prefixn",
    "pwmN",
    "pwr",
    "ram",
    "rapp",
    "rec",
    "rnd",
    "rr",
    "s",
    "s2hms",
    "sa",
    "say",
    "sb",
    "sc",
    "secs",
    "sf",
    "sht",
    "sin",
    "sl",
    "slen",
    "slp",
    "sml",
    "smlj",
    "smls",
    "smlv",
    "smw",
    "so",
    "sp",
    "spi",
    "sqrt",
    "sr",
    "sra",
    "srb",
    "st",
    "stack",
    "sunrise",
    "sunset",
    "sw",
    "swa",
    "swb",
    "tbut",
    "time",
    "tinit",
    "topic",
    "tper",
    "tset",
    "tstamp",
    "ttget",
    "upd",
    "upsecs",
    "uptime",
    "wbut",
    "wcf",
    "wcs",
    "wday",
    "wdclk",
    "wfs",
    "wific",
    "wifid",
    "wifis",
    "wm",
    "wtch",
    "year",
    ]

# A list of sections, where a special replacement handling is done.
W_SECTION_LIST = [
    "W",
    "WS",
    "WM"
    ]


def continuous_alphabetic_list(ascii_type=ascii_lowercase):
    """Create iterating variable names starting from a,b,...,aa,ab,..."""
    for size in itertools.count(1):
        for variable_new_name in itertools.product(ascii_type, repeat=size):
            yield "".join(variable_new_name)


def print_info():
    """Print tool information"""
    print("# " + "=" * 78)
    print("Author: " + __author__)
    print("Copyright: " + __copyright__)
    print("Credits: " + ", ".join(__credits__))
    print("License: " + __license__)
    print("Version: " + __version__)
    print("Maintainer: " + __maintainer__)
    # print("Email: " + __email__)
    print("Status: " + __status__)
    print("Date: " + __date__)
    print("Username: " + __username__)
    print("Description: " + __description__)
    print("Example 1:" + __example1__)
    print("Example 2:" + __example2__)
    print("# " + "=" * 78)

def main(argv):
    """It's the main and does all the work"""

    assert sys.version_info >= (3, 0)

    if ("-i" in argv) or ("-info" in argv):
        print_info()
        sys.exit()

    parser = argparse.ArgumentParser(prog = "Tasmota Script Minimizer",
                                     description="Minimizes Tasmota scripts.")
    parser.add_argument("file",
                        help="input file",
                        default="")
    parser.add_argument("-o", "--output",
                        help="output file",
                        default="")
    parser.add_argument("-a", "--aggressivity",
                        help="aggressivity of minimization [0-5]",
                        type=int, default=1)
    parser.add_argument("-d", "--dictprint",
                        help="print dictionary [0-2]",
                        type=int, default=0)
    parser.add_argument("-i", "--info",
                        help="print tool information",
                        default=False, action="store_true")
    args = parser.parse_args()

    var_found_names = []
    file_out = ""
    file_out_size = 0
    actual_section = ""
    var_count = 0
    perm_var_count = 0
    arr_count = 0
    string_count = 0


    # if args.info is True:
        # print_info()

    if args.output == "":
        f_name, f_ext = os.path.splitext(args.file)
        file_out = f_name+"_"+datetime.now().strftime("%Y_%m_%d-%H_%M_%S")+f_ext
    else:
        file_out = args.output

    file_stats = os.stat(args.file)

    # Read whole file, tasmota scripts are not so big
    lines = []

    try:
        reader = open(args.file, "r", encoding="utf-8")
        lines = reader.readlines()
    # except Exception as e:
        # print(e.__class__, "occurred.")
    finally:
        reader.close()

    line_idx = 0
    line = ""

    # Check lines for start of >D section and variable names
    for line_idx, line in enumerate(lines, start=0):
         # Removes leading and trailing spaces in case of e.g.
         # " p:day " or "  ; comment"
         # and check if line still has characters left
        if line.strip():
            if line.startswith(">D"):
                continue
            if line[0]==">"or line[0]=="#":
                break
            if ";" in line and not line[0].isalpha():
                continue
            var = line.split("=")[0].strip()
            val = line.split("=")[1].strip()
            if val:
                if "\"" in val:
                    string_count += 1
            if var:
                if ":" in var:
                    vartype, var = var.split(":")
                    if vartype=="p":
                        perm_var_count += 1
                    elif vartype=="m":
                        arr_count += 1
                var_found_names.append(var)
                var_count += 1
            else:
                print("Variable Error in line:"+str(line_idx)+" >> "+line)
                sys.exit(1)

    # Check rest of lines for sub routines
    for line_idx, line in enumerate(lines, start=line_idx):
        if line.strip():
            if "#" in line and line[0] == "#":
                var = line.split("#")[1].strip()
                if "(" in var:
                    # para = re.search(r"\((.*?)\)",var).group(1)
                    var = var.split("(")[0]
                    # At this point adding the subr para is not neccessary!
                    # para must be a already defined variable
                    # and also multiple para are possible
                    # var_found_names.append(para)

                var_found_names.append(var)


    # Build a name replacement list for all found names
    var_new_names = []
    for variable_new_name in continuous_alphabetic_list():
        if variable_new_name not in EXCLUDE_LIST:
            var_new_names.append(variable_new_name)
        if len(var_new_names) == len(var_found_names):
            break

    #Build a replacement dictionary
    var_repl_dict = dict(zip(var_found_names, var_new_names))

    if args.aggressivity >= 0:
        # remove space before and after special characters
        remove_spaces_pattern = (
            r"\s*(?=[=+\-*/%&|^<>!()\[\]])|"
            r"(?<=[=+\-*/%&|^<>!()\[\]])\s*|"
            r"\s*\n|(?<![a-zA-Z0-9])\s+"
        )
    if args.aggressivity >= 1:
        # remove space after key words
        remove_spaces_pattern = remove_spaces_pattern + (
            r"|(?<=\band\b)\s*|(?<=\bor\b)\s*|"
            r"(?<=\bthen\b)\s*|(?<=\bprint\b)\s*|"
            r"(?<=\bfor\b)\s*|(?<=\bif\b)\s*|"
            r"(?<=\bswitch\b)\s*|(?<=\bcase\b)\s*"
        )
    if args.aggressivity >= 2:
        # remove spaces before key words only if number before space
        remove_spaces_pattern = remove_spaces_pattern + (
            r"|(?<=[0-9])\s*(?=\band\b)|(?<=[0-9])\s*(?=\bor\b)|"
            r"(?<=[0-9])\s*(?=\bthen\b)|(?<=[0-9])\s*(?=\bcase\b)|"
        )


    def replace(match):
        """Returns the new variable name from replacement dict for the found match"""
        key = match.group(0).strip()
        return var_repl_dict[key]

    # Clean the lines and replace variable and sub routine names
    lines_out = []
    for line_idx, line in enumerate(lines, start=0):
        # Check if line contains characters after removing leading and trailing spaces
        if line.strip():
            # Start of section
            if ">" in line and line[0]==">":
                actual_section = line[1]
            # If commented line
            if ";" in line and line[0]==";" and actual_section not in W_SECTION_LIST:
                continue
            # If comment after code
            if ";" in line and actual_section not in W_SECTION_LIST:
                mline = line.split(";")[0].strip()+"\n"
            else:
                mline = line

            # Handling of all sections except W,WS,WM
            if actual_section not in W_SECTION_LIST:
                if (mline.startswith("print") is not True or args.aggressivity > 4):

                    # manual fixing the string issue, NOT as good as regex,
                    # but still no regex fix for
                    # "look-behind requires fixed-width pattern" at this point
                    var,*val= mline.split("\"",1)

                    # check for subroutine names assigned to variables as string, special condition!
                    # if subr in splitted string val we do not handle the line
                    # as a string, so we reassign var to mline and val to None
                    if val and "=#" in val[0]:
                        var = mline
                        val = None
                    mline = re.sub("|".join(r"\b%s\b" % re.escape(s) for s in var_repl_dict), replace, var)
                    if val:
                        mline += "\""+"\"".join(val)

                else:
                    count = 0
                    for element in var_found_names:
                        element_p = element+"%"
                        dictval_p = var_new_names[count]+"%"
                        mline = mline.replace(element_p, dictval_p)
                        count += 1

            # Handling of sections W,WS,WM
            else:
                mline = re.sub("|".join(r"(?<=([^\"]))(?<=([\(%%\d\#]))(%s\b)" % re.escape(s) for s in var_repl_dict), replace, mline)

            # Remove spaces in all sections except W,WS,WM
            if args.aggressivity != 0:
                if actual_section not in W_SECTION_LIST:
                    if (mline.startswith("print") is not True or args.aggressivity > 3):
                        mline = re.sub(remove_spaces_pattern, "", mline, flags = re.MULTILINE)+"\n"

            file_out_size = file_out_size + len(mline) + 1
            lines_out.append(mline)


    try:
        writer = open(file_out, "wt", encoding="utf-8")
        for line_out in lines_out:
            # write each item on a new line
            writer.write("%s" % line_out)
    # except Exception as e:
        # print(e.__class__, "occurred.")
    finally:
        writer.close()

    # file_out_size = file_out_size -1

    reduction_rate = 100 - (100*file_out_size / file_stats.st_size)

    if args.dictprint < 2:
        print("INPUT")
        print("File: "+args.file)
        print("File Size: "+str(file_stats.st_size) +" byte")
        print("Variable Count: "+str(var_count))
        print("String Count: "+str(string_count))
        print("Array Count: "+str(arr_count))
        print("Permanent Variable Count: "+str(perm_var_count))
        print("---------------------------")
        print("OUTPUT")
        print("File: "+file_out)
        print("Minimized Size: "+str(file_out_size)+" byte")
        print("Reduction Rate: %.2f%%" % reduction_rate)

        if file_out_size > 2560:
            print("Warning: Script is longer than 2560 byte!")
        if var_count > 50:
            print("Warning: More than 50 variables used!")
        if perm_var_count > 12:
            print("Warning: More than 12 permanent variables used!")

    if args.dictprint > 0:
        # print(var_repl_dict)
        print("\n".join("{}\t{}".format(v, k) for k, v in var_repl_dict.items()))

    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
