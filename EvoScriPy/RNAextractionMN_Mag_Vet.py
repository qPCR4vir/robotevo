__author__ = 'Ariel'

from RobotInitRNAextraction import *
import Labware as Lab
import Reactive as React
from protocol import *

from Instructions_Te_MagS import *
import Instructions as Itr

Reactives     = Lab.Labware(Lab.EppRack16_2mL, Lab.Labware.Location(7, 1 ), "Reactives")
Eluat         = Lab.Labware(Lab.EppRack3x16R,  Lab.Labware.Location(8, 1 ), "Eluat" )
Samples       = Lab.Labware(Lab.EppRack3x16,   Lab.Labware.Location(11, 1), "Proben")


LysisBuffer     = React.Reactive("VL - Lysis Buffer "              , LysBuf,    volpersample=180 ,defLiqClass=B_liquidClass)
IC2             = React.Reactive("IC2 -synthetic RNA"              , Reactives, pos=11, volpersample=  4 ,defLiqClass=W_liquidClass)
BindingBuffer   = React.Reactive("VEB - Binding Buffer "           , BindBuf,   volpersample=600 ,defLiqClass=B_liquidClass)
B_Beads         = React.Reactive("B-Beads"                         , Reactives, pos=1, volpersample= 20 , replicas=2, defLiqClass=W_liquidClass)#todo change, define new in Evo

VEW1            = React.Reactive("VEW1 - Wash Buffer"              ,
                                 Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(22, 4), "4-VEW1 Wash Buffer"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
VEW2            = React.Reactive("VEW2 - WashBuffer"               ,
                                 Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(22, 5), "5-VEW2-WashBuffer"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
EtOH80p         = React.Reactive("Ethanol 80%"                     ,
                                 Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(24, 1), "7-Ethanol 80%"   ),
                                 volpersample=600 ,defLiqClass=B_liquidClass)
ElutionBuffer   = React.Reactive("Elution Buffer"                  , ElutBuf,     volpersample=100 ,defLiqClass=B_liquidClass)

ProtK           = React.Reactive("Proteinase K"                    ,
                                 Reactives, pos=16, volpersample= 20 ,defLiqClass=W_liquidClass)
cRNA            = React.Reactive("Carrier RNA"                     ,
                                 Reactives, pos=15, volpersample=  4 ,defLiqClass=W_liquidClass)
IC_MS2          = React.Reactive("IC MS2 - bacterial phage culture",
                                 Reactives, pos=14, volpersample= 20 ,defLiqClass=W_liquidClass)  #, pos=14
pK_cRNA_MS2     = React.preMix  ("ProtK,carrier RNA and interne Control IC-MS2 premix"        ,
                                 Reactives, pos=12,   components=[ ProtK, cRNA, IC_MS2 ]
                                 ,defLiqClass=W_liquidClass, replicas=2)

mix_mag_sub = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix.esc" .decode(EvoMode.Mode.encoding)


def extractRNA_with_MN_Vet_Kit(NumOfSamples):
    Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()

    DiTi1000_1.fill('B06')
    DiTi1000_2.fill('A11')
    DiTi1000_3.fill('A10')
    Itr.set_DITI_Counter2(posInRack='B06').exec()

    React.NumOfSamples = NumOfSamples
    all_samples = range(React.NumOfSamples)

    Te_MagS_ActivateHeater(50).exec()
    Te_MagS_MoveToPosition(T_Mag_Instr.Dispense).exec()

    reuse_tips_and_drop(reuse=True, drop=False)
    pK_cRNA_MS2.make()

    reuse_tips_and_drop(reuse=True, drop=False)
    spread  (  reactive=pK_cRNA_MS2,   to_labware_region= TeMag.selectOnly(all_samples))

    reuse_tips_and_drop(reuse=True, drop=True)
    transfer(  Samples.selectOnly(all_samples),TeMag,200,("Serum Asp preMix3","Serum Disp postMix3"),
                     False, True, NumSamples=React.NumOfSamples)

    reuse_tips_and_drop(reuse=False, drop=True)
    spread  (  reactive=LysisBuffer,   to_labware_region= TeMag.selectOnly(all_samples))

    with incubation(10): pass

    reuse_tips_and_drop(reuse=False, drop=True)

    spread( reactive=B_Beads,      to_labware_region=TeMag.selectOnly(all_samples))

    reuse_tips_and_drop(reuse=False, drop=True)
    wash_in_TeMag(reactive=BindingBuffer, wells=all_samples,
                        using_liquid_class=("Serum Asp preMix3", "Serum Disp postMix3"),
                        vol=pK_cRNA_MS2.volpersample+200+LysisBuffer.volpersample
                            + B_Beads.volpersample+BindingBuffer.volpersample)

    wash_in_TeMag(reactive=VEW1, wells=all_samples)

    wash_in_TeMag(reactive=VEW2, wells=all_samples)

    with group("Wash in TeMag with " + EtOH80p.name):
        spread( reactive=EtOH80p,to_labware_region=TeMag.selectOnly(all_samples))
        Itr.subroutine(mix_mag_sub,Itr.subroutine.Continues).exec()
        mix( TeMag.selectOnly(all_samples), EtOH80p.defLiqClass,600)
        Itr.subroutine(mix_mag_sub,Itr.subroutine.Waits_previous).exec()
        waste( from_labware_region=TeMag.selectOnly(all_samples),
               using_liquid_class =("Serum Asp preMix3","Serum Disp postMix3"),
               volume=600)

    spread( reactive=ElutionBuffer, to_labware_region=TeMag.selectOnly(all_samples))
    Itr.subroutine(mix_mag_sub, Itr.subroutine.Continues).exec()
    mix(TeMag.selectOnly(all_samples), ElutionBuffer.defLiqClass,600)
    Itr.subroutine(mix_mag_sub,Itr.subroutine.Waits).exec()
    transfer(from_labware_region=TeMag.selectOnly(all_samples),
             to_labware_region=Eluat.selectOnly(all_samples),
             using_liquid_class=("Serum Asp preMix3", "Serum Disp postMix3"),
             volume=100, optimizeTo=False )

def wash_in_TeMag( reactive, wells=None, using_liquid_class=None, vol=None):
        """

        :param reactive:
        :param wells:
        :param using_liquid_class: dict
        :param vol:
        """
        wells = wells or reactive.labware.selected() or range(Rtv.NumOfSamples)
        using_liquid_class = using_liquid_class or (reactive.defLiqClass, reactive.defLiqClass)
        with group("Wash in TeMag with " + reactive.name):
            reuse_tips_and_drop(reuse=False, drop=False)
            spread(reactive=reactive, to_labware_region=TeMag.selectOnly(wells))
            reuse_tips_and_drop(reuse=True, drop=True)
            with parallel_execution_of(mix_mag_sub):
                mix(TeMag.selectOnly(wells), reactive.defLiqClass, vol or reactive.volpersample)
            waste(TeMag.selectOnly(wells), using_liquid_class, vol or reactive.volpersample)
