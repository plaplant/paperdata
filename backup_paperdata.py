#!/usr/bin/python
# -*- coding: utf-8 -*-
# Load data into MySQL table 

# import the MySQLdb and sys modules
import MySQLdb
import sys
import getpass
import time
import csv

datab = 'paperdata'
usrnm = raw_input('Username: ')
pswd = getpass.getpass('Password: ')

time_date = time.strftime("%d-%m-%Y_%H:%M:%S")

table = 'paperdata' 
dbnum = '/data2/home/immwa/scripts/paper_output/paperdata_backup_%s.csv'%(time_date)

print dbnum
resultFile = open(dbnum,'wb+')

#create 'writer' object
wr = csv.writer(resultFile, dialect='excel')

#Load data into named database and table

# open a database connection
# be sure to change the host IP address, username, password and database name to match your own
connection = MySQLdb.connect (host = 'shredder', user = usrnm, passwd = pswd, db = datab, local_infile=True)

# prepare a cursor object using cursor() method
cursor = connection.cursor()

# execute the SQL query using execute() method.
cursor.execute('SELECT * FROM paperdata')
results = cursor.fetchall()

for item in results:
	#write to csv file by item in list
	wr.writerow(item)

#cursor.execute('''SELECT * INTO OUTFILE '%s'
#FIELDS TERMINATED BY ','
#LINES TERMINATED BY '\n' 
#FROM paperdata '''%(dbnum))

print time_date
print 'Table data backup saved'

# close the cursor object
cursor.close()

#save changes to database
connection.commit()

# close the connection
connection.close()

# exit the program
sys.exit()