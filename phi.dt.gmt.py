#!/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob

txt=glob.glob('2*txt')

data=pd.read_csv(txt[0],delim_whitespace=True)
colors=np.array([238,118,33])/255
alphi=[]
aldt=[]
for ind,phi in enumerate(data.phi) :
    if np.abs(data.CC[ind])>=0.8 and np.abs(data.CR[ind])>=0.8 and data.SNR[ind]>=3:
        if phi < 0 :
            alphi.append(360+phi)
            aldt.append(data.dt[ind])
        else :
            alphi.append(phi)
            aldt.append(data.dt[ind])
            
phi=np.array(alphi)
dt=np.array(aldt)
print(len(phi),len(dt))

#### rose diagram
bin_edges = np.arange(-5, 360, 10)
number_of_phi, bin_edges = np.histogram(phi, bin_edges)
#fig,ax=plt.subplots(2,1,figsize=(15,9))
fig = plt.figure(figsize=(15,9))
ax = fig.add_subplot(221, projection='polar')
#ax[0].subplot(number_of_phi, bin_edges, projection='polar')
ax.bar(np.deg2rad(np.arange(0, 360, 10)),number_of_phi,width=np.deg2rad(10), bottom=0.0, 
       color=colors, edgecolor='k')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
ax.set_title('Fast_direction', y=1.10, fontsize=15)

### histrogram
ax = fig.add_subplot(222)
ax.hist(dt,bins=10,rwidth=0.85,density=False)
ax.set_ylabel('# of events')
ax.set_xlabel('Delay time[s]')
ax.set_xlim([0,3])
ax.set_title('Delay time', y=1.10, fontsize=15)

plt.savefig('dt.phi.jpg',dpi=600,orientation='portrait',format='jpg')
plt.close(fig)

