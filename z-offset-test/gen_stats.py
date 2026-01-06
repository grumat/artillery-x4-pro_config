#!py -3
# This work is derived from `probe_accuracy.py` and customizes the 
# results for my Wiki page.
#
# spellchecker:words ztrace zstddevtrace btrace btemp bset bstrace etemp eset etrace atherms estrace rangemode showlegend tozero tozeroy zrange

import argparse
import json
import os
import math
from statistics import pstdev, fmean

import plotly.graph_objects as pgo
from plotly.subplots import make_subplots

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Samples to evaluate for power transitions
OFFSET_POWER = 20
# Samples to evaluate for temperature offset shifts
OFFSET_TEMP = 30

parser = argparse.ArgumentParser()
parser.add_argument('--data', default='./data/probe_accuracy_0.json')
parser.add_argument('--out', default='./data/probe_accuracy_0.jpg')
parser.add_argument('--title', default='Probe Accuracy: Standard')
parser.add_argument('--alt', action='store_true')


class HeatSoak(object):
	"""Computes heat soak values for phase having heat bead and hot end active"""
	def __init__(self, soak_time : int) -> None:
		self.soak_time = soak_time
		self.sd = 0.0
		self.diff = 0.0
		self.avg = 0.0
	def ComputeSoak(self, data : list[tuple[float, float]], cold : float, z_min : float):
		offset = data[0][0]
		start = self.soak_time * 60.0 + offset
		samples = [z for ts, z in data if ts >= start]
		self.sd = pstdev(samples)
		self.diff = max(samples) - min(samples)
		self.avg = fmean(samples)
		self.displace = self.avg - cold
		self.displace0 = self.avg - z_min
	def Print(self):
		if self.soak_time == 0:
			print("Total")
		else:
			print(f"After {self.soak_time} min")
		print(f"    Z avg = {self.avg:6.4f} mm")
		print(f"    Z disp = {self.displace:6.4f} mm")
		print(f"    Z stdev = {1000.0 * self.sd:6.4f} µm")
		print(f"    Z diff = {1000.0 * self.diff:6.4f} µm")


class SoakStats(object):
	def __init__(self, z_min : float, cold :list[float], data : list[tuple[float, float]]) -> None:
		self.z_min = z_min
		self.cold = cold
		self.cold_avg = fmean(cold)
		self.data = data
		self.total = HeatSoak(0)
		self.m1 = HeatSoak(1)
		self.m2 = HeatSoak(2)
		self.m3 = HeatSoak(3)
		self.m5 = HeatSoak(5)
		self.m10 = HeatSoak(10)
		self.total.ComputeSoak(data, self.cold_avg, z_min)
		self.m1.ComputeSoak(data, self.cold_avg, z_min)
		self.m2.ComputeSoak(data, self.cold_avg, z_min)
		self.m3.ComputeSoak(data, self.cold_avg, z_min)
		self.m5.ComputeSoak(data, self.cold_avg, z_min)
		self.m10.ComputeSoak(data, self.cold_avg, z_min)
	def Print(self):
		print("===Heat Soak Statistics===")
		self.total.Print()
		self.m1.Print()
		self.m2.Print()
		self.m3.Print()
		self.m5.Print()
		self.m10.Print()



def load_data(data_file: str) -> list:
	if not os.path.isabs(data_file):
		data_file = os.path.normpath(os.path.join(SCRIPT_DIR, data_file))
	with open(data_file, 'r') as f:
		return [json.loads(line) for line in f]


def write_chart(data: list, output_file: str, chart_title: str, alt : bool, soak_stats : SoakStats):

	if not os.path.isabs(output_file):
		output_file = os.path.normpath(os.path.join(SCRIPT_DIR, output_file))

	min_ts = data[0]['ts']

	z_min = min([x['z'] for x in data if 'z' in x])
	
	ztrace = pgo.Scatter(
		x=[x['ts'] - min_ts for x in data if 'z' in x],
		y=[(x['z'] - z_min) for x in data if 'z' in x],
		name='Z',
		mode='lines',
		line={'color': 'black'},
		yaxis='y2'
	)
	assert ztrace is not None, "Unknown error on plotly"
	assert ztrace.y is not None, "Unknown error on plotly"

	z_max = max(ztrace.y)
	z_hi = 0.3
	while z_hi < z_max:
		z_hi += 0.2
	
	sdy_local = [pstdev(ztrace.y[i-9:i+1]) * 1000 for i, ts in enumerate(ztrace.y) if i >= 9]
	final = fmean(sdy_local)
	dif_local = [(max(ztrace.y[i-9:i+1]) - min(ztrace.y[i-9:i+1])) for i, ts in enumerate(ztrace.y) if i >= 9]
	dif_local = fmean(dif_local)

	zstddevtrace = pgo.Scatter(
		x=[ts for i, ts in enumerate(ztrace.x) if i >= 4],
		y=[pstdev(ztrace.y[i-4:i+1]) * 1000 for i, ts in enumerate(ztrace.y) if i >= 4],
		name='Z stddev',
		mode='markers',
		line={'color': 'gray'},
		yaxis='y3'
	)

	btrace = pgo.Scatter(
		x=[x['ts'] - min_ts for x in data if 'btemp' in x],
		y=[x['btemp'] for x in data if 'btemp' in x],
		name='bed temperature',
		mode='lines',
		line={'color': 'blue'}
	)
	bstrace = pgo.Scatter(
		x=[x['ts'] - min_ts for x in data if 'bset' in x],
		y=[x['bset'] for x in data if 'bset' in x],
		showlegend=False,
		mode='none',
		fill='tozeroy',
		fillcolor='rgba(128,128,255,0.3)'
	)

	etrace = pgo.Scatter(
		x=[x['ts'] - min_ts for x in data if 'etemp' in x],
		y=[x['etemp'] for x in data if 'etemp' in x],
		name='extruder temperature',
		mode='lines',
		line={'color': 'red'}
	)
	estrace = pgo.Scatter(
		x=[x['ts'] - min_ts for x in data if 'eset' in x],
		y=[x['eset'] for x in data if 'eset' in x],
		showlegend=False,
		mode='none',
		fill='tozeroy',
		fillcolor='rgba(255,128,128,0.3)'
	)

	layout = pgo.Layout(
		autosize=False,
		width=1280,
		height=600
	)
	fig = pgo.Figure(layout=layout)
	fig.add_trace(ztrace)
	fig.add_trace(zstddevtrace)
	fig.add_trace(btrace)
	fig.add_trace(bstrace)
	fig.add_trace(etrace)
	fig.add_trace(estrace)

	thermistors_xy = {}
	for d in data:
		if not 'atherms' in d:
			continue

		ts = d['ts'] - min_ts
		for ad in d['atherms']:
			therm_id = ad['id']
			temp = ad['temp']
			try:
				thermistors_xy[therm_id]['x'].append(ts)
				thermistors_xy[therm_id]['y'].append(temp)
			except KeyError:
				thermistors_xy[therm_id] = {
					'x': [ts],
					'y': [temp]
				}

	for therm_id, xy in thermistors_xy.items():
		trace = pgo.Scatter(
			x=xy['x'],
			y=xy['y'],
			name=f'{therm_id} temperature',
			mode='lines'
		)
		fig.add_trace(trace)

	if alt:
		zrange = None
	else:
		zrange = [-0.1,z_hi]

	fig.update_layout(
		title=dict(
			text=chart_title
		),
		legend=dict(
			x=1.1
		),
		xaxis=dict(
			title='seconds',
			domain=[0, 0.9]
		),
		yaxis=dict(
			title='°C',
		),
		yaxis2=dict(
			title='Z10+ diff = {:.5f} (mm)'.format(1000.0 * soak_stats.m10.diff),
			anchor='x',
			overlaying='y',
			side='right',
			position=0.9,
			range=zrange
		),
		yaxis3=dict(
			title='Z10+ stddev = {:.2f} µm'.format(1000.0 * soak_stats.m10.sd),
			rangemode='tozero',
			anchor='free',
			overlaying='y',
			side='right',
			position=1.0,
			range=[0,20]
		),
	)

	fig.write_image(output_file)


def real_world_stats(data : list) -> SoakStats:
	"Only the phase where heat-bed and hot-end are on are actually important"
	min_ts = data[0]['ts']
	cold_ts = min_ts + 5*60.0
	start_found = False
	cold = []
	samples = []
	for i, rec in enumerate(data):
		if "etemp" in rec:
			if not start_found:
				if rec["eset"] != 0.0:
					# Start of phase 3 with stable temp
					if abs(rec["etemp"] - rec["eset"]) <= 1.0:
						start_found = True
			elif rec["eset"] == 0.0:
				# End of phase 3
				break
		if "z" in rec:
			ts = rec["ts"]
			z = rec["z"]
			if (ts <= cold_ts):
				cold.append(z)
			if start_found:
				samples.append((ts, z))
	z_min = min([x['z'] for x in data if 'z' in x])
	return SoakStats(z_min, cold, samples)




def moving_stats(col : list):
	sdy = [pstdev(col[i-9:i+1]) * 1000 for i, ts in enumerate(col) if i >= 9]
	sdy = fmean(sdy)
	dif = [(max(col[i-9:i+1]) - min(col[i-9:i+1])) for i, ts in enumerate(col) if i >= 9]
	dif = fmean(dif) * 1000.0
	return sdy, dif


def print_stats(data : list, title : str):
	min_ts = data[0]['ts']
	start_btemp = data[0]['btemp']
	start_etemp = data[0]['etemp']

	print('{:}\n'.format(title))
	print('Start Condition:')
	print('- Bed Temperature: {:.1f}'.format(start_btemp))
	print('- Nozzle Temperature: {:.1f}'.format(start_etemp))
	print()

	cur_t = 0.0
	phase = 1
	phase1 = []
	cold_bed_level = []
	before_bed = []
	cold_watch = 2 * 60.0
	phase2 = []
	hot_bed_level = []
	hot_bed_watch = 12 * 60.0
	after_bed = []
	hot_bed_final_level = []
	hot_bed_final_watch = 35 * 60.0
	before_nozzle = []
	phase3 = []
	hot_nozzle_level = []
	hot_nozzle_watch = 39 * 60.0
	hot_nozzle_final_level = []
	hot_nozzle_final_watch = 51 * 60.0
	after_nozzle = []
	phase4 = []
	all_z = []
	for d in data:
		if 'z' in d:
			z = d['z']
			all_z.append(z)
			if phase == 1:
				phase1.append(z)
				if (cold_watch < cur_t) and len(cold_bed_level) < OFFSET_TEMP:
					cold_bed_level.append(z)
			elif phase == 2:
				phase2.append(z)
				if len(after_bed) < OFFSET_POWER:
					after_bed.append(z)
				if (hot_bed_watch < cur_t) and len(hot_bed_level) < OFFSET_TEMP:
					hot_bed_level.append(z)
				if (hot_bed_final_watch < cur_t) and len(hot_bed_final_level) < OFFSET_TEMP:
					hot_bed_final_level.append(z)
			elif phase == 3:
				phase3.append(z)
				if len(after_nozzle) < OFFSET_POWER:
					after_nozzle.append(z)
				if (hot_nozzle_watch > 0.0) and (hot_nozzle_watch < cur_t) and len(hot_nozzle_level) < OFFSET_TEMP:
					hot_nozzle_level.append(z)
				if (hot_nozzle_final_watch > 0.0) and (hot_nozzle_final_watch < cur_t) and len(hot_nozzle_final_level) < OFFSET_TEMP:
					hot_nozzle_final_level.append(z)
			else:
				phase4.append(z)
		else:
			cur_t = d['ts'] - min_ts
			if d['bset'] == 0.0:
				if phase > 1:
					phase = 4
			elif d['eset'] == 0.0:
				phase = 2
				if not before_bed:
					before_bed = all_z[-OFFSET_POWER:]
			else:
				phase = 3
				if not before_nozzle:
					before_nozzle = all_z[-OFFSET_POWER:]
				if hot_nozzle_watch == 0.0:
					hot_nozzle_watch = cur_t + 60.0
					hot_nozzle_final_watch = cur_t + (13 * 60.0)


	# Moving window
	sdy, dif = moving_stats(all_z)
	sdy1, dif1 = moving_stats(phase1)
	sdy2, dif2 = moving_stats(phase2)
	sdy3, dif3 = moving_stats(phase3)
	sdy4, dif4 = moving_stats(phase4)

	print('Stats for Moving Window of 10 Consecutive Elements:')
	print('- Total Diff/StdDev: {:.2f} µm / {:.2f} µm'.format(dif, sdy))
	print('- Phase 1 Diff/StdDev: {:.2f} µm / {:.2f} µm'.format(dif1, sdy1))
	print('- Phase 2 Diff/StdDev: {:.2f} µm / {:.2f} µm'.format(dif2, sdy2))
	print('- Phase 3 Diff/StdDev: {:.2f} µm / {:.2f} µm'.format(dif3, sdy3))
	print('- Phase 4 Diff/StdDev: {:.2f} µm / {:.2f} µm'.format(dif4, sdy4))
	print()

	bed_power = (fmean(after_bed) - fmean(before_bed)) * 1000
	nozzle_power = (fmean(after_nozzle) - fmean(before_nozzle)) * 1000
	cold = fmean(cold_bed_level) * 1000
	bed_warm = fmean(hot_bed_level) * 1000
	bed_long_warm = fmean(hot_bed_final_level) * 1000
	nozzle_warm = fmean(hot_nozzle_level) * 1000
	nozzle_long_warm = fmean(hot_nozzle_final_level) * 1000
	print('Offset Shift for Power Supply Load:')
	print('- Bed Power On: {:.2f}'. format(bed_power))
	print('- Nozzle Power On: {:.2f}'. format(nozzle_power))
	print()
	print('Offset Shift By Test Duration:')
	print('- Reference (2 min): {:.2f} µm'. format(cold))
	print('- dZ @12 min: {:.2f} µm'. format(bed_warm - cold))
	print('- dZ @35 min: {:.2f} µm'. format(bed_long_warm - bed_warm))
	print('- dZ @41 min: {:.2f} µm'. format(nozzle_warm - bed_long_warm))
	print('- dZ @54 min: {:.2f} µm'. format(nozzle_long_warm - nozzle_warm))
	print('\n')

	print('For tab:')
	print('{:.1f}'.format(start_btemp))
	print('{:.1f}'.format(start_etemp))
	print('{:.2f}'.format(dif1))
	print('{:.2f}'.format(dif2))
	print('{:.2f}'.format(dif3))
	print('{:.2f}'.format(dif4))
	print('{:.2f}'.format(dif))
	print('{:.2f}'.format(sdy1))
	print('{:.2f}'.format(sdy2))
	print('{:.2f}'.format(sdy3))
	print('{:.2f}'.format(sdy4))
	print('{:.2f}'.format(sdy))
	print('{:.2f}'.format(bed_power))
	print('{:.2f}'.format(nozzle_power))
	print('{:.2f}'.format(cold))
	print('{:.2f}'.format(bed_warm - cold))
	print('{:.2f}'.format(bed_long_warm - bed_warm))
	print('{:.2f}'.format(nozzle_warm - bed_long_warm))
	print('{:.2f}'.format(nozzle_long_warm - nozzle_warm))
	print('\n')


def main():
	args = parser.parse_args()

	data = load_data(args.data)
	soak_stats = real_world_stats(data)

	write_chart(data, args.out, args.title, args.alt, soak_stats)
	print_stats(data, args.title)

	soak_stats.Print()
	print()
	print()


if __name__ == '__main__':
	main()
