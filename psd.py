#!/bin/env python3
from obspy import read
import obspy.core
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
import obspy.io.sac.sacpz as pz

import numpy as np
import matplotlib.pyplot as plt

import glob



st = read('RAW/*',debug_headers=True)
k=len(st)
i=0
while i < k:
	tr=st[i]
	print(tr.id,tr.stats.starttime.year,tr.stats.starttime.julday)
	### differential Volcity to Accerletion
	diftr=obspy.core.trace.Trace.differentiate(tr)

	### Pole and Zero
	chn=tr.stats.channel
	sta=tr.stats.station
	Ps="PZs/"+"*"+sta+"*"+"HHZ"+"*"
	HH_paz=glob.glob(Ps)
	pz.attach_paz(diftr,HH_paz[0])
	paz = dict(diftr.stats.paz)

	### power spectrum density
	ppsd = PPSD(diftr.stats, paz,ppsd_length=3600.0,overlap=0.95)
	ppsd.add(diftr)
	[t,amp]=ppsd.get_mode()
	
	### Output
	ts=str(tr.stats.starttime.year)+"."+str(tr.stats.starttime.julday)
	txt=sta+"."+chn+"."+ts+".txt"
	with open (txt,mode="w") as f:
		for j in range(len(t)):
			f.write("%e %6.2f\n" % (t[j], amp[j]))

	i+=1





