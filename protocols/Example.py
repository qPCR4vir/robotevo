# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016

__author__ = 'qPCR4vir'

import EvoMode
from Instructions import *
from Instructions_Te_MagS import *
from Labware import *
import Robot
import Reactive as React
from RNAextractionMN_Mag_Vet import extractRNA_with_MN_Vet_Kit

EvoMode.current = EvoMode.multiple([EvoMode.AdvancedWorkList('AWL.gwl'),
                                   EvoMode.ScriptBody('AWL.esc.txt'),
                                   EvoMode.Script(template='RNAext_MNVet.ewt',
                                                     filename='AWL.esc',
                                                     arms=Robot.Robot.Arm(4) ),
                                   EvoMode.StdOut()
                                    ])

extractRNA_with_MN_Vet_Kit( NumOfSamples=35 )

exit()








Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()


robot.spread( reactive=ElutionBuffer, to_labware_region=Eluat )
exit()

# todo Describe all the possibles variants of the protocol. Here now only the "canonical" protocol

#Goal: Te_Mag.Incubate(Samples.select(all_samples), time=10*60, mix_pippeting=True)

robot.transfer(Samples.select(all_samples), TeMag)
Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()
startTimer().exec()
waitTimer(timeSpan=10*60).exec()


robot.transfer(TeMag.select(all_samples),Eluat)




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

Aspirate( 8, "BufferNewXDX", vol,1,1,1,MP.wellSelectionStr() ,LOp, Pipette.LiHa1)

vol=[1.1,2.2]
LOp+=[LoopOption("tip",LoopOption.VaryColumn,10),LoopOption("ROW",LoopOption.VaryRow,3) ]

Dispence(3,"Otro Buffer",10.1,1,1,1,"NNSelectionxx", LOp ,Pipette.LiHa1)

print("\n done")
#VEW1          = Labware(Trough_100ml, Labware.Location(22,0), "4-VEW1 Wash Buffe"   )
#VEW1          = Labware(Trough_100ml, Labware.Location(22 ,3), "4-VEW1 Wash Buffe"   ) # Plus RACK_OFFSET = 3 ??!!
#VEW2          = Labware(Trough_100ml, Labware.Location(22,1), "5-VEW2-WashBuffer"   )
#EtOH80p       = Labware(Trough_100ml, Labware.Location(24,0), "7-EtOH80p"           )



from RobotInitRNAextraction import *
from Labware import *
import Reactive as React

Reactives     = Labware(EppRack16_2mL, Labware.Location(7,0),"Reactives")
Eluat         = Labware(EppRack3x16R, Labware.Location(8,0),"Eluat")
Samples       = Labware(EppRack3x16, Labware.Location(11,0),"Proben")


LysisBuffer     = React.Reactive("VL - Lysis Buffer "              , LysBuf,    volpersample=180 ,defLiqClass=B_liquidClass)
IC2             = React.Reactive("IC2 -synthetic RNA"              , Reactives, pos=11, volpersample=  4 ,defLiqClass=W_liquidClass)
BindingBuffer   = React.Reactive("VEB - Binding Buffer "           , BindBuf,   volpersample=600 ,defLiqClass=B_liquidClass)
B_Beads         = React.Reactive("B-Beads"                         , Reactives, pos=13, volpersample= 20 , replicas=2, defLiqClass=W_liquidClass)#todo change, define new in Evo

VEW1            = React.Reactive("VEW1 - Wash Buffer"              ,
                                 Labware(Trough_100ml, Labware.Location(22,0), "4-VEW1 Wash Buffer"   ),
                                 volpersample=100 ,defLiqClass=B_liquidClass)
VEW2            = React.Reactive("VEW2 - WashBuffer"               ,
                                 Labware(Trough_100ml, Labware.Location(22,1), "5-VEW2-WashBuffer"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
EtOH80p         = React.Reactive("Ethanol 80%"                     ,
                                 Labware(Trough_100ml, Labware.Location(24,0), "7-Ethanol 80%"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
ElutionBuffer   = React.Reactive("Elution Buffer"                  , ElutBuf,     volpersample=100 ,defLiqClass=B_liquidClass)



IC_MS2          = React.Reactive("IC MS2 - bacterial phage culture",
                                 Reactives, pos=14, volpersample= 20 ,defLiqClass=W_liquidClass)
ProtK           = React.Reactive("Proteinase K"                    ,
                                 Reactives, pos=16, volpersample= 20 ,defLiqClass=W_liquidClass)
cRNA            = React.Reactive("Carrier RNA"                     ,
                                 Reactives, pos=15, volpersample=  4 ,defLiqClass=W_liquidClass)
pK_cRNA_MS2     = React.preMix  ("ProtK,carrier RNA and interne Control IC-MS2 premix"        ,
                                 Reactives, pos=12,   components=[ ProtK, cRNA, IC_MS2 ]
                                 ,defLiqClass=W_liquidClass)

import Robot



from Instructions_Te_MagS import *
from Instructions import *

def extractRNA_with_MN_Vet_Kit(withRobot):
    robot=Robot.current
    assert isinstance(robot,Robot.Robot)

    Te_MagS_ActivateHeater(50).exec()
    Te_MagS_MoveToPosition(T_Mag_Instr.Dispense).exec()
    React.NumOfSamples = 35
    all_samples=range(React.NumOfSamples)

    pK_cRNA_MS2.make()
    robot.spread  (  reactive=pK_cRNA_MS2,   to_labware_region= TeMag.select(all_samples))
    robot.transfer(  Samples.select(all_samples),TeMag,200,("Serum Asp preMix3","Serum Disp postMix3"),False,True,NumSamples=React.NumOfSamples)
    robot.spread  (  reactive=LysisBuffer,   to_labware_region= TeMag.select(all_samples))
    startTimer().exec()
    waitTimer(timeSpan=10*60)

    robot.spread( reactive=B_Beads,      to_labware_region=TeMag.select(all_samples))
    robot.spread( reactive=BindingBuffer,to_labware_region=TeMag.select(all_samples))
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Continues).exec()
    robot.mix( TeMag.select(all_samples), BindingBuffer.defLiqClass,600)
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Waits_previous).exec()
    robot.waste(from_labware_region=TeMag.select(all_samples),
                using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                volume=100)
    Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()

    robot.spread( reactive=VEW1,to_labware_region=TeMag.select(all_samples))
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Continues).exec()
    robot.mix( TeMag.select(all_samples), VEW1.defLiqClass,600)
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Waits_previous).exec()
    robot.waste(from_labware_region=TeMag.select(all_samples),
                using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                volume=100)
    Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()


    robot.spread( reactive=VEW2,to_labware_region=TeMag.select(all_samples))
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Continues).exec()
    robot.mix( TeMag.select(all_samples), VEW2.defLiqClass,600)
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Waits_previous).exec()
    robot.waste(from_labware_region=TeMag.select(all_samples),
                using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                volume=100)
    Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()

    robot.spread( reactive=EtOH80p,to_labware_region=TeMag.select(all_samples))
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Continues).exec()
    robot.mix( TeMag.select(all_samples), EtOH80p.defLiqClass,600)
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Waits_previous).exec()
    robot.waste(from_labware_region=TeMag.select(all_samples),
                using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                volume=100)
    Te_MagS_Execution([Te_MagS_Execution.mix(cycles=3,hh=0,mm=0,ss=3) ]).exec()


    robot.spread( reactive=ElutionBuffer,to_labware_region=TeMag.select(all_samples))
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Continues).exec()
    robot.mix( TeMag.select(all_samples), ElutionBuffer.defLiqClass,600)
    subroutine("..\EvoScripts\scripts\avr_MagMix.esc",subroutine.Waits).exec()
    robot.transfer(from_labware_region=TeMag.select(all_samples),
                   to_labware_region=Eluat.select(all_samples),
                   using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                   volume=100, optimizeTo=False ),



