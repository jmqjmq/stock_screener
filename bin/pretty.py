#!/usr/bin/python3

import json
import sys

if len(sys.argv) != 2:
    print("Error:  Usage pretty.py filename")
    exit()

filename = sys.argv[1]

fp = open(filename)
data = json.load(fp)

json_str = json.dumps(data, indent=4)
print(json_str)

