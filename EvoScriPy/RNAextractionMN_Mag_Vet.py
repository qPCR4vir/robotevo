__author__ = 'Ariel'

from RobotInitRNAextraction import *
from Labware import *
import Labware as Lab
import Reactive as React
from protocol import *

from Instructions_Te_MagS import *
import Instructions as Itr

Reactives     = Lab.Labware(EppRack16_2mL, Lab.Labware.Location(7,0),"Reactives")
Eluat         = Lab.Labware(EppRack3x16R, Lab.Labware.Location(8,0),"Eluat")
Samples       = Lab.Labware(EppRack3x16, Lab.Labware.Location(11,0),"Proben")


LysisBuffer     = React.Reactive("VL - Lysis Buffer "              , LysBuf,    volpersample=180 ,defLiqClass=B_liquidClass)
IC2             = React.Reactive("IC2 -synthetic RNA"              , Reactives, pos=11, volpersample=  4 ,defLiqClass=W_liquidClass)
BindingBuffer   = React.Reactive("VEB - Binding Buffer "           , BindBuf,   volpersample=600 ,defLiqClass=B_liquidClass)
B_Beads         = React.Reactive("B-Beads"                         , Reactives, pos=13, volpersample= 20 , replicas=2, defLiqClass=W_liquidClass)#todo change, define new in Evo

VEW1            = React.Reactive("VEW1 - Wash Buffer"              ,
                                 Lab.Labware(Trough_100ml, Lab.Labware.Location(22,0), "4-VEW1 Wash Buffer"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
VEW2            = React.Reactive("VEW2 - WashBuffer"               ,
                                 Lab.Labware(Trough_100ml, Lab.Labware.Location(22,1), "5-VEW2-WashBuffer"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
EtOH80p         = React.Reactive("Ethanol 80%"                     ,
                                 Lab.Labware(Trough_100ml, Lab.Labware.Location(24,0), "7-Ethanol 80%"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
ElutionBuffer   = React.Reactive("Elution Buffer"                  , ElutBuf,     volpersample=100 ,defLiqClass=B_liquidClass)



IC_MS2          = React.Reactive("IC MS2 - bacterial phage culture",
                                 Reactives, volpersample= 20 ,defLiqClass=W_liquidClass)  #, pos=14
ProtK           = React.Reactive("Proteinase K"                    ,
                                 Reactives, pos=16, volpersample= 20 ,defLiqClass=W_liquidClass)
cRNA            = React.Reactive("Carrier RNA"                     ,
                                 Reactives, pos=15, volpersample=  4 ,defLiqClass=W_liquidClass)
pK_cRNA_MS2     = React.preMix  ("ProtK,carrier RNA and interne Control IC-MS2 premix"        ,
                                 Reactives, pos=12,   components=[ ProtK, cRNA, IC_MS2 ]
                                 ,defLiqClass=W_liquidClass)

import Robot



def extractRNA_with_MN_Vet_Kit(NumOfSamples):
    robot=Robot.current
    #assert isinstance(robot,Robot.Robot)


    Te_MagS_ActivateHeater(50).exec()
    Te_MagS_MoveToPosition(T_Mag_Instr.Dispense).exec()
    React.NumOfSamples = NumOfSamples
    all_samples=range(React.NumOfSamples)

    Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()

    pK_cRNA_MS2.make()

    spread  (  reactive=pK_cRNA_MS2,   to_labware_region= Robot.TeMag.selectOnly(all_samples))
    transfer(  Samples.selectOnly(all_samples),Robot.TeMag,200,("Serum Asp preMix3","Serum Disp postMix3"),
                     False,True,NumSamples=React.NumOfSamples)
    spread  (  reactive=LysisBuffer,   to_labware_region= Robot.TeMag.selectOnly(all_samples))
    Itr.startTimer().exec()
    Itr.waitTimer(timeSpan=10*60).exec()

    spread( reactive=B_Beads,      to_labware_region=Robot.TeMag.selectOnly(all_samples))

    wash_in_TeMag(reactive=BindingBuffer, wells=all_samples,
                        using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                        vol=pK_cRNA_MS2.volpersample+200+LysisBuffer.volpersample
                            +B_Beads.volpersample+BindingBuffer.volpersample)

    wash_in_TeMag(reactive=VEW1, wells=all_samples)

    wash_in_TeMag(reactive=VEW2, wells=all_samples)

    spread( reactive=EtOH80p,to_labware_region=Robot.TeMag.selectOnly(all_samples))
    Itr.subroutine("avr_MagMix.esc",Itr.subroutine.Continues).exec()
    mix( Robot.TeMag.selectOnly(all_samples), EtOH80p.defLiqClass,600)
    Itr.subroutine("avr_MagMix.esc",Itr.subroutine.Waits_previous).exec()
    waste( from_labware_region=Robot.TeMag.selectOnly(all_samples),
           using_liquid_class =("Serum Asp preMix3","Serum Disp postMix3"),
           volume=600)

    spread( reactive=ElutionBuffer,to_labware_region=Robot.TeMag.selectOnly(all_samples))
    Itr.subroutine("avr_MagMix.esc",Itr.subroutine.Continues).exec()
    mix( Robot.TeMag.selectOnly(all_samples), ElutionBuffer.defLiqClass,600)
    Itr.subroutine("avr_MagMix.esc",Itr.subroutine.Waits).exec()
    transfer(from_labware_region=Robot.TeMag.selectOnly(all_samples),
                   to_labware_region=Eluat.selectOnly(all_samples),
                   using_liquid_class=("Serum Asp preMix3","Serum Disp postMix3"),
                   volume=100, optimizeTo=False )
