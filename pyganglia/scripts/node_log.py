#!/usr/bin/python
# -*- coding: utf-8 -*-
# Load data into MySQL table 

# import the MySQLdb and sys modules
import MySQLdb
import sys
import getpass
import os
import csv
import glob
import socket
import time
import subprocess

### Script to check the status of folio at any point
### Checks /data4 for space, uses iostat to check for cpu usage and I/O statistics

### Author: Immanuel Washington
### Date: 01-20-15

def calculate_folio_space(dir):
	#Calculates the free space left on input dir
	folio = subprocess.check_output(['df', '-B', '1'])
	#/data4 should be filesystem
	#Amount of available bytes should be free_space

	folio_space = 0
	for output in folio.split('\n'):
		filesystem = output.split(' ')[-1]
		if filesystem in ['/data4']:
			folio_space = int(output.split(' ')[-4])
	return folio_space

def iostat():
	#Calculates cpu usage on folio nodes
	folio = subprocess.check_output(['iostat'])

	folio_use = []
	folio_name = folio.split('\n')[0].split(' ')[2].strip('()')
	for output in folio.split('\n'):
		device = output.split(' ')[0]
		if device in ['Device:', 'sda', 'sda1', 'sda2','dm-0', 'dm-1']:
			line = output[:].split(' ')
			new_line = filter(lambda a: a not in [''], line)
			folio_use.append(new_line)

	folio_use = folio_use[1:]

	return [folio_name, folio_use]

def ram_free():
	#Calculates ram usage on folio
	folio = subprocess.check_output(['free', '-b'])
	ram = []
	for output in folio.split('\n'):
		line = output[:].split(' ')
		new_line = filter(lambda a: a not in [''], line)
		ram.append(new_line)	

	reram = []
	for key, row in enumerate(ram[1:-1]):
		if key in [0]:
			for item in row[1:]:
				reram.append(item)
		if key in [1]:
			for item in row[2:]:
				reram.append(item)
		if key in [2]:
			for item in row[1:]:
				reram.append(item)

	return [reram]

def cpu_perc():
	#Calculates cpu usage on folio
	folio = subprocess.check_output(['mpstat', '-P', 'ALL'])
	cpu = []
	for output in folio.split('\n'):
		if output in [folio.split('\n')[0],folio.split('\n')[1]]:
			continue
		line = output[:].split(' ')
		new_line = filter(lambda a: a not in [''], line)
		cpu.append(new_line)

	recpu = []

	for row in cpu[3:]:
		dummy_cpu = []
		for key, item in enumerate(row):
			if key in [2,3,5,6,10,11]:
				dummy_cpu.append(item)
		recpu.append(dummy_cpu)

	return recpu

"""
def processes():
	#Calculates cpu usage on folio
	folio = subprocess.check_output(['top', '-n1'])
	pro = []
	#for output in folio.split('\n'):
	for output in folio.split('\n'):
		if output in folio.split('\n')[:6]:
			continue
		line = output[:].split(' ')
		new_line = filter(lambda a: a not in [''], line)
		pro.append(new_line[1:-1])

	return pro
"""

#def write_file(usrnm, pswd, folio_data, time_date, folio_space, host_name, usage, ram, cpu, pro):
def write_file((usrnm, pswd, folio_data, time_date, folio_space, host_name, usage, ram, cpu):
	dbr = open(folio_data, 'ab')
	wr = csv.writer(dbr, delimiter='|', lineterminator='\n', dialect='excel')
	wr.writerow([time_date])
	wr.writerow(['Space on folio', folio_space])
	wr.writerow(['Host', host_name])
	wr.writerow(['Average CPU statistics:'])
	for row in usage:
		wr.writerow(row)
	wr.writerow(['RAM:'])
	for row in ram:
		wr.writerow(row)
	wr.writerow(['CPU Usage:'])
	for row in cpu:
		wr.writerow(row)
	#wr.writerow(['Processes:'])
	#for row in pro:
	#	wr.writerow(row)

	dbr.close()
	# open a database connection
	connection = MySQLdb.connect (host = 'shredder', user = usrnm, passwd = pswd, db = 'ganglia', local_infile=True)

	# prepare a cursor object using cursor() method
	cursor = connection.cursor()

	#execute the SQL query using execute() method.
	for row in usage:
		val = tuple(row)
		values = ('iostat', host_name) + val + (time_date,)
		cursor.execute('''INSERT INTO %s VALUES(%s,%s,%.2f,%.2f,%.2f,%d,%d,%s)''', values)
	for row in ram:
		val = tuple(row)
		values = ('ram', host_name) + val + (time_date,)
		cursor.execute('''INSERT INTO %s VALUES(%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%s)''', values)
	for row in cpu:
		val = tuple(row)
		values = ('cpu', host_name) + val + (time_date,)
		cursor.execute('''INSERT INTO %s VALUES(%s,%d,%.2f,%.2f,%.2f,%.2f,%d,%s)''', values)

	#Close and save changes to database
	cursor.close()
	connection.commit()
	connection.close()
	
	return None

def data_out(time_date):
	#Create output file
	time_day = time.strftime('%d-%m-%Y')
	host = socket.gethostname()
	folio_data = '/data4/paper/paperoutput/log_%s_%s.psv' %(host, time_day)
	print folio_data
	dbr = open(folio_data, 'wb')
	dbr.close()

	return folio_data

def monitor(auto):
	time_date = time.strftime('%d-%m-%Y_%H:%M:%S')

	#Create output file
	folio_data = data_out(time_date)

	start_time = time.time()
	interval = 1

	if auto in ['y']:
		usrnm = 'immwa'
		pswd = 'immwa3978'
	else:
		usrnm = raw_input('Username: ')
		pswd = getpass.getpass('Password: ')

	for i in range(3):
		time_date = time.strftime('%d-%m-%Y_%H:%M:%S')

		#Checks all filesystems
		dir = '/*'
		folio_space = calculate_folio_space(dir)

		host_name, usage = iostat()
		ram = ram_free()
		cpu = cpu_perc()
		#pro = processes()

		#write_file((usrnm, pswd, folio_data, time_date, folio_space, host_name, usage, ram, cpu, pro)
		write_file((usrnm, pswd, folio_data, time_date, folio_space, host_name, usage, ram, cpu)
		time.sleep(start_time + (i + 1) * interval - time.time())

	if auto in ['y']:
		time.sleep(60)

	return None
if __name__ == '__main__':
	auto = 'n'
	monitor(auto)