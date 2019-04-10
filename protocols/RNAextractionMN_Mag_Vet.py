# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'Ariel'

from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100_FLI import Evo100_FLI
import EvoScriPy.Reactive as Rtv
from EvoScriPy.Instructions_Te_MagS import *


mix_mag_sub = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)
mix_mag_eluat = br"C:\Prog\robotevo\EvoScriPy\avr_MagMix_Eluat.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)
# Rbt.rep_sub = br"repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)
Rbt.rep_sub = br"C:\Prog\robotevo\EvoScriPy\repeat_subroutine.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)


class RNAextr_MN_Vet_Kit(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "RNA extraction with the MN_Vet kit"
    min_s, max_s = 1, 48

    def def_versions(self):
        self.versions = {'Serum with Liquid detection + tracking'    : not_implemented,
                         'Serum without Liquid detection + tracking' : not_implemented,
                         'Tissue without Liquid detection + tracking': not_implemented,
                         'Tissue with Liquid detection + tracking'   : not_implemented}


    def __init__(self, GUI = None,  run_name = None):

        Evo100_FLI.__init__(self,
                            GUI                         = GUI,
                            NumOfSamples                = RNAextr_MN_Vet_Kit.max_s,
                            worktable_template_filename = '../EvoScripts/wt_templates/avr_RNAext_MNVet_15TeMag.ewt',
                            output_filename             ='../current/AWL_RNAext_MNVet',
                            run_name                    = run_name)

    def Run(self):
        self.set_EvoMode()
        self.initialize()
        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()

                                                               # Get Labwares (Cuvette, eppys, etc.) from the work table

        LysBuf      = wt.getLabware(Lab.Trough_100ml,   "2-Vl Lysis Buffer"     )
        BindBuf     = wt.getLabware(Lab.Trough_100ml,   "3-VEB Binding Buffer"  )
        ElutBuf     = wt.getLabware(Lab.Trough_100ml,   "1-VEL-ElutionBuffer"   )

        Eluat     = wt.getLabware(Lab.EppRack3x16R,    "Eluat")
        Samples   = wt.getLabware(Lab.EppRack3x16,     "Proben")

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Reactives   = wt.getLabware(Lab.GreinRack16_2mL, "Reactives" )

        self.TeMg_Heat = wt.getLabware(Lab.TeMag48, "48 Pos Heat")
        self.TeMag     = wt.getLabware(Lab.TeMag48, "48PosMagnet")
        TeMag          = self.TeMag

                                                               #  Set the initial position of the tips

        self.go_first_pos()

                                                               # Set volumen / sample

        SampleVolume        = 200.0
        LysisBufferVolume   = 180.0             # VL
        IC2Volume           = 4.0               # IC2
        BindingBufferVolume = 600.0             # VEB
        B_BeadsVolume       = 20.0              # B-Beads
        VEW1Volume          = 600.0             # VEW1
        VEW2Volume          = 600.0             # VEW2
        EtOH80pVolume       = 600.0
        ProtKVolume         = 20.0
        cRNAVolume          = 4.0
        IC_MS2Volume        = 20.0              # MS2
        ElutionBufferVolume = 100.0             # VEL

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass      = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]
        par         = TeMag.parallelOrder(self.nTips, all_samples)

                                                        # Define the reactives in each labware (Cuvette, eppys, etc.)

        # IC2         = Rtv.Reactive("IC2 - synthetic RNA " ,  Reactives, pos=13, volpersample=  IC2Volume ,defLiqClass=W_liquidClass)

        ProtK = Rtv.Reactive("Proteinase K ",
                             Reactives,
                             replicas=2,
                             pos=[15, 16],               # only 16 ?  pos=16
                             volpersample=ProtKVolume,
                             defLiqClass=Small_vol_disp)

        cRNA   = Rtv.Reactive("Carrier RNA ", Reactives, pos=14, volpersample=cRNAVolume, defLiqClass=Small_vol_disp)
        IC_MS2 = Rtv.Reactive("IC MS2 phage culture ", Reactives, pos=13, volpersample=IC_MS2Volume, defLiqClass=Small_vol_disp)

        pK_cRNA_MS2 = Rtv.preMix("ProtK+cRNA+IC-MS2 mix ",
                                 Reactives,
                                 pos=8,
                                 components=[cRNA, ProtK, IC_MS2],
                                 defLiqClass=W_liquidClass,
                                 excess=20)

        LysisBuffer = Rtv.Reactive("VL - Lysis Buffer ", LysBuf, volpersample=LysisBufferVolume, defLiqClass='MN VL')

        B_Beads         = Rtv.Reactive("B - Beads " ,
                                       Reactives,
                                       pos          = [1,2],
                                       initial_vol  = 1200,
                                       volpersample = B_BeadsVolume ,
                                       defLiqClass  = Beads_LC_2,
                                       maxFull      = 70)

        BindingBuffer   = Rtv.Reactive("VEB - Binding Buffer " ,  BindBuf,   volpersample=BindingBufferVolume , defLiqClass=B_liquidClass)

        VEW1            = Rtv.Reactive( "VEW1 - Wash Buffer ",
                                        wt.getLabware(Lab.Trough_100ml, "4-VEW1 Wash Buffe"),
                                        volpersample  = VEW1Volume    ,
                                        defLiqClass   = B_liquidClass)

        VEW2            = Rtv.Reactive("VEW2 - WashBuffer "  ,
                                       wt.getLabware(Lab.Trough_100ml,  "5-VEW2-WashBuffer" ),
                                       volpersample  =VEW2Volume    ,
                                       defLiqClass   =B_liquidClass)

        EtOH80p         = Rtv.Reactive("Ethanol 80% "                     ,
                                         Lab.getLabware(Lab.Trough_100ml,  "7-EtOH80p"     ),
                                         volpersample=EtOH80pVolume , defLiqClass=B_liquidClass)

        ElutionBuffer   = Rtv.Reactive("Elution Buffer ",
                                       ElutBuf,
                                       volpersample  =ElutionBufferVolume ,
                                       defLiqClass   =B_liquidClass)            # defLiqClass="Eluat"   ??

                                                        # Show the CheckList GUI to the user for possible small changes
        self.CheckList()
        self.set_EvoMode()
                                                        # Define the reactives not shown in the CheckList GUI
                                                        # Define samples and the place for temporal reactions
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
            pK_cRNA_MS2.make(NumOfSamples)
            spread  (  reactive=pK_cRNA_MS2,   to_labware_region= TeMag.selectOnly(all_samples))

        with tips(reuse=True, drop=True, preserve=True):
            transfer(  from_labware_region= Samples,
                       to_labware_region=   TeMag,
                       volume=              SampleVolume,
                       using_liquid_class=  (SampleLiqClass, "Serum Disp postMix3"),
                       optimizeFrom         =False,     optimizeTo= True,
                       NumSamples=          NumOfSamples)
        Itr.wash_tips(wasteVol=4, FastWash=True).exec()

        with tips(reuse=True, drop=False):    # better reuse=True, drop=False ??
            spread  (  reactive=LysisBuffer,   to_labware_region= TeMag.selectOnly(all_samples))

        with incubation(10): pass

        with tips(tipsMask=maxMask, reuse=True, drop=False):
            for p in [40, 50, 60, 65]:
                mix_reactive(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)
    #        mix_reactive(B_Beads, LiqClass=Beads_LC_2, cycles=3, maxTips=maxTips, v_perc=90)

        with tips(reuse=True, drop=True):
            spread( reactive=B_Beads,      to_labware_region=TeMag.selectOnly(all_samples))

        with tips(reuse=True, drop=False, preserve=True, usePreserved=True):
            self.wash_in_TeMag(reactive=BindingBuffer, wells=all_samples)

        with tips(reuse=True, drop=False, preserve=True):
            self.wash_in_TeMag(reactive=VEW1, wells=all_samples)
            self.wash_in_TeMag(reactive=VEW2, wells=all_samples)

            with group("Wash in TeMag with " + EtOH80p.name), tips():
                spread( reactive=EtOH80p, to_labware_region= TeMag.selectOnly(all_samples))

                with parallel_execution_of(mix_mag_sub, repeat=NumOfSamples//self.nTips + 1):
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
            with parallel_execution_of(mix_mag_eluat, repeat=NumOfSamples//self.nTips+1):
                mix(TeMag.selectOnly(all_samples), ElutionBuffer.defLiqClass)

            with tips(usePreserved=preserveingTips(), preserve=False, drop=True):
                with incubation(minutes=1.0, timer=2):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
                transfer(from_labware_region=   TeMag.selectOnly(all_samples),
                         to_labware_region=     Eluat.selectOnly(all_samples),
                         volume=                ElutionBufferVolume,
                         optimizeTo=            False,
                         using_liquid_class=(ElutionBuffer.defLiqClass, ElutionBuffer.defLiqClass))
        self.done()

    def wash_in_TeMag( self, reactive, wells=None, using_liquid_class=None, vol=None):
            """

            :param reactive:
            :param wells:
            :param using_liquid_class: dict
            :param vol:
            """
            # import protocols.RNAextractionMN_Mag.RobotInitRNAextraction as RI

            wells = wells or reactive.labware.selected() or range(self.NumOfSamples)
            if not using_liquid_class:
                using_liquid_class =  reactive.defLiqClass
            with group("Wash in TeMag with " + reactive.name):

                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
                spread(reactive=reactive, to_labware_region=self.TeMag.selectOnly(wells))

                with parallel_execution_of(mix_mag_sub, repeat=self.NumOfSamples//self.nTips + 1):
                    mix(self.TeMag.selectOnly(wells), using_liquid_class, vol)

                with incubation(minutes=0.5, timer=2):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
                with tips(usePreserved=preserveingTips(), preserve=False, drop=True):
                    waste(self.TeMag.selectOnly(wells), using_liquid_class, vol)
