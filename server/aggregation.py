import json

from datebase import put_check_data, get_check_properties
from notices.common import Notification


class Host(object):
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self.status = 'OK'
        self.checks_list = []

    def __str__(self):
        return self.host_ip

    def set_status(self):
        for item in self.checks_list:
            if item.status != 'OK':
                self.status = item.status

    def check_status(self):
        self.set_status()
        if self.status != 'OK':
            self.check_dict = {'host' : self.host_ip, 'checks': {}}
            for item in self.checks_list:
                self.check_dict['checks'][item.name] = {'value': item.value, 'status': item.status}
                item.send_to_db()
            self.notification = Notification(self.host_ip, self.status, self.check_dict)


class CheckType(object):
    def __init__(self, name):
        self.name = name
        self.config = None
        if self.name == 'common':
            self.countable = True
        elif self.name == 'daemon':
            self.countable = False
        elif self.name == 'logging':
            self.config = True

    def __str__(self):
        return self.name


class Check(object):
    def __init__(self, name, value, host, timestamp):
        self.name = name
        self.host = host
        self.value = value
        self.timestamp = timestamp

        check_properties = get_check_properties(self.name)
        self.type = CheckType(check_properties['type'])
        if self.type.countable:
            self.crit_limit = int(check_properties['crit'])
            self.warn_limit = int(check_properties['warn'])
            self.value = int(self.value)

            if self.value > self.warn_limit:
                if self.value > self.crit_limit:
                    self.status = 'CRIT'
                else:
                    self.status = 'WARN'
        else:
            try:
                status = int(self.value.split(';')[0])
                print(self.name)
            except ValueError:
                status = None
            if status == 2:
                self.status = 'CRIT'
            elif status == 1:
                self.status = 'WARN'
            elif status == 0:
                self.status = 'OK'
            else:
                self.status = 'CRIT'

    def send_to_db(self):
        put_check_data(self.host, self.name, self.value, self.timestamp)


def make_check(json_data):
    checks_dict = json.loads(json_data)
    checks = checks_dict["checks"]
    host = Host(checks_dict["host"])
    for item in checks:
        check = Check(item, checks[item], host, checks_dict["timestamp"])
        host.checks_list.append(check)
    host.check_status()


if __name__ == "__main__":
    main()