import sqlite3
import hashlib
import subprocess
import logging
import sys
import os
import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import BASE_FUNC
import requests
import json
from requests.auth import HTTPBasicAuth
import argparse
import re

BASE_FUNC.LOGGER_INIT("INFO", "./user_management.log", print_log_init = False,shell_output= True)

class NagvisUser():
    def __init__(self):
        self.data = {}
        self.sqlite3_file = "/usr/share/nagvis/etc/auth.db"
        # self.php_file = "/opt/SVTECH-Junos-Automation/module_utils/user_management/generate_sha1_hash.php"
        self.salt_string = "29d58ead6a65f5c00342ae03cdc6d26565e20954"

    def connection(self):
        try:
            conn = sqlite3.connect(self.sqlite3_file)
            return conn
        except Exception as e:
            logging.exception(e)
            sys.exit()

    def generate_hash_via_php(self,
                              password="",
                              salt_string=""):
        try:
            # proc = subprocess.Popen("sudo php {} {} {}".format(php_file, password, salt_string), shell=True, stdout=subprocess.PIPE)
            # hash_string = proc.stdout.read().decode()
            string = salt_string + password
            hash_string = hashlib.sha1(string.encode())
            return hash_string.hexdigest()

        except Exception as e:
            logging.exception(e)
            sys.exit()

    def set_user2roles(self, conn, username, role):
        try:
            userId = ""
            roleId = ""
            get_userId = conn.execute("SELECT userId FROM users where name='{}';".format(username)).fetchall()
            if get_userId != []:
                userId = get_userId[0][0]

            get_roleId = conn.execute("SELECT roleId FROM roles where name='{}';".format(role)).fetchall()
            if get_roleId != []:
                roleId = get_roleId[0][0]

            conn.execute("INSERT INTO users2roles(userId, roleId) VALUES ({},{})".format(userId, roleId))
            conn.commit()
            logging.info("Set Permission for Nagvis user: <{}> successfully !".format(username))

        except Exception as e:
            logging.info("Fail to Set Permission for Nagvis user: <{}> !".format(username))
            logging.exception(e)
            sys.exit()

    def add_user(self, username, password, role):
        """ Add user """
        try:
            conn = self.connection()
            check_user_exist = conn.execute("SELECT name FROM users where name='{}';".format(username)).fetchall()

            if check_user_exist != []:
                logging.error("Fail to Create Nagvis User <{}>. User already exist !".format(username))
                conn.close()
                sys.exit()
            else:
                hash_string = self.generate_hash_via_php(password = password,
                                                        salt_string = self.salt_string)

                conn.execute("INSERT INTO users(name, password) VALUES ('{}','{}')".format(username, hash_string))
                conn.commit()
                logging.info("Create Nagvis user: <{}> successfully !".format(username))

                if role == "User":
                    self.set_user2roles(conn, username, "Managers")
                elif role == "Admin":
                    self.set_user2roles(conn, username, "Administrators")

                conn.close()
        except Exception as e:
            logging.exception(e)
            sys.exit()

    def delete_user(self, username):
        """ Delete user """
        try:
            conn = self.connection()
            check_user_exist = conn.execute("SELECT name FROM users where name='{}';".format(username)).fetchall()

            if check_user_exist == []:
                logging.error("Fail to Delete User <{}>. User is not exists !".format(username))
                conn.close()
                # sys.exit()
            else:
                userId = ""
                get_userId = conn.execute("SELECT userId FROM users where name='{}';".format(username)).fetchall()
                if get_userId != []:
                    userId = get_userId[0][0]

                conn.execute("DELETE FROM users WHERE name='{}'".format(username))
                conn.execute("DELETE FROM users2roles WHERE userId={}".format(userId))

                conn.commit()
                conn.close()
                logging.info("Delete Nagvis user: <{}> successfully !".format(username))
        except Exception as e:
            logging.exception(e)
            # sys.exit()


    def change_password(self, username, new_password):
        """ Change Password """
        try:
            conn = self.connection()
            check_user_exist = conn.execute("SELECT name FROM users where name='{}';".format(username)).fetchall()

            if check_user_exist == []:
                logging.error("Fail to Change Password Nagvis User <{}>. User is not exists !".format(username))
                conn.close()
                sys.exit()
            else:
                hash_string = self.generate_hash_via_php(password = new_password,
                                                        salt_string = self.salt_string)
                conn.execute("UPDATE users SET password='{}' WHERE name='{}'".format(hash_string, username))
                conn.commit()
                conn.close()
                logging.info("Change Password Nagvis user: <{}> successfully !".format(username))
        except Exception as e:
            logging.exception(e)
            sys.exit()



class GrafanaUser(object):
    def __init__(self, admin_user, admin_password):
        self.ip = "localhost"
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.pre_url    = 'http://{}'.format(self.ip)
        self.headers    = {"Content-Type":"application/json"}
        self.auth       = HTTPBasicAuth(self.admin_user, self.admin_password)


    def getUserInfo(self, username):
        """ Get user """
        path = "/grafana/api/users/lookup"
        params = { "loginOrEmail": username }
        url = "{}{}".format(self.pre_url, path)
        response = requests.get(url,
                                    headers = self.headers,
                                    auth = self.auth,
                                    params = params)
        result = json.loads(response.text)
        return result

    def set_permission(self, username, role):

        try:
            userInfo = self.getUserInfo(username)
            if 'id' not in userInfo:
                logging.error("Fail to Set Permission for Grafana user: <{}>. User is not exists !".format(username))
                # sys.exit()
            else:
                userID = userInfo["id"]
                path = "/grafana/api/org/users/{}".format(str(userID))
                url = "{}{}".format(self.pre_url, path)
                if role == "User":
                    data = '{"role": "Viewer"}'
                elif role == "Admin":
                    data = '{"role": "Admin"}'

                set_permission_user = requests.patch(url,
                                            headers = self.headers,
                                            auth = self.auth,
                                            data = data)
                result = json.loads(set_permission_user.text)
                if set_permission_user.status_code == 200:
                    logging.info("Set Permission for Grafana user: <{}> successfully !".format(username))
                else:
                    logging.error("Fail to Set Permission for Grafana user: <{}> !".format(username))

        except Exception as e:
            logging.exception(e)
            # sys.exit()

    def add_user(self, username, password, role):
        """ Add user """

        try:
            path = "/grafana/api/admin/users"
            data = {
                        "name": "User",
                        "email": "{}@local".format(username),
                        "login": username,
                        "password": password,
                    }

            url = "{}{}".format(self.pre_url, path)
            create_user = requests.post(url,
                                        headers = self.headers,
                                        auth = self.auth,
                                        json = data)
            result = json.loads(create_user.text)
            if create_user.status_code == 200:
                logging.info("Create Grafana user: <{}> successfully !".format(username))
            elif create_user.status_code == 500:
                logging.error("Fail to create Grafana user: <{}>. User already exists !".format(username))
                sys.exit()

            self.set_permission(username, role)

        except Exception as e:
            logging.exception(e)
            sys.exit()


    def delete_user(self, username):
        """ Delete user """

        try:
            userInfo = self.getUserInfo(username)
            if 'id' not in userInfo:
                logging.error("Fail to Delete Grafana user: <{}>. User is not exists !".format(username))
                # sys.exit()
            else:
                userID = userInfo["id"]
                path = "/grafana/api/admin/users/{}".format(str(userID))
                url = "{}{}".format(self.pre_url, path)
                delete_user = requests.delete(url,
                                            headers = self.headers,
                                            auth = self.auth)
                result = json.loads(delete_user.text)
                if delete_user.status_code == 200:
                    logging.info("Delete Grafana user: <{}> successfully !".format(username))

        except Exception as e:
            logging.exception(e)
            # sys.exit()

    def change_password(self, username, new_password):
        """ Change Password """

        try:
            userInfo = self.getUserInfo(username)
            if 'id' not in userInfo:
                logging.error("Fail to Change Password Grafana user: <{}>. User is not exists !".format(username))
                sys.exit()
            else:
                userID = userInfo["id"]
                path = "/grafana/api/admin/users/{}/password".format(str(userID))
                data = {"password": new_password}
                url = "{}{}".format(self.pre_url, path)
                update_user = requests.put(url,
                                            headers = self.headers,
                                            auth = self.auth,
                                            json = data)
                result = json.loads(update_user.text)
                if update_user.status_code == 200:
                    logging.info("Change Password Grafana user: <{}> successfully !".format(username))

        except Exception as e:
            logging.exception(e)
            sys.exit()


class RundeckUser():
    def __init__(self):
        self.config_file = "/etc/rundeck/realm.properties"
        self.admin_acl_file = "/etc/rundeck/admin.aclpolicy"

    def getListUser(self):
        list_user = []
        with open(self.config_file, "r") as file:
            readlines = file.readlines()
            for line in readlines:
                if ":" in line:
                    split_line = line.split(",")
                    user_and_pass = split_line[0]
                    user = user_and_pass.split(":")[0]
                    list_user.append(user)
        return list_user

    def set_admin_permission(self, username):
        try:
            list_username = []
            with open(self.admin_acl_file, 'r') as admin_acl_file:
                read_file = admin_acl_file.readlines()

                for line in read_file:
                    if "username" in line:
                        regex_username = re.findall(r"\[(.*)\]", line.replace(" ", ""))
                        if regex_username[0] != "":
                            list_username = regex_username[0].split(",")
                            break

            list_username.append(username)
            new_list_username_string = str(list_username).replace("'", "").replace("\"", "")

            with open(self.admin_acl_file, 'w') as write_admin_acl_file:
                for line in read_file:
                    if "username" in line:
                        string = "{}{}\n".format("  username: ", new_list_username_string)
                        write_admin_acl_file.write(string)
                    else:
                        write_admin_acl_file.write(line)

            logging.info("Set Admin Permission for Rundeck user: <{}> successfully !".format(username))

        except Exception as e:
            logging.error("Fail to Set Permission for Rundeck user: <{}> !".format(username))
            logging.exception(e)
            sys.exit()

    def add_user(self, username, password, role):
        """ Add user """
        try:
            list_user = self.getListUser()
            if username in list_user:
                logging.error("Fail to create Rundeck user: <{}>. User already exists !".format(username))
                sys.exit()
            else:
                with open(self.config_file, "a+") as file:
                    file.write("{}:{}\n".format(username, password))
                    logging.info("Create Rundeck user: <{}> successfully !".format(username))

            if role == "Admin":
                self.set_admin_permission(username)

        except Exception as e:
            logging.exception(e)
            sys.exit()

    def delete_user(self, username):
        """ Delete user """

        try:
            list_user = self.getListUser()
            if username not in list_user:
                logging.error("Fail to Delete Rundeck user: <{}>. User is not exists !".format(username))
                # sys.exit()
            else:
                delete_line = ""
                with open(self.config_file, "r") as read_file:
                    readlines = read_file.readlines()
                    data = readlines[:]
                    for line in readlines:
                        line_split = line.split(",")
                        user_pass = line_split[0].split(":")
                        user = user_pass[0]

                        if username == user:
                            delete_line = line

                with open(self.config_file, "w") as write_file:
                    for each_line in data:
                        if delete_line == each_line:
                            pass
                        else:
                            write_file.write(each_line)
                logging.info("Delete Rundeck user: <{}> successfully !".format(username))

        except Exception as e:
            logging.exception(e)
            # sys.exit()

    def change_password(self, username, new_password):
        """ Change Password """
        try:
            list_user = self.getListUser()
            if username not in list_user:
                logging.error("Fail to Change Password Rundeck user: <{}>. User is not exists !".format(username))
                sys.exit()

            def change_pass(data, line, user, new_pass):
                new_line = user + ":" + new_pass
                with open(self.config_file, "w+") as open_file:
                    for each_line in data:
                        if line == each_line:
                            open_file.write(new_line + "\n")
                        else:
                            open_file.write(each_line)

            with open(self.config_file, "r") as file:
                readlines = file.readlines()
                data = readlines[:]

                for line in readlines:
                    line_split = line.split(",")
                    user_pass = line_split[0].split(":")
                    user = user_pass[0].replace("\n", "")
                    if user == username:
                        change_pass(data, line, user, new_password)

            logging.info("Change Password Rundeck user: <{}> successfully !".format(username))

        except Exception as e:
            logging.exception(e)
            # sys.exit()


if __name__=="__main__":
    cmdline = argparse.ArgumentParser(description="Global User Managemnet")
    cmdline.add_argument("-rundeck", help="Rundeck User Action", action='store_true')
    cmdline.add_argument("-grafana", help="Grafana User Action", action='store_true')
    cmdline.add_argument("-nagivs", help="Nagvis User Action", action='store_true')

    cmdline.add_argument("-add", help="Action Add User", action='store_true')
    cmdline.add_argument("-change", help="Action Change Password", action='store_true')
    cmdline.add_argument("-delete", help="Action Delete User", action='store_true')

    cmdline.add_argument("-u", help="Input Username", action='store')
    cmdline.add_argument("-p", help="Input Password", action='store')

    cmdline.add_argument("-admin_user", help="Admin User", action='store')
    cmdline.add_argument("-admin_password", help="Admin Password", action='store')

    cmdline.add_argument("-role", help="User Role", action='store')

    args = cmdline.parse_args()

    if args.admin_user and args.add and args.u and args.p and args.role:
        RundeckUser().add_user(args.u, args.p, args.role)
        NagvisUser().add_user(args.u , args.p, args.role)
        GrafanaUser(args.admin_user, args.admin_password).add_user(args.u, args.p, args.role)


    if args.admin_user and args.change and args.u and args.p:
        RundeckUser().change_password(args.u, args.p)
        NagvisUser().change_password(args.u , args.p)
        GrafanaUser(args.admin_user, args.admin_password).change_password(args.u, args.p)


    if args.admin_user and args.delete and args.u:
        RundeckUser().delete_user(args.u)
        NagvisUser().delete_user(args.u)
        GrafanaUser(args.admin_user, args.admin_password).delete_user(args.u)



# NagvisUser().connection()
# NagvisUser().add_user("hahaha", "hahaha", "Admin")
# NagvisUser().delete_user("hahaha")
# NagvisUser().change_password("ha_test1", "12345")


# conn = sqlite3.connect("/usr/share/nagvis/etc/auth.db")
# rows = conn.execute('SELECT * FROM users2roles;').fetchall()
# # conn.execute("DELETE FROM users2roles WHERE userId=9")
# # conn.commit()
# for row in rows:
#     print(row)



# GrafanaUser().getUserInfo("juniper")
# GrafanaUser("grafanaadmin", "grafanaadmin").delete_user("hahaha")
# GrafanaUser("grafanaadmin", "grafanaadmin").add_user("hahaha", "hahaha", "User")
# GrafanaUser().change_password("haha", "12345")
# GrafanaUser("grafanaadmin", "grafanaadmin").delete_user("hahaha")

# RundeckUser().delete_user("ha_test")
# RundeckUser().add_user("ha_test", "12345", "Admin")
# RundeckUser().change_password("ha_test", "1234567")
# RundeckUser().set_admin_permission("ha_test")
