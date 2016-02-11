"""
    DO NOT USE THIS FOR ANY PUBLIC FACING DATABASES - IT IS INSECURE
"""

import sqlite3

class Database(object):
    """ Provides an easy-to-use wrapper for sqlite3 databases """
    def __init__(self, name):

        # Open the database
        
        self.name = name
        if ".db" not in name:
            self.name += ".db"

        self._main = sqlite3.connect(self.name)
        self._main.row_factory = sqlite3.Row

        # Load table names and column names into memory
        self._tables = {}
        self._db = self._main.cursor()

        
        for table in self.get_tables():
            self._tables[table] = self.get_columns(table)

    def __getitem__(self, table):
        """ Returns the contents of a table """
        self._db.execute("SELECT * FROM %s" % table)
        return self._db.fetchall()

    def get_tables(self):
        self._db.execute("SELECT * FROM sqlite_master WHERE type='table'")
        return [str(tbl['name']) for tbl in self._db.fetchall()]

    def tables(self):
        return self._tables.keys()

    def create_table(self, table_name, col):
        """ items in col should be tuples of column name and type """

        columns = ",".join(["%s %s" % (name, datatype) for name, datatype in col ])

        query = "CREATE TABLE %s (%s)" % (table_name, columns)

        self._db.execute(query)

        self._tables[table_name] = tuple(c[0] for c in col)
        
        return
        
    def get_columns(self, table):
        self._db.execute("PRAGMA table_info(%s)" % table)
        return [str(column['name']) for column in self._db.fetchall()]

    def columns(self, table):
        return self._tables[table]
    
    def insert(self, table, data):
        """ data should be a list of tuples (col, data) """
        # Get column names of the table
        columns = self.columns(table)
        
        # Use names to organise data into an acceptable row
        data = dict(data)
        row  = [data[col] for col in columns]
        
        # Insert
        query = "INSERT INTO {} VALUES (%s)".format(table) % ','.join((["?"]*len(row)))

        self._db.execute(query, row)
        
        return

    def update(self, table, column, new, identifier, value):
        """ e.g. db.update(tbl1, name, ryan, id, 3) updates the name of tbl1 with id 3 to Ryan """

        query = "UPDATE {} SET {} = {} WHERE {} = {}".format(table, column, new, identifier, value)

        self._db.execute(query)

        return

    def save(self):
        self._main.commit()
        return self

    def close(self):
        self._main.close()
        del self
