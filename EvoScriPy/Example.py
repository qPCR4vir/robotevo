__author__ = 'elisa.reader'

import EvoMode
EvoMode.CurEvo = EvoMode.AdvancedWorkList('AWL.txt')

from Instructions import *
from Labware import *

ElutionBuffer = Labware(Trough_100ml, Labware.Location(6, 0, "1-VEL-ElutionBuffer" ))
LysisBuffer   = Labware(Trough_100ml, Labware.Location(6, 1, "2-Vl Lysis Buffer"   ))
BindingBuffer = Labware(Trough_100ml, Labware.Location(6, 2, "3-VEB Binding Buffer"))
VEW1          = Labware(Trough_100ml, Labware.Location(22,3, "4-VEW1 Wash Buffe"   ))
#VEW1          = Labware(Trough_100ml, Labware.Location(6 ,0, "4-VEW1 Wash Buffe"   )) # Plus RACK_OFFSET = 3 ??!!
VEW2          = Labware(Trough_100ml, Labware.Location(22,4, "5-VEW2-WashBuffer"   ))
BioWaste      = Labware(Trough_100ml, Labware.Location(22,5, "6-Waste"             ))
EtOH80p       = Labware(Trough_100ml, Labware.Location(24,0, "7-EtOH80p"           ))
Unnused8      = Labware(Trough_100ml, Labware.Location(24,1, "8-Unnused"           ))
Unnused9      = Labware(Trough_100ml, Labware.Location(24,2, "9-Unnused"           ))

Reactives     = Labware(EppRack16_2mL, Labware.Location(7,0,"Reactives"))

Eluat         = Labware(EppRack3x16R, Labware.Location(8,0,"Eluat"))

Proben        = Labware(EppRack3x16, Labware.Location(11,0,"Proben"))

TeMg_Heat     = Labware(TeMag48, Labware.Location(14,0,"48 Pos Heat"))
TeMag         = Labware(TeMag48, Labware.Location(14,1,"48PosMagnet"))

DiTi1000_1    = Labware(DiTi_1000ul, Labware.Location(11,0,"1000-1"))
DiTi1000_2    = Labware(DiTi_1000ul, Labware.Location(11,1,"1000-2"))
DiTi1000_3    = Labware(DiTi_1000ul, Labware.Location(11,2,"1000-3"))


Asp = aspirate(volume=50.3, labware=ElutionBuffer)
Asp.exec()
Dsp = dispense(volume=40.3, labware=TeMag)
Dsp.exec()


LOp=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

vol=list(def_vol)
vol[0]=5.5

MP = Labware(type=MP96well)
MP.Wells[0].selFlag = True
MP.Wells[MP.offset("F01")].selFlag = True


from EvoScriptCommands import *

Aspirate( 8, "BufferNewXDX", vol,1,1,1,"xwellSelectionxx",LOp, Pippet.LiHa1)

vol=[1.1,2.2]
LOp+=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

Dispence(3,"Otro Buffer",10.1,1,1,1,"NNSelectionxx", LOp ,Pippet.LiHa1)








