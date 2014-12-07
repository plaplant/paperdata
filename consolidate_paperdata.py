#!/usr/bin/python
# -*- coding: utf-8 -*-

# import the MySQLdb and sys modules
import MySQLdb
import sys
import getpass
import os
import csv

def consolidate(dbo):
	resultFile = open(dbo,'wb')
	resultFile.close()

	connection = MySQLdb.connect (host = 'shredder', user = 'paperboy', passwd = 'paperboy', db = 'paperdata', local_infile=True)
	cursor = connection.cursor()

	back = []
	front = []

	#path is [0]
	#jday is [5]
	#jdate is [6]
	#raw_location is [9]

	cursor.execute('SELECT * from paperdata where compressed = 1 order by julian_date asc')
	resa = cursor.fetchall()

	cursor.execute('SELECT * from paperdata where compressed = 0 order by julian_date asc')
	resb = cursor.fetchall()

	for item in resa:
		if item[9] != 'NULL':
			if item[0] in ['NULL', 'ON TAPE']:
				path = item[0]
			else:
				compr_host = item[0].split(':')[0]
				compr = item[0].split(':')[1]
				if compr_host == 'folio' and not os.path.isdir(compr):
					path = 'NULL'
				else:
					path = item[0]
			if item[9] in  ['NULL', 'ON TAPE']:
				raw_path = item[9]
			else:
				raw_host = item[9].split(':')[0]
				raw = item[9].split(':')[1]
				if raw_host == 'folio' and not os.path.isdir(raw):
					raw_path = 'NULL'
				else:
					raw_path = item[9]

			if raw_path == 'NULL' and path == 'NULL':
				continue

			if raw_path == 'NULL': 
				raw_sz = 0.0
			else:
				raw_sz = item[13]

			if path == 'NULL':
				compr_sz = 0.0
			else:
				compr_sz = item[12]

			it = (path,item[1],item[2],item[3],item[4],item[5],item[6],item[7],item[8],raw_path,item[10],item[11],compr_sz,raw_sz,item[14],item[15],item[16],item[17],item[18])
			back.append(it)
		else:
			#do stuff
			cursor.execute('''SELECT * from paperdata where julian_date = '%.5f' and polarization = '%s' order by julian_date asc''' %(item[6], item[7]))
			ras = cursor.fetchall()
			for ra in ras:
				if len(ras) > 1:
					if item == ra:
						continue
				if len(ra) > 0:
					if ra[8] == 0.00000:
						length = item[8]
					else:
						length = ra[8]
					if item[10] == 'NULL':
						cal = ra[10]
					else:
						cal = item[10]

					if item[0] == 'NULL':
                                                path = 'NULL'
                                        else:
                                                compr_host = item[0].split(':')[0]
                                                compr = item[0].split(':')[1]
                                                if compr_host == 'folio' and not os.path.isdir(compr):
                                                        path = 'NULL'
                                                else:
                                                        path = item[0]
                                        if ra[9] == 'NULL':
                                                raw_path = 'NULL'
                                        else:
                                                raw_host = ra[9].split(':')[0]
                                                raw = ra[9].split(':')[1]
                                                if raw_host == 'folio' and not os.path.isdir(raw):
                                                        raw_path = 'NULL'
                                                else:
                                                        raw_path = ra[9]

					if raw_path == 'NULL' and path == 'NULL':
						continue

					if raw_path == 'NULL': 
						raw_sz = 0.0
					else:
						raw_sz = ra[13]

					if path == 'NULL':
						compr_sz = 0.0
					else:
						compr_sz = item[12]

					it = (path,item[1],item[2],item[3],ra[4],item[5],item[6],ra[7],length,raw_path,cal,ra[11],compr_sz,raw_sz,item[14],item[15],item[16],item[17],item[18])
					back.append(it)
				else:
					back.append(item)
	for ra in resb:
		if ra[0] != 'NULL':
			continue
		else:
			#do stuff
			cursor.execute('''SELECT * from paperdata where julian_date = '%.5f' and polarization = '%s' order by julian_date asc''' %(ra[6], ra[7]))
        	        items = cursor.fetchall()
			for item in items:
				if len(items) > 1:
					if item == ra:
						continue
	                	if len(item) > 0:
					if item[8] == 0.00000:
						length = ra[8]
					else:
						length = item[8]
					if ra[10] == 'NULL':
						cal = item[10]
					else:
						cal = ra[10]

					if item[0] == 'NULL':
						path = 'NULL'
					else:
						compr_host = item[0].split(':')[0]
						compr = item[0].split(':')[1]
						if compr_host == 'folio' and not os.path.isdir(compr):
							path = 'NULL'
						else:
							path = item[0]
					if ra[9] == 'NULL': 
						raw_path = 'NULL'
					else:
						raw_host = ra[9].split(':')[0]
						raw = ra[9].split(':')[1]
						if raw_host == 'folio' and not os.path.isdir(raw):
							raw_path = 'NULL'
						else:
							raw_path = ra[9]

					if raw_path == 'NULL' and path == 'NULL':
						continue

					if raw_path == 'NULL':
						raw_sz = 0.0
					else:
						raw_sz = ra[13]

					if path == 'NULL':
						compr_sz = 0.0
					else:
						compr_size = item[12]

	                        	it = (path,item[1],item[2],item[3],ra[4],item[5],item[6],ra[7],length,raw_path,cal,ra[11],compr_sz,raw_sz,item[14],item[15],item[16],item[17],item[18])
	                        	front.append(it)
				else:
					front.append(ra)

	#Takes only unique entries
	total = tuple(back + front)
	backup = set(total)
	backup = sorted(backup, key=lambda x: (x[6], x[9], x[0]))

	for item in backup:
		resultFile = open(dbo,'ab')
		wr = csv.writer(resultFile, delimiter='|', dialect='excel')
		wr.writerow(item)
		resultFile.close()

	# Close database
	cursor.close()
	connection.close()

	return None

if __name__ == '__main__':
	dbo = '/data2/home/immwa/scripts/paperdata/single_entry.psv'
	consolidate(dbo)
