# -*- coding: utf-8 -*-

import os
import json
import subprocess
from collections import defaultdict

SCRIPTS_PATH = "scripts"
CHECK_TYPES = {'py': "python", 'sh': 'bash'}


class CheckCollector(object):
    def __init__(self):
        self.checks_data = defaultdict()
        for root, dirs, files in os.walk(SCRIPTS_PATH):
            self.checks_list = files

        for file in self.checks_list:
            check_name = str(file.split(".")[0])
            check_type = str(file.split(".")[1])
            check_response = subprocess.Popen([CHECK_TYPES[check_type], "{}/{}".format(root, file)],
                                              stdout=subprocess.PIPE).communicate()[0].splitlines()[0].decode('utf-8')
            self.checks_data[check_name] = check_response

    def get_collect_data(self):
        return json.dumps(self.checks_data)


if __name__ == "__main__":
    pass




