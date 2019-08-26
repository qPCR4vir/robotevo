# author Ariel Vina-Rodriguez (qPCR4vir)
# this example is free to use at your onw risk
# 2019-2019
__author__ = 'Ariel'

# Tutorial

from EvoScriPy.protocol_steps import *
from protocols.evo200_f.evo200_f import Evo200_FLI


class Tutorial_HL_RoMa(Evo200_FLI):
    """
    Put a plate in place and transfer 50 µL to 1 column from a wells in 2nd column of another plate

    Starting with 2 plates (A amd B, B somewhere else (1- other carrier, 2- on some plate pedestal - hotel)
    move plate B into a different location;
    then transfer 50 µL of aqueous buffer from column 1 of plate A to column 2 of plate B.

    There are different ways to achieve that. Here is one:
    - Define a reagent buffer_A in column 1 of `plateA` , with 100 uL per well.
    - Generate check list
    - Transfer plate B from the original location `plateB_origen` to the final location `plateB`
    - Create a reagent buffer_B in column 2 of `plateB`.
    - Transfer 50µL of buffer_A to buffer_B.

    """

    name = "Tutorial_HL_RoMa. Dilutions."
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

        this = Path(__file__).parent

        Evo200_FLI.__init__(self,
                        GUI                         = GUI,
                        num_of_samples              = num_of_samples or Tutorial_HL_RoMa.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      this / 'tutorial_hl_RoMa_dilution.ewt',
                        output_filename             = output_filename or this / 'scripts' / 'RoMa_HL',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()           # if needed calls Executable.initialize() and set_EvoMode
                                    # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        assert 1 <= self.num_of_samples <= Tutorial_HL_RoMa.max_s - 8, "Using 96 well plates."
        # assert self.num_of_samples == 8, "testing just one column."

        wt = self.worktable

        self.comment('Transfer 50 uL to a moved plate.')

        # Get Labwares (Cuvette, eppys, etc.) from the work table    -----------------------------------------------
        plate_A = wt.get_labware("plateA")
        plate_B = wt.get_labware("plateB_origen")
        new_location = wt.get_labware("plateB").location

        v  = 50                                       # uL to be distribute

        buffer_A = Reagent("buffer",              # Define the reagents in each labware (Cuvette, eppys, etc.) -
                               labware      = plate_A,
                               wells        = "A1",
                               replicas     = self.num_of_samples,
                               volpersample = v,
                               initial_vol  = [100]*self.num_of_samples,
                               defLiqClass  = self.Water_free,
                               minimize_aliquots= False)

        self.check_list()                                          # Show the check_list   -------------------------
        self.user_prompt("Put the plate B in " + str(plate_B.location))

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        instructions.transfer_rack(plate_B, new_location).exec()

        buffer_B = Reagent("buffer B",              # Define place for intermediate reactions  ----------
                           labware      = plate_B,
                           wells        = "A1",
                           replicas     = self.num_of_samples,
                           defLiqClass  = self.Water_free,
                           minimize_aliquots= False)

        with group("Fill column"):

            with self.tips(tip_type="DiTi 200 ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = buffer_A,
                                to_labware_region = buffer_B.select_all())

        self.done()

if __name__ == "__main__":
    p = Tutorial_HL_RoMa(num_of_samples= 8,
                         run_name        = "_8s")

    p.use_version('No version')
    p.Run()
