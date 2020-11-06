#!/usr/bin/env python3
#-*- coding: utf-8 -*-
from obspy import UTCDateTime
import numpy as np
import glob , os , sys
from obspy import read 
from obspy.signal.rotate import rotate_ne_rt
import pandas as pd
import matplotlib.pyplot as plt

def sac_read (eve):
    st=read(eve)
    sta=st[0].stats.station
    r_file=str(eve).replace('HZ','HR');t_file=str(eve).replace('HZ','HT')
    st+=read(glob.glob(r_file)[0]); st+=read(glob.glob(t_file)[0])
    stf=st.copy()
    return stf

def checkData(stf):
    sta=stf[0].stats.station
    if os.path.isfile('t1.log'):
        try:
            global t1catalog
            t1=t1catalog.loc[sta].t1
            a=1
        except:
            sta1="*"+sta+"*"
            for mm in glob.glob(sta1):
                os.remove(mm)
            a=0
    else:
        try :
            vname='dsp.'+sta+".*.dif"
            st=read(glob.glob(vname)[0])
            t9=st[0].stats.sac.t9
            sta1="*"+sta+"*"
            for mm in glob.glob(sta1):
                os.remove(mm)
            a=0
        except:
            a=1

    
    return a

def correct_t1t2(stf,timeshift=300):
    t2=float(f"{stf[0].stats.sac.t2-timeshift:.3f}")
    sta=stf[0].stats.station

    ###  
    if os.path.isfile('t1.log'):
        global t1catalog
        t1=t1catalog.loc[sta].t1
    else:
        vname='dsp.'+sta+".*.dif"
        vel=glob.glob(vname)[0]        
        t1=float(f"{read(vel)[0].stats.sac.t1-timeshift:.3f}")
        os.remove(vel)
        global stationt1
        stat1=str(sta)+","+str(t1)
        stationt1.append(stat1)
    
    
    for st in stf:
        st.stats.sac.t1=t1
        st.stats.sac.t2=t2
      
    
    return stf

def filterbymag(stf):
    mag = stf[0].stats.sac.mag
    global n_pole
    
    if mag >= 6:
        freqmin=0.01;freqmax=0.04
    elif mag < 4.5 :
        freqmin=0.03;freqmax=0.05
    else :
        freqmin=0.02;freqmax=0.06

    stf.filter("bandpass", freqmin=freqmin,freqmax=freqmax,corners=n_pole, zerophase=False)
    stf.taper(0.05, type='hann')
    
    return stf,freqmin,freqmax

def decimate_100to1Hz(stf):
    global n_pole
    if stf[0].stats.sampling_rate == 100   :
        stf.decimate(5,no_filter=True)
        stf.filter("lowpass", freq=stf[0].stats.sampling_rate*0.5*0.8,corners=n_pole, zerophase=True)
        stf.decimate(5,no_filter=True)
        stf.filter("lowpass", freq=stf[0].stats.sampling_rate*0.5*0.8,corners=n_pole, zerophase=True)
        stf.decimate(4,no_filter=True)
        stf.filter("lowpass", freq=stf[0].stats.sampling_rate*0.5*0.8,corners=n_pole, zerophase=True)
    elif stf[0].stats.sampling_rate == 40 :
        stf.decimate(8,no_filter=True)
        stf.filter("lowpass", freq=stf[0].stats.sampling_rate*0.5*0.8,corners=n_pole, zerophase=True)
        stf.decimate(5,no_filter=True)
        stf.filter("lowpass", freq=stf[0].stats.sampling_rate*0.5*0.8,corners=n_pole, zerophase=True)
    
    return stf

def snr (stf,timeshiht=300):
    global allsnr
    zrt=str(stf[0].stats.station)
    for sac in stf:
        dist = sac.stats.sac.dist
        ### lenth by dist
        if dist < 50 :
            lenth=40
        elif dist < 200 :
            lenth=80
        elif dist < 300 :
            lenth=100
        elif dist < 400 :
            lenth=120
        elif dist < 500 :
            lenth=160
        elif dist < 600 :
            lenth=180
        elif dist < 700 :
            lenth=200
        elif dist >= 700 :
            lenth=300
        
        sacf=sac.copy()
        p=sacf.stats.starttime+float(sacf.stats.sac.t1)+float(300)

        ss=sacf.copy().trim(starttime=p,endtime=p+lenth)
        nn=sacf.trim(starttime=p-110,endtime=p-10)

        signal=np.sum(ss.data**2)/len(ss.data)
        noise=np.sum(nn.data**2)/len(nn.data)
        snr2= f"{signal/noise:.3f}"
        zrt+=","+snr2
    
    allsnr.append(zrt)

##### Main #####
### BB file
if not os.path.isdir('BB'):
    os.makedirs(os.path.join('BB'))
### filter pole : bp co 0.02 0.06 n 3(n_pole) 
n_pole=3
### p arrival(t1) correct ##### 
if os.path.isfile('t1.log'):
    t1catalog=pd.read_csv('t1.log')
    t1catalog=t1catalog.set_index('sta', drop=True)
else:
    stationt1=[]
    stationt1.append("sta,t1")

### SNR ###
if os.path.isfile('snr.log'):
    os.remove('snr.log')
    
allsnr=[]
allsnr.append("sta,zsnr,rsnr,tsnr")


for eve in glob.glob('dsp*.?HZ'):
    stf=sac_read(eve)
    #### CHECK DATA
    a=checkData(stf)
    if a==0 :
        continue ### 結束本次迴圈
    stf=correct_t1t2(stf)
    stf,fmin,fmax=filterbymag(stf)
    stf=decimate_100to1Hz(stf)
    snr(stf)
    ### trim to eventtime ~ eventtime
    stf=stf.trim(starttime=stf[0].stats.starttime+300 , endtime = stf[0].stats.endtime)
    for st in stf:
        st.stats.starttime=st.stats.starttime-300
        st.data=st.data*100 # M to cm
    rname='BB/dsp.'+stf[0].stats.station+'.LHR'
    tname=rname.replace('LHR','LHT')
    zname=rname.replace('LHR','LHZ')
    
    stf[1].write(rname, format="sac")
    stf[2].write(tname, format="sac")
    stf[0].write(zname, format="sac")


###### output file #######
if not os.path.isfile('t1.log'):
    with open ('t1.log',mode='a') as f :
        for txt in stationt1:
            f.write("%s\n" % txt)

# output snr.log
with open ('snr.log',mode='a') as f :
    for txt in allsnr:
        f.write("%s\n" % txt)


#### BB and stalist ####
if os.path.isfile('BB/stalst'):
    os.remove('BB/stalst')
num_sta=len(glob.glob('BB/*.LHZ'))

with open('eveID',mode='r') as f :
    eventID=str(f.read().strip())[:-5] ### remove last 5 char


with open ('../vmodel.log',mode='r') as f :
    model=str(f.read().strip()) ##strip remove "\n"

first=str(num_sta)+" "+\
    str(stf[0].stats.delta)+" "+\
    str(fmin)+" "+str(fmax)+" "+\
    str(n_pole)+" "+str(eventID)
print(first)

### weighting i for staion j for zrt
df=pd.read_csv('snr.log',skipinitialspace=True)
for i in range(num_sta):
    for j in [1,2,3]:
        if df.iloc[i,j] >= 5:
            df.iloc[i,j]=1.0
        elif df.iloc[i,j] < 2:
            df.iloc[i,j]=0.0
        else:
            df.iloc[i,j]=0.5

with open ('BB/stalst',mode='a') as f:
    f.write("%s\n" % first)
    for i in range(num_sta):
        f.write("%s %2.1f %2.1f %2.1f %s\n"
                % (df.iloc[i].sta,df.iloc[i].zsnr,df.iloc[i].rsnr,df.iloc[i].tsnr,model))

