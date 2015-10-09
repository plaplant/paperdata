#!/usr/bin/python
# -*- coding: utf-8 -*-
# Add files to paper

from __future__ import print_function
import os
import sys
import socket
from paper.data import dbi as pdbi
import paper.convert as convert
import aipy as A

### Script to calculate uv data on any/other hosts
### output uv_data in csv format: 

### Author: Immanuel Washington
### Date: 5-06-15
def five_round(num):
	'''
	rounds number to five significant figures

	Parameters
	----------
	num | float: number

	Returns
	-------
	float(5): number
	'''
	return round(num, 5)

def jdpol2obsnum(jd, pol, djd):
	'''
	calculates unique observation number for observations

	Parameters
	----------
	jd | float: julian date float
	pol | str: polarization
	length | float: length of obs in fraction of julian date

	Returns
	-------
	int: a unique integer index for observation
	'''
	dublinjd = jd - 2415020  #use Dublin Julian Date
	obsint = int(dublinjd/djd)  #divide up by length of obs
	polnum = A.miriad.str2pol[pol]+10
	assert(obsint < 2**31)

	return int(obsint + polnum*(2**32))

def date_info(julian_date):
	'''
	indicates julian day and set of data
	calculates local sidereal hours for that julian date

	Parameters
	----------
	julian_date | float: julian date

	Returns
	-------
	tuple:
		int: era of julian date
		int: julian day
		float(1): lst hours rounded to one decimal place
	'''
	if julian_date < 2456100:
		era = 32
	elif julian_date < 2456400:
		era = 64
	else:
		era = 128

	julian_day = int(julian_date)

	gmst = convert.juliandate_to_gmst(julian_date)
	lst = convert.gmst_to_lst(gmst, longitude=25)

	return era, julian_day, round(lst, 1)

def is_edge(prev_obs, next_obs):
	'''
	checks if observation is on the edge of each day's observation cycle

	Parameters
	----------
	prev_obs (database object): previous observation
	next_obs (database object): next observation

	Returns
	-------
	bool: on the edge of a julian day
	'''
	if (prev_obs, next_obs) == (None, None):
		is_edge = None
	else:
		is_edge = (None in (prev_obs, next_obs))

	return is_edge

def calc_times(uv):
	'''
	takes in uv file and calculates time based information

	Parameters
	----------
	uv | file object: uv file object

	Returns
	-------
	tuple:
		float(5): time start
		float(5): time end
		float(5): delta time
		float(5): length of uv file object
	OR
	tuple:
		None for very field
	'''
	time_start = 0
	time_end = 0
	n_times = 0
	c_time = 0

	try:
		for (uvw, t, (i, j)), d in uv.all():
			if time_start == 0 or t < time_start:
				time_start = t
			if time_end == 0 or t > time_end:
				time_end = t
			if c_time != t:
				c_time = t
				n_times += 1
	except:
		return (None,) * 4

	if n_times > 1:
		delta_time = -(time_start - time_end) / (n_times - 1)
	else:
		delta_time = -(time_start - time_end) / (n_times)

		length = five_round(n_times * delta_time)
		time_start = five_round(time_start)
		time_end = five_round(time_end)
		delta_time = five_round(delta_time)

	return time_start, time_end, delta_time, length

def calc_npz_data(dbi, filename):
	'''
	takes in npz files and pulls data about observation

	Parameters
	----------
	dbi | object: database interface object
	filename | str: filename of npz file [Ex: zen.2456640.24456.xx.uvcRE.npz OR zen.2456243.24456.uvcRE.npz]

	Returns
	-------
	tuple:
		float(5): time start
		float(5): time end
		float(5): delta time
		float(5): julian date
		str: polarization
		float(5): length
		int: obsnum of uv file object
	OR
	tuple:
		None for every field if no corresponding observation found
	'''
	filetype = filename.split('.')[-1]
	if filetype not in ('npz',):
		return (None,) * 7
	
	jdate = '.'.join((filename.split('.')[1], filename.split('.')[2]))
	julian_date = round(float(jdate, 5))

	with dbi.session_scope() as s:
		if len(filename.split('.')) == 5:
			polarization = 'all'
		elif len(filename.split('.')) == 6:
			polarization = filename.split('.')[3]
		table = getattr(pdbi, 'Observation')
		OBS = s.query(table).filter(getattr(table, 'julian_date') == julian_date)\
							.filter(getattr(table, 'polarization') == polarization).one()

		time_start = getattr(OBS, 'time_start')
		time_end = getattr(OBS, 'time_end')
		delta_time = getattr(OBS, 'delta_time')
		length = getattr(OBS, 'length')
		obsnum = getattr(OBS, 'obsnum')

	return time_start, time_end, delta_time, julian_date, polarization, length, obsnum

def calc_uv_data(host, path):
	'''
	takes in uv* files and pulls data about observation

	Parameters
	----------
	host | str: host of system
	path | str: path of uv* file

	Returns
	-------
	tuple:
		float(5): time start
		float(5): time end
		float(5): delta time
		float(5): julian date
		str: polarization
		float(5): length
		int: obsnum of uv file object
	OR
	tuple:
		None for every field if no corresponding observation found
	'''
	named_host = socket.gethostname()
	if named_host == host:
		filetype = path.split('.')[-1]
		#allows uv access
		if filetype not in ('uv', 'uvcRRE'):
			return (None,) * 7
		else:
			try:
				uv = A.miriad.UV(path)
			except:
				return (None,) * 7

			time_start, time_end, delta_time, length = calc_times(uv)

			#indicates julian date
			julian_date = round(uv['time'], 5)

			pol_dict = pdbi.str2pol
			#assign letters to each polarization
			if uv['npol'] == 1:
				polarization = pol_dict[uv['pol']]
			elif uv['npol'] == 4:
				polarization = 'all'

			#gives each file unique id
			if length > 0:
				obsnum = jdpol2obsnum(julian_date, polarization, length)
			else:
				obsnum = None

	else:
		uv_data_script = os.path.expanduser('~/paperdata/paper/data/uv_data.py')
		moved_script = './uv_data.py'
		uv_comm = 'python {moved_script} {host} {path}'.format(moved_script=moved_script, host=host, path=path)
		with ppdata.ssh_scope(host) as ssh:
			with ssh.open_sftp() as sftp:
				try:
					filestat = sftp.stat(uv_data_script)
				except(IOError):
					try:
						filestat = sftp.stat(moved_script)
					except(IOError):
						sftp.put(uv_data_script, moved_script)

			_, uv_dat, _ = ssh.exec_command(uv_comm)
			time_start, time_end, delta_time, julian_date, polarization, length, obsnum = [round(float(info), 5) if key in (0, 1, 2, 3, 5)
																							else int(info) if key in (6,)
																							else info
																							for key, info in enumerate(uv_dat.read().split(','))]
	return time_start, time_end, delta_time, julian_date, polarization, length, obsnum

if __name__ == '__main__':
	input_host = sys.argv[1]
	input_path = sys.argv[2]
	if len(sys.argv) == 4:
		mode = sys.argv[3]

	uv_data = calc_uv_data(input_host, input_path)
	if uv_data is None:
		sys.exit()
	output_string = ','.join(uv_data)
	print(output_string)
