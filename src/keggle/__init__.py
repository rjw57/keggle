from __future__ import print_function

import logging
import numpy as np
import scipy.io as sio
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')

def parse_claims(input_csv_filename, days_y2_csv_filename, days_y3_csv_filename, output_mat_filename):
	input_csv = open(input_csv_filename)

	# Read the header line
	header = input_csv.readline()
	logging.info('CSV header: ' + header.strip())

	members = {}
	specialities = []
	places = []
	length_of_stays = []
	dsfss = []
	primary_condition_groups = []
	procedure_groups = []
	charlsons = []
	pay_delays = []

	logging.info('Reading: ' + input_csv_filename)
	for line in input_csv:
		(member_id, provider_id, vendor, pcp, year, speciality,
		 place_svc, pay_delay, length_of_stay, dsfs, primary_condition_group,
		 charlson, procedure_group, sup_los) = line.strip().split(',')

		year=int(year[1:]) # 1, 2 or 3

		# Record speciality in array if required
		try:
			speciality_idx = specialities.index(speciality)
		except ValueError:
			speciality_idx = len(specialities)
			specialities.append(speciality)

		# Record place in array if required
		try:
			place_idx = places.index(place_svc)
		except ValueError:
			place_idx = len(places)
			places.append(place_svc)

		# Record dsfs in array if required
		try:
			dsfs_idx = dsfss.index(dsfs)
		except ValueError:
			dsfs_idx = len(dsfss)
			dsfss.append(dsfs)

		# Record length_of_stay in array if required
		try:
			length_of_stay_idx = length_of_stays.index(length_of_stay)
		except ValueError:
			length_of_stay_idx = len(length_of_stays)
			length_of_stays.append(length_of_stay)

		# Record pay_delay in array if required
		try:
			pay_delay_idx = pay_delays.index(pay_delay)
		except ValueError:
			pay_delay_idx = len(pay_delays)
			pay_delays.append(pay_delay)

		# Record charlson in array if required
		try:
			charlson_idx = charlsons.index(charlson)
		except ValueError:
			charlson_idx = len(charlsons)
			charlsons.append(charlson)

		# Record primary_condition_group in array if required
		try:
			primary_condition_group_idx = primary_condition_groups.index(primary_condition_group)
		except ValueError:
			primary_condition_group_idx = len(primary_condition_groups)
			primary_condition_groups.append(primary_condition_group)

		# Record procedure_group in array if required
		try:
			procedure_group_idx = procedure_groups.index(procedure_group)
		except ValueError:
			procedure_group_idx = len(procedure_groups)
			procedure_groups.append(procedure_group)

		# Create a new member description if necessary
		if member_id not in members:
			members[member_id] = {
				'id': member_id,
				'claims': [[], [], []],
				'days': [0, 0, 0],
			}

		member_record = [
			int(provider_id) if len(provider_id) > 0 else 0,
			int(vendor) if len(vendor) > 0 else 0,
			int(pcp) if len(pcp) > 0 else 0,
			speciality_idx + 1, # 1-based indexing in MATLAB
			place_idx + 1, # 1-based indexing in MATLAB
			pay_delay_idx + 1,
			length_of_stay_idx + 1,
			dsfs_idx + 1,
			primary_condition_group_idx + 1, # 1-based indexing in MATLAB
			charlson_idx + 1,
			procedure_group_idx + 1, # 1-based indexing in MATLAB
			int(sup_los) if len(sup_los) > 0 else 0,
		]

		members[member_id]['claims'][year-1].append(member_record)
	
	# Parse days in hospital data
	for year in range(2,4):
		if year == 2:
			filename = days_y2_csv_filename
		elif year == 3:
			filename = days_y3_csv_filename
		else:
			raise RuntimeError('Unexpected year: %s' % (year,))

		logging.info('Reading: ' + filename)
		csv = open(filename)
		header = csv.readline()

		for line in csv:
			(member_id, claims_truncated, days) = line.strip().split(',')
			members[member_id]['days'][year-1] = int(days)

	
	logging.info('Found %i specialities.' % (len(specialities),))
	logging.info('Found %i places.' % (len(places),))
	logging.info('Found %i procedure groups.' % (len(procedure_groups),))
	logging.info('Writing output...')
	sio.savemat(output_mat_filename,
			{
				'members': np.array(members.values(), dtype=np.object),
				'specialities': np.array(specialities, dtype=np.object),
				'places': np.array(places, dtype=np.object),
				'dsfss': np.array(dsfss, dtype=np.object),
				'length_of_stays': np.array(length_of_stays, dtype=np.object),
				'primary_condition_groups': np.array(primary_condition_groups, dtype=np.object),
				'charlsons': np.array(charlsons, dtype=np.object),
				'pay_delays': np.array(pay_delays, dtype=np.object),
				'procedure_groups': np.array(procedure_groups, dtype=np.object),
			},
			oned_as='row', do_compression=True)

def main():
	if len(sys.argv) != 5:
		print('usage: ' + sys.argv[0] + ' claims.csv days_y2.csv days_y3.csv output.mat')
		sys.exit(1)
	
	parse_claims(*sys.argv[1:])

