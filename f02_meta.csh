#!/bin/csh
set pwd = `pwd`
set file = `echo $pwd | awk -F"/" '{print $5}'`
set ff = `echo $file | awk -F. '{print $1"-"$2"-"$3"T"$4":"$5}'`
echo $file $ff
set evla = `grep $ff ../event.txt | awk '{print $2}'`
set evlo = `grep $ff ../event.txt | awk '{print $3}'`
set evdp = `grep $ff ../event.txt | awk '{print $4}'`
set mw = `grep $ff ../event.txt | awk '{print $5}'`

echo $evlo $evla $evdp $mw
set t1 = `echo $file | awk -F. '{print $1"."$2"."$3}'`
set time = `echo $file | awk -F. '{print $4,$5,$6,"000"}'`
set jday = `date2jday $t1`
echo $jday $time

set al_sacf = `ls *.SAC`


foreach sacf ($al_sacf)
set sta = `saclst kstnm f $sacf | awk '{print $2}'`
set stla = `awk '($1==sta){print $2}' sta=$sta ../PZ/fmarray_station.txt`
set stlo = `awk '($1==sta){print $3}' sta=$sta ../PZ/fmarray_station.txt`
echo $sta $stlo $stla
sac<<! >&/dev/null
r $sacf
rmean;rtr;taper
synch
ch O GMT $jday $time
eval to t0 ( -1 * &1,O )
ch allt %t0 IZTYPE IO
ch evla $evla
ch evlo $evlo
ch evdp $evdp
ch stla $stla
ch stlo $stlo
ch MAG $mw
w over
q
!
taup_setsac -mod iasp91 -ph P-5,p-5,S-6,s-6 -evdpkm $sacf

end

