#!/usr/bin/python
# -*- coding: utf-8 -*-
# Add files to paperdev

import MySQLdb
import sys
import getpass
import time
import subprocess
import aipy as A
import hashlib
import glob
import socket
import os
import paramiko
import shutil
import paperdev_dbi as pdbi

### Script to move files and update paperdev database
### Move files and update db using dbi

### Author: Immanuel Washington
### Date: 5-06-15

def delete_check(input_host):
	dbi = pdbi.DataBaseInterface()
	s = dbi.Session()
	FILEs = s.query(pdbi.File).filter(pdbi.File.delete_file==True).filter(pdbi.File.tape_index!=None).filter(pdbi.File.host==input_host).all()
	s.close()
	#all files on same host
	filenames = tuple(os.path.join(FILE.path, FILE.filename) for FILE in FILEs)
		
	return filenames


def rsync_copy(source, destination):
	subprocess.check_output(['rsync', '-ac', source, destination])
	return None

def delete_files(input_host, input_paths, output_host, output_dir):
	named_host = socket.gethostname()
	destination = ''.join((output_host, ':', output_dir))
	action = 'delete'
	table = 'file'
	if named_host == input_host:
		dbi = pdbi.DataBaseInterface()
		s = dbi.Session()
		for source in input_paths:
			rsync_copy(source, destination)
			#change in database
			full_path = ''.join((input_host, ':', source))
			timestamp = int(time.time())
			FILE = dbi.get_entry('file', full_path)
			dbi.set_entry(FILE, 'host', output_host)
			dbi.set_entry(FILE, 'path', output_dir)
			dbi.set_entry(FILE, 'delete_file', False)
			dbi.set_entry(FILE, 'timestamp', timestamp)
			log_data = {'action':action,
						'table':table,
						'obsnum':None,
						'host':input_host,
						'full_path':source,
						'feed_path':None,
						'timestamp':timestamp}
			dbi.add_log(log_data)
			shutil.rmtree(source)
		s.close()
	else:
		dbi = pdbi.DataBaseInterface()
		s = dbi.Session()
		ssh = pdbi.login_ssh(host)
		for source in input_paths:
			rsync_copy_command = '''rsync -ac {source} {destination}'''.format(source=source, destination=destination)
			rsync_del_command = '''rm -r {source}'''.format(source=source)
			ssh.exec_command(rsync_copy_command)
			full_path = ''.join((input_host, ':', source))
			timestamp = int(time.time())
			FILE = dbi.get_entry('file', full_path)
			dbi.set_entry(FILE, 'host', output_host)
			dbi.set_entry(FILE, 'path', output_dir)
			dbi.set_entry(FILE, 'delete_file', False)
			dbi.set_entry(FILE, 'timestamp', timestamp)
			ssh.exec_command(rsync_del_command)
		ssh.close()
		s.close()

	print 'Completed transfer'
	return None

if __name__ == '__main__':
	input_host = raw_input('Source directory host: ')
	output_host = raw_input('Destination directory host: ')
	output_dir = raw_input('Destination directory: ')
	input_paths = delete_check(input_host)
	delete_files(input_host, input_paths, output_host, output_dir)
