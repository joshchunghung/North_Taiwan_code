program SNR
implicit none
integer, parameter :: max=8640010
integer :: nerr(2), nlen, ios, k
real, dimension(max) :: yarray 
real :: beg, del, dist
real :: t1,t2,singal=0.0,noise=0.0
integer :: t5,t3,t4,t6
integer :: i,j
real :: n1,n2
character (len=200) :: kname,aname
character (len=8) :: kstnm
integer,external :: time2pt
real,external :: pt2time
write(*,*)'t1lease input SAC file name.'
read(*,'(a)')kname


!!! read sac file
	call rsac1(trim(kname),yarray,nlen,beg,del,max,nerr(1))
	call getfhv('T1',t1,nerr(2))
	call getfhv('T2',t2,nerr(2))
if (ANY(nerr /= 0)) then
write(*,*)'error,no this file'
stop
endif
write(*,*)t1,t2

!!! t1rat1are
t5=time2pt(t1,beg,del)
t6=time2pt(t2,beg,del)

t4=time2pt(t1-1,beg,del)
t3=time2pt(2*t1-1-t2,beg,del)
write(*,*)t5,t6,t3,t4

n1=0.
do i=t5,t6
singal=singal+yarray(i)**2.
n1=n1+1.
enddo
singal=singal/n1

n2=0.
do j=t3,t4
noise=noise+yarray(j)**2.
n2=n2+1.
enddo
noise=noise/n2


!write(77,*)sqrt(singal)/sqrt(noise)
write(*,*)"signal",singal,n1
write(*,*)"noise",noise,n2
write(*,*)sqrt(singal/noise)
!close(77)
stop
end program SNR

  FUNCTION time2pt(time, bt, dt)
   implicit NONE
   INTEGER :: time2pt
   REAL    :: time, bt, dt
   time2pt = NINT((time - bt)/dt) + 1
  END FUNCTION time2pt

  FUNCTION pt2time(pt, bt, dt)
   implicit NONE
   REAL      :: pt2time
   INTEGER   :: pt
   REAL      :: bt, dt
   pt2time = REAL(pt - 1)*dt + bt
  END FUNCTION pt2time

