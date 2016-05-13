"""
    SQL.py

    Module for creating and querying the Recordings.db database
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

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_val, trace):
        self.close()

    def query(self, table, p_id, columns=None):
        """ Returns the selected columns from table where performance_id == p_id """
        columns = "*" if columns is None else ",".join(columns)
        self._db.execute("SELECT {} FROM {} WHERE performance_id={}".format(columns, table, p_id))
        return self._db.fetchall()

    def delete(self, table, condition):
        self._db.execute("DELETE FROM {} WHERE {}".format(table, condition))
        print "DELETE FROM {} WHERE {}".format(table, condition)
        return

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

    def get(self, columnA, table, columnB, value):
        """ Returns value in Column A where the value in Column B is equal to the one supplied """
        tbl = self[table]
        for row in tbl:
            if row[columnB] == value:
                return row[columnA]
        return None

    def save(self):
        self._main.commit()
        return self

    def close(self):
        self._main.close()
        del self

# Database Constants

JOINT_NAMES_TABLE  = "tbl_JointNames"
HAND_STATES_TABLE  = "tbl_HandStates"
TRACK_STATES_TABLE = "tbl_TrackStates"

PERFORMANCE_NAME_TABLE  = "tbl_PerformanceName"
VIDEO_PATH_TABLE        = "tbl_VideoPath"
VIDEO_TIME_TABLE        = "tbl_VideoTime"
AUDIO_PATH_TABLE        = "tbl_AudioPath"
AUDIO_TIME_TABLE        = "tbl_AudioTime"
JOINT_DATA_TABLE        = "tbl_JointData"
HAND_DATA_TABLE         = "tbl_HandData"
BODY_TIME_TABLE         = "tbl_BodyTime"
BODY_NAME_TABLE         = "tbl_BodyName"

def CreateDatabase(filename):
    """ Creates the database and adds tables used by all performance data tables """

    import Skeleton
    
    db = Database(filename)

    # JointNames

    db.create_table(JOINT_NAMES_TABLE, [("joint_id","integer"),("joint_name","text")])

    for joint in Skeleton.JointTypes:

        db.insert(JOINT_NAMES_TABLE, [("joint_id", joint._id), ("joint_name", str(joint))])

    # HandStates5

    db.create_table(HAND_STATES_TABLE, [("hand_state", "integer"),("state_name","text")])

    for state in Skeleton.HandStates:

        db.insert(HAND_STATES_TABLE, [("hand_state", state._id), ("state_name", str(state))])

    # TrackStates

    db.create_table(TRACK_STATES_TABLE, [("tracking_state","integer"),("state_name","text")])

    for state in Skeleton.TrackStates:

        db.insert(TRACK_STATES_TABLE, [("tracking_state", state._id), ("state_name", str(state))])

    # Empty tables for storing recorded performance data

    db.create_table(PERFORMANCE_NAME_TABLE, [("performance_id","integer"), ("name","text")])

    db.create_table(JOINT_DATA_TABLE, [("performance_id","integer"),
                                       ("body","integer"),
                                       ("frame","integer"),
                                       ("joint_id","integer"),
                                       ("x", "real"),
                                       ("y", "real"),
                                       ("z", "real"),
                                       ("pixel_x","integer"),
                                       ("pixel_y","integer"),
                                       ("tracking_state","integer")])
    
    db.create_table(BODY_TIME_TABLE,  [("performance_id","integer"),
                                       ("frame","integer"),
                                       ("time","real")])

    db.create_table(BODY_NAME_TABLE,  [("performance_id","integer"),
                                       ("body","integer"),
                                       ("name","text")])
    
    db.create_table(HAND_DATA_TABLE, [("performance_id","integer"),
                                      ("body","integer"),
                                      ("frame","integer"),
                                      ("left_hand_state","integer"),
                                      ("left_hand_confidence","real"),
                                      ("right_hand_state","integer"),
                                      ("right_hand_confidence","real")])

    db.create_table(VIDEO_PATH_TABLE, [("performance_id","integer"),
                                       ("path","text"),
                                       ("start_time","real")])
    
    db.create_table(VIDEO_TIME_TABLE, [("performance_id","integer"),
                                       ("frame","integer"),
                                       ("time","real")])

    db.create_table(AUDIO_PATH_TABLE, [("performance_id","integer"),
                                       ("path","text")])

    db.create_table(AUDIO_TIME_TABLE, [("performance_id","integer"),
                                       ("start_time","real"),
                                       ("end_time","real")])

    db.save()
    db.close()

    return True
