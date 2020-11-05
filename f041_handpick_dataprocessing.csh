#!/bin/csh
set al_sta = `awk '{print $1}' t1t2.log `
foreach sta ($al_sta)
#set t1 = `awk '{print $2}' t1t2.log `
#set t2 = `awk '{print $3}' t1t2.log `
## &1 t6 S wave

sac<<! >>&/dev/null
r *$sta*dec.alg
rmean;rtr;taper
bp co 0.04 0.2 n 2 p 1
setbb t5 ( &1,t6 ) 
eval to t6 ( %t5 + 40)
eval to t4 ( %t5 - 30)
w append .bp
cut %t4 %t6
r *$sta*.bp
w append .cut
cut of
q
!



end
