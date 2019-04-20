import yaml

import mysql.connector
from mysql.connector import errorcode

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


def put_check_data(host, check_name, value, timestamp):
    cnx = connect()
    cursor = cnx.cursor()
    query_insert = ("INSERT INTO checks_data (host, check_name, value, timestamp) "
                    "VALUES (%s, %s, %s, %s)")

    data_insert = (str(host), check_name, value, timestamp)
    cursor.execute(query_insert, data_insert)
    cnx.commit()

    cursor.close()
    cnx.close()


def get_check_properties(check_name):
    cnx = connect()
    cursor = cnx.cursor()
    query = ("SELECT check_name, type, warn_limit, crit_limit FROM checks WHERE check_name = %s;")
    cursor.execute(query, (check_name,))

    for (check_name, type, warn_limit, crit_limit) in cursor:
        check_data = {}
        check_data['name'] = check_name
        check_data['type'] = type
        check_data['warn'] = warn_limit
        check_data['crit'] = crit_limit
        return check_data


if __name__ == "__main__":
    pass


