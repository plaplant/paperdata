from app import db_utils, models
from app.flask_app import app, db
from flask import request, g, make_response, jsonify, render_template
from datetime import datetime

def insert_set_into_db(name, start, end, flagged_range_dicts, polarization, era, era_type, total_data_hrs, flagged_data_hrs):
	new_set = getattr(models, 'Set')()
	setattr(new_set, 'username', g.user.username)
	setattr(new_set, 'name', name)
	setattr(new_set, 'start', start)
	setattr(new_set, 'end', end)
	setattr(new_set, 'polarization', polarization)
	setattr(new_set, 'era_type', era_type)
	setattr(new_set, 'host', host)
	setattr(new_set, 'filetype', filetype)
	setattr(new_set, 'total_data_hrs', total_data_hrs)
	setattr(new_set, 'flagged_data_hrs', flagged_data_hrs)

	db.session.add(new_set)
	db.session.flush()
	db.session.refresh(new_set) # So we can get the set's id

	for flagged_range_dict in flagged_range_dicts:
		flagged_subset = getattr(models, 'Flagged_Subset')()
		setattr(flagged_subset, 'set_id', getattr(new_set, 'id'))
		setattr(flagged_subset, 'start', flagged_range_dict['start_gps'])
		setattr(flagged_subset, 'end', flagged_range_dict['end_gps'])

		db.session.add(flagged_subset)
		db.session.flush()
		db.session.refresh(flagged_subset) # So we can get the id

		for obs_id in flagged_range_dict['flaggedRange']:
			flagged_obs_id = getattr(models, 'Flagged_Obs_Ids')()
			setattr(flagged_obs_id, 'obs_id', obs_id)
			setattr(flagged_obs_id, 'flagged_subset_id', getattr(flagged_subset, 'id'))

			db.session.add(flagged_obs_id)

	db.session.commit()

def is_obs_flagged(obs_id, flagged_range_dicts):
	for flagged_range_dict in flagged_range_dicts:
		if obs_id >= flagged_range_dict['start_gps'] and obs_id <= flagged_range_dict['end_gps']:
			return True
	return False

def get_data_hours_in_set(start, end, polarization, era_type, flagged_range_dicts):
	total_data_hrs = flagged_data_hrs = 0

	all_obs_ids_tuples = db_utils.query(database='paperdata', table='observation',
										field_tuples=(('time_start', '>=', start), ('time_end', '<=', end),
										('polarization', None if polarization == 'all' else '==', polarization),
										('era_type', None if era_type == 'all' else '==', era_type)),
										sort_tuples=(('time_start', 'asc'),), output_vars=('time_start', 'time_end'))
	for times in all_obs_ids_tuples:
		time_start = getattr(time, 'time_start')
		time_end = getattr(time, 'time_end')
		data_hrs = (time_start - time_end) / 3600
		total_data_hrs += data_hrs
		if is_obs_flagged(obs_id, flagged_range_dicts):
			flagged_data_hrs += data_hrs

	return (total_data_hrs, flagged_data_hrs)

@app.route('/save_new_set', methods=['POST'])
def save_new_set():
	if (g.user is not None and g.user.is_authenticated()):
		request_content = request.get_json()

		name = request_content['name']

		if name is None:
			return jsonify(error=True, message='Name cannot be empty.')

		name = name.strip()

		if len(name) == 0:
			return jsonify(error=True, message='Name cannot be empty.')

		sets = db_utils.query(database='eorlive', table='set', field_tuples=(('name', '>=', name),))
		if len(sets) > 0:
			return jsonify(error=True, message='Name must be unique.')

		flagged_range_dicts = []

		GPS_LEAP_SECONDS_OFFSET, GPS_UTC_DELTA = db_utils.get_gps_utc_constants()

		for flagged_range_dict in request_content['flaggedRanges']:
			flagged_gps_dict = {}
			flagged_gps_dict['flaggedRange'] = [pair[1] for pair in flagged_range_dict['flaggedRange']]
			flagged_gps_dict['start_gps'] = int(flagged_range_dict['start_millis'] / 1000) +\
				GPS_LEAP_SECONDS_OFFSET - GPS_UTC_DELTA
			flagged_gps_dict['end_gps'] = int(flagged_range_dict['end_millis'] / 1000) +\
				GPS_LEAP_SECONDS_OFFSET - GPS_UTC_DELTA
			flagged_range_dicts.append(flagged_gps_dict)

		start_gps = request_content['startObsId']
		end_gps = request_content['endObsId']
		polarization = request_content['polarization']
		era_type = request_content['era_type']
		host = request_content['host']
		filetype = request_content['filetype']

		total_data_hrs, flagged_data_hrs = get_data_hours_in_set(start_gps, end_gps, polarization, era_type, flagged_range_dicts)

		insert_set_into_db(name, start_gps, end_gps, flagged_range_dicts,
							polarization, era_type, host, filetype, total_data_hrs, flagged_data_hrs)

		return jsonify()
	else:
		return make_response('You need to be logged in to save a set.', 401)

@app.route('/upload_set', methods=['POST'])
def upload_set():
	if (g.user is not None and g.user.is_authenticated()):
		set_name = request.form['set_name']

		if set_name is None:
			return jsonify(error=True, message='Name cannot be empty.')

		set_name = set_name.strip()

		if len(set_name) == 0:
			return jsonify(error=True, message='Name cannot be empty.')

		sets = db_utils.query(database='eorlive', table='set', field_tuples=(('name', '==', set_name),))
		if len(sets) > 0:
			return jsonify(error=True, message='Name must be unique.')

		f = request.files['file']

		good_obs_ids = []

		for line in f.stream:
			line = str(line.decode('utf-8').strip())
			if line == '':
				continue
			try:
				obs_id = int(line)
				good_obs_ids.append(obs_id)
			except ValueError as ve:
				return jsonify(error=True, message=''.join('Invalid content in file: ', line))

		good_obs_ids.sort()

		start_gps = good_obs_ids[0]
		end_gps = good_obs_ids[len(good_obs_ids) - 1]

		polarization = request.form['polarization']
		era_type = request.form['era_type']
		host = request.form['host']
		filetype = request.form['filetype']

		all_obs_ids_tuples = db_utils.query(database='paperdata', table='observation',
										field_tuples=(('time_start', '>=', start_gps), ('time_end', '<=', end_gps),
										('polarization', None if polarization == 'all' else '==', polarization),
										('era_type', None if era_type == 'all' else '==', era_type)),
										sort_tuples=(('time_start', 'asc'),), output_vars=('obsnum',))

		all_obs_ids = [getattr(obs, 'obsnum') for obs in all_obs_ids_tuples]

		last_index = 0

		bad_ranges = []

		for good_obs_id in good_obs_ids:
			try:
				next_index = all_obs_ids.index(good_obs_id)
			except ValueError as e:
				return jsonify(error=True, message=''.join('''Obs ID {obsnum}
						not found in the set of observations corresponding
						to Polarization: {polarization} and ERA_TYPE: {era_type}'''\
						.format(obsnum=good_obs_id, polarization=polarization, era_type=era_type)))
			if next_index > last_index:
				bad_range_dict = {}
				bad_range_dict['start_gps'] = all_obs_ids[last_index]
				bad_range_dict['end_gps'] = all_obs_ids[next_index - 1]
				bad_range_dict['flaggedRange'] = all_obs_ids[last_index:next_index]
				bad_ranges.append(bad_range_dict)

			last_index = next_index + 1

		total_data_hrs, flagged_data_hrs = get_data_hours_in_set(start_gps, end_gps, polarization, era_type, bad_ranges)

		insert_set_into_db(set_name, start_gps, end_gps, bad_ranges, polarization, era_type, host, filetype, total_data_hrs, flagged_data_hrs)

		return 'OK'
	else:
		return make_response('You need to be logged in to upload a set.', 401)

@app.route('/download_set')
def download_set():
	set_id = request.args['set_id']

	the_set = db_utils.query(database='eorlive', table='set',
											field_tuples=(('id', '==', set_id),),)[0]

	if the_set is not None:
		flagged_subsets = db_utils.query(database='eorlive', table='flagged_subset', field_tuples=(('set_id', '==', getattr(the_set, 'id')),),)

		polarization = getattr(the_set, 'polarization')
		era_type = getattr(the_set, 'era_type')
		host = getattr(the_set, 'host')
		filetype = getattr(the_set, 'filetype')

		all_obs_ids_tuples = db_utils.query(database='paperdata', table='observation',
										field_tuples=(('time_start', '>=', start_gps), ('time_end', '<=', end_gps),
										('polarization', None if polarization == 'all' else '==', polarization),
										('era_type', None if era_type == 'all' else '==', era_type)),
										sort_tuples=(('time_start', 'asc'),), output_vars=('obsnum',))

		all_obs_ids = [getattr(obs, 'obsnum') for obs in all_obs_ids_tuples]

		good_obs_ids_text_file = ''

		for obs_id in all_obs_ids:
			good = True # assume obs_id is good
			for flagged_subset in flagged_subsets:
				if obs_id >= getattr(flagged_subset, 'start') and obs_id <= getattr(flagged_subset, 'end'): # obs_id is flagged, so it's not good
					good = False
					break
			if good:
				good_obs_ids_text_file = ''.join(good_obs_ids_text_file, str(obs_id), '\n')

		response = make_response(good_obs_ids_text_file)
		filename = ''.join(the_set.name.replace(' ', '_'), '.txt')
		response.headers['Content-Disposition'] = ''.join('attachment; filename=', filename)
		return response
	else:
		return make_response('That set was not found.', 500)

@app.route('/get_filters')
def get_filters():
	users = db_utils.query(database='eorlive', table='user')
	return render_template('filters.html', users=users)

@app.route('/get_sets', methods = ['POST'])
def get_sets():
	if (g.user is not None and g.user.is_authenticated()):
		request_content = request.get_json()
		set_controls = request_content['set_controls']
		username = set_controls['user']
		polarization = set_controls['polarization']
		era_type = set_controls['era_type']
		host = set_controls['host']
		filetype = set_controls['filetype']
		sort = set_controls['sort']
		ranged = set_controls['ranged']

		if ranged:
			start_utc = request_content['starttime']
			end_utc = request_content['endtime']
			start_datetime = datetime.strptime(start_utc, '%Y-%m-%dT%H:%M:%SZ')
			end_datetime = datetime.strptime(end_utc, '%Y-%m-%dT%H:%M:%SZ')
			start_gps, end_gps = db_utils.get_gps_from_datetime(start_datetime, end_datetime)

		field_tuples = (('username', '==' if username else None, username),
							('polarization', '==' if polarization else None, polarization),
							('era_type', '==' if era_type else None, era_type),
							('host', '==' if host else None, host),
							('filetype', '==' if filetype else None, filetype),
							('start', '>=' if ranged else None, start_gps),
							('end', '>=' if ranged else None, end_gps))
	
		sort_tuples = None
		if sort:
			if sort == 'hours'
				sort_tuples = (('total_data_hrs', 'desc'),)
			elif sort == 'time':
				sort_tuples = (('created_on', 'desc'),)

		setList = db_utils.query(database='eorlive', table='set', field_tuples=field_tuples, sort_tuples=sort_tuples)

		include_delete_buttons = request_content['includeDeleteButtons']

		return render_template('setList.html', sets=setList, include_delete_buttons=include_delete_buttons)
	else:
		return render_template('setList.html', logged_out=True)

@app.route('/delete_set', methods = ['POST'])
def delete_set():
	if (g.user is not None and g.user.is_authenticated()):
		set_id = request.form['set_id']

		theSet = db_utils.query(database='eorlive', table='set', field_tuples=(('id', '==', set_id),),)[0]

		db.session.delete(theSet)
		db.session.commit()
		return 'Success'
	else:
		return redirect(url_for('login'))
