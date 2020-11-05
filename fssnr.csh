#!/bin/csh
#set al_sta = `ls -d ???? | awk -F"/" '{print $1}'`
#if ( -e fsSNR.log) rm -f fsSNR.log
#foreach sta ($al_sta)
#if ( -e $sta/waveform.ff && -e $sta/waveform.ss) then
set sta = $1
set t1 = `saclst t1 f *$sta*BHE*cut | awk '{print $2}'`
set dt = `saclst t1 t2 f *$sta*BHE*cut | awk '{print $3-$2}'`

set ss = `awk 'BEGIN{sum=0;n=0} ($1 >= t1 && $1 <= dt+t1){sum+=$2**2 ; n+=1} END {print (sum/n)**0.5}' t1=$t1 dt=$dt waveform.ff`
set nn = `awk 'BEGIN{sum=0;n=0} ($1 >= t1-dt-1 && $1 <= t1){sum+=$2**2 ; n+=1} END {print (sum/n)**0.5}' t1=$t1 dt=$dt waveform.ff`
set fsnr = `echo $ss $nn | awk '{print $1/$2}'`



set ss = `awk 'BEGIN{sum=0;n=0} ($1 >= t1 && $1 <= dt+t1){sum+=$2**2 ; n+=1} END {print (sum/n)**0.5}' t1=$t1 dt=$dt waveform.ss`
set nn = `awk 'BEGIN{sum=0;n=0} ($1 >= t1-dt-1 && $1 <= t1){sum+=$2**2 ; n+=1} END {print (sum/n)**0.5}' t1=$t1 dt=$dt waveform.ss`
set ssnr = `echo $ss $nn | awk '{print $1/$2}'`

echo $sta $fsnr $ssnr >> fsSNR.log

#endif
#end
