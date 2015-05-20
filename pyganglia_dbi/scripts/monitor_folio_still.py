#!/usr/global/paper/bin/python
from ddr_compress.dbi import DataBaseInterface,Observation,File
from sqlalchemy import func
import curses,time,os
import jdcal
import pyganglia_dbi as pyg

#setup my output file
#node_data = '/data4/paper/paperoutput/monitor_folio_log.psv'
file_log = []
file_status = {}
file_time = {}
file_pid = {}
file_start = {}
file_end = {}

#setup my curses stuff following
# https://docs.python.org/2/howto/curses.html
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
stdscr.nodelay(1)

#setup my db connection
dbi = DataBaseInterface()
pyg_dbi = pyg.DataBaseInterface()

stdscr.addstr("PAPER Distiller Status Board")
stdscr.addstr(1,0,"Press 'q' to exit")
statheight = 50
statusscr = curses.newwin(statheight,200,5,0)
statusscr.keypad(1)
statusscr.nodelay(1)
curline = 2
colwidth = 50
obslines = 20
i=0
stat = ['\\','|','/','-','.']
try:
	while(1):
		time_date = time.strftime('%Y:%m:%d:%H:%M:%S')
		temp_time = time_date.split(':')
		time_date = jdcal.gcal2jd(temp_time[0],temp_time[1],temp_time[2],temp_time[3],temp_time[4],temp_time[5])
		log_info = []
		#get the screen dimensions

		#load the currently executing files
		i += 1
		curline = 2
		stdscr.addstr(0,30,stat[i%len(stat)])
		s = dbi.Session()
		totalobs = s.query(Observation).count()
		stdscr.addstr(curline,0,"Number of observations currently in the database: {totalobs}".format(totalobs=totalobs))
		curline += 1
		OBSs = s.query(Observation).filter(Observation.status!='NEW').filter(Observation.status!='COMPLETE').all()
		#OBSs = s.query(Observation).all()
		obsnums = [OBS.obsnum for OBS in OBSs]
		stdscr.addstr(curline,0,"Number of observations currently being processed {num}".format(num=len(obsnums)))
		curline += 1
		statusscr.erase()
		statusscr.addstr(0,0,"  ----  Still Idle  ----   ")
		for j,obsnum in enumerate(obsnums):
			try:
				host,path,filename= dbi.get_input_file(obsnum)
				status = dbi.get_obs_status(obsnum)
				still_host = dbi.get_obs_still_host(obsnum)
				current_pid = dbi.get_obs_pid(obsnum)
			except:
				host,path,filename = 'host','/path/to/','zen.2345672.23245.uv'
				status = 'WTF'
			col = int(j/statusscr.getmaxyx()[0])
			#print col*colwidth
			if j==0 or col==0:
				row = j
			else:
				row = j%statheight
			try:
				statusscr.addstr(row,col*colwidth,"{filename} {status} {still_host}".format(col=col,filename=os.path.basename(filename),status=status,still_host=still_host))
			except:
				continue
			#check for new filenames
			if filename not in file_pid.keys():
				file_pid.update({filename:current_pid})
				time_start = int(time.time())
				file_start.update({filename:time_start})
				file_end.update({filename:-1})
			if file_pid[filename] not in [current_pid]:
				time_end = int(time.time())
				file_end.update({filename:time_end})
				del_time = -1
				file_log.append((filename, status, del_time, file_start[filename], file_end[filename], still_host, time_date))
				file_pid.update({filename:current_pid})
				time_start = int(time.time())
				file_start.update({filename:time_start})
				file_end.update({filename:-1})
			if filename not in file_status.keys():
				file_status.update({filename:status})
				del_time = 0
				file_log.append((filename, status, del_time, file_start[filename], file_end[filename], still_host, time_date))
				file_time.update({filename:time.time()})
			#write output log
			if file_status[filename] not in [status]:
				del_time = time.time() - file_time[filename]
				file_log.append((filename, status, del_time, file_start[filename], file_end[filename], still_host, time_date))
				file_status.update({filename:status})
				file_time.update({filename:time.time()})
		pyg_dbi.add_monitor(*file_log)
		file_log = []
		s.close()
		statusscr.refresh()
		c = stdscr.getch()
		if c==ord('q'):
			break
		time.sleep(1)
except(KeyboardInterrupt):
	s.close()
	pass
#terminate
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()