# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# Tutorial, generic Evo200

from   EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions   as     Itr
import EvoScriPy.Labware        as     Lab
import EvoScriPy.Reagent        as     Rgt

from protocols.Evo200 import Evo200


class Tutorial_LL(Evo200):
    """
    Created n wells with 100 uL of mix1 diluted 1:10. A diluent is provided.
    A reagent "mix1" is diluted (distributed) in n wells 1:10.
    The final volume of each dilution is vf=100 uL.

    There are many ways to achieve that. Here is one:
    - Calculate how much to distribute from mix1 to each Dil_10. v= vf/10 and from diluent vd.
    - Create well mix1 in an Eppendorf Tube 1,5 mL for v uL per "sample".
    - Create wells diluent in a cubette 100 mL for vd uL per "sample".
    - Generate check list
    - Create n Dil_10_i wells ( 1 from 0 to n-1 )
    - Distribute mix1
    - Distribute diluent

    """

    name = "Tutorial_LL. Dilutions."
    min_s, max_s = 1, 96   # all dilutions in one 96 well plate

    # for now just ignore the variants
    def def_versions(self):
        self.versions = {'No version': self.V_def               }

    def V_def(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 NumOfSamples: int           = 8,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        Evo200.__init__(self,
                        GUI                         = GUI,
                        NumOfSamples                = NumOfSamples or Tutorial_LL.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      '../EvoScripts/wt_templates/tutorial_hl_dilution.ewt',
                        output_filename             = output_filename or '../current/dilutions_LL',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()    # if needed calls Executable.initialize() and set_EvoMode
                             # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        n = self.NumOfSamples
        assert 1 <= n <= Tutorial_LL.max_s , "In this demo we want to set dilutions in a 96 well plate."
        wt           = self.worktable

        Itr.comment('Dilute1:10  a mix in {:d} wells.'.format(n)).exec()

                                                            # Get Labwares (Cuvette, eppys, etc.) from the work table
        diluent_cuvette   = wt.get_labware(Lab.Trough_100ml, "BufferCub")
        assert isinstance(diluent_cuvette, Lab.Cuvette)

        mixes             = wt.get_labware(Lab.Eppendorfrack, "mixes")
        assert isinstance(mixes, Lab.Labware)


        self.go_first_pos()                                             #  Set the initial position of the tips ??

                                                                                  # Set volumen / sample
        dilutions = range(n)
        maxTips     = min  (self.nTips, n)
        maxMask     = Rbt.tipsMask[maxTips]

        vf = 100                                # The final volume of every dilution, uL

        v  = vf /10                             # to be distribute from original mix1 to each Dil_10
        vd = vf - v
        excess = 1.04   # 4%

        # Define the wells in each labware (Cuvette, eppys, etc.)

        diluent = diluent_cuvette.Wells[0:7]
        diluent[0].vol = vd * n * excess

        mix1    = mixes.Wells[0]
        mix1.vol = v * n * excess

        # Show the check_list

        Itr.userPrompt("Put diluent in "+str(diluent[0]) ).exec()
        Itr.userPrompt("Put mix1 in " + str(mix1)).exec()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        plate = wt.get_labware(Lab.MP96MachereyNagel, "plate1")
        assert isinstance(plate, Lab.Labware)

        # Define place for temporal reactions
        dilution = plate.Wells[:n]

        with group("Fill dilutions"):

            Itr.userPrompt("Put the plate for dilutions in " + str(plate.location)).exec()

            with self.tips(tip_type="DiTi 200 ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = mix1,
                                to_labware_region = dilution.select_all())

            with self.tips(tip_type="DiTi 1000ul", reuse=True, drop=False, drop_last=True):
                self.distribute(reagent           = diluent,
                                to_labware_region = dilution.select_all())

            self.drop_tips()

        self.done()


if __name__ == "__main__":
    p = Tutorial_LL(NumOfSamples    = 42,
                                run_name        = "_42s")

    p.use_version('No version')
    # p.go_first_pos('A01')
    p.Run()