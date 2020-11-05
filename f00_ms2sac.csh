#!/bin/csh
cd RAW
set al_mseed = `ls *.mseed*`
cd ..
set pwd = `pwd`
foreach mseed ($al_mseed)
set ff = `echo $mseed | awk -F. '{print $1}'`
set yy = `echo $ff | cut -c1-4`
set mon = `echo $ff | cut -c5-6`
set dd = `echo $ff | cut -c7-8`
set hh = `echo $ff | cut -c9-10`
set min = `echo $ff | cut -c11-12`
set ss = `echo $ff | cut -c13-14`
set dir = `echo $yy.$mon.$dd.$hh.$min.$ss`
echo $dir
if ( ! -d $dir) mkdir $dir
cd $dir 
mseed2sac ../RAW/$mseed
cd $pwd
end


