#!/usr/bin/python
# -*- coding: utf-8 -*-
# Create paperdev tables

import paperdev_dbi as pdbi
import sys
import json
import paperdev_db as pdb
import glob
import sqlalchemy.exc

### Script to create paperdev database
### Instantiates tables

### Author: Immanuel Washington
### Date: 5-06-15

def load_backup(backup, table=None):
	dbi = pdbi.DataBaseInterface()
	with open(backup, 'r') as backup_db:
		read = json.load(backup_db)
		if table is None:
			return None
		else:
			for row in read:
				print row.items()
				try:
					if table == 'observation':
						dbi.add_observation(row)
					elif table == 'file':
						dbi.add_file(row)
					#elif table == 'feed':
					#	dbi.add_feed(row)
					elif table == 'log':
						dbi.add_log(row)
					#elif table == 'rtp_file':
					#	dbi.add_rtp_file(row)
				except:
					print('Failed to load in entry')

	return None

if __name__ == '__main__':
	if len(sys.argv) == 3:
		backup_obs = sys.argv[1]
		backup_file = sys.argv[2]
	else:
		backup_list = glob.glob('/data4/paper/paperdev_backup/[0-9]*')
		backup_list.sort(reverse=True)
		backup_dir = backup_list[0]
		timestamp = int(backup_dir.split('/')[-1])
		backup_obs = '/data4/paper/paperdev_backup/{timestamp}/obs_{timestamp}.json'.format(timestamp=timestamp)
		backup_file = '/data4/paper/paperdev_backup/{timestamp}/file_{timestamp}.json'.format(timestamp=timestamp)
		backup_feed = '/data4/paper/paperdev_backup/{timestamp}/feed_{timestamp}.json'.format(timestamp=timestamp)
		backup_log = '/data4/paper/paperdev_backup/{timestamp}/log_{timestamp}.json'.format(timestamp=timestamp)
		#backup_rtp_file = '/data4/paper/paperdev_backup/{timestamp}/rtp_file_{timestamp}.json'.format(timestamp=timestamp)
		
	
	#load_backup(backup_obs, table='observation')
	load_backup(backup_file, table='file')
	#load_backup(backup_feed, table='feed')
	#load_backup(backup_log, table='log')
	#load_backup(backup_rtp, table='rtp_file'
