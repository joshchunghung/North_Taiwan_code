#!/usr/bin/env python3
#-*- coding: utf-8 -*-
import numpy as np
import glob , os , sys
import pandas as pd

from obspy import read 
from obspy.geodetics import gps2dist_azimuth,kilometers2degrees
from obspy.taup import TauPyModel
from obspy.io.sac import attach_paz
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

def dist_baz_az2(eve,sta):
    global StaDict
    global AllEveDict
    gcarcinfo = gps2dist_azimuth(StaDict[sta]['stla'],StaDict[sta]['stlo'],
                                 AllEveDict[eve]['EVLA'], AllEveDict[eve]['EVLO'])
    gcarc = kilometers2degrees(gcarcinfo[0]/1000)
    dist=gcarcinfo[0]/1000
    baz=gcarcinfo[1]
    az=gcarcinfo[2]
    
    return f"{gcarc:.3f} {dist:.3f} {baz:.3f} {az:.3f}"

def predict_p_s(evdp,gcarc,phaselist=["p","s"],model="iasp91"):
    v_model = TauPyModel(model=model)
    phase_time=[]
    for phase in phaselist:
        if len(phase)== 1 : 
            capphase=phase.upper()
            parrival = v_model.get_travel_times(source_depth_in_km=EVDP,
                                            distance_in_degree=float(gcarc),
                                            phase_list=[phase,capphase])      
        else:
            parrival = v_model.get_travel_times(source_depth_in_km=EVDP,
                                                distance_in_degree=float(gcarc),
                                                phase_list=[phase])
        
        t1 = f"{parrival[0].time:.2f}"
        p=str(parrival[0].name)
        
        phase_time.append(p)
        phase_time.append(t1)
    
    return phase_time

def decon(stf,PZ=None,lowf=0.005,highf=0.008):
    nqf=stf[0].stats.sampling_rate/2
    pre_filt = [lowf, highf , nqf-2, nqf]
    
    if stf[0].stats.station == 'HNR':  
        stf.remove_response(pre_filt=pre_filt,output='disp')
        
    else:
        for i in range(3):
            attach_paz(stf[i],PZ[0])
            
        paz = dict(stf[0].stats.paz)
        stf.simulate(paz_remove=paz,pre_filt=pre_filt)

    stf.taper(0.05, type='hann')
    
    return stf

def write2sac(stf,dirs,time_shift,GcDistBazAz,pstimelist):
    global StaDict
    global AllEveDict

    print(sta,float(StaDict[sta]['stlo']),float(StaDict[sta]['stla'])) 
    for st in stf:
        chnl=st.stats.channel
        sacname=dirs+'/dsp.'+sta+"."+chnl
        #print(sacname)
        st.write(sacname, format="sac")
        st3=read(sacname)
        ### p s time
        st3[0].stats.sac.kt1=str(pstimelist[0])
        st3[0].stats.sac.t1=float(pstimelist[1])+float(time_shift)
        st3[0].stats.sac.kt2=str(pstimelist[2])
        st3[0].stats.sac.t2=float(pstimelist[3])+float(time_shift)
        ### eve infor
        st3[0].stats.sac.evlo=float(AllEveDict[dirs]['EVLO'])        
        st3[0].stats.sac.evla=float(AllEveDict[dirs]['EVLA'])
        st3[0].stats.sac.evdp=float(AllEveDict[dirs]['EVDP'])
        st3[0].stats.sac.mag=float(AllEveDict[dirs]['mag'])
        ### sta infor
        st3[0].stats.sac.stlo=float(StaDict[sta]['stlo'])        
        st3[0].stats.sac.stla=float(StaDict[sta]['stla'])
        ### dist infor
        st3[0].stats.sac.gcarc=float(GcDistBazAz[0])
        st3[0].stats.sac.dist=float(GcDistBazAz[1])
        st3[0].stats.sac.baz=float(GcDistBazAz[2])
        st3[0].stats.sac.az=float(GcDistBazAz[3])
        st3.write(sacname, format="sac")

#### MAiN #####

### event location research range
locationDic={"minlat":-12,"maxlat":-5,"minlon":153,"maxlon":167}
#locationDic={"minlat":-90,"maxlat":90,"minlon":-180,"maxlon":180}
### get the event
eveTime=UTCDateTime("2018091811")

client = Client("IRIS")
Catalog = client.get_events(starttime=eveTime, endtime=eveTime+3600, 
                         minlatitude=locationDic['minlat'],maxlatitude=locationDic['maxlat'], 
                         minlongitude=locationDic['minlon'], maxlongitude=locationDic['maxlon'], 
                         minmag=5,catalog="GCMT")

### TW station
sta_catalog=pd.read_csv('solomon_site.txt',sep=" ",names=['lon','lat','sta','net'])
sta_catalog = sta_catalog.set_index('sta', drop=True) 
StaDict={}
for sta in sta_catalog.index:
    single_sta=dict(stlo=float(f"{sta_catalog.loc[sta].lon:.3f}"),
                    stla=float(f"{sta_catalog.loc[sta].lat:.3f}"))
    StaDict[sta]=single_sta
    
del sta_catalog,single_sta
print(StaDict)
AllEveDict = {}
for Cata in Catalog:
    
    ### event
    EVLO=Cata.origins[0].longitude 
    EVLA=Cata.origins[0].latitude
    EVDP=Cata.origins[0].depth/1000
    EVTtime=Cata.origins[0].time
    mag=Cata.magnitudes[0].mag

    eve_dict=dict(EVLO=EVLO,EVLA=EVLA,EVDP=EVDP,mag=mag)


    ### dir
    dirs=str(EVTtime).split("T")[0].replace("-",".")+"."\
    +str(EVTtime).split("T")[1].replace(":",".").split("000Z")[0]
    print(dirs)
    AllEveDict[dirs]=eve_dict    
    if not os.path.isdir(dirs):
        os.makedirs(os.path.join(dirs))

    ID=dirs+"/eveID"
    with open(ID,mode='w') as f:
        f.write(f"{dirs.replace('.','')}")
    


    ### station 
    inventory = client.get_stations(network="IU", station="HNR",location="00",channel="BH*",level="channel")
    #HNR_az=inventory.get_orientation("IU.HNR.00.BH1",eveTime)["azimuth"]
    #STLA = inventory[0].stations[0].latitude
    #STLO = inventory[0].stations[0].longitude
    #StaInforList=[STLO,STLA]

    ### HNR
    time_shift=300
    st_HNR = client.get_waveforms(network="IU", station="HNR",
                                  location="00", channel="BH?",
                                  starttime=EVTtime-time_shift, 
                                  endtime=EVTtime + 600, 
                                  attach_response=True)
    
    stf=st_HNR.copy()
    
    GcDistBazAz=dist_baz_az2(dirs,stf[0].stats.station).split()
    pstimelist=predict_p_s(EVDP,GcDistBazAz[0])

    stf=stf.rotate(method="->ZNE",inventory=inventory)
    stf=stf.rotate(method="NE->RT",back_azimuth=float(GcDistBazAz[2]))
    stf.detrend(type='demean')
    stf.detrend(type='linear')
    stf=decon(stf)
    sta=stf[0].stats.station
    write2sac(stf,dirs,time_shift,GcDistBazAz,pstimelist)
    del GcDistBazAz,pstimelist
    
    ### TW
    jday=str(EVTtime.year)+"."+str(EVTtime.julday).zfill(3)
    eve="RAW/*HHZ*"+jday

    for sacf in glob.glob(eve):
        st=read(sacf)
        n_file=str(sacf).replace("HHZ","HHN") ; e_file=str(sacf).replace("HHZ","HHE")
        try:
            st+=read(glob.glob(n_file)[0])
            st+=read(glob.glob(e_file)[0])
        except:
            continue
        
        stf=st.copy()
        
        ### Taup
        GcDistBazAz=dist_baz_az2(dirs,stf[0].stats.station).split()
        pstimelist=predict_p_s(EVDP,GcDistBazAz[0])

        try:
            if stf[0].stats.station in ['TATA','NGOA','SAVO'] :
                stf[1].data=stf[1].data*-1;stf[2].data=stf[2].data*-1
            ### cut  
            stf.trim(starttime=EVTtime-time_shift, endtime = EVTtime + 600)

            ### NE to RT
            stf.rotate(method="NE->RT",back_azimuth=float(GcDistBazAz[2]))

            stf.detrend(type='demean')
            stf.detrend(type='linear')
            ### decon        
            PZ_file='PZ/*_'+stf[0].stats.station+"_HHZ*"
            PZ=glob.glob(PZ_file)
            stf=decon(stf,PZ)

            ### save to sac
            sta=stf[0].stats.station
            write2sac(stf,dirs,time_shift,GcDistBazAz,pstimelist)
            
            del GcDistBazAz,pstimelist
        except:
            #print("2")
            continue

    #### eventlist
    eventID=dirs.replace('.','')[:-5]

    evelist=dirs+"/eventlist"
    if os.path.isfile(evelist):
        os.remove(evelist)

    tt=str(EVTtime.date).replace("-"," ")+" "+ \
        str(EVTtime).split("T")[1].replace(":"," ").split(".")[0]

    with open (evelist,mode='a') as f:
        f.write(f"{tt} {EVLA:.3f} {EVLO:.3f} {EVDP:.2f} {mag:.1f} {eventID} \n")
                

    

