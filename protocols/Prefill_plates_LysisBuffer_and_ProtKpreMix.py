# Copyright (C) 2018-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2018

from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100_FLI import Evo100_FLI
import EvoScriPy.Reactive as Rtv      # ??

__author__ = 'Ariel'


class Prefill_plates_LysisBuffer_and_ProtKpreMix(Evo100_FLI):
    """
    Prefill plates with LysisBuffer for the
    Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL
    with washes in the Fischer Robot.
    """

    name = "Prefill plates with LysisBuffer and ProtK preMix for KingFisher"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'3 plate': self.V_3_plate,
                         '2 plate': self.V_2_plate,
                         '1 plate': self.V_1_plate,
                         '3 plate from Cuvette preMix': self.V_3_plate_Cuvette,
                         '2 plate from Cuvette preMix': self.V_2_plate_Cuvette,
                         '1 plate from Cuvette preMix': self.V_1_plate_Cuvette
                         }

    def V_1_plate(self):
        self.num_plates = 1
        self.preMix_from_Cuvette = False


    def V_2_plate(self):
        self.num_plates = 2
        self.preMix_from_Cuvette = False

    def V_3_plate(self):
        self.num_plates = 3
        self.preMix_from_Cuvette = False

    def V_1_plate_Cuvette(self):
        self.num_plates = 1
        self.preMix_from_Cuvette = True

    def V_2_plate_Cuvette(self):
        self.num_plates = 2
        self.preMix_from_Cuvette = True

    def V_3_plate_Cuvette(self):
        self.num_plates = 3
        self.preMix_from_Cuvette = True

    def __init__(self, GUI=None, run_name="Prefill plates with LysisBuffer"):
        self.num_plates = 1
        self.preMix_from_Cuvette = False
        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            NumOfSamples            = Prefill_plates_LysisBuffer_and_ProtKpreMix.max_s,
                            worktable_template_filename='../EvoScripts/wt_templates/Prefill_plates_LysisBuffer.ewt',   # Prefill_plates_LysisBuffer_and_ProtKpreMix.ewt',
                            output_filename         ='../current/' + run_name,
                            run_name                = run_name)

    def Run(self):
        self.set_EvoMode()
        self.initialize()
        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill {:d} plates with Lysis Buffer and ProtK preMix  for {:d} samples.'\
                       .format(self.num_plates,
                               NumOfSamples     )).exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table
        if self.preMix_from_Cuvette:
            preMixProtKCuvette = wt.getLabware(Lab.Trough_100ml, "8-preMix ProtK")
        LysBufCuvette      = wt.getLabware(Lab.Trough_100ml, "2-Vl Lysis Buffer")

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Reactives   = wt.getLabware(Lab.GreinRack16_2mL, "Reactives" )


        self.go_first_pos()                      #  Set the initial position of the tips

        # Set volumen / sample
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        LysisBufferVolume   = 100.0       # VL1 or VL
        IC_MS2Volume        =  10.0
        #IC2Volume           =   5.0       # ? 4

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

        # Define the reactives in each labware (Cuvette, eppys, etc.)

        if self.preMix_from_Cuvette:
            pK_cRNA_MS2 = Rtv.Reactive("preMix ProtK+cRNA+MS2 ",
                                         preMixProtKCuvette,
                                         volpersample=ProtKVolume + cRNAVolume + IC_MS2Volume,
                                         defLiqClass=Small_vol_disp,
                                         num_of_samples=self.num_plates * NumOfSamples )
        else:
            ProtK = Rtv.Reactive("Proteinase K ",
                                 Reactives,
                                 volpersample   = ProtKVolume,
                                 defLiqClass    = Small_vol_disp,
                                 num_of_samples = self.num_plates * NumOfSamples,
                                 maxFull        = 90  )
            ProtK.maxFull=0.96

            cRNA = Rtv.Reactive("Carrier RNA ",
                                Reactives,
                                volpersample    = cRNAVolume,
                                defLiqClass     = Small_vol_disp,
                                num_of_samples  = self.num_plates * NumOfSamples,
                                maxFull         = 95  )

            IC_MS2 = Rtv.Reactive("IC MS2 phage culture ",
                                  Reactives,
                                  volpersample   = IC_MS2Volume,
                                  defLiqClass    = Small_vol_disp,
                                  num_of_samples = self.num_plates * NumOfSamples,
                                  maxFull        = 95  )

            pK_cRNA_MS2 = Rtv.preMix("ProtK+cRNA+IC-MS2 mix ",
                                     Reactives,
                                     components     = [cRNA, ProtK, IC_MS2],
                                     defLiqClass    = W_liquidClass,
                                     excess         = 8,
                                     maxFull        = 90,
                                     num_of_samples = self.num_plates * NumOfSamples  )
            pK_cRNA_MS2.maxFull = 0.95

        LysisBufferReact = Rtv.Reactive("VL - Lysis Buffer ",
                                        LysBufCuvette,
                                        volpersample    = LysisBufferVolume,
                                        defLiqClass     = 'MN VL',
                                        num_of_samples  = self.num_plates * NumOfSamples  )

        # Show the CheckList GUI to the user for possible small changes

        self.CheckList()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        LysPlat = [wt.getLabware(Lab.MP96deepwell, "Plate lysis-"+str(i+1)) for i in range(self.num_plates)]

        par = LysPlat[0].parallelOrder(self.nTips, all_samples)

        # Define place for temporal "reactions"
        for i, LP in enumerate(LysPlat):
            for s in all_samples:
                Rtv.Reactive(   "lysis_{:d}-{:02d}".format( i+1, s + 1),
                                LP,
                                initial_vol =0.0,
                                pos         =s + 1,
                                excess      =0        )

        with group("Prefill plates with LysisBufferReact"):

            if not self.preMix_from_Cuvette:
                with self.tips(tipsMask=maxMask, reuse=True, drop=False):
                    self.makePreMix(pK_cRNA_MS2, NumSamples=self.num_plates * NumOfSamples)


            Itr.userPrompt("Put the plates for LysisBufferReact").exec()

            for LP in LysPlat:
                with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.spread(reactive=pK_cRNA_MS2, to_labware_region=LP.selectOnly(all_samples))

                with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.spread(reactive=LysisBufferReact, to_labware_region=LP.selectOnly(all_samples))

        self.dropTips()

        self.done()
