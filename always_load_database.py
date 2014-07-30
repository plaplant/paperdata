#!/usr/bin/python
# -*- coding: utf-8 -*-
# Load data into MySQL table 

# import the MySQLdb and sys modules
import MySQLdb
import sys
import getpass
import os
import inspect
import csv
import aipy as A


#WILL NOT WORK UNLESS AIPY.MIRIAD.STR2POL ALTERED OR FILE ALREADY SEPARATED BY POLARIZATION

t_min = 0
t_max = 0
n_times = 0
c_time = 0

def get_size(start_path):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size

def sizeof_fmt(num):
	for x in ['bytes','KB','MB','GB']:
		if num < 1024.0:
			return "%3.1f%s" % (num, x)
		num /= 1024.0
	return "%3.1f%s" % (num, 'TB')

#db = raw_input('32, 64, or 128?: ')
#set initial database
db = '32'

data32 = '/data4/raw_data/'
data64 = '/data4/paper/2012EoR/psa_live/'
data128 = ''

db32 = '/data2/home/immwa/scripts/paper_output/db_output32.csv'
db64 = '/data2/home/immwa/scripts/paper_output/db_output64.csv'
db128 = '/data2/home/immwa/scripts/paper_output/db_output128.csv'


#create function to uniquely identify files
def jdpol2obsnum(jd,pol,djd):
        """
        input: julian date float, pol string. and length of obs in fraction of julian date
        output: a unique index
        """
        dublinjd = jd - 2415020  #use Dublin Julian Date
        obsint = int(dublinjd/djd)  #divide up by length of obs
        polnum = A.miriad.str2pol[pol]+10
        assert(obsint < 2**31)
        return int(obsint + polnum*(2**32))


#Always search through folio to update directory with new files
while True:
	#searches for only particular files
	if db == '32':
		datanum = data32
		dbnum = db32
	elif db == '64':
		datanum = data64
		dbnum = db64
	elif db == '128':
		datanum = data128
		dbnum = db128

	resultFile = open(dbnum,'wb')

	#create 'writer' object
	wr = csv.writer(resultFile, dialect='excel')

	#iterates through directories, listing information about each one
	for root, dirs, files in os.walk(datanum):
		#newname indicates directory right before filename
		if db =='32':
			datatruth = len(root) > 26 and len(root) < 34 and root[16] =='p'
		elif db == '64':
			datatruth = len(root) > 36 and len(root) < 64 and root[30] == 'p'
		elif db == '128':
			###need to change to 128 specifications!!!
			datatruth = len(root) > 36 and len(root) < 64 and root[30] == 'p'

		if datatruth:
			for dir in dirs:
				#if filename ends with uvcRRE, record into file
				if dir[-6:] == 'uvcRRE' and len(dir) > 6:
					#indicates name of full directory
					#rt = root[0:24]

					location = os.path.join(root, dir)

					#indicates size of file
					sz = sizeof_fmt(get_size(location))

					visdata = os.path.join(location, 'visdata')
					if not os.path.isfile(visdata):
						continue

	                                #allows uv access
					try:
		                               uv = A.miriad.UV(location)
					except:
						continue	

					#indicates julian date
					jdate = uv['time']


					#indicates julian day
					if datanum == data32:
						jday = int(str(jdate)[4:7])
					elif datanum == data64:
						jday = int(str(jdate)[3:7])

					#indicates set of data used
					if datanum == data32:
						antennas = 32
					elif datanum == data64:
						antennas = 64

					#indicates name of file to be used
					filename = dir

					#assign letters to each polarization
					if uv['npol'] == 1:
						if uv['pol'] == -5:
							polarization = 'xx'
						elif uv['pol'] == -6:
							polarization = 'yy'
						elif uv['pol'] == -7:
							polarization = 'xy'
						elif uv['pol'] == -8:
							polarization = 'yx' 
					elif uv['npol'] == 4:
						polarization = 'all'

					#indicates length of information in file
					#length = uv['inttime'] 

					t_min = 0
					t_max = 0
					n_times = 0
					c_time = 0

					for (uvw, t, (i,j)),d in uv.all():
                                        if t_min == 0 or t < t_min:
                                                t_min = t
                                        if t_max == 0 or t > t_max:
                                                t_max = t
                                        if c_time != t:
                                                c_time = t
                                                n_times += 1

	                                dt = -(t_min - t_max)/(n_times - 1)
	                                length = n_times * dt

					#gives each file unique id
					obsnum = jdpol2obsnum(jdate,polarization,length)

					#location of calibrate files
	                                if datanum == data32:
						cal_location = '/usr/global/paper/capo/arp/calfiles/psa898_v003.py'
	                                elif datanum == data64:
						cal_location = '/usr/global/paper/capo/zsa/calfiles/psa6240_v003.py'

					#create list of important data and open csv file
					databs = [[filename,location,antennas,obsnum,jday,jdate,polarization,length,cal_location,str(sz)]]
				#	datab = [[filename,location,antennas,id,jday,jdate,cal_location,str(sz)]]
					#print databs 

					#write to csv file by item in list
					for item in databs:
						wr.writerow(item)


	#Load data
	table = raw_input('Load data into table named:')
	datab = raw_input('Database:')
	pswd = getpass.getpass('Password:')
	# open a database connection
	# be sure to change the host IP address, username, password and database name to match your own
	connection = MySQLdb.connect (host = 'shredder', passwd = pswd, db = datab, local_infile=True)

	# prepare a cursor object using cursor() method
	cursor = connection.cursor()

	#print resultFile 
	# execute the SQL query using execute() method.
	cursor.execute('''USE paperdata;
	LOAD DATA LOCAL INFILE '%s' INTO TABLE %s
	COLUMNS TERMINATED BY ','
	LINES TERMINATED BY '\n' '''%(resultFile, table))

	#print 'Table data loaded.'

	# close the cursor object
	cursor.close()

	#save changes to database
	connection.commit()

	# close the connection
	connection.close()


	#moves to next era of data
	if db == '32':
		db = '64'
	elif db =='64':
		db = '128'
	elif db = '128':
		db = '32'

# exit the program
sys.exit()