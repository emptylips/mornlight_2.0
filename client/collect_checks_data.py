# -*- coding: utf-8 -*-

import os
import json
import subprocess
import hashlib
import glob
from collections import defaultdict


SCRIPTS_PATH = "scripts"
CHECK_TYPES = {'py': "python", 'sh': 'bash'}


def get_scripts_hash():
    common_data = ''
    for root, dirs, files in os.walk(SCRIPTS_PATH):
        for file in files:
            with open(root + '/' + file, 'rb') as inputfile:
                common_data += str(inputfile.read())

    return hashlib.md5(common_data.encode('utf-8')).hexdigest()



def collect_data():
    checks_data = defaultdict()
    for root, dirs, files in os.walk(SCRIPTS_PATH):
        print(root, dirs, files)
        for file in files:
            print(root, file)
            check_name = str(file.split(".")[0])
            check_type = str(file.split(".")[1])
            if CHECK_TYPES[check_type] == 'bash':
                check_response = subprocess.Popen(["bash", "{}/{}".format(root, file)], stdout=subprocess.PIPE)
            elif CHECK_TYPES[check_type] == 'python':
                check_response = subprocess.Popen(["python", "{}/{}".format(root, file)], stdout=subprocess.PIPE)
            response_data = check_response.communicate()[0].splitlines()[0]
            response_data = response_data.decode('utf-8')
            checks_data[check_name] = response_data
    return json.dumps(checks_data)


def main():
    print(get_scripts_hash())


if __name__ == "__main__":
    main()

