from logger import logger

from notices.common import Notification
from database_refactor import connect, get_host_checks, get_checks_properties, put_host_condition


def delete_spaces(str):
    return str.lstrip()


class UnknownHost(Exception):
    pass


class Host(object):
    def __init__(self, host_ip, checks, session):
        self.ip = host_ip
        self.status = None
        self.checks = checks

        for check in self.checks:
            if check.status == 'WARN':
                self.status = 'WARN'
            elif check.status == 'CRIT':
                self.status = 'CRIT'
                break
        try:
            put_host_condition(self.ip, self.checks)
            logger.info("HOST {} PUT HOST CONDITION {}".format(self.ip, session))
        except Exception as e:
            logger.exception("HOST {} error due putting host condition from database".format(self.ip), exc_info=True)

        if self.status == 'CRIT' or self.status == 'WARN':
            Notification(self.ip, self.status, self.checks, session)


class CheckType(object):
    def __init__(self, type_name):
        self.name = type_name
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
    def __init__(self, check_name, check_prop, value):
        self.name = check_name
        self.type = CheckType(check_prop['type'])
        self.status = None
        self.value = value
        if self.type.countable:
            self.warn = int(check_prop['warn_limit'])
            self.crit = int(check_prop['crit_limit'])
            self.value = float(self.value)
            if self.value > self.warn:
                if self.value > self.crit:
                    self.status = 'CRIT'
                else:
                    self.status = 'WARN'
            else:
                self.status = 'OK'

        else:
            try:
                status = int(self.value.split(';')[0])
                self.value = self.value.split(';')[1]
            except ValueError:
                status = None
                log.error('Check {}. Cannot get status because value is {}'.format(self.name, self.value))
            if status == 2:
                self.status = 'CRIT'
            elif status == 1:
                self.status = 'WARN'
            elif status == 0:
                self.status = 'OK'
            else:
                self.status = 'CRIT'


class Aggregation():
    def __init__(self, host, values, session):
        self.db_connect = connect()
        self.host = host
        self.values = values
        host_checks = get_host_checks(self.host)
        if host_checks is not None:
            self.checks = list(map(delete_spaces, get_host_checks(self.host)))
            logger.info('AGGREGATION GET HOSTS CHECK {}'.format(session) + ', '.join(self.checks))
        else:
            logger.error('AGGREGATION NO HOSTS CHECK DATA {}'.format(session))
            raise UnknownHost('AGGREGATION HOST {} IS NOT IN DATABASE {}'.format(self.host, session))
        try:
            self.checks_properties = get_checks_properties(connect, self.checks)
        except Exception as exc:
            logger.error('AGGREGATION CANNOT GET CHECK PROPERTIES {}'.format(session), exc_info=True)

        self.checks_obj = [Check(i, self.checks_properties[i], values[i]) for i in self.checks]
        '''
        !!!OLD!!!
        for item in self.checks:
            check = Check(item, self.checks_properties[item], values[item])
            self.checks_obj.append(check)
        '''
        try:
            Host(self.host, self.checks_obj, session)
        except TypeError as e:
            logger.error('HOST {} TypeError '.format(self.host), exc_info=True)
            exit()


