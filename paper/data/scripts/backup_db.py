#!/usr/bin/python
# -*- coding: utf-8 -*-
# Load data into MySQL table 

# import the MySQLdb and sys modules
from __future__ import print_function
import sys
import time
import os
import json
import paper as ppdata
from paper.data import dbi as pdbi

### Script to Backup paper database
### Finds time and date and writes table into .csv file

### Author: Immanuel Washington
### Date: 8-20-14

def json_data(dbo, dump_objects):
	'''
	dumps list of objects into a json file

	Args:
		dbo (str): filename
		dump_objects (list): database objects query
	'''
	with open(dbo, 'w') as f:
		data = [ser_data.to_dict() for ser_data in dump_objects.all()]
		json.dump(data, f, sort_keys=True, indent=1, default=ppdata.decimal_default)

	return None

def paperbackup(dbi):
	'''
	backups database by loading into json files, named by timestamp

	Args:
		dbi (object): database interface object
	'''
	timestamp = int(time.time())
	backup_dir = os.path.join('/data4/paper/paperdata_backup', str(timestamp))
	if not os.path.isdir(backup_dir):
		os.mkdir(backup_dir)

	#tables = ('Observation', 'File', 'Feed', 'Log')
	tables = ('Observation', 'File', 'Log')
	table_sorts = {'Observation': {'first': 'julian_date', 'second': 'polarization'},
					'File': {'first': 'obsnum', 'second': 'filename'},
					'Feed': {'first': 'julian_day', 'second': 'filename'},
					'Log': {'first': 'timestamp', 'second': 'action'}}
	with dbi.session_scope() as s:
		print(timestamp)
		for table in tables:
			db_file = '{table}_{timestamp}.json'.format(table=table, timestamp=timestamp)
			dbo = os.path.join(backup_dir, db_file)
			print(db_file)

			DB_table = getattr(pdbi, table.title())
			DB_dump = s.query(DB_table).order_by(getattr(DB_table, table_sorts[table]['first']).asc(),
												getattr(DB_table, table_sorts[table]['second']).asc())
			json_data(dbo, DB_dump)
			print('Table data backup saved')

	return None

if __name__ == '__main__':
	dbi = pdbi.DataBaseInterface()
	paperbackup(dbi)
