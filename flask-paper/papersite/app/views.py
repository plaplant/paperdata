from flask import render_template, flash, redirect, url_for, request, g, make_response
from flask.ext.login import current_user
from app.flask_app import app, db
from app import models, db_utils, histogram_utils, data_sources
from datetime import datetime
import os
import paperdata_dbi as pdbi
import pyganglia as pyg
import time
from collections import OrderedDict

def time_val(value):
	#determines how much time to divide by
	time_val = 1 if value < 500 else 60 if value < 3600 else 3600 if value < 86400 else 86400
	return value / time_val

def str_val(value):
	#determines which time segment to use
	str_val = 'seconds' if value < 500 else 'minutes' if value < 3600 else 'hours' if value < 86400 else 'days'
	str_val = ' '.join(str_val, 'ago')
	return str_val

@app.route('/')
@app.route('/index')
@app.route('/index/set/<setName>')
@app.route('/set/<setName>')
def index(setName = None):
	active_data_sources = []

	if g.user is not None and g.user.is_authenticated():
		active_data_sources = g.user.active_data_sources

	if setName is not None:
		the_set = db_utils.query(database='eorlive', table='set', field_tuples=(('name', '==', setName),))[0]

		if the_set is not None:
			start_datetime, end_datetime = db_utils.get_datetime_from_gps(
				the_set.start, the_set.end)
			start_time_str_full = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
			end_time_str_full = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
			start_time_str_short = start_datetime.strftime('%Y/%m/%d %H:%M')
			end_time_str_short = end_datetime.strftime('%Y/%m/%d %H:%M')

			return render_template('index.html', the_set=the_set,
				start_time_str_full=start_time_str_full,
				end_time_str_full=end_time_str_full,
				start_time_str_short=start_time_str_short,
				end_time_str_short=end_time_str_short,
				active_data_sources=active_data_sources)
		else:
			flash('That set doesn\'t exist', 'error')

	return render_template('index.html', active_data_sources=active_data_sources)

@app.route('/get_graph')
def get_graph():
	graph_type_str = request.args.get('graphType')
	if graph_type_str is None:
		return make_response('No graph type', 500)

	data_source_str = request.args.get('dataSource')
	if data_source_str is None:
		return make_response('No data source', 500)

	data_source = db_utils.query(database='eorlive', table='graph_data_source', field_tuples=(('name', '==', data_source_str),))[0]

	set_str = request.args.get('set')

	template_name = ''.join(('js/', graph_type_str.lower(), '.js'))

	if set_str is None: # There should be a date range instead.
		start_time_str = request.args.get('start')
		end_time_str = request.args.get('end')
		if start_time_str is None or end_time_str is None:
			return make_response('No date range specified', 500)

		start_datetime = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M:%SZ')

		end_datetime = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M:%SZ')

		start_gps, end_gps = db_utils.get_gps_from_datetime(start_datetime, end_datetime)

		if graph_type_str == 'Obs_Err':
			return histogram_utils.get_obs_err_histogram(start_gps, end_gps, start_time_str, end_time_str)
		elif graph_type_str == 'File':
			return histogram_utils.get_file_histogram(start_gps, end_gps, start_time_str, end_time_str)
		else:
			graph_data = data_sources.get_graph_data(data_source_str, start_gps, end_gps, None)
			data_source_str_nospace = data_source_str.replace(' ', 'ಠ_ಠ')
			return render_template('graph.html',
				data_source_str=data_source_str, graph_data=graph_data,
				plot_bands=[], template_name=template_name, is_set=False,
				data_source_str_nospace=data_source_str_nospace,
				start_time_str_short=start_datetime.strftime('%Y-%m-%d %H:%M'),
				end_time_str_short=end_datetime.strftime('%Y-%m-%d %H:%M'),
				width_slider=data_source.width_slider)
	else:
		the_set = db_utils.query(database='eorlive', table='set', field_tuples=(('name', '==', set_str),))[0]

		if the_set is None:
			return make_response('Set not found', 500)

		plot_bands = histogram_utils.get_plot_bands(the_set)

		set_start, set_end = getattr(the_set, 'start'), getattr(the_set, 'end')
		start_datetime, end_datetime = db_utils.get_datetime_from_gps(set_start, set_end)

		start_time_str_short = start_datetime.strftime('%Y-%m-%d %H:%M')
		end_time_str_short = end_datetime.strftime('%Y-%m-%d %H:%M')

		if graph_type_str == 'Obs_Err':
			set_polarization, set_era, set_era_type = getattr(the_set, 'polarization'), getattr(the_set, 'era'), getattr(the_set, 'era_type')
			obs_count, obs_map = histogram_utils.get_observation_counts(set_start, set_end, set_polarization, set_era, set_era_type)
			error_counts = histogram_utils.get_error_counts(set_start, set_end)[0]
			range_end = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ') # For the function in histogram_utils.js
			which_data_set = data_sources.which_data_set(the_set)
			return render_template('setView.html', the_set=the_set,
									obs_count=obs_count, error_counts=error_counts,
									plot_bands=plot_bands, start_time_str_short=start_time_str_short,
									end_time_str_short=end_time_str_short, range_end=range_end,
									which_data_set=which_data_set, is_set=True, obs_map=obs_map)
		elif graph_type_str == 'File':
		else:
			graph_data = data_sources.get_graph_data(data_source_str, set_start, set_end, the_set)
			data_source_str_nospace = data_source_str.replace(' ', 'ಠ_ಠ')
			which_data_set = data_sources.which_data_set(the_set)
			return render_template('graph.html',
				data_source_str=data_source_str, graph_data=graph_data, plot_bands=plot_bands,
				template_name=template_name, is_set=True, data_source_str_nospace=data_source_str_nospace,
				width_slider=data_source.width_slider, the_set=the_set,
				which_data_set=which_data_set, start_time_str_short=start_time_str_short,
				end_time_str_short=end_time_str_short)

@app.route('/data_amount', methods = ['GET'])
def data_amount():
	data = db_utils.query(database='eorlive', table='data_amount', sort_tuples=(('created_on', 'desc'),))[0]

	data_time = hours_sadb = hours_paperdata = hours_with_data = 'N/A'

	if data is not None:
		data_time = getattr(data, 'created_on')
		hours_sadb = getattr(data, 'hours_sadb')
		hours_paperdata = getattr(data, 'hours_paperdata')
		hours_with_data = getattr(data, 'hours_with_data')

	return render_template('data_amount_table.html', data_time=data_time,
							hours_sadb=hours_sadb, hours_paperdata=hours_paperdata,	hours_with_data=hours_with_data, data_time=data_time)

@app.route('/source_table', methods = ['GET'])
def source_table():
	sort_tuples = (('timestamp', 'desc'),)
	output_vars = ('timestamp', 'julian_day')
	
	corr_source = db_utils.query(database='paperdata', table='rtp_file',
										field_tuples=(('transferred', '==', None),),
										sort_tuples=sort_tuples, output_vars=output_vars)[0]

	rtp_source = db_utils.query(database='paperdata', table='rtp_file',
										field_tuples=(('transferred', '==', True),),
										sort_tuples=sort_tuples, output_vars=output_vars)[0]

	paper_source = db_utils.query(database='paperdata', table='observation',
										sort_tuples=sort_tuples, output_vars=output_vars)[0]

	source_tuples = (('Correlator', corr_source), ('RTP', rtp_source), ('Folio Scan', paper_source))
	source_names = (source_name for source_name, _ in source_tuples)
	source_dict = {source_name: {'time': 'N/A', 'day': 'N/A', 'time_segment': 'N/A'} for source_name in source_names}

	for source_name, source in source_tuples:
		if source is not None:
			source_time = int(time.time() - getattr(source, 'timestamp'))

			#limiting if seconds or minutes or hours shows up on last report
			source_dict[source_name]['time_segment'] = str_val(source_time)
			source_dict[source_name]['time'] = time_val(source_time)
			source_dict[source_name]['day'] = getattr(source, 'julian_day')

	return render_template('source_table.html', source_names=source_names, source_dict=source_dict)

@app.route('/filesystem', methods = ['GET'])
def filesystem():
	systems = db_utils.query(database='ganglia', table='filesystem',
										sort_tuples=(('timestamp', 'desc'), ('host', 'asc')),
										group_tuples=('host',), output_vars=('host', 'timestamp', 'percent_space'))

	system_names = (getattr(system, 'host') for system in systems)
	system_dict = {system_name: {'time': 'N/A', 'space': 100.0, 'time_segment': 'N/A'} for system_name in system_names}

	for system in systems:
		if system is not None:
			system_time = int(time.time() - getattr(system, 'timestamp'))

			#limiting if seconds or minutes or hours shows up on last report
			system_dict[system_name]['time_segment'] = str_val(system_time)
			system_dict[system_name]['time'] = time_val(system_time)
			system_dict[system_name]['space'] = getattr(system, 'percent_space')

	return render_template('filesystem_table.html', system_names=system_names, system_dict=system_dict)

@app.route('/error_table', methods = ['POST'])
def error_table():
	starttime = datetime.utcfromtimestamp(int(request.form['starttime']) / 1000)

	endtime = datetime.utcfromtimestamp(int(request.form['endtime']) / 1000)

	start_gps, end_gps = db_utils.get_gps_from_datetime(starttime, endtime)

	obscontroller_response = db_utils.query(database='eor', table='obscontroller_log',
														(('reference_time', '>=', start_gps), ('reference_time', '<=', end_gps)),
														sort_tuples=(('reference_time', 'asc'),),
														output_vars=('reference_time', 'observation_number', 'comment'))

	recvstatuspolice_response = db_utils.query(database='eor', table='recvstatuspolice_log',
														(('reference_time', '>=', start_gps), ('reference_time', '<=', end_gps)),
														sort_tuples=(('reference_time', 'asc'),),
														output_vars=('reference_time', 'observation_number', 'comment'))

	return render_template('error_table.html', obscontroller_error_list=obscontroller_response,
							recvstatuspolice_error_list=recvstatuspolice_response,
							start_time=starttime.strftime('%Y-%m-%dT%H:%M:%SZ'),
							end_time=endtime.strftime('%Y-%m-%dT%H:%M:%SZ'))

@app.before_request
def before_request():
	g.user = current_user
	paper_dbi = pdbi.DataBaseInterface()
	pyg_dbi = pyg.DataBaseInterface()
	try :
		g.paper_session = paper_dbi.Session()
		g.pyg_session = pyg_dbi.Session()
		g.eorlive_session = db.session
	except Exception as e:
		print('Cannot connect to database - {e}'.format(e))

@app.teardown_request
def teardown_request(exception):
	paper_db = getattr(g, 'paper_session', None)
	pyg_db = getattr(g, 'pyg_session', None)
	eorlive_db = getattr(g, 'eorlive_session', None)
	db_list = (paper_db, pyg_db, eorlive_db)
	for open_db in db_list:
		if open_db is not None:
			open_db.close()

@app.route('/profile')
def profile():
	if (g.user is not None and g.user.is_authenticated()):
		user = db_utils.query(database='eorlive', table='user',	field_tuples=(('username', '==', g.user.username),),)[0]

		setList = db_utils.query(database='eorlive', table='set', field_tuples=(('username', '==', g.user.username),))[0]

		return render_template('profile.html', user=user, sets=setList)
	else:
		return redirect(url_for('login'))

@app.route('/user_page')
def user_page():
	if (g.user is not None and g.user.is_authenticated()):
		user = db_utils.query(database='eorlive', table='user',	field_tuples=(('username', '==', g.user.username),))[0]

		userList = db_utils.query(database='eorlive', table='user')[0]

		setList = db_utils.query(database='eorlive', table='set')[0]

		return render_template('user_page.html', theUser=user, userList=userList, setList=setList)
	else:
		return redirect(url_for('login'))

@app.route('/data_summary_table', methods=['POST'])
def data_summary_table():
	#table that shows on side of website under login
	starttime = request.form['starttime']
	endtime = request.form['endtime']

	startdatetime = datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ')
	enddatetime = datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')

	start_gps, end_gps = db_utils.get_gps_from_datetime(startdatetime, enddatetime)

	response = db_utils.query(database='paperdata', table='observation',
										field_tuples=(('time_start', '>=', start_gps), ('time_end', '<=', end_gps),
										sort_tuples=(('time_start', 'asc'),),
										output_vars=('time_start', 'time_end', 'polarization', 'era', 'era_type')))

	pol_strs = ('xx', 'xy', 'yx', 'yy')
	era_strs = (32, 64, 128)
	obs_map = {pol_str: {era_str: {'obs_count': 0, 'obs_hours': 0} for era_str in era_strs} for pol_str in pol_strs}

	for obs in response:
		polarization = getattr(obs, 'polarization')
		era = getattr(obs, 'era')
		era_type = getattr(obs, 'era_type')

		# Actual UTC time of the obs (for the graph)
		obs_start = getattr(obs, 'time_start')
		obs_end = getattr(obs, 'time_end')

		obs_map[polarization][era]['obs_count'] += 1
		obs_map[polarization][era]['obs_hours'] += (obs_end - obs_start) / 3600.0

	all_strs = pol_strs + era_strs
	obs_total = {all_str: {'count':0, 'hours':0} for all_str in all_strs}

	for pol_era, obs_dict in obs_map.iteritems():
		for pol, era in pol_era.split('-'):
			obs_total[era]['count'] += obs_dict['obs_count']
			obs_total[era]['hours'] += obs_dict['obs_hours']
			obs_total[pol]['count'] += obs_dict['obs_count']
			obs_total[pol]['hours'] += obs_dict['obs_hours']

	error_counts, error_count = histogram_utils.get_error_counts(start_gps, end_gps)

	return render_template('summary_table.html', error_count=error_count, pol_strs=pol_strs, era_strs=era_strs,
													obs_map=obs_map, obs_total=obs_total)
