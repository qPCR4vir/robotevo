__author__ = 'elisa.reader'
d=1
c=2

import EvoMode
EvoMode.CurEvo = EvoMode.AdvancedWorkList('AWL.txt')

from Instructions import *
from Labware import *

vol=list(def_vol)
vol[0]=5.5

MP = Labware(type=MP96well)
MP.Wells[0].selFlag = True
MP.Wells[MP.offset("F01")].selFlag = True

LOp=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

#Aspirate(8,"BufferNewXDX",vol,1,1,1,"xwellSelectionxx",LOp, "RackNameXX",1)

vol=[1.1,2.2]
LOp+=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

Dispence(3,"Otro Buffer",10.1,1,1,1,"NNSelectionxx", LOp,"Rackoooo",1)


EvoMode.CurEvo.f.write("\n" + MP.wellSelectionStr())


EvoMode.CurEvo.f.close()


