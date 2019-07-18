# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'
# todo: deprecate, this is now one version in Prefill_plates_LysisBuffer_and_ProtKpreMix

from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100 import Evo100_FLI
import EvoScriPy.Reagent as Rgt


class Prefill_plates_LysisBuffer(Evo100_FLI):
    """
    Prefill plates with LysisBuffer for the
    Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL
    with washes in the Fischer Robot.
    """

    name = "Prefill plates with LysisBuffer for KingFisher"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'3 plate': self.V_3_plate,
                         '2 plate': self.V_2_plate,
                         '1 plate': self.V_1_plate                         }

    def V_1_plate(self):
        self.num_plates = 1

    def V_2_plate(self):
        self.num_plates = 2

    def V_3_plate(self):
        self.num_plates = 3

    def __init__(self, GUI=None, run_name="Prefill plates with LysisBuffer"):

        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            NumOfSamples            = Prefill_plates_LysisBuffer.max_s,
                            worktable_template_filename='../EvoScripts/wt_templates/Prefill_plates_LysisBuffer.ewt',
                            output_filename         ='../current/' + run_name,
                            run_name                = run_name)

    def Run(self):
        self.initialize()

        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill {:d} plates with LysisBufferReact for {:d} samples.'\
                       .format(self.num_plates,
                               NumOfSamples     )).exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table
        LysBufCuvette = wt.get_labware(Lab.Trough_100ml, "2-Vl Lysis Buffer")

        DiTi1000_1  = wt.get_labware(Lab.DiTi_1000ul, "1000-1")
        DiTi1000_2  = wt.get_labware(Lab.DiTi_1000ul, "1000-2")
        DiTi1000_3  = wt.get_labware(Lab.DiTi_1000ul, "1000-3")


        self.go_first_pos()                      #  Set the initial position of the tips

        # Set volumen / sample
        LysisBufferVolume   = 100.0       # VL1 or VL

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

        # Define the reactives in each labware (Cuvette, eppys, etc.)

        LysisBufferReact = Rgt.Reagent("VL - Lysis Buffer ",
                                       LysBufCuvette,
                                       volpersample = LysisBufferVolume,
                                       defLiqClass  = 'MN VL',
                                       num_of_samples= self.num_plates * NumOfSamples)

        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        LysPlat = [wt.get_labware(Lab.MP96deepwell, "Plate lysis-" + str(i + 1)) for i in range(self.num_plates)]

        par = LysPlat[0].parallelOrder(self.nTips, all_samples)

        # Define place for temporal reactions
        for i, LP in enumerate(LysPlat):
            for s in all_samples:
                Rgt.Reagent("lysis_{:d}-{:02d}".format(i + 1, s + 1),
                            LP,
                            initial_vol =0.0,
                            wells=s + 1,
                            excess      =0)

        with group("Prefill plates with LysisBufferReact"):

            Itr.userPrompt("Put the plates for LysisBufferReact").exec()

            for LP in LysPlat:
                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=LysisBufferReact, to_labware_region=LP.selectOnly(all_samples))
                self.drop_tips()

        self.done()
