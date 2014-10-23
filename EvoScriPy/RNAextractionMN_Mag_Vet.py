__author__ = 'Ariel'


if __name__ == "__main__":
    import EvoMode
    from Instructions import Pipette
    iRobot = EvoMode.iRobot(Pipette.LiHa1, nTips=4)
    Script = EvoMode.Script(template='RNAext_MNVet.ewt', filename='AWL.esc')
    comments = EvoMode.Comments()

    EvoMode.current = EvoMode.multiple([iRobot,
                                        Script,
                                        EvoMode.AdvancedWorkList('AWL.gwl'),
                                        EvoMode.ScriptBody('AWL.esc.txt'),
                                        EvoMode.StdOut(), comments
                                        ])

from RobotInitRNAextraction import *
import Labware as Lab
import Reactive as Rtv
from protocol import *

from Instructions_Te_MagS import *
import Instructions as Itr

Reactives  = Lab.Labware(Lab.GreinRack16_2mL, Lab.Labware.Location(7, 1 ), "Reactives")
Eluat      = Lab.Labware(Lab.EppRack3x16R,    Lab.Labware.Location(8, 1 ), "Eluat" )
Samples    = Lab.Labware(Lab.EppRack3x16,     Lab.Labware.Location(11, 1), "Proben")

mix_mag_sub = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix.esc" .decode(EvoMode.Mode.encoding)
mix_mag_eluat = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix_Eluat.esc" .decode(EvoMode.Mode.encoding)
# Rbt.rep_sub = br"repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)
Rbt.rep_sub = br"C:\Prog\robotevo\EvoScriPy\repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)

def extractRNA_with_MN_Vet_Kit(NumOfSamples):

    Rtv.NumOfSamples = NumOfSamples

    Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()

    #DiTi1000_1.fill('C06')
    #DiTi1000_2.fill('A11')
    #DiTi1000_3.fill('A10')
    Itr.set_DITI_Counter2(DiTi1000_1, posInRack='A01').exec()

    SampleVolume        = 200.0
    LysisBufferVolume   = 180.0
    IC2Volume           = 4.0
    BindingBufferVolume = 600.0
    B_BeadsVolume       = 20.0
    VEW1Volume          = 600.0
    VEW2Volume          = 600.0
    EtOH80pVolume       = 600.0
    ProtKVolume         = 20.0
    cRNAVolume          = 4.0
    IC_MS2Volume        = 20.0
    ElutionBufferVolume = 100.0

    all_samples = range(Rtv.NumOfSamples)
    maxTips     = min(Rbt.nTips, Rtv.NumOfSamples)
    maxMask     = Rbt.tipsMask[maxTips]
    par         = TeMag.parallelOrder(Rbt.nTips, all_samples)

    for s in all_samples:
        Rtv.Reactive("probe_{:02d}".format(s+1), Samples, single_use=SampleVolume,
                                            pos=s+1, defLiqClass=def_liquidClass, excess=0)
        Rtv.Reactive("lysis_{:02d}".format(s+1), TeMag, initial_vol= 0.0,
                                            pos=par[s]+1, defLiqClass=def_liquidClass, excess=0)
        Rtv.Reactive(  "RNA_{:02d}".format(s+1), Eluat, initial_vol= 0.0,
                                            pos=s+1, defLiqClass=def_liquidClass, excess=0)


    LysisBuffer     = Rtv.Reactive("VL - Lysis Buffer "              ,
                                     LysBuf,    volpersample=LysisBufferVolume ,defLiqClass=B_liquidClass)
    IC2             = Rtv.Reactive("IC2 -synthetic RNA"              ,
                                     Reactives, pos=11, volpersample=  IC2Volume ,defLiqClass=W_liquidClass)
    BindingBuffer   = Rtv.Reactive("VEB - Binding Buffer "           ,
                                     BindBuf,   volpersample=BindingBufferVolume ,defLiqClass=B_liquidClass)
    B_Beads         = Rtv.Reactive("B-Beads"                         ,
                                     Reactives, pos=1, volpersample= B_BeadsVolume , replicas=2, defLiqClass=Beads_LC_2)

    VEW1            = Rtv.Reactive("VEW1 - Wash Buffer"              ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22, 4), "4-VEW1 Wash Buffer"),
                                     volpersample=VEW1Volume , defLiqClass=B_liquidClass)
    VEW2            = Rtv.Reactive("VEW2 - WashBuffer"               ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22, 5), "5-VEW2-WashBuffer" ),
                                     volpersample=VEW2Volume , defLiqClass=B_liquidClass)
    EtOH80p         = Rtv.Reactive("Ethanol 80%"                     ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24, 1), "7-Ethanol 80%"   ),
                                     volpersample=EtOH80pVolume , defLiqClass=B_liquidClass)
    ElutionBuffer   = Rtv.Reactive("Elution Buffer"                  ,
                                     ElutBuf,     volpersample=ElutionBufferVolume , defLiqClass="Eluat")

    ProtK           = Rtv.Reactive("Proteinase K"                    ,
                                     Reactives, pos=16, volpersample= ProtKVolume , defLiqClass=Small_vol_disp)
    cRNA            = Rtv.Reactive("Carrier RNA"                     ,
                                     Reactives, pos=15, volpersample=  cRNAVolume , defLiqClass=Small_vol_disp)
    IC_MS2          = Rtv.Reactive("IC MS2 - bacterial phage culture",
                                     Reactives, pos=14, volpersample= IC_MS2Volume , defLiqClass=Small_vol_disp)
    pK_cRNA_MS2     = Rtv.preMix  ("ProtK,carrier RNA and interne Control IC-MS2 premix"        ,
                                     Reactives, pos=12,   components=[ ProtK, cRNA, IC_MS2 ]
                                     ,defLiqClass=W_liquidClass, replicas=2)
    Waste           = Rtv.Reactive("Waste"  , WashWaste )


    Itr.wash_tips(wasteVol=30).exec()
    Te_MagS_ActivateHeater(50).exec()
    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()

    with tips(tipsMask=maxMask, reuse=True, drop=False):
        pK_cRNA_MS2.make()
        spread  (  reactive=pK_cRNA_MS2,   to_labware_region= TeMag.selectOnly(all_samples))

    with tips(reuse=True, drop=True, preserve=True):
        transfer(  from_labware_region= Samples,
                   to_labware_region=   TeMag,
                   volume=              SampleVolume,
                   using_liquid_class=  ("Serum Asp preMix3","Serum Disp postMix3"),
                   optimizeFrom         =False,     optimizeTo= True,
                   NumSamples=          Rtv.NumOfSamples)
    Itr.wash_tips(wasteVol=4).exec()

    with tips(reuse=False, drop=True):
        spread  (  reactive=LysisBuffer,   to_labware_region= TeMag.selectOnly(all_samples))

    with incubation(10): pass

    with tips(tipsMask=maxMask, reuse=True, drop=False):
        mix_reactive(B_Beads, LiqClass=Beads_LC_1, cycles=2, maxTips=maxTips)
        mix_reactive(B_Beads, LiqClass=Beads_LC_2, cycles=3, maxTips=maxTips)

    with tips(reuse=True, drop=True):
        spread( reactive=B_Beads,      to_labware_region=TeMag.selectOnly(all_samples))

    with tips(reuse=True, drop=False, preserve=True, usePreserved=True):
        wash_in_TeMag(reactive=BindingBuffer, wells=all_samples)

    with tips(reuse=True, drop=False, preserve=True):
        wash_in_TeMag(reactive=VEW1, wells=all_samples)
        wash_in_TeMag(reactive=VEW2, wells=all_samples)

        with group("Wash in TeMag with " + EtOH80p.name), tips():
            spread( reactive=EtOH80p,to_labware_region=TeMag.selectOnly(all_samples))

            with parallel_execution_of(mix_mag_sub, repeat=Rtv.NumOfSamples//Rbt.nTips +1):
                mix( TeMag.selectOnly(all_samples), EtOH80p.defLiqClass)
            with incubation(minutes=0.5):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()
            with tips(usePreserved=preserveingTips()):
                waste( from_labware_region=    TeMag.selectOnly(all_samples))

            with incubation(minutes=4):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()
            with incubation(minutes=4):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()

        spread( reactive=ElutionBuffer, to_labware_region=TeMag.selectOnly(all_samples))
        with incubation(minutes=2):
            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()

        Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
        with parallel_execution_of(mix_mag_eluat, repeat=Rtv.NumOfSamples//Rbt.nTips+1):
            mix(TeMag.selectOnly(all_samples), ElutionBuffer.defLiqClass)

        with tips(usePreserved=preserveingTips(), preserve=False, drop=True):
            with incubation(minutes=1.0, timer=2):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
            transfer(from_labware_region=   TeMag.selectOnly(all_samples),
                     to_labware_region=     Eluat.selectOnly(all_samples),
                     volume=                ElutionBufferVolume,
                     optimizeTo=            False,
                     using_liquid_class=(ElutionBuffer.defLiqClass, ElutionBuffer.defLiqClass))

def wash_in_TeMag( reactive, wells=None, using_liquid_class=None, vol=None):
        """

        :param reactive:
        :param wells:
        :param using_liquid_class: dict
        :param vol:
        """
        wells = wells or reactive.labware.selected() or range(Rtv.NumOfSamples)
        if not using_liquid_class:
            using_liquid_class =  reactive.defLiqClass
        with group("Wash in TeMag with " + reactive.name):

            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
            spread(reactive=reactive, to_labware_region=TeMag.selectOnly(wells))

            with parallel_execution_of(mix_mag_sub, repeat=Rtv.NumOfSamples//Rbt.nTips +1):
                mix(TeMag.selectOnly(wells), using_liquid_class, vol)

            with incubation(minutes=0.5, timer=2):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
            with tips(usePreserved=preserveingTips(), preserve=False, drop=True):
                waste(TeMag.selectOnly(wells), using_liquid_class, vol)


if __name__ == "__main__":
    extractRNA_with_MN_Vet_Kit(48)
    pass