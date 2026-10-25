import os

from psycopg2 import sql


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

    def create_indexes_concurrently(self, table, indexes):
        """
        Build indexes on a live table without blocking its writes, the way
        0233 does. indexes maps an index name to its CREATE INDEX
        CONCURRENTLY IF NOT EXISTS statement; the calling migration must set
        atomic = False. A failed concurrent build leaves an invalid index
        that IF NOT EXISTS would skip on retry, so those are dropped first.
        """
        with self.conn.cursor() as c:
            c.execute(
                'SELECT cls.relname FROM pg_index idx '
                'JOIN pg_class cls ON cls.oid = idx.indexrelid '
                'WHERE NOT idx.indisvalid AND cls.relname = ANY(%s)',
                [list(indexes)],
            )
            self.drop_indexes_concurrently([row[0] for row in c.fetchall()])
            for statement in indexes.values():
                c.execute(statement)
            c.execute(sql.SQL('ANALYZE {}').format(sql.Identifier(table)))

    def drop_indexes_concurrently(self, index_names):
        with self.conn.cursor() as c:
            for index_name in index_names:
                c.execute(
                    sql.SQL('DROP INDEX CONCURRENTLY IF EXISTS {}').format(
                        sql.Identifier(index_name)
                    )
                )
