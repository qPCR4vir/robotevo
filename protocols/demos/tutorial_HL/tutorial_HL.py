# author Ariel Vina-Rodriguez (qPCR4vir)
# this example is free to use at your onw risk
# 2019-2019
__author__ = 'Ariel'

# Tutorial

from EvoScriPy.protocol_steps import *
from protocols.evo200_f.evo200_f import Evo200_FLI


class Tutorial_HL(Evo200_FLI):
    """
    Prepare a dilution 1:10 of mix1 in n 100 uL wells. A diluent is provided.

    A reagent "mix1" is diluted (distributed) in n wells 1:10.
    The final volume of each dilution is vf=100 uL.

    There are many ways to achieve that. Here is one:
    - Calculate how much to distribute from mix1 to each dilution_10. v= vf/10 and from diluent vd.
    - Define a reagent `mix1` in an Eppendorf rack (labware) `mixes` for v uL per "sample".
    - Define a reagent `diluent` in a 100 mL cubette `BufferCub` for vd uL per "sample".
    - Generate a check list
    - Define a `diluted` reagent in microplate `plate` with n "replicas"
    - Distribute mix1
    - Distribute diluent

    """

    name = "Tutorial_HL. Dilutions."
    min_s, max_s = 1, 96                    # all dilutions in one 96 well plate

    def def_versions(self):                 # for now just ignore the variants
        self.versions = {'No version': self.v_def}

    def v_def(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 num_of_samples: int         = 8,
                 worktable_template_filename = None,
                 output_filename             = None,
                 first_tip                   = None,
                 run_name: str               = ""):

        this = Path(__file__).parent

        Evo200_FLI.__init__(self,
                            GUI                         = GUI,
                            num_of_samples              = num_of_samples or Tutorial_HL.max_s,
                            worktable_template_filename = worktable_template_filename or
                                                          this / 'tutorial_hl_dilution.ewt',
                            output_filename             = output_filename or this / 'scripts' / 'dilutions_HL',
                            first_tip= first_tip,
                            run_name                    = run_name)

    def run(self):
        self.initialize()           # if needed calls Executable.initialize() and set_EvoMode
                                    # which calls GUI.update_parameters() and set_defaults() from Evo200
        self.show_runtime_check_list = True

        assert 1 <= self.num_of_samples <= Tutorial_HL.max_s, "In this demo we want to set dilutions in a 96 well plate."
        wt = self.worktable

        self.comment('Dilute 1:10 mix1 in {:d} wells.'.format(self.num_of_samples))

        vf = 100                                      # The final volume of every dilution, uL
        v  = vf /10                                   # uL to be distribute from original mix1 to each dilution_10
        vd = vf - v                                   # uL to be distribute from diluent to each dilution_10

        # Define the reagents in each labware (Cuvette, eppys, etc.) -
        diluent = Reagent("diluent", labware="BufferCub", def_liq_class=self.Water_free, volpersample = vd)
        mix1    = Reagent("mix1",  labware="mixes", def_liq_class=self.Water_free,  volpersample = v)

        self.check_list()                                          # Show the check_list   -------------------------

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        plate = wt.get_labware("plate")

        diluted = Reagent("mix1, diluted 1:10",                    # Define derived reagents  ---------------------
                          plate,
                          replicas         = self.num_of_samples,
                          def_liq_class    = self.Water_free,
                          minimize_aliquots= False)

        with group("Fill dilutions"):

            self.user_prompt("Put the plate for dilutions in " + str(plate.location))

            with self.tips(tip_type="DiTi 200 ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = mix1,
                                to_labware_region = diluted.select_all())

            with self.tips(tip_type="DiTi 1000ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = diluent,
                                to_labware_region = diluted.select_all())

        self.done()


if __name__ == "__main__":
    logging.basicConfig(filename=('scripts/Tutorial_HL.log.txt'), filemode='w', level=logging.INFO)
    p = Tutorial_HL(num_of_samples=42, run_name="_42s")
    p.run()
