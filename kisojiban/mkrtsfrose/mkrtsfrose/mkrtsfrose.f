c     FLIP no data  kara tms text data wo sakusei
c mkrtsfh.f wo syusei 2013/1/27 disMax tuika
c flipRose taiou txy-tmax gamxy-gammax
c                stat sigy tmax elemsf tuika
c sigxZan,sigxMax tuika
c
      DIMENSION xn(30000),yn(30000),ax(30000),ay(30000),tmx(30000)
      DIMENSION pp(30000),nsol(30000,4),dx(30000),dy(30000)
      DIMENSION dxm(30000),dym(30000)
      DIMENSION np(30000),gamax(30000),ne(30000)
      DIMENSION sigy(30000),tmxs(30000),sig1(30000),deg(30000)
      DIMENSION sig1y(30000),sig1x(30000)
      DIMENSION sigxZan(30000),sigxMax(30000)
C
      OPEN (UNIT=5,FILE='flip.fmesh')
      OPEN (UNIT=6,FILE='./dyna/flip.32')
      OPEN (UNIT=7,FILE='./dyna/flip.34')
      OPEN (UNIT=11,FILE='./dyna/flip.35')
      OPEN (UNIT=8,FILE='./dyna/flip.36')
      OPEN (UNIT=12,FILE='./stat/flip.36')
      OPEN (UNIT=9,FILE='rts.dat')
C     OPEN (UNIT=10,FILE='chk.lst')
C
      READ (5,501,END=9) 
      read (5,502) nnod,nele
      READ (5,501,END=9) 
      nmax=0
      do 4 i=1,nnod
      READ (5,501,END=9) np(i),xn(np(i)),yn(np(i))
c     yn(np(i))=yn(np(i))*20.0
      dx(np(i))=0.0
      dy(np(i))=0.0
      ax(np(i))=0.0
      ay(np(i))=0.0
      if (np(i).gt.nmax) nmax=np(i)
    4 continue
  501 format (i5,5x,2f10.1)
  502 format (2i5)
    9 continue
c
      READ (5,503,END=9) 
      READ (5,503,END=19) 
      nemax=0
      do 5 i=1,nele
      nsol(ne(i),3)=0
      nsol(ne(i),4)=0
      READ (5,503,END=19) ne(i),nsol(ne(i),1)
     &,nsol(ne(i),2),nsol(ne(i),3),nsol(ne(i),4)
      tmx(ne(i))=0.0
      pp(ne(i))=0.0
      sig1(ne(i))=0.0
      sigy(ne(i))=0.0
      tmxs(ne(i))=0.0
      if (ne(i).gt.nemax) nemax=ne(i)
    5 continue
  503 format (i5,5x,4i5)
   19 continue
c
      READ (6,602,END=39) ndis
      do 16 i=1,ndis
      READ (6,601,END=39) nj,dx(nj),dy(nj)
   16 continue
      READ (6,601,END=39)
      do 6 i=1,ndis
      READ (6,601,END=39) nj,dxm(nj),dym(nj)
    6 continue
  601 format (i5,2e10.3)
  602 format (i5)
   39 continue
c
      READ (7,702,END=29) nacc
      do 17 i=1,nacc
      READ (7,701,END=29)
   17 continue
      READ (7,701,END=29)
      do 7 i=1,nacc
      READ (7,701,END=29) nj,ax(nj),ay(nj)
    7 continue
  701 format (i5,2e10.3)
  702 format (i5)
   29 continue
c
      READ (8,802,END=49) npp
      do 18 i=1,npp
      READ (8,804,END=49) nj,sigxZan(nj)
   18 continue
      READ (8,801,END=49)
      do 8 i=1,npp
      READ (8,801,END=49) nj,sigxMax(nj),pp(nj),tmx(nj)
    8 continue
  801 format (i5,e10.3,40x,e10.3,30x,e10.3)
  802 format (i5)
  804 format (i5,e10.3)
   49 continue
c
      READ (11,802,END=59) npp
      do 55 i=1,npp
      READ (11,803,END=59)
   55 continue
      READ (11,803,END=59)
      do 56 i=1,npp
      READ (11,803,END=59) nj,gamax(nj)
   56 continue
  803 format (i5,60x,e10.3)
   59 continue
c
c     READ (12,802,END=109) npp
c     do 101 i=1,npp
c     READ (12,803,END=109)
c 101 continue
      READ (12,803,END=109)
      do 102 i=1,npp
      READ (12,805,END=109) nj,sigy(nj),deg(nj),sig1(nj),tmxs(nj)
      sig1x(nj)=sig1(nj)*cos((deg(nj)+90.0)/180.0*3.1415926)
      sig1y(nj)=sig1(nj)*sin((deg(nj)+90.0)/180.0*3.1415926)
  102 continue
  805 format (i5,10x,e10.3,40x,e10.3,10x,2e10.3)
  109 continue
c
          WRITE (9,901)
          WRITE (9,902)
          WRITE (9,903)
          WRITE (9,904)
          WRITE (9,905)
          WRITE (9,906)
          WRITE (9,907)
          WRITE (9,908)
          WRITE (9,909)
          WRITE (9,932)
          WRITE (9,910)
          WRITE (9,971)
          WRITE (9,972)
          WRITE (9,951)
          WRITE (9,952)
          WRITE (9,961)
          WRITE (9,962)
          WRITE (9,963)
          WRITE (9,964)
c
          WRITE (9,911)
        do 60 i=1,nmax
          WRITE (9,912) np(i),xn(np(i)),yn(np(i))
   60   CONTINUE
          WRITE (9,913)
        do 70 i=1,nemax
          if (nsol(ne(i),3).eq.0) goto 78
          if (nsol(ne(i),3).eq.nsol(ne(i),4)) goto 75
          WRITE (9,914) ne(i),(nsol(ne(i),j),j=1,4)
          goto 76
   75     WRITE (9,915) ne(i),(nsol(ne(i),j),j=1,3)
          goto 76
   78     WRITE (9,935) ne(i),(nsol(ne(i),j),j=1,2)
   76   CONTINUE
   70   CONTINUE
          WRITE (9,916)
          WRITE (9,917)
          WRITE (9,918)
          WRITE (9,919)
        do 80 i=1,nmax
          WRITE (9,920) dx(np(i))
   80   CONTINUE
          WRITE (9,921)
c
          WRITE (9,922)
        do 82 i=1,nmax
          WRITE (9,920) dy(np(i))
   82   CONTINUE
          WRITE (9,921)
c
          WRITE (9,924)
        do 84 i=1,nmax
          WRITE (9,920) abs(ax(np(i)))
   84   CONTINUE
          WRITE (9,921)
c
          WRITE (9,925)
        do 86 i=1,nmax
          WRITE (9,920) abs(ay(np(i)))
   86   CONTINUE
          WRITE (9,921)
c
          WRITE (9,926)
        do 88 i=1,nemax
          WRITE (9,920) abs(tmx(ne(i)))
   88   CONTINUE
          WRITE (9,921)
c
          WRITE (9,933)
        do 89 i=1,nemax
          WRITE (9,934) abs(gamax(ne(i)))
   89   CONTINUE
          WRITE (9,921)
c
          WRITE (9,927)
        do 90 i=1,nemax
          WRITE (9,920) pp(ne(i))
   90   CONTINUE
          WRITE (9,921)
c
          WRITE (9,973)
        do 107 i=1,nemax
          WRITE (9,920) sigxZan(ne(i))
  107   CONTINUE
          WRITE (9,921)
c
          WRITE (9,974)
        do 108 i=1,nemax
          WRITE (9,920) abs(sigxMax(ne(i)))
  108   CONTINUE
          WRITE (9,921)
c
          WRITE (9,953)
        do 96 i=1,nmax
          WRITE (9,920) abs(dxm(np(i)))
   96   CONTINUE
          WRITE (9,921)
c
          WRITE (9,954)
        do 97 i=1,nmax
          WRITE (9,920) abs(dym(np(i)))
   97   CONTINUE
          WRITE (9,921)
c
          WRITE (9,965)
        do 103 i=1,nemax
          WRITE (9,920) sigy(ne(i))
  103   CONTINUE
          WRITE (9,921)
c
          WRITE (9,966)
        do 104 i=1,nemax
          WRITE (9,920) tmxs(ne(i))
  104   CONTINUE
          WRITE (9,921)
c
          WRITE (9,967)
        do 105 i=1,nemax
          WRITE (9,920) sig1x(ne(i))
  105   CONTINUE
          WRITE (9,921)
c
          WRITE (9,968)
        do 106 i=1,nemax
          WRITE (9,920) sig1y(ne(i))
  106   CONTINUE
          WRITE (9,921)
c
  901 format (8H#TPTMS10)
  902 format (11H[ATTRIBUTE])
  903 format (25Hdescription="FLIP OUTPUT")
  904 format (6H[ITEM])
  905 format (17HdisxZanryu={-1,1})
  906 format (17HdisyZanryu={-1,2})
  907 format (14HaccxMax={-1,0})
  908 format (14HaccyMax={-1,0})
  909 format (12HtauMax={0,0})
  932 format (12HgamMax={0,0})
  910 format (8HPP={0,0})
  951 format (14HdisxMax={-1,0})
  952 format (14HdisyMax={-1,0})
  961 format (14HStatsigy={0,0})
  962 format (16HStattauMax={0,0})
  963 format (15HStatsig1x={0,0})
  964 format (15HStatsig1y={0,0})
  911 format (6H[NODE])
  912 format (i5,2H={,f10.3,1H,,f10.3,1H})
  913 format (9H[ELEMENT])
  914 format (i5,2H={,i5,1H,,i5,1H,,i5,1H,,i5,1H})
  915 format (i5,2H={,i5,1H,,i5,1H,,i5,1H})
  916 format (6H[STEP])
  917 format (8Htime=0.0)
  918 format (14Hprocname="Max")
  919 format (14HdisxZanryu={ \)
  953 format (11HdisxMax={ \)
  954 format (11HdisyMax={ \)
  920 format (f10.3,2H,\)
  934 format (e10.3,2H,\)
  923 format (i10,2H,\)
  921 format (1H})
  922 format (14HdisyZanryu={ \)
  924 format (11HaccxMax={ \)
  925 format (11HaccyMax={ \)
  926 format (10HtauMax={ \)
  933 format (10HgamMax={ \)
  927 format (6HPP={ \)
  965 format (12HStatsigy={ \)
  966 format (14HStattauMax={ \)
  967 format (13HStatsig1x={ \)
  968 format (13HStatsig1y={ \)
  935 format (i5,2H={,i5,1H,,i5,1H})
  971 format (13HsigxZan={0,0})
  972 format (13HsigxMax={0,0})
  973 format (11HsigxZan={ \)
  974 format (11HsigxMax={ \)
   99 STOP
      END
