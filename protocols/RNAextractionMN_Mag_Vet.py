# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'Ariel'

from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100 import Evo100_FLI
import EvoScriPy.Reagent as Rtv
from EvoScriPy.Instructions_Te_MagS import *


mix_mag_sub = br"C:\Prog\robotevo\EvoScripts\subroutines\avr_MagMix.esc" .decode(EvoScriPy.EvoMode.Mode.encoding)
mix_mag_eluat = br"C:\Prog\robotevo\EvoScripts\subroutines\avr_MagMix_Eluat.esc".decode(EvoScriPy.EvoMode.Mode.encoding)
# Rbt.rep_sub = br"repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)
Rbt.rep_sub = br"C:\Prog\robotevo\EvoScripts\subroutines\repeat_subroutine.esc".decode(EvoScriPy.EvoMode.Mode.encoding)


class RNAextr_MN_Vet_Kit(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "RNA extraction with the MN_Vet kit"
    min_s, max_s = 1, 48


    def def_versions(self):
        self.versions = {'VL-pKmix prefill'    : self.V_fill_preMix_inactivation,
                         'VL-only prefill'     : self.V_fill_inactivation,
                         'VL-only inactivated' : self.V_VL_inactivated,
                         'VL-pKmix Inactivated': self.V_preMix_inactivated,
                         'original samples'    : self.V_original_samples                }


    def V_default(self):
        self.add_samples    = True
        self.add_preMix     = True
        self.add_VL         = True
        self.do_extraction  = True

    def V_original_samples(self):
        self.V_default()

    def V_VL_inactivated(self):
        self.V_default()
        self.add_VL         = False
        self.add_samples    = False

    def V_preMix_inactivated(self):
        self.V_VL_inactivated()
        self.add_preMix     = False

    def V_fill_preMix_inactivation(self):
        self.V_default()
        self.add_samples   = False
        self.do_extraction = False

    def V_fill_inactivation(self):
        self.V_fill_preMix_inactivation()
        self.add_preMix     = False

    def __init__(self,
                 GUI                            = None,
                 NumOfSamples       : int       = None,
                 worktable_template_filename    ='../EvoScripts/wt_templates/avr_RNAext_MNVet_15TeMag.ewt',
                 output_filename                ='../current/RNAext_MNVet_TeMag',
                 run_name           : str       = ""):

        self.V_default()

        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            NumOfSamples            = NumOfSamples or RNAextr_MN_Vet_Kit.max_s,
                            worktable_template_filename
                                                    = worktable_template_filename,
                            output_filename         = output_filename + run_name,
                            run_name                = run_name)

    def Run(self):
        self.set_EvoMode()
        self.initialize()
        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment((self.version + 'for extracting RNA from {:s} samples with the MN-Vet kit')
                    .format(str(NumOfSamples))).exec()

                                                               # Get Labwares (Cuvette, eppys, etc.) from the work table

        if self.add_VL:
            LysBuf      = wt.getLabware(Lab.Trough_100ml,   "2-Vl Lysis Buffer"     )

        if self.do_extraction:
            BindBuf     = wt.getLabware(Lab.Trough_100ml,   "3-VEB Binding Buffer"  )
            ElutBuf     = wt.getLabware(Lab.Trough_100ml,   "1-VEL-ElutionBuffer"   )
            Eluat       = wt.getLabware(Lab.EppRack3x16R,    "Eluat")

        Samples     = wt.getLabware(Lab.EppRack3x16,     "Proben")
        Lysis       = Samples

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Reagents   = wt.getLabware(Lab.GreinRack16_2mL, "Reactives" )

        if self.do_extraction:
            self.TeMg_Heat = wt.getLabware(Lab.TeMag48, "48 Pos Heat")
            self.TeMag     = wt.getLabware(Lab.TeMag48, "48PosMagnet")
            TeMag          = self.TeMag
            Lysis  =  TeMag

                                                               #  Set the initial position of the tips

        self.go_first_pos()

                                                               # Set volumen / sample

        SampleVolume        = 200.0
        LysisBufferVolume   = 180.0             # VL
        IC2Volume           =   4.0             # IC2
        IC_MS2Volume        =  10.0             # MS2
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        BindingBufferVolume = 600.0             # VEB
        B_BeadsVolume       =  20.0             # B-Beads
        VEW1Volume          = 600.0             # VEW1
        VEW2Volume          = 600.0             # VEW2
        EtOH80pVolume       = 600.0
        ElutionBufferVolume = 100.0             # VEL

        InitLysisVol        = 0.0
        if self.do_extraction:
            if not self.add_samples:    InitLysisVol += SampleVolume
            if not self.add_preMix:     InitLysisVol += ProtKVolume + cRNAVolume + IC_MS2Volume
            if not self.add_VL:         InitLysisVol += LysisBufferVolume

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass      = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]
        if self.do_extraction:
            par         = TeMag.parallelOrder(self.nTips, all_samples)

                                                        # Define the Reagents in each labware (Cuvette, eppys, etc.)

        # IC2         = Rtv.Reagent("IC2 - synthetic RNA " ,  Reagents, pos=13,
        #                            volpersample=  IC2Volume ,defLiqClass=W_liquidClass)

        if self.add_preMix:
            ProtK = Rtv.Reagent("Proteinase K ",
                                Reagents,
                                replicas            = 2,
                                pos=[15, 16],                   # only 16 ?  pos=16
                                volpersample        = ProtKVolume,
                                defLiqClass         = Small_vol_disp)

            cRNA   = Rtv.Reagent("Carrier RNA ",
                                 Reagents,
                                 pos                = 14,
                                 volpersample       = cRNAVolume,
                                 defLiqClass        = Small_vol_disp)

            IC_MS2 = Rtv.Reagent("IC MS2 phage culture ",
                                 Reagents,
                                 pos                = 13,
                                 volpersample       = IC_MS2Volume,
                                 defLiqClass        = Small_vol_disp)

            pK_cRNA_MS2 = Rtv.preMix("ProtK+cRNA+IC-MS2 mix ",
                                     Reagents,
                                     pos            = 8,
                                     components     = [cRNA, ProtK, IC_MS2],
                                     defLiqClass    = W_liquidClass,
                                     excess         = 20)

        if self.add_VL:
            LysisBuffer = Rtv.Reagent("VL - Lysis Buffer ",
                                      LysBuf,
                                      volpersample  =LysisBufferVolume,
                                      defLiqClass   ='MN VL')

        if self.do_extraction:
            B_Beads         = Rtv.Reagent("B - Beads ",
                                          Reagents,
                                          pos          = [1,2],
                                          initial_vol  = 1200,
                                          volpersample = B_BeadsVolume,
                                          defLiqClass  = Beads_LC_2,
                                          maxFull      = 70)

            BindingBuffer   = Rtv.Reagent("VEB - Binding Buffer ",
                                          BindBuf,
                                          volpersample  = BindingBufferVolume,
                                          defLiqClass   = B_liquidClass)

            VEW1            = Rtv.Reagent("VEW1 - Wash Buffer ",
                                          wt.getLabware(Lab.Trough_100ml, "4-VEW1 Wash Buffe"),
                                          volpersample  = VEW1Volume,
                                          defLiqClass   = B_liquidClass)

            VEW2            = Rtv.Reagent("VEW2 - WashBuffer ",
                                          wt.getLabware(Lab.Trough_100ml,  "5-VEW2-WashBuffer" ),
                                          volpersample  =VEW2Volume,
                                          defLiqClass   =B_liquidClass)

            EtOH80p         = Rtv.Reagent("Ethanol 80% ",
                                          Lab.getLabware(Lab.Trough_100ml,  "7-EtOH80p"     ),
                                          volpersample=EtOH80pVolume, defLiqClass=B_liquidClass)

            ElutionBuffer   = Rtv.Reagent("Elution Buffer ",
                                          ElutBuf,
                                          volpersample  =ElutionBufferVolume,
                                          defLiqClass   =B_liquidClass)            # defLiqClass="Eluat"   ??

                                                        # Show the CheckList GUI to the user for possible small changes
        self.CheckList()
        self.set_EvoMode()
                                                        # Define the Reagents not shown in the CheckList GUI
                                                        # Define samples and the place for temporal reactions
        for s in all_samples:
            Rtv.Reagent("lysis_{:02d}".format(s + 1),
                        Lysis,
                        initial_vol     = InitLysisVol,
                        pos             = s + 1,
                        defLiqClass     = SampleLiqClass,
                        excess          = 0)

            if self.do_extraction:
                Rtv.Reagent("RNA_{:02d}".format(s + 1),
                            Eluat,
                            initial_vol = 0.0,
                            pos         = s+1,
                            defLiqClass = def_liquidClass,
                            excess      = 0)

                if self.add_samples:
                    Rtv.Reagent("probe_{:02d}".format(s + 1),
                                Samples,
                                single_use  = SampleVolume,
                                pos         = s+1,
                                defLiqClass = SampleLiqClass,
                                excess      = 0)

        Itr.wash_tips(wasteVol=30, FastWash=True).exec()
        if self.do_extraction:
            Te_MagS_ActivateHeater(50).exec()
            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()

        if self.add_preMix:                                                               #  add  ProtK+cRNA+MS2 mix
            with self.tips(tipsMask=maxMask, reuse=True, drop=False):
                self.makePreMix(pK_cRNA_MS2)
                self.spread  (reagent=pK_cRNA_MS2, to_labware_region= Lysis.selectOnly(all_samples))

        if self.add_samples:                                                               # add samples
            with self.tips(reuse=True, drop=True, preserve=True):
                self.transfer( from_labware_region  = Samples,
                               to_labware_region    = Lysis,
                               volume               = SampleVolume,
                               using_liquid_class   = (SampleLiqClass, "Serum Disp postMix3"),
                               optimizeFrom         = False,
                               optimizeTo           = True,
                               NumSamples           = NumOfSamples)
            Itr.wash_tips(wasteVol=4, FastWash=True).exec()

        if self.add_VL:                                                                     # add  LysisBuffer
            with self.tips(reuse=True, drop=False, drop_first=True):
                self.spread  (reagent=LysisBuffer, to_labware_region= Lysis.selectOnly(all_samples))


        if not self.do_extraction:
            self.done()
            return

        with incubation(10): pass


        with group("Beads binding"):

            with self.tips(tipsMask=maxMask, reuse=True, drop=False):
                for p in [40, 50, 60, 65]:
                    self.mix_reagent(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)
            with self.tips(reuse=True, drop=True):
                self.spread(reagent=B_Beads, to_labware_region=TeMag.selectOnly(all_samples))

            with self.tips(reuse=True, drop=False, preserve=True, usePreserved=self.add_samples):
                self.wash_in_TeMag(reagent=BindingBuffer, wells=all_samples)

        with self.tips(reuse=True, drop=False, preserve=True):
            self.wash_in_TeMag(reagent=VEW1, wells=all_samples)
            self.wash_in_TeMag(reagent=VEW2, wells=all_samples)

            with group("Wash in TeMag with " + EtOH80p.name), self.tips():
                self.spread(reagent=EtOH80p, to_labware_region= TeMag.selectOnly(all_samples))

                with parallel_execution_of(mix_mag_sub, repeat=NumOfSamples//self.nTips + 1):
                    self.mix( TeMag.selectOnly(all_samples), EtOH80p.defLiqClass)
                with incubation(minutes=0.5):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()
                with self.tips(usePreserved=self.preserveingTips()):
                    self.waste( from_labware_region=    TeMag.selectOnly(all_samples))

                with incubation(minutes=4):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()
                with incubation(minutes=4):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()

            self.spread(reagent=ElutionBuffer, to_labware_region=TeMag.selectOnly(all_samples))
            with incubation(minutes=2):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()

            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
            with parallel_execution_of(mix_mag_eluat, repeat=NumOfSamples//self.nTips+1):
                self.mix(TeMag.selectOnly(all_samples), ElutionBuffer.defLiqClass)

            with self.tips(usePreserved=self.preserveingTips(), preserve=False, drop=True):
                with incubation(minutes=1.0, timer=2):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
                self.transfer(   from_labware_region=   TeMag.selectOnly(all_samples),
                                 to_labware_region=     Eluat.selectOnly(all_samples),
                                 volume=                ElutionBufferVolume,
                                 optimizeTo=            False,
                                 using_liquid_class=(ElutionBuffer.defLiqClass, ElutionBuffer.defLiqClass))
        self.dropTips()
        self.done()

    def wash_in_TeMag(self, reagent, wells=None, using_liquid_class=None, vol=None):
        """

        :param reagent:
        :param wells:
        :param using_liquid_class: dict
        :param vol:
        """
        # import protocols.RNAextractionMN_Mag.RobotInitRNAextraction as RI

        wells = wells or reagent.labware.selected() or range(self.NumOfSamples)
        if not using_liquid_class:
            using_liquid_class =  reagent.defLiqClass
        with group("Wash in TeMag with " + reagent.name):

            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
            self.spread(reagent=reagent, to_labware_region=self.TeMag.selectOnly(wells))

            with parallel_execution_of(mix_mag_sub, repeat=self.NumOfSamples//self.nTips + 1):
                self.mix(self.TeMag.selectOnly(wells), using_liquid_class, vol)

            with incubation(minutes=0.5, timer=2):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
            with self.tips(usePreserved=self.preserveingTips(), preserve=False, drop=True):
                self.waste(self.TeMag.selectOnly(wells), using_liquid_class, vol)
