# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# Tutorial

from EvoScriPy.protocol_steps import *
from protocols.evo200_f.evo200_f import Evo200_FLI


class Tutorial_HL_RoMa(Evo200_FLI):
    """
    Starting with 2 plates (A amd B, B on some plate pedestal - hotel) move plate B into a different location;
    then transfer 50µL of aqueous buffer from column 1 of plate A to column 2 of plate B.

    There are different ways to achieve that. Here is one:
    - Create a reagent buffer_A in column 1 of plate A, with 100 uL per well.
    - Generate check list
    - Transfer plate B from the hotel to the worktable
    - Create a reagent buffer_B in column 2 of plate B.
    - Transfer 50µL of buffer_A to buffer_B.

    """

    name = "Tutorial_HL. Dilutions."
    min_s, max_s = 1, 96                                            # 96 well plate ??

    def def_versions(self):                                         # for now just ignore the variants
        self.versions = {'No version': self.no_versions}

    def no_versions(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 num_of_samples: int         = 8,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        Evo200_FLI.__init__(self,
                        GUI                         = GUI,
                        num_of_samples=num_of_samples or Tutorial_HL_RoMa.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      '../EvoScripts/wt_templates/tutorial_hl_dilution.ewt',
                        output_filename             = output_filename or '../current/RoMa_HL',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()           # if needed calls Executable.initialize() and set_EvoMode
                                    # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        assert 1 <= self.num_of_samples <= Tutorial_HL_RoMa.max_s, "Using 96 well plates."
        wt = self.worktable

        instr.comment('Transfer 50 uL to a moved plate.').exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table    -----------------------------------------------
        plate_A = wt.get_labware("plate")
        plate_A = wt.get_labware("plate")

        v  = 50                                       # uL to be distribute


        buffer_A = Reagent("buffer",              # Define the reagents in each labware (Cuvette, eppys, etc.) -
                               labware      = plate_A,
                               wells        = "A1",
                               replicas     = 8,
                               volpersample = v)

        self.check_list()                                          # Show the check_list   -------------------------

        instr.wash_tips(wasteVol=5, FastWash=True).exec()

        plate = wt.get_labware(label="plate", labw_type="96 Well Microplate")

        dilution = Reagent("mix1, diluted 1:10",               # Define place for intermediate reactions  ----------
                                plate,
                                replicas         = n,
                                minimize_aliquots= False)

        with group("Fill dilutions"):

            instr.userPrompt("Put the plate for dilutions in " + str(plate.location)).exec()

            with self.tips(tip_type="DiTi 200 ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = mix1,
                                to_labware_region = dilution.select_all())

            with self.tips(tip_type="DiTi 1000ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = diluent,
                                to_labware_region = dilution.select_all())

            self.drop_tips()

        self.done()


if __name__ == "__main__":
    p = Tutorial_HL_RoMa(num_of_samples= 42,
                         run_name        = "_42s")

    p.use_version('No version')
    p.Run()
