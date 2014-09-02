__author__ = 'qPCR4vir'

import EvoMode
from Instructions import *
from Labware import *
import Robot


EvoMode.CurEvo = EvoMode.multiEvo([EvoMode.AdvancedWorkList('AWL.gwl'),
                                   EvoMode.ScriptBody('AWL.esc.txt'),
                                   EvoMode.EvoScript(template='RNAext_MNVet.ewt',
                                                     filename='AWL.esc',
                                                     arms=Robot.Robot.arm(4) ),
                                   EvoMode.EvoStdOut()
                                    ])


ElutionBuffer = Labware(Trough_100ml, Labware.Location(6, 0), "1-VEL-ElutionBuffer" )
LysisBuffer   = Labware(Trough_100ml, Labware.Location(6, 1), "2-Vl Lysis Buffer"   )
BindingBuffer = Labware(Trough_100ml, Labware.Location(6, 2), "3-VEB Binding Buffer")
VEW1          = Labware(Trough_100ml, Labware.Location(22,3), "4-VEW1 Wash Buffe"   )
#VEW1          = Labware(Trough_100ml, Labware.Location(22 ,0), "4-VEW1 Wash Buffe"   ) # Plus RACK_OFFSET = 3 ??!!
VEW2          = Labware(Trough_100ml, Labware.Location(22,4), "5-VEW2-WashBuffer"   )
BioWaste      = Labware(Trough_100ml, Labware.Location(22,5), "6-Waste"             )
EtOH80p       = Labware(Trough_100ml, Labware.Location(24,0), "7-EtOH80p"           )
Unnused8      = Labware(Trough_100ml, Labware.Location(24,1), "8-Unnused"           )
Unnused9      = Labware(Trough_100ml, Labware.Location(24,2), "9-Unnused"           )

Reactives     = Labware(EppRack16_2mL, Labware.Location(7,0),"Reactives")

Eluat         = Labware(EppRack3x16R, Labware.Location(8,0),"Eluat")

Proben        = Labware(EppRack3x16, Labware.Location(11,0),"Proben")

TeMg_Heat     = Labware(TeMag48, Labware.Location(14,0),"48 Pos Heat")
TeMag         = Labware(TeMag48, Labware.Location(14,1),"48PosMagnet")

DiTi1000_1    = Labware(DiTi_1000ul, Labware.Location(25,0),"1000-1")
DiTi1000_2    = Labware(DiTi_1000ul, Labware.Location(25,1),"1000-2")
DiTi1000_3    = Labware(DiTi_1000ul, Labware.Location(25,2),"1000-3")

B_liquidClass = "Buffer free DITi 1000-AVR"
W_liquidClass = "AVR-Water free DITi 1000"
Std_liquidClass = "Water free dispense DiTi 1000"




set_DITI_Counter2( DiTi1000_2,  DiTi1000_2.offsetFromName('A7')  ).exec()
getDITI2(LabwareTypeName=DiTi1000_2).exec()

ElutionBuffer.selectOnly(range(2,2+4))
Asp = aspirate(liquidClass =B_liquidClass, volume=50.3, labware=ElutionBuffer)
Asp.exec()

TeMag.selectOnly(range(0,0+4))
Dsp = dispense(volume=50.3, labware=TeMag, liquidClass =W_liquidClass)
Dsp.exec()

samples = 3  #for 3*4 = 12 samples
for s in range(samples):
    Asp.exec()
    TeMag.selectOnly(range(4*s,4*s+4))
    Dsp.exec()

dropDITI().exec()

exit()






# MP = Labware( MP96well, Labware.Location(1,1) )


Mx= mix(labware=Proben)
Mx.exec()
# Wtips=wash_tips()
gDITI=getDITI(8,0)
gDITI.exec()
gDITI2=getDITI2(LabwareTypeName=DiTi1000_1)
gDITI2.exec()
dropTips=dropDITI(AirgapSpeed=100)
dropTips.exec()
dropDITI().exec()
sDiTi=set_DITI_Counter(2,labware = DiTi1000_2)
sDiTi.exec()

from Instructions_Te_MagS import *
Te_MagS_MoveToPosition(T_Mag_Instr.Aspirate,22).exec()
Te_MagS_ActivateHeater(50).exec()
Te_MagS_DeactivateHeater().exec()

exP= [Te_MagS_Execution.mix  (3,0,0,15,22),
      Te_MagS_Execution.wait (0,0,25),
      Te_MagS_Execution.incub(0,0,40),
      Te_MagS_Execution.move (T_Mag_Instr.Aspirate,22)   ]

Te_MagS_Execution(exP).exec()

LOp=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

vol=list(def_vol)
vol[0]=5.5


MP.Wells[0].selFlag = True
MP.Wells[MP.offset("F01")].selFlag = True


from EvoScriptCommands import *

Aspirate( 8, "BufferNewXDX", vol,1,1,1,MP.wellSelectionStr() ,LOp, Pippet.LiHa1)

vol=[1.1,2.2]
LOp+=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

Dispence(3,"Otro Buffer",10.1,1,1,1,"NNSelectionxx", LOp ,Pippet.LiHa1)

print("\n done")








