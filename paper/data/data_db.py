#!/usr/bin/python
# -*- coding: utf-8 -*-
# Module to creation of db schema

### Author: Immanuel Washington
### Date: 05-17-14

from __future__ import print_function

class file:
	def __init__(self):
		self.table = 'file'
		self.db_list = ('host',
						'path',
						'filename',
						'filetype',
						'full_path',
						'obsnum',
						'filesize',
						'md5sum',
						'tape_index',
						'source_host',
						'write_to_tape',
						'delete_file',
						'timestamp')
		self.db_descr = {'host': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'host of file system that file is located on'},
						'path': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'directory that file is located in'},
						'filename': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'name of file (ex: zen.2446321.16617.uvcRRE)'},
						'filetype': {'type': 'VARCHAR(20)', 'default': 'None',
						'primary key': 'No', 'description': 'filetype (ex: uv, uvcRRE, npz)'},
						'full_path': {'type': 'VARCHAR(200)', 'default': 'None',
						'primary key': 'Primary', 'description':
													'combination of host, path, and filename which is a unique identifier for each file'},
						'obsnum': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Foreign', 'description': 'observation number used to track files using integer'},
						'filesize': {'type': 'DECIMAL(7, 2)', 'default': 'None',
						'primary key': 'No', 'description': 'size of file in megabytes'},
						'md5sum': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': '32-bit integer md5 checksum of file'},
						'tape_index': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'indexed location of file on tape'},
						'source_host': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'original source(host) of file'},
						'write_to_tape': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicated whether file needs to be written to tape'},
						'delete_file': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicated whether file needs to be deleted from its host'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time entry was last updated'}}

class observation:
	def __init__(self):
		self.table = 'observation'
		self.db_list = ('obsnum',
						'julian_date',
						'polarization',
						'julian_day',
						'lst',
						'era',
						'era_type',
						'length',
						'time_start',
						'time_end',
						'delta_time',
						'prev_obs',
						'next_obs',
						'edge',
						'timestamp')
		self.db_descr = {'obsnum': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Primary', 'description': 'observation number used to track files using integer'},
						'julian_date': {'type': 'DECIMAL(12, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'julian date of observation'},
						'polarization': {'type': 'VARCHAR(4)', 'default': 'None',
						'primary key': 'No', 'description': 'polarization of observation'},
						'julian_day': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'integer value of julian date'},
						'lst': {'type': 'DECIMAL(3, 1)', 'default': 'None',
						'primary key': 'No', 'description': 'local sidereal time for south africa at julian date'},
						'era': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'era of observation taken: 32, 64, 128'},
						'era_type': {'type': 'VARCHAR(20)', 'default': 'None',
						'primary key': 'No', 'description': 'type of observation taken: dual pol, etc.'},
						'length': {'type': 'DECIMAL(6, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'length of time data was taken for particular observation'},
						'time_start': {'type': 'DECIMAL(12, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'start time of observation'},
						'time_end': {'type': 'DECIMAL(12, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'end time of observation'},
						'delta_time': {'type': 'DECIMAL(12, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'time step of observation'},
						'prev_obs': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Unique', 'description': 'observation number of previous observation'},
						'next_obs': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Unique', 'description': 'observation number of next observation'},
						'edge': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicating if observation at beginning/end of night or not'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time entry was last updated'}}

class feed:
	def __init__(self):
		self.table = 'feed'
		self.db_list = ('host',
						'path',
						'filename',
						'full_path',
						'julian_day',
						'ready_to_move',
						'moved_to_distill',
						'timestamp')
		self.db_descr = {'host': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'host of file system that file is located on'},
						'path': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'directory that file is located in'},
						'filename': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'name of file (ex: zen.2446321.16617.uvcRRE)'},
						'full_path': {'type': 'VARCHAR(200)', 'default': 'None',
						'primary key': 'Primary', 'description':
													'combination of host, path, and filename which is a unique identifier for each file'},
						'julian_day': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'integer value of julian date'},
						'ready_to_move': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicated whether file is ready to be moved to distill'},
						'moved_to_distill': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicated whether file has been moved to distill yet'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time entry was last updated'}}

class log:
	def __init__(self):
		self.table = 'log'
		self.db_list = ('action',
						'table',
						'identifier',
						'timestamp')
		self.db_descr = {'action': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'action taken by script'},
						'table': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'table script is acting on'},
						'identifier': {'type': 'VARCHAR(200)', 'default': 'None',
						'primary key': 'No', 'description': 'primary key of item that was changed'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time action was taken'}}

class rtp_file:
	def __init__(self):
		self.table = 'rtp_file'
		self.db_list = ('host',
						'path',
						'filename',
						'filetype',
						'full_path',
						'obsnum',
						'md5sum',
						'transferred',
						'julian_day',
						'new_host',
						'new_path',
						'timestamp')
		self.db_descr = {'host': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'host of file system that file is located on'},
						'path': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'directory that file is located in'},
						'filename': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'name of file (ex: zen.2446321.16617.uvcRRE)'},
						'filetype': {'type': 'VARCHAR(20)', 'default': 'None',
						'primary key': 'No', 'description': 'filetype (ex: uv, uvcRRE, npz)'},
						'full_path': {'type': 'VARCHAR(200)', 'default': 'None',
						'primary key': 'Primary', 'description':
													'combination of host, path, and filename which is a unique identifier for each file'},
						'obsnum': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Foreign', 'description': 'observation number used to track files using integer'},
						'transferred': {'type': 'BOOLEAN', 'default': 'None',
						'primary key': 'No', 'description': 'boolean value indicated whether file has bee copied to USDB'},
						'md5sum': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': '32-bit integer md5 checksum of file'},
						'julian_day': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'integer value of julian date'},
						'new_host': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'new source(host) of file'},
						'new_path': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'new path of file of new host'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time entry was last updated'}}

class rtp_observation:
	def __init__(self):
		self.table = 'rtp_observation'
		self.db_list = ('obsnum',
						'julian_date',
						'polarization',
						'julian_day',
						'era',
						'length',
						'prev_obs',
						'next_obs',
						'timestamp')
		self.db_descr = {'obsnum': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Primary', 'description': 'rtp_observation number used to track files using integer'},
						'julian_date': {'type': 'DECIMAL(12, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'julian date of rtp_observation'},
						'polarization': {'type': 'VARCHAR(4)', 'default': 'None',
						'primary key': 'No', 'description': 'polarization of rtp_observation'},
						'julian_day': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'integer value of julian date'},
						'era': {'type': 'INTEGER', 'default': 'None',
						'primary key': 'No', 'description': 'era of rtp_observation taken: 32, 64, 128'},
						'length': {'type': 'DECIMAL(6, 5)', 'default': 'None',
						'primary key': 'No', 'description': 'length of time data was taken for particular rtp_observation'},
						'prev_obs': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Unique', 'description': 'rtp_observation number of previous rtp_observation'},
						'next_obs': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'Unique', 'description': 'rtp_observation number of next rtp_observation'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time entry was last updated'}}

class rtp_log:
	def __init__(self):
		self.table = 'rtp_log'
		self.db_list = ('action',
						'table',
						'identifier',
						'timestamp')
		self.db_descr = {'action': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'action taken by script'},
						'table': {'type': 'VARCHAR(100)', 'default': 'None',
						'primary key': 'No', 'description': 'table script is acting on'},
						'identifier': {'type': 'VARCHAR(200)', 'default': 'None',
						'primary key': 'No', 'description': 'primary key of item that was changed'},
						'timestamp': {'type': 'BIGINT', 'default': 'None',
						'primary key': 'No', 'description': 'time action was taken'}}

#dictionary of instantiated classes
instant_class = {'file':file(),
				'observation':observation(),
				'feed':feed(),
				'log':log(),
				'rtp_file':rtp_file(),
				'rtp_observation':rtp_observation(),
				'rtp_log':rtp_log()}
classes = instant_class.keys()
all_classes = instant_class.values()

#Only do things if running this script, not importing
if __name__ == '__main__':
	print('Not a script file, just a module')
