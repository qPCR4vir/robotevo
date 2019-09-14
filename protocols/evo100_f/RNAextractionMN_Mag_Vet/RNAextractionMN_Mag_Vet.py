# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'Ariel'

from protocols.evo100_f.evo100_f import *
from EvoScriPy.instructions_Te_MagS import *


mix_mag_sub = br"C:\Prog\robotevo\EvoScripts\subroutines\avr_MagMix.esc" .decode(EvoScriPy.evo_mode.Mode.encoding)
mix_mag_eluat = br"C:\Prog\robotevo\EvoScripts\subroutines\avr_MagMix_Eluat.esc".decode(EvoScriPy.evo_mode.Mode.encoding)
# robot.rep_sub = br"repeat_subroutine.esc" .decode(mode.Mode.encoding)
robot.rep_sub = br"C:\Prog\robotevo\EvoScripts\subroutines\repeat_subroutine.esc".decode(EvoScriPy.evo_mode.Mode.encoding)


class RNAextr_MN_Vet_Kit(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "RNA extraction with the MN_Vet kit"
    min_s, max_s = 1, 48

    def def_versions(self):
        self.versions = {'VL-only prefill'     : self.ver_fill_inactivation,
                         'VL-pKmix prefill'    : self.ver_fill_preMix_inactivation,
                         'VL-only inactivated' : self.ver_VL_inactivated,
                         'VL-pKmix Inactivated': self.ver_preMix_inactivated,
                         'original samples'    : self.ver_original_samples}
        # add new version from plate to plate

    def versions_defaults(self):
        self.add_samples    = True
        self.add_preMix     = True
        self.add_VL         = True
        self.do_extraction  = True

    def ver_original_samples(self):
        self.versions_defaults()

    def ver_VL_inactivated(self):
        self.versions_defaults()
        self.add_VL         = False
        self.add_samples    = False

    def ver_preMix_inactivated(self):
        self.ver_VL_inactivated()
        self.add_preMix     = False

    def ver_fill_preMix_inactivation(self):
        self.versions_defaults()
        self.add_samples   = False
        self.do_extraction = False

    def ver_fill_inactivation(self):
        self.ver_fill_preMix_inactivation()
        self.add_preMix     = False

    def __init__(self,
                 GUI                            = None,
                 num_of_samples       : int       = None,
                 worktable_template_filename    = None,
                 output_filename                = None,
                 firstTip                       = None,
                 run_name           : str       = ""):

        self.versions_defaults()
        this = Path(__file__).parent
        Evo100_FLI.__init__(self,
                            GUI                         = GUI,
                            num_of_samples=num_of_samples or RNAextr_MN_Vet_Kit.max_s,
                            worktable_template_filename = worktable_template_filename or
                                                          this / 'avr_RNAext_MNVet_15TeMag.ewt',
                            output_filename         = output_filename or this / 'scripts' / 'RNAext_MNVet_TeMag',
                            firstTip                = firstTip,
                            run_name                = run_name)

    def run(self):
        self.initialize()

        num_of_samples = self.num_of_samples
        wt           = self.worktable

        self.comment((self.version + 'for extracting RNA from {:s} samples with the MN-Vet kit')
                     .format(str(num_of_samples)))

                                                               # Get Labwares (Cuvette, eppys, etc.) from the work table

        if self.add_VL:
            LysBuf      = wt.get_labware("2-Vl Lysis Buffer", labware.Trough_100ml)

        if self.do_extraction:
            BindBuf     = wt.get_labware("3-VEB Binding Buffer", labware.Trough_100ml)
            ElutBuf     = wt.get_labware("1-VEL-ElutionBuffer", labware.Trough_100ml)
            Eluat       = wt.get_labware("Eluat", labware.EppRack3x16R)

        Samples     = wt.get_labware("Proben", labware.EppRack3x16)
        Lysis       = Samples

        DiTi1000_1  = wt.get_labware("1000-1", labware.DiTi_1000ul)
        DiTi1000_2  = wt.get_labware("1000-2", labware.DiTi_1000ul)
        DiTi1000_3  = wt.get_labware("1000-3", labware.DiTi_1000ul)

        Reagents   = wt.get_labware("Reactives", labware.GreinRack16_2mL)

        if self.do_extraction:
            self.TeMg_Heat = wt.get_labware("48 Pos Heat", labware.TeMag48)
            self.TeMag     = wt.get_labware("48PosMagnet", labware.TeMag48)
            TeMag          = self.TeMag
            Lysis          = TeMag

                                                               #  Set the initial position of the tips

        self.set_first_tip()

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

        all_samples = range(num_of_samples)
        maxTips     = min  (self.n_tips, num_of_samples)
        maxMask     = robot.tipsMask[maxTips]
        par         = Lysis.parallelOrder(self.n_tips, all_samples)

                                                        # Define the Reagents in each labware (Cuvette, eppys, etc.)

        # IC2         = Reagent("IC2 - synthetic RNA " ,  Reagents, pos=13,
        #                            volpersample=  IC2Volume ,def_liq_class=W_liquidClass)

        if self.add_preMix:
            ProtK = Reagent("Proteinase K ",
                                Reagents,
                                replicas            = 2,
                                minimize_aliquots   = False,
                                wells               = [15, 16],  # only 16 ?  pos=16
                                volpersample        = ProtKVolume,
                                def_liq_class         = self.Small_vol_disp)

            cRNA   = Reagent("Carrier RNA ",
                                 Reagents,
                                 wells= 14,
                                 volpersample       = cRNAVolume,
                                 def_liq_class        = self.Small_vol_disp)

            IC_MS2 = Reagent("IC MS2 phage culture ",
                                 Reagents,
                                 wells= 13,
                                 volpersample       = IC_MS2Volume,
                                 def_liq_class        = self.Small_vol_disp)

            pK_cRNA_MS2 = preMix("ProtK+cRNA+IC-MS2 mix ",
                                     Reagents,
                                     pos            = 8,
                                     components     = [cRNA, ProtK, IC_MS2],
                                     def_liq_class    = self.W_liquidClass,
                                     excess         = 20)

        if self.add_VL:
            LysisBuffer = Reagent("VL - Lysis Buffer ",
                                      LysBuf,
                                      volpersample  =LysisBufferVolume,
                                      def_liq_class   ='MN VL')

        if self.do_extraction:
            B_Beads         = Reagent("B - Beads ",
                                          Reagents,
                                          wells= [1, 2],
                                          initial_vol  = 1200.0,
                                          volpersample = B_BeadsVolume,
                                          def_liq_class  = self.Beads_LC_2,
                                          maxFull      = 70)

            BindingBuffer   = Reagent("VEB - Binding Buffer ",
                                          BindBuf,
                                          volpersample  = BindingBufferVolume,
                                          def_liq_class   = self.B_liquidClass)

            VEW1            = Reagent("VEW1 - Wash Buffer ",
                wt.get_labware("4-VEW1 Wash Buffe", labware.Trough_100ml),
                                          volpersample  = VEW1Volume,
                                          def_liq_class   = self.B_liquidClass)

            VEW2            = Reagent("VEW2 - WashBuffer ",
                wt.get_labware("5-VEW2-WashBuffer", labware.Trough_100ml),
                                          volpersample  =VEW2Volume,
                                          def_liq_class   =self.B_liquidClass)

            EtOH80p         = Reagent("Ethanol 80% ",
                                      labware.getLabware(labware.Trough_100ml,  "7-EtOH80p"     ),
                                      volpersample=EtOH80pVolume, def_liq_class=self.B_liquidClass)

            ElutionBuffer   = Reagent("Elution Buffer ",
                                      ElutBuf,
                                      volpersample  =ElutionBufferVolume,
                                      def_liq_class   =self.B_liquidClass)            # def_liq_class="Eluat"   ??

                                                        # Show the check_list GUI to the user for possible small changes
        self.check_list()
        self.set_EvoMode()
                                                        # Define the Reagents not shown in the check_list GUI
                                                        # Define samples and the place for intermediate reactions
        for s in all_samples:
            Reagent("lysis_{:02d}".format(s + 1),
                        Lysis,
                        initial_vol    = InitLysisVol,
                        wells          = par[s] + 1,
                        def_liq_class  = SampleLiqClass,
                        excess         = 0)

            if self.do_extraction:
                Reagent("RNA_{:02d}".format(s + 1),
                            Eluat,
                            initial_vol   = 0.0,
                            wells         = s + 1,
                            def_liq_class = self.Water_free,
                            excess        = 0)

                Reagent("probe_{:02d}".format(s + 1),
                            Samples,
                            single_use    = SampleVolume if self.add_samples else InitLysisVol,
                            wells         = s + 1,
                            def_liq_class = SampleLiqClass,
                            excess        = 0)

        instructions.wash_tips(wasteVol=30, FastWash=True).exec()
        if self.do_extraction:
            Te_MagS_ActivateHeater(50).exec()                                     # set incubation temperature at 50°C
            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()

        if self.add_preMix:                                                               # add  ProtK+cRNA+MS2 mix
            with group("Add pre mix Prot K."), self.tips(tips_mask=maxMask, reuse=True, drop=False):
                self.makePreMix(pK_cRNA_MS2)
                self.distribute  (reagent=pK_cRNA_MS2, to_labware_region= Lysis.selectOnly(all_samples))

        if self.do_extraction:                                                            # add samples
            with self.tips(reuse=True, drop=True, preserve=False):
                self.transfer( from_labware_region  = Samples,
                               to_labware_region    = Lysis,
                               volume               = SampleVolume if self.add_samples else InitLysisVol,
                               using_liquid_class   = (SampleLiqClass, "Serum Disp postMix3"),
                               optimize_from        = False,
                               optimizeTo           = True,
                               num_samples          = num_of_samples)
            instructions.wash_tips(wasteVol=4, FastWash=True).exec()

        if self.add_VL:                                                                     # add  LysisBuffer
            with self.tips(reuse=True, drop=False, drop_first=True):
                self.distribute  (reagent=LysisBuffer, to_labware_region= Lysis.selectOnly(all_samples))

        if not self.do_extraction:
            self.done()
            return

        with incubation(10): pass # if self.add_samples

        with group("Add B-Beads"):

            with self.tips(tips_mask=maxMask, reuse=True, drop=False):
                for p in [40, 50, 60, 65]:
                    self.mix_reagent(B_Beads, LiqClass=self.Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)
            with self.tips(reuse=True, drop=True):
                self.distribute(reagent=B_Beads, to_labware_region=TeMag.selectOnly(all_samples))

        with self.tips(reuse=True, drop=False, preserve=True):
            self.wash_in_TeMag(reagent=BindingBuffer,   wells=all_samples)
            self.wash_in_TeMag(reagent=VEW1,            wells=all_samples)
            self.wash_in_TeMag(reagent=VEW2,            wells=all_samples)

            with group("Wash in TeMag with " + EtOH80p.name), self.tips():   # Atypical wash. Include incubation at 50°C

                self.distribute(reagent=EtOH80p, to_labware_region= TeMag.selectOnly(all_samples))

                with parallel_execution_of(mix_mag_sub, repeat=num_of_samples // self.n_tips + 1):
                    self.mix( TeMag.selectOnly(all_samples), EtOH80p.def_liq_class)

                with incubation(minutes=0.5):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()

                with self.tips(use_preserved=self.preserveingTips()):
                    self.waste( from_labware_region=    TeMag.selectOnly(all_samples))

                with incubation(minutes=4):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()

                with incubation(minutes=4):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate, z_pos=24).exec()

        with group("Elution"):

            with self.tips(reuse=True, drop=False):

                self.distribute(reagent=ElutionBuffer, to_labware_region=TeMag.selectOnly(all_samples))

                with incubation(minutes=2):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Incubation).exec()
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()

            with self.tips(reuse=True, drop=True):

                with parallel_execution_of(mix_mag_eluat, repeat=num_of_samples // self.n_tips + 1):
                    self.mix(TeMag.selectOnly(all_samples), ElutionBuffer.def_liq_class)

                with incubation(minutes=1.0, timer=2):
                    Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()

                self.transfer(   from_labware_region=   TeMag.selectOnly(all_samples),
                                 to_labware_region=     Eluat.selectOnly(all_samples),
                                 volume=                ElutionBufferVolume,
                                 optimizeTo=            False,
                                 using_liquid_class=(ElutionBuffer.def_liq_class, ElutionBuffer.def_liq_class))

        self.drop_tips()
        self.done()

    def wash_in_TeMag(self, reagent, wells=None, using_liquid_class=None, vol=None):
        """

        :param reagent:
        :param wells:
        :param using_liquid_class: dict
        :param vol:
        """
        wells = wells or reagent.labware.selected() or range(self.num_of_samples)
        if not using_liquid_class:
            using_liquid_class = reagent.def_liq_class
        with group("Wash in TeMag with " + reagent.name):

            Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Dispense).exec()
            self.distribute(reagent=reagent, to_labware_region=self.TeMag.selectOnly(wells))

            with parallel_execution_of(mix_mag_sub, repeat=self.num_of_samples // self.n_tips + 1):
                self.mix(self.TeMag.selectOnly(wells), using_liquid_class, vol)

            with incubation(minutes=0.5, timer=2):
                Te_MagS_MoveToPosition(Te_MagS_MoveToPosition.Aspirate).exec()
            with self.tips(use_preserved=self.preserveingTips(), preserve=False, drop=True):
                self.waste(self.TeMag.selectOnly(wells), using_liquid_class, vol)


if __name__ == "__main__":

    p = RNAextr_MN_Vet_Kit(num_of_samples= 48, run_name= "_48_original samples")

    p.use_version('original samples')
    p.set_first_tip('A01')
    p.run()
