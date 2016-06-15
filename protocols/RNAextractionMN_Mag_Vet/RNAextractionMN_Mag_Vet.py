# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016

__author__ = 'Ariel'


if __name__ == "__main__":
    import EvoMode
    from EvoScriPy.Instructions import Pipette
    iRobot = EvoMode.iRobot(Pipette.LiHa1, nTips=4)
    Script = EvoMode.Script(template='RNAext_MNVet.ewt', filename='AWL.esc')
    comments = EvoMode.Comments()

    EvoMode.current = EvoMode.multiple([iRobot,
                                        Script,
                                        EvoMode.AdvancedWorkList('AWL.gwl'),
                                        EvoMode.ScriptBody('AWL.esc.txt'),
                                        EvoMode.StdOut(), comments
                                        ])

from protocols.RNAextractionMN_Mag_Vet.RobotInitRNAextraction import *
import EvoScriPy.Labware as Lab
import EvoScriPy.Reactive as Rtv
from EvoScriPy.protocol_steps import *

from EvoScriPy.Instructions_Te_MagS import *
import EvoScriPy.Instructions as Itr


Reactives  = Lab.Labware(Lab.GreinRack16_2mL, Lab.Labware.Location(7, 1 ), "Reactives")
Eluat      = Lab.Labware(Lab.EppRack3x16R,    Lab.Labware.Location(8, 1 ), "Eluat" )
Samples    = Lab.Labware(Lab.EppRack3x16,     Lab.Labware.Location(11, 1), "Proben")

mix_mag_sub = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)
mix_mag_eluat = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix_Eluat.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)
# Rbt.rep_sub = br"repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)
Rbt.rep_sub = br"C:\Prog\robotevo\EvoScriPy\repeat_subroutine.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)




class RNAextr_MN_Vet_Kit(Protocol):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL. """
    name = "RNA extraction with the MN_Vet kit"
    versions = {'Serum with Liquid detection + tracking': not_implemented,
                'Serum without Liquid detection + tracking': not_implemented,
                'Tissue without Liquid detection + tracking': not_implemented,
                'Tissue with Liquid detection + tracking': not_implemented}

    def __init__(self,GUI, NumOfSamples):
        Protocol.__init__(self,GUI)
        self.NumOfSamples = NumOfSamples


    def Run(self):
        extractRNA_with_MN_Vet_Kit(self.NumOfSamples, self.CheckList)


def extractRNA_with_MN_Vet_Kit(NumOfSamples, CheckList = None):

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

    SampleLiqClass      = TissueHomLiqClass # ="Serum Asp"   # SerumLiqClass="Serum Asp preMix3"

    all_samples = range(Rtv.NumOfSamples)
    maxTips     = min(Rbt.nTips, Rtv.NumOfSamples)
    maxMask     = Rbt.tipsMask[maxTips]
    par         = TeMag.parallelOrder(Rbt.nTips, all_samples)

    LysisBuffer     = Rtv.Reactive("VL - Lysis Buffer "              ,
                                     LysBuf,    volpersample=LysisBufferVolume ,defLiqClass=B_liquidClass)
    IC2             = Rtv.Reactive("IC2 - synthetic RNA "              ,
                                     Reactives, pos=11, volpersample=  IC2Volume ,defLiqClass=W_liquidClass)
    BindingBuffer   = Rtv.Reactive("VEB - Binding Buffer "           ,
                                     BindBuf,   volpersample=BindingBufferVolume ,defLiqClass=B_liquidClass)
    B_Beads         = Rtv.Reactive("B - Beads " ,Reactives, initial_vol=1200,
                                     pos=1, volpersample= B_BeadsVolume , replicas=2, defLiqClass=Beads_LC_2)

    VEW1            = Rtv.Reactive("VEW1 - Wash Buffer "              ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22, 4), "4-VEW1 Wash Buffer"),
                                     volpersample=VEW1Volume , defLiqClass=B_liquidClass)
    VEW2            = Rtv.Reactive("VEW2 - WashBuffer "               ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22, 5), "5-VEW2-WashBuffer" ),
                                     volpersample=VEW2Volume , defLiqClass=B_liquidClass)
    EtOH80p         = Rtv.Reactive("Ethanol 80% "                     ,
                                     Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24, 1), "7-Ethanol 80%"   ),
                                     volpersample=EtOH80pVolume , defLiqClass=B_liquidClass)
    ElutionBuffer   = Rtv.Reactive("Elution Buffer "                  ,
                                     ElutBuf,     volpersample=ElutionBufferVolume , defLiqClass="Eluat")

    ProtK           = Rtv.Reactive("Proteinase K "                    ,
                                     Reactives, pos=16, volpersample= ProtKVolume , defLiqClass=Small_vol_disp)
    cRNA            = Rtv.Reactive("Carrier RNA "                     ,
                                     Reactives, pos=15, volpersample=  cRNAVolume , defLiqClass=Small_vol_disp)
    IC_MS2          = Rtv.Reactive("IC MS2 phage culture ",
                                     Reactives, pos=14, volpersample= IC_MS2Volume , defLiqClass=Small_vol_disp)
    pK_cRNA_MS2     = Rtv.preMix  ("ProtK+cRNA+IC-MS2 mix "        ,
                                     Reactives, pos=12,   components=[ ProtK, cRNA, IC_MS2 ]
                                     ,defLiqClass=W_liquidClass, replicas=2)
    Waste           = Rtv.Reactive("Waste "  , WashWaste )

    if CheckList is not None:
        CheckList()

    for s in all_samples:
        Rtv.Reactive("probe_{:02d}".format(s+1), Samples, single_use=SampleVolume,
                                            pos=s+1, defLiqClass=SampleLiqClass, excess=0)
        Rtv.Reactive("lysis_{:02d}".format(s+1), TeMag, initial_vol= 0.0,
                                            pos=par[s]+1, defLiqClass=def_liquidClass, excess=0)
        Rtv.Reactive(  "RNA_{:02d}".format(s+1), Eluat, initial_vol= 0.0,
                                            pos=s+1, defLiqClass=def_liquidClass, excess=0)



    Itr.wash_tips(wasteVol=30, FastWash=True).exec()
    Te_MagS_ActivateHeater(50).exec()
    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()

    with tips(tipsMask=maxMask, reuse=True, drop=False):
        pK_cRNA_MS2.make()
        spread  (  reactive=pK_cRNA_MS2,   to_labware_region= TeMag.selectOnly(all_samples))

    with tips(reuse=True, drop=True, preserve=True):
        transfer(  from_labware_region= Samples,
                   to_labware_region=   TeMag,
                   volume=              SampleVolume,
                   using_liquid_class=  (SampleLiqClass,"Serum Disp postMix3"),
                   optimizeFrom         =False,     optimizeTo= True,
                   NumSamples=          Rtv.NumOfSamples)
    Itr.wash_tips(wasteVol=4, FastWash=True).exec()

    with tips(reuse=False, drop=True):
        spread  (  reactive=LysisBuffer,   to_labware_region= TeMag.selectOnly(all_samples))

    with incubation(10): pass

    with tips(tipsMask=maxMask, reuse=True, drop=False):
        for p in [40, 50, 60, 60, 60, 65]:
            mix_reactive(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)
        mix_reactive(B_Beads, LiqClass=Beads_LC_2, cycles=3, maxTips=maxTips, v_perc=90)

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