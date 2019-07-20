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


class Tutorial_HL(Evo200):
    """
    Created n wells with 100 uL of mix1 diluted 1:10 and another n diluted 1:100. A diluent is provided.
    A reagent "mix1" is diluted (distributed) in n wells 1:10. This is used to create n more wells diluted 1:10
    (mix1 1:100). The final volume of every dilution is vf=100 uL.

    There are many ways to achieve that. Here is one:
    - Calculate how much of one Dil_10, we need to `transfer` to prepare one Dil_100: v_10 = vf / 10 and how much
    to distribute from the diluent, vd_10.
    - Calculate how much to distribute from mix1 to each Dil_10. v= (vf+v_10)/10 and from diluent vd.
    - Create a reagent mix1 in an Eppendorf Tube 1,5 mL for v uL per "sample".
    - Create a reagent diluent in an cubette 100 mL for vd_10+vd uL per "sample".
    - Generate check list
    - Create n Dil_10_i reagents ( 1 from 0 to n-1 )
    - Create n Dil_100_i reagents ( 1 from 0 to n-1 )
    - Distribute diluent
    - Distribute mix1
    - Mix and transfer, Dil_10 to Dil_100


    """

    name = "Tutorial_HL. Dilutions."
    min_s, max_s = 1, 96/2   # all dilutions in one 96 well plate

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
                        NumOfSamples                = NumOfSamples or Tutorial_HL.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      '../EvoScripts/wt_templates/demo-two.mixes.Evo200example.ewt',
                        output_filename             = output_filename or '../current/dilutions_HL',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()    # if needed calls Executable.initialize() and set_EvoMode
                             # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        n = self.NumOfSamples
        assert 1 <= n <= Tutorial_HL.max_s , "In this demo we want to set 2x NumOfSamples in a 96 well plate."
        wt           = self.worktable

        Itr.comment('Dilute a mix 1:10 and 1:100 in {:d} wells each dilution.'.format(n)).exec()

                                                            # Get Labwares (Cuvette, eppys, etc.) from the work table
        diluent_cuvette   = wt.getLabware(Lab.Trough_100ml, "BufferCub")
        mixes             = wt.getLabware(Lab.Eppendorfrack,    "mixes")


        self.go_first_pos()                                             #  Set the initial position of the tips ??

                                                                                  # Set volumen / sample
        dilutions = range(n)
        maxTips     = min  (self.nTips, n)
        maxMask     = Rbt.tipsMask[maxTips]

        buf_per_sample =0
        vf = 100                  # The final volume of every dilution, uL

        dil_mix1_100 = well_v / 10              # to be transfered from mix1_10 to mix1_100
        buf_mix1_100 = well_v - dil_mix1_100
        buf_per_sample += buf_mix1_100

        dil_mix1_10 = well_v /10                # to be distribute from original mix1 to mix1_10
        buf_mix1_10 = well_v - dil_mix1_10
        buf_per_sample += buf_mix1_10

        dil_mix2_10 = well_v / 10               # to be distribute from original mix2 to mix2_10
        buf_mix2_10 = well_v - dil_mix2_10
        buf_per_sample += buf_mix2_10



        # Define the reactives in each labware (Cuvette, eppys, etc.)

        buffer_reag = Rgt.Reagent("Buffer ",
                                  BufCuvette,
                                  volpersample = buf_per_sample,
                                  # defLiqClass  = 'MN VL',
                                  # num_of_samples= NumOfSamples
                                  )

        mix1 =Rgt.Reagent("mix1",
                          master_mixes_,
                          volpersample = dil_mix1_10,
                          # defLiqClass  = 'MN VL'
                          )

        mix2 = Rgt.Reagent("mix2",
                           master_mixes_,
                           volpersample  = dil_mix2_10,
                           # defLiqClass  = 'MN VL'
                           )

        # Show the check_list GUI to the user for possible small changes

        self.check_list()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        Plat1 = wt.getLabware(Lab.MP96MachereyNagel, "plate1")
        Plat2 = wt.getLabware(Lab.MP96well,          "plate2")

        # Define place for temporal reactions
        Rgt.Reagent.use_minimal_number_of_aliquots = False
        mix1_10 = Rgt.Reagent(f"mix1, diluted 1:10",
                        Plat1,
                        initial_vol = 0.0,
                        replicas    = NumOfSamples,
                        excess      = 0)

        mix2_10 = Rgt.Reagent(f"mix2, diluted 1:10",
                        Plat1,
                        initial_vol = 0.0,
                        replicas    = NumOfSamples,
                        excess      = 0)

        mix1_100 = Rgt.Reagent(f"mix1, diluted 1:100",
                              Plat2,
                              initial_vol=0.0,
                              replicas=NumOfSamples,
                              excess=0)

        mix2_100 = Rgt.Reagent(f"mix2, diluted 1:100",
                              Plat2,
                              initial_vol=0.0,
                              replicas=NumOfSamples,
                              excess=0)

        loc = Plat2.location               # just showing how to move the plate from one site to the next in the carrier
        loc.site -= 1
        car = Lab.Carrier(Lab.Carrier.Type("MP 3Pos", nSite=3), loc.grid, label = "MP 3Pos")
        loc.rack = car
        Itr.transfer_rack(Plat2, loc ).exec()                                              # just showing how RoMa works.

        with group("Fill plate with mixes "):

            Itr.userPrompt("Put the plates for Buffer ").exec()

            with self.tips(reuse=True, drop=False):
                self.distribute(reagent           = mix1,
                                to_labware_region = mix1_10.select_all())

            with self.tips(reuse=True, drop=False):
                self.distribute(reagent           = mix2,
                                to_labware_region = mix2_10.select_all())

            with self.tips(reuse=True, drop=False):
                self.distribute(reagent=buffer_reag, to_labware_region=mix1_10.select_all(), volume=buf_mix1_10)
                self.distribute(reagent=buffer_reag, to_labware_region=mix2_10.select_all(), volume=buf_mix2_10)

            with self.tips(reuse=True, drop=False):
                self.transfer(from_labware_region = mix1_10.select_all(),
                              to_labware_region   = mix1_100.select_all(),
                              volume              = dil_mix1_100)

            with self.tips(reuse=True, drop=False):
                self.transfer(from_labware_region = mix2_10.select_all(),
                              to_labware_region   = mix2_100.select_all(),
                              volume              = dil_mix2_100)

            with self.tips(reuse=True, drop=False):
                self.distribute(reagent=buffer_reag, to_labware_region=mix1_100.select_all(), volume=buf_mix1_100)
                self.distribute(reagent=buffer_reag, to_labware_region=mix2_100.select_all(), volume=buf_mix2_100)

            self.drop_tips()

        self.done()


if __name__ == "__main__":
    p = Tutorial_HL(NumOfSamples    = 4,
                                run_name        = "_4s_mix_1_2")

    p.use_version('No version')
    # p.go_first_pos('A01')
    p.Run()
