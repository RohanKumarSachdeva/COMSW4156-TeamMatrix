import sqlite3
from sqlite3 import Error

"""
Initializes the Table CIPHER - one time
"""


def init_db(dbname):
    """
    creates a table named CIPHER in the database
    :param dbname: Name of Database
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        conn.execute('CREATE TABLE IF NOT EXISTS CIPHER'
                     '(user_id TEXT, app_name TEXT,' +
                     'password TEXT, key TEXT)')
        conn.commit()
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


def add_record(dbname, record):
    """
    Adds a new record to the database
    :param dbname: Name of Database
    :param record: tuple (user_id, app_name, password, key)
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        insert_q = "INSERT INTO CIPHER (user_id, app_name," \
                   " password, key) VALUES(?, ?, ?, ?)"
        conn.execute(insert_q, record)
        conn.commit()
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


def get_record(dbname, user_id, app_name):
    """
    Returns list of tuples of format: app_name, encrypted_password, key
    for the specified user.
    Returns all passwords if app_name is set to all
    :param dbname: Name of Database
    :param user_id:
    :param app_name: application name or 'all'
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        select_q = "SELECT app_name, password, key" \
                   " FROM CIPHER WHERE user_id = ?"
        args = (user_id, )
        if app_name != 'all':
            select_q += " AND app_name = ?"
            args = (user_id, app_name)
        cur = conn.cursor()

        list_passwords = []
        for record in cur.execute(select_q, args):
            list_passwords.append((record[0], record[1], record[2]))
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()
    return list_passwords


def update_record(dbname, record):
    """
    Updates the password for the specified application
    :param dbname: Name of Database
    :param record: tuple (user_id, app_name, password, key)
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        update_q = "UPDATE CIPHER SET password=?, key=?" \
                   " WHERE user_id=? AND app_name=?"
        args = (record[2], record[3], record[0], record[1])
        cur = conn.cursor()
        cur.execute(update_q, args)
        conn.commit()
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


def delete_record(dbname, user_id, app_name):
    """
    Deletes the password for the provided application.
    :param dbname: Name of Database
    :param user_id:
    :param app_name: application name or 'all'
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        select_q = "DELETE FROM CIPHER WHERE user_id=?"
        args = (user_id, )
        if app_name != 'all':
            select_q += " AND app_name=?"
            args = (user_id, app_name)
        cur = conn.cursor()
        cur.execute(select_q, args)
        conn.commit()
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


def clear(dbname):
    conn = None
    try:
        conn = sqlite3.connect(dbname)
        conn.execute("DROP TABLE CIPHER")
        conn.commit()
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()
