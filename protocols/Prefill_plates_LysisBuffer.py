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


class Prefill_plates_LysisBuffer(Evo100_FLI):
    """
    Prefill plates with LysisBuffer for the
    Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL
    with washes in the Fischer Robot.
    """

    name = "Prefill plates with LysisBuffer for KingFisher"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'1 plate': self.V_1_plate,
                         '2 plate': self.V_2_plate,
                         '3 plate': self.V_3_plate,                      }

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
        self.set_EvoMode()
        self.initialize()
        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill {:d} plates with LysisBuffer for {:d} samples.'\
                       .format(self.num_plates,
                               NumOfSamples     )).exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table
        LysBuf = wt.getLabware(Lab.Trough_100ml, "2-Vl Lysis Buffer")

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")


        self.go_first_pos()                      #  Set the initial position of the tips

        # Set volumen / sample
        LysisBufferVolume   = 100.0       # VL1 or VL

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

        # Define the reactives in each labware (Cuvette, eppys, etc.)

        LysisBuffer = Rtv.Reactive("VL - Lysis Buffer ",
                                    LysBuf,
                                    volpersample = LysisBufferVolume,
                                    defLiqClass  = 'MN VL'             )

        # Show the CheckList GUI to the user for possible small changes

        self.CheckList()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        LysPlat = [wt.getLabware(Lab.MP96deepwell, "Plate lysis-"+str(i)) for i in range(1, self.num_plates)]  # move to 23.5

        par = LysPlat[0].parallelOrder(self.nTips, all_samples)

        # Define place for temporal reactions
        for s in all_samples:
            [Rtv.Reactive("lysis_{:d}-{:02d}".format( i, s + 1),
                         LP,
                         initial_vol=0.0,
                         pos=s + 1,
                         excess=0        ) for i, LP in enumerate(LysPlat) ]

        with group("Prefill plates with LysisBuffer"):

            Itr.userPrompt("Put the plates for LysisBuffer").exec()

            with self.tips(reuse=True, drop=False):
                for LP in LysPlat:
                    self.spread(reactive=LysisBuffer, to_labware_region=LP.selectOnly(all_samples))

        self.dropTips()

        self.done()
