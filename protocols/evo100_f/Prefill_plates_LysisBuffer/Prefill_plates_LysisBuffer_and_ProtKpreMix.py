# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *
from protocols.evo100_f.evo100_f import Evo100_FLI


class Prefill_plates_LysisBuffer_and_ProtKpreMix(Evo100_FLI):
    """
    Prefill plates with LysisBuffer for the
    Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL
    with washes in the Fischer Robot.
    """

    name = "Prefill plates with LysisBuffer and ProtK PreMix for KingFisher"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'3 plate': self.v_3_plate,
                         '2 plate': self.v_2_plate,
                         '1 plate': self.v_1_plate,
                         '3 plate from Cuvette PreMix': self.V_3_plate_Cuvette,
                         '2 plate from Cuvette PreMix': self.V_2_plate_Cuvette,
                         '1 plate from Cuvette PreMix': self.V_1_plate_Cuvette,
                         '3 plate from Cuvette LysBuf-pK-PreMix': self.V_3_plate_LysBuf_pK_Cuvette,
                         '2 plate from Cuvette LysBuf-pK-PreMix': self.V_2_plate_LysBuf_pK_Cuvette,
                         '1 plate from Cuvette LysBuf-pK-PreMix': self.V_1_plate_LysBuf_pK_Cuvette
                         }

    def v_1_plate(self):        self.def_init(1)
    def v_2_plate(self):        self.def_init(2)
    def v_3_plate(self):        self.def_init(3)

    def plate_pK_Cuvette(self, num_plates=1):
        self.def_init(num_plates)
        self.preMix_from_Cuvette = True
    def V_1_plate_Cuvette(self):        self.plate_pK_Cuvette(1)
    def V_2_plate_Cuvette(self):        self.plate_pK_Cuvette(2)
    def V_3_plate_Cuvette(self):        self.plate_pK_Cuvette(3)

    def plate_LysBuf_pK_Cuvette(self, num_plates=1):
        self.def_init(num_plates)
        self.preMix_from_LysBuf_pK_Cuvette = True
    def V_1_plate_LysBuf_pK_Cuvette(self):        self.plate_LysBuf_pK_Cuvette(1)
    def V_2_plate_LysBuf_pK_Cuvette(self):        self.plate_LysBuf_pK_Cuvette(2)
    def V_3_plate_LysBuf_pK_Cuvette(self):        self.plate_LysBuf_pK_Cuvette(3)

    def def_init(self, num_plates=1):
        self.num_plates = num_plates
        self.preMix_from_Cuvette = False
        self.preMix_from_LysBuf_pK_Cuvette = False

    def __init__(self, GUI=None, run_name=None, output_filename=None):
        self.def_init()
        this = Path(__file__).parent
        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            num_of_samples          = Prefill_plates_LysisBuffer_and_ProtKpreMix.max_s,
                            worktable_template_filename=this / 'Prefill_plates_LysisBuffer.ewt',
                            output_filename         = output_filename or (this / 'scripts' / 'Prefill_LysisBuffer_pK'),
                            run_name                = run_name)

    def run(self):
        self.initialize()

        num_of_samples = self.num_of_samples
        wt           = self.worktable

        self.comment('Prefill {:d} plates with Lysis Buffer and ProtK PreMix  for {:d} samples.'\
                     .format(self.num_plates, num_of_samples))

                                                            # Get Labwares (Cuvette, eppys, etc.) from the work table

        preMixProtKCuvette = wt.get_labware("8-PreMix ProtK", labware.Trough_100ml)
        LysBufCuvette      = wt.get_labware("2-Vl Lysis Buffer", labware.Trough_100ml)

        DiTi1000_1  = wt.get_labware("1000-1", labware.DiTi_1000ul)
        DiTi1000_2  = wt.get_labware("1000-2", labware.DiTi_1000ul)
        DiTi1000_3  = wt.get_labware("1000-3", labware.DiTi_1000ul)

        Reagents_TubeRack   = wt.get_labware("Reactives", labware.GreinRack16_2mL)


        self.set_first_tip()                                 #  Set the initial position of the tips

                                                            # Set volumen / sample
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        LysisBufferVolume   = 100.0       # VL1 or VL
        IC_MS2Volume        =  10.0
        #IC2Volume           =   5.0              # IC2     4 uL?
        preMixVol           = ProtKVolume + cRNAVolume + IC_MS2Volume
        preMixName          = "ProtK+cRNA+MS2 "
        if self.preMix_from_LysBuf_pK_Cuvette:
            preMixVol += LysisBufferVolume
            preMixName += "+LysB "

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        all_samples = range(num_of_samples)
        maxTips     = min  (self.n_tips, num_of_samples)
        maxMask     = robot.mask_tips[maxTips]

                                                        # Define the reagents in each labware (Cuvette, eppys, etc.)

        if self.preMix_from_Cuvette or self.preMix_from_LysBuf_pK_Cuvette:
            pK_cRNA_MS2 = Reagent(preMixName,
                                      preMixProtKCuvette,
                                      volpersample=preMixVol,
                                      def_liq_class='MN VL',
                                      num_of_samples=self.num_plates * num_of_samples)
        else:
            ProtK = Reagent("Proteinase K ",
                                Reagents_TubeRack,
                                volpersample   = ProtKVolume,
                                def_liq_class    = self.Small_vol_disp,
                                num_of_samples = self.num_plates * num_of_samples,
                                fill_limit_aliq= 90)
            ProtK.fill_limit_aliq=0.96

            cRNA = Reagent("Carrier RNA ",
                               Reagents_TubeRack,
                               volpersample    = cRNAVolume,
                               def_liq_class     = self.Small_vol_disp,
                               num_of_samples  = self.num_plates * num_of_samples,
                               fill_limit_aliq= 95)

            IC_MS2 = Reagent("IC MS2 phage culture ",
                                 Reagents_TubeRack,
                                 volpersample   = IC_MS2Volume,
                                 def_liq_class    = self.Small_vol_disp,
                                 num_of_samples = self.num_plates * num_of_samples,
                                 fill_limit_aliq= 95)

            pK_cRNA_MS2 = PreMix("ProtK+cRNA+IC-MS2 mix ",
                                 Reagents_TubeRack,
                                 components     = [cRNA, ProtK, IC_MS2],
                                 def_liq_class    = self.W_liquidClass,
                                 excess         = 8,
                                 fill_limit_aliq= 90,
                                 num_of_samples = self.num_plates * num_of_samples)
            pK_cRNA_MS2.fill_limit_aliq = 0.95

        if not self.preMix_from_LysBuf_pK_Cuvette:
            LysisBufferReact = Reagent("VL - Lysis Buffer ",
                                           LysBufCuvette,
                                           volpersample    = LysisBufferVolume,
                                           def_liq_class     = 'MN VL',
                                           num_of_samples  = self.num_plates * num_of_samples)

                                                        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        LysPlat = [wt.get_labware("Plate lysis-" + str(i + 1), labware.MP96deepwell) for i in range(self.num_plates)]

        par = LysPlat[0].parallelOrder(self.n_tips, all_samples)

        # Define place for intermediate "reactions"
        for i, LP in enumerate(LysPlat):
            for s in all_samples:
                Reagent("lysis_{:d}-{:02d}".format(i + 1, s + 1),
                            LP,
                            initial_vol =0.0,
                            wells=s + 1,
                            excess      =0)

        with group("Prefill plates with LysisBufferReact"):

            if not (self.preMix_from_Cuvette or self.preMix_from_LysBuf_pK_Cuvette):
                with self.tips(tips_mask=maxMask, reuse=True, drop=False):
                    self.make_pre_mix(pK_cRNA_MS2, num_samples=self.num_plates * num_of_samples)


            self.user_prompt("Put the plates for LysisBufferReact")

            for LP in LysPlat:
                with self.tips(tips_mask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.distribute(reagent=pK_cRNA_MS2, to_labware_region=LP.selectOnly(all_samples))

                if not self.preMix_from_LysBuf_pK_Cuvette:
                    with self.tips(tips_mask=maxMask, reuse=True, drop=False, drop_last=True):
                        self.distribute(reagent=LysisBufferReact, to_labware_region=LP.selectOnly(all_samples))

        self.drop_tips()

        self.done()


if __name__ == "__main__":

    p = Prefill_plates_LysisBuffer_and_ProtKpreMix(run_name='1 plate')

    p.use_version('1 plate')
    p.run()
