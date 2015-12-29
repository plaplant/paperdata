'''
paper.distiller.scripts.backup_db

backups paperdistiller database into json file

author | Immanuel Washington

Functions
---------
json_data | dumps dictionaries to json file
paperbackup | backs up paperdistiller database
'''
from __future__ import print_function
import os
import sys
import time
import paper as ppdata
from paper.distiller import dbi as ddbi

def paperbackup(dbi):
    '''
    backups database by loading into json files, named by timestamp

    Parameters
    ----------
    dbi | object: database interface object
    '''
    timestamp = int(time.time())
    backup_dir = os.path.join('/data4/paper/paperdistiller_backup', str(timestamp))
    if not os.path.isdir(backup_dir):
        os.mkdir(backup_dir)

    tables = ('Observation', 'File', 'Log')
    table_sorts = {'Observation': {'first': 'julian_date', 'second': 'pol'},
                    'File': {'first': 'obsnum', 'second': 'filename'},
                    'Log': {'first': 'obsnum', 'second': 'timestamp'}}
    with dbi.session_scope() as s:
        print(timestamp)
        for table in tables:
            db_file = '{table}_{timestamp}.json'.format(table=table.lower(), timestamp=timestamp)
            backup_path = os.path.join(backup_dir, db_file)
            print(db_file)
            table = table.lower()
            DB_table = getattr(ddbi, table)
            DB_dump = s.query(DB_table).order_by(getattr(DB_table, table_sorts[table]['first']).asc(),
                                                    getattr(DB_table, table_sorts[table]['second']).asc())
            ppdata.json_data(backup_path, DB_dump)
            print('Table data backup saved')

if __name__ == '__main__':
    dbi = ddbi.DataBaseInterface()
    paperbackup(dbi)
