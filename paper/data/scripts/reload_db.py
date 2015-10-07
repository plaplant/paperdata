#!/usr/bin/python
# -*- coding: utf-8 -*-
# Create paper tables

import os
import socket
import paper as ppdata
import add_files

### Script to reload paper database
### Crawls all hosts for files

### Author: Immanuel Washington
### Date: 5-06-15

def find_paths(input_host):
	'''
	finds all uv* files on a host

	Parameters
	----------
	input_host (str): system host of files

	Returns
	-------
	tuple:
		list: uv* files
		list: .npz files
	'''
	named_host = socket.gethostname()
	input_paths = []
	npz_paths = []
	if input_host == named_host:
		for root, dirs, files in os.walk('/'):
			for direc in dirs:
				if direc.endswith('uv') or direc.endswith('uvcRRE'):
					input_paths.append(os.path.join(root, direc))
			for file_path in files:
				if file_path.endswith('npz'):
					npz_paths.append(os.path.join(root, file_path))
	else:
		with ppdata.login_ssh(input_host) as ssh:
			find = '''find / -name '*.uv' -o -name '*.uvcRRE' -o -name '*.npz' 2>/dev/null'''
			_, all_paths, _ = ssh.exec_command(find)
		for path in all_paths.split('\n'):
			if direc.endswith('uv') or direc.endswith('uvcRRE'):
				 input_paths.append(path)
			elif file_path.endswith('npz'):
				 npz_paths.append(path)

	return sorted(input_paths), sorted(npz_paths)

if __name__ == '__main__':
	if len(sys.argv) == 2:
		input_host = sys.argv[1]
	else:
		input_host = raw_input('Source directory host: ')

	for paths in find_paths(input_host):
		paths = sorted(add_files.dupe_check(input_host, all_paths))
		add_files.add_files(input_host, paths)
