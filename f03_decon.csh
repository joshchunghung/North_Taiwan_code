#!/bin/csh
set al_sacf = `ls *.SAC`

foreach sacf ($al_sacf)
set sta = `saclst kstnm f $sacf | awk '{print $2}'`
set chn = `saclst KCMPNM f $sacf | awk '{print $2}'`
set khole = `saclst khole f $sacf | awk '{print $2}' | awk '{ if ($1 != -12345) print $1}'`
set pz = `ls ../PZ/SAC_PZs_*_{$sta}_{$chn}_{$khole}_*`
echo $sacf $pz
sac<<! >&/dev/null
r $sacf
rmean;rtr;taper
trans from polezero s $pz to none freq 0.005 0.008 8 10
w append .dec
q
!

end

