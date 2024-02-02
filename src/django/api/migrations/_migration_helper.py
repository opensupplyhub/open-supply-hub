import os


class MigrationHelper:
    def __init__(self, connection):
        self.conn = connection

    def run_sql_file(self, file_name):
        file_path = os.path.join('./sqls/', file_name)
        with open(file_path) as sql_file:
            with self.conn.cursor() as c:
                c.execute(sql_file.read())

    def run_sql_files(self, file_list):
        for file_name in file_list:
            self.run_sql_file(file_name)

    def drop_function(self, func):
        with self.conn.cursor() as c:
            c.execute(
                "DROP FUNCTION IF EXISTS {}".format(func)
            )
