# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *
from protocols.evo100_f.evo100_f import Evo100_FLI


class PreKingFisher_RNAextNucleoMag_EtOH80p(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "PreKingFisher for RNA extraction modified NucleoMag MN_Vet kit and EtOH80p Plate preFill"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'VL-pKmix prefill'     : self.V_fill_preMix_inactivation,
                         'VL-only prefill'      : self.V_fill_inactivation,
                         'VL-only inactivated'  : self.V_VL_inactivated,
                         'VL-pKmix Inactivated' : self.V_preMix_inactivated,
                         'original samples'     : self.V_original_samples           }

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
        self.add_samples    = False
        self.do_extraction  = False

    def V_fill_inactivation(self):
        self.V_fill_preMix_inactivation()
        self.add_preMix     = False


    def __init__(self,
                 GUI                            = None,
                 num_of_samples       : int       = None,
                 worktable_template_filename    = None,
                 output_filename                = None,
                 first_tip                       = None,
                 run_name           : str       = ""):

        self.V_default()
        this = Path(__file__).parent
        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            num_of_samples=num_of_samples or PreKingFisher_RNAextNucleoMag_EtOH80p.max_s,
                            worktable_template_filename
                                                    = worktable_template_filename or
                                                      this / 'PreKingFisher_RNAextNucleoMag_EtOH80p.ewt',
                            output_filename         = output_filename or
                                                      this / 'scripts' / 'PreKingFisher_RNAextNucleoMag_EtOH80p',
                            first_tip= first_tip,
                            run_name                = run_name)

    def run(self):
        self.initialize()                       # set_defaults ??

        wt           = self.worktable

        self.comment((self.version + 'for extracting RNA from {:s} samples with the MN-Vet kit')
                     .format(str(self.num_of_samples)))

                                                        # Get Labwares (Cuvette, eppys, etc.) from the work table

        if self.add_VL:
            LysBuf      = wt.get_labware("2-Vl Lysis Buffer", labware.Trough_100ml)

        if self.do_extraction:
            BindBuf     = wt.get_labware("3-VEB Binding Buffer", labware.Trough_100ml)

        DiTi1000_1  = wt.get_labware("1000-1", labware.DiTi_1000ul)
        DiTi1000_2  = wt.get_labware("1000-2", labware.DiTi_1000ul)
        DiTi1000_3  = wt.get_labware("1000-3", labware.DiTi_1000ul)

        Reagents    = wt.get_labware("Reactives", labware.GreinRack16_2mL)

                                                                # Set the initial position of the tips

        self.set_first_tip()

                                                                # Set volumen / sample

        SampleVolume        = 100.0
        LysisBufferVolume   = 100.0                 # VL
        # IC2Volume         =   5.0                 # IC2 ? 4
        IC_MS2Volume        =  10.0                 # MS2
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        BindingBufferVolume = 350.0                 # VEB
        B_BeadsVolume       =  20.0                 # B-Beads
        EtOH80pVolume       = 600.0

        InitLysisVol        =   0.0
        if self.do_extraction:
            if not self.add_samples:    InitLysisVol += SampleVolume
            if not self.add_preMix:     InitLysisVol += ProtKVolume + cRNAVolume + IC_MS2Volume
            if not self.add_VL:         InitLysisVol += LysisBufferVolume

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass = "Serum Asp"

        all_samples = range(self.num_of_samples)
        maxTips     = min  (self.n_tips, self.num_of_samples)
        maxMask     = robot.mask_tips[maxTips]

                                                        # Define the reactives in each labware (Cuvette, eppys, etc.)

        if self.add_preMix:                             # we need to add ProtK+cRNA+MS2 mix
            ProtK       = Reagent("Proteinase K ",
                                      Reagents,
                                      num_of_aliquots= 2,
                                      minimize_aliquots=False,
                                      wells= [15, 16],
                                      volpersample = ProtKVolume,
                                      def_liq_class  = self.Small_vol_disp)

            cRNA        = Reagent("Carrier RNA ",
                                      Reagents,
                                      wells= 14,
                                      volpersample  = cRNAVolume,
                                      def_liq_class   = self.Small_vol_disp)

            IC_MS2      = Reagent("IC MS2 phage culture ",
                                      Reagents,
                                      wells= 13,
                                      volpersample  = IC_MS2Volume,
                                      def_liq_class   = self.Small_vol_disp)

            # IC2         = Reagent("IC2 - synthetic RNA " ,  Reagents, pos=13,
            #                           volpersample=  IC2Volume ,def_liq_class=W_liquidClass)

            pK_cRNA_MS2 = preMix  ("ProtK+cRNA+IC-MS2 mix "  ,
                                       Reagents,
                                       pos          = 8,
                                       components   = [cRNA, ProtK, IC_MS2] ,
                                       def_liq_class  = self.W_liquidClass,
                                       excess       = 20)

        if self.add_VL:
            LysisBuffer = Reagent("VL - Lysis Buffer ",
                                      LysBuf,
                                      volpersample  = LysisBufferVolume,
                                      def_liq_class   = 'MN VL')

        if self.do_extraction:
            B_Beads         = Reagent("B - Beads ",
                                      Reagents,
                                      wells= [1, 2],
                                      initial_vol  = 1200,
                                      volpersample = B_BeadsVolume,
                                      def_liq_class  = self.Beads_LC_2,
                                      fill_limit_aliq= 70)

            BindingBuffer   = Reagent("VEB - Binding Buffer ",
                                      BindBuf,
                                      volpersample  = BindingBufferVolume,
                                      def_liq_class   = self.B_liquidClass)

        EtOH80p         = Reagent("Ethanol 80% ",
                                  wt.get_labware("7-EtOH80p", labware.Trough_100ml),
                                  volpersample      =EtOH80pVolume,
                                  def_liq_class       =self.B_liquidClass)

                                                        # Show the check_list GUI to the user for possible small changes
        self.check_list()
        self.set_EvoMode()

                                                        # Define the Reagents not shown in the check_list GUI
                                                        # Define samples and the place for intermediate reactions

        Plate_lysis = wt.get_labware("Plate lysis", labware.MP96deepwell)  # Plate 12 x 8 ?
        Plate_EtOH  = wt.get_labware("Plate EtOH", labware.MP96deepwell)  # Plate 12 x 8 ? MP96well !!

        if self.version != 'original samples':
           Samples  = wt.get_labware("Proben", labware.EppRack6x16)  # 6x16 = 12 x 8 ?


        par = Plate_lysis.parallelOrder(self.n_tips, all_samples)

        for s in all_samples:

            Reagent("lysis_{:02d}".format(s + 1),
                        Plate_lysis,
                        initial_vol = InitLysisVol,
                        wells=par[s] + 1,
                        excess      = 0)

            Reagent("EtOH80p_{:02d}".format(s + 1),
                        Plate_EtOH,
                        initial_vol = 0.0,
                        wells=par[s] + 1,  # todo revise order !!!
                        excess      = 0)

            if self.add_samples:
                Reagent("probe_{:02d}".format(s + 1),
                            Samples,
                            single_use  = SampleVolume,
                            wells=s + 1,
                            def_liq_class = SampleLiqClass,
                            excess      = 0)


        instructions.wash_tips(wasteVol=30, FastWash=True).exec()

        with group("Prefill plate with EtOH80p"):

            with self.tips(reuse=True, drop=False, drop_last=True):
                self.distribute(reagent=EtOH80p, to_labware_region=Plate_EtOH.selectOnly(all_samples))

        with group("Sample Lysis"):

            if self.add_preMix:                                          # add  ProtK+cRNA+MS2 mix

                with self.tips(tips_mask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.make_pre_mix(pK_cRNA_MS2)
                    self.distribute  (reagent=pK_cRNA_MS2, to_labware_region= Plate_lysis.selectOnly(all_samples))

            if self.add_VL:                                             # add  LysisBuffer

                with self.tips(tips_mask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.distribute  (reagent=LysisBuffer, to_labware_region= Plate_lysis.selectOnly(all_samples))

            if self.add_samples:                                        # add samples

                self.user_prompt("Please make sure the samples are in place")
                with self.tips(reuse=False, drop=True):
                    self.transfer( from_labware_region  = Samples,
                                   to_labware_region    = Plate_lysis,
                                   volume               = SampleVolume,
                                   using_liquid_class   = (SampleLiqClass, "Serum Disp postMix3"),
                                   optimize_from= False,
                                   optimize_to= True,           # todo Really ??
                                   num_samples          = num_of_samples)

                instructions.wash_tips(wasteVol=4, FastWash=True).exec()

            if self.do_extraction and self.add_preMix:
                self.user_prompt("Please Schutteln the plates for lysis in pos 1")
                with incubation(minutes=5):
                    pass

        if self.do_extraction:
            self.user_prompt("Please make sure the samples are back in place")

            with group("Beads binding"):

                with self.tips(tips_mask=maxMask, reuse=True, drop=False):
                    for p in [40, 50, 60, 65]:
                        self.mix_reagent(B_Beads, liq_class=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)

                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=B_Beads, to_labware_region=Plate_lysis.selectOnly(all_samples))

                self.drop_tips()

                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=BindingBuffer, to_labware_region=Plate_lysis.selectOnly(all_samples))

                self.user_prompt("Please Schutteln the plates for lysis in pos 1")

        self.drop_tips()
        self.done()


if __name__ == "__main__":

    p = PreKingFisher_RNAextNucleoMag_EtOH80p(num_of_samples= 96,
                                              run_name        = "")

    p.use_version('VL-pKmix Inactivated')
    # p.set_first_tip('A01')
    p.run()
