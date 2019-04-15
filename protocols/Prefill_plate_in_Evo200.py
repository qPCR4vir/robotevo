# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# just testing a new, generic Evo200

from   EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions   as     Itr
import EvoScriPy.Labware        as     Lab
import EvoScriPy.Reactive       as     Rtv

from protocols.Evo200 import Evo200


class Prefill_plate_in_Evo200(Evo200):
    """
    Prefill one plate with Buffer.
    """

    name = "Prefill one plate with Buffer."
    min_s, max_s = 1, 96

    # for now just ignore the variants
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

    def __init__(self, GUI=None, run_name="Prefill plate"):

        Evo200.__init__(self,
                            GUI                     = GUI,
                            NumOfSamples            = Prefill_plate_in_Evo200.max_s,
                            worktable_template_filename='../EvoScripts/wt_templates/Prefill_plates_LysisBuffer.ewt',
                            output_filename         ='../current/pp200' + run_name,
                            run_name                = run_name)

    def Run(self):
        self.set_EvoMode()   # this add: self.iRobot = EvoMode.iRobot(Itr.Pipette.LiHa1, nTips=self.nTips)
                             # in which: self.robot = Rbt.Robot(index=index, arms=arms, nTips=nTips)
        self.initialize()    # if needed calls Executable.initialize() and set_EvoMode
                             # which calls GUI.update_parameters() and set_defaults() from Evo200

        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill {:d} plates with LysisBufferReact for {:d} samples.'\
                       .format(self.num_plates,
                               NumOfSamples     )).exec()

                                                            # Get Labwares (Cuvette, eppys, etc.) from the work table
        BufCuvette = wt.getLabware(Lab.Trough_100ml, "2-Vl Lysis Buffer")




        self.go_first_pos()                                                     #  Set the initial position of the tips

                                                                                  # Set volumen / sample
        BufferVolume   = 100.0       # VL1 or VL

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

                                                        # Define the reactives in each labware (Cuvette, eppys, etc.)

        BufferReact = Rtv.Reactive("Buffer ",
                                        BufCuvette,
                                        volpersample = BufferVolume,
                                        defLiqClass  = 'MN VL',
                                        num_of_samples= self.num_plates * NumOfSamples)

        # Show the CheckList GUI to the user for possible small changes

        self.CheckList()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        LysPlat = [wt.getLabware(Lab.MP96deepwell, "Plate lysis-"+str(i+1)) for i in range(self.num_plates)]

        par = LysPlat[0].parallelOrder(self.nTips, all_samples)

        # Define place for temporal reactions
        for i, LP in enumerate(LysPlat):
            for s in all_samples:
                Rtv.Reactive(   "lysis_{:d}-{:02d}".format( i+1, s + 1),
                                LP,
                                initial_vol =0.0,
                                pos         =s + 1,
                                excess      =0        )

        with group("Prefill plates with BufferReact"):

            Itr.userPrompt("Put the plates for BufferReact").exec()

            for LP in LysPlat:
                with self.tips(reuse=True, drop=False):
                    self.spread(reactive=BufferReact, to_labware_region=LP.selectOnly(all_samples))
                self.dropTips()

        self.done()
