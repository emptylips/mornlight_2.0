import yaml

import datetime
import mysql.connector
from mysql.connector import errorcode
from collections import defaultdict

NOW = datetime.datetime.now()

with open("db_connect.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def connect():
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


def get_host_checks(host):
    cnx = connect()
    cursor = cnx.cursor()
    query = ("SELECT * FROM knows_hosts WHERE host = %s;")
    cursor.execute(query, (host,))

    for (host, checks, type) in cursor:
        if len(checks.split(',')) == 0:
            raise HostNotInBase('Host {} not in database'.format(host))
        else:
            return checks.split(',')


def get_checks_properties(connect, checks):
    new_string = ""
    for item in checks:
        new_string += "'"+item.lstrip()+"'"+','
    new_string = new_string.rstrip(',')
    cnx = connect()
    cursor = cnx.cursor()
    query = ("SELECT check_name, type, warn_limit, crit_limit FROM checks WHERE check_name IN ({});".format(new_string))
    cursor.execute(query)
    check_dict = {}
    for (check_name, type, warn_limit, crit_limit) in cursor:
        check_dict[check_name] = {'type': type, 'warn_limit': warn_limit, 'crit_limit':crit_limit}
    return check_dict


def put_host_condition(host, data):
    cnx = connect()
    cursor = cnx.cursor()

    query = ("INSERT INTO checks_data (host, check_name, value, timestamp) VALUES ")

    for check in data:
        query += "('{}', '{}', '{}', '{}'), ".format(host, check.name, check.value, NOW)
    query = query.rstrip(', ') + ';'
    cursor.execute(query)
    cnx.commit()

    cursor.close()
    cnx.close()


def get_host_condition_by_time(host, time=3000):
    cnx = connect()
    cursor = cnx.cursor()
    period = datetime.datetime.fromtimestamp(NOW.timestamp() - time * 60).strftime("%Y-%m-%d %H:%M")
    query = ("SELECT check_name, value, timestamp FROM checks_data WHERE host='{}' and timestamp > '{}';".format(host, period))
    cursor.execute(query)
    host_condition = {host: {}}

    for (check_name, value, timestamp) in cursor:
        if check_name in host_condition[host]:
            host_condition[host][check_name].append({'timestamp': timestamp, 'value': value})
        else:
            host_condition[host][check_name] = [{'timestamp': timestamp, 'value': value}]

    return host_condition


if __name__ == "__main__":
    print(get_host_checks('127.0.011.1'))