#!/bin/csh
set al_sta = `saclst kstnm f  *BHE*.dec*.cut  | awk '{print $2}'`
set eve = `pwd | awk -F"/" '{print $5}'`
set evloa = `saclst evla evlo f *BHZ*dec | awk '{print $2,$3}' | head -n1`
set evdp = `saclst evdp f *BHZ*dec | awk '{print $2}' | head -n1`
if (-e $eve.sol.txt) rm -f $eve.sol.txt
echo "sta phi dt "Incidentangle" "SNR"  "CC" "CR" "DOF" "INI_POL"" > $eve.sol.txt
if ( -e t1t2.log ) rm -f t1t2.log
if ( -e fsSNR.log) rm -f fsSNR.log

snr.csh

foreach sta ($al_sta)
### incident angle
set stloa = `saclst stla stlo f *$sta*BHZ*dec | awk '{print $2,$3}'`
set s = `saclst gcarc f *$sta*BHE*dec | awk '{if ($2 > 15) print "S" ; else print "s"}'`
taup_time -mod iasp91 -sta $stloa -evt $evloa -h $evdp -ph $s  > incs.txt
set inca = `awk '{print $7}' incs.txt | tail -n2 | head -n1`


if (! -d $sta) mkdir $sta
set fnn = `ls *$sta*BHN*.cut`
set fee = `ls *$sta*BHE*.cut`

#echo $sta $fnn $fee

ssplit<<! >>&/dev/null
$fnn
$fee
!

if ( -e solution.out ) then
set phi = `awk '(NR==3){print $3}' solution.out`
set dt = `awk '(NR==3){print $4}' solution.out`
set snr = `awk '(NR==2){print $4}' solution.out`
set cc = `awk '(NR==4){print $4}' solution.out`
set cr = `awk '(NR==5){print $4}' solution.out`
set dof = `awk '(NR==7){print $5}' solution.out`
set ini_pol = `awk '(NR==6){print $5}' solution.out`
echo $sta $phi $dt $inca $snr $cc $cr $dof $ini_pol
echo $sta $phi $dt $inca $snr $cc $cr $dof $ini_pol >> $eve.sol.txt

fssnr.csh $sta
draw.csh $sta

endif
mv -f $sta.result.jpg $eve.$sta.split.jpg
mv -f split.* $sta/.
mv -f solution.out $sta/.
mv -f incs.txt $sta/.
mv -f waveform* $sta/.
rm -f time_scale* 
rm -f title.txt
rm -f pmd?.dat
rm -f auto?
rm -f az_dt*


end
#rm -f *.dec.*
