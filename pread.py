#!/usr/bin/python3.9
import pandas as pd
import sys
import getopt
from pprint import pprint
# + + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡

argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "-hf:", ["help","file"])
except getopt.GetoptError as err:
    sys.exit(2)

input_filename = False
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print("-h, --help   this ")
        print("-f, --file   pickle file")
        sys.exit(0)

    if opt in ("-f", "--filer"):
        input_filename = arg
# + + ≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡≡
object = pd.read_pickle(input_filename)

pprint(object, width=1, indent=4, depth=10)


