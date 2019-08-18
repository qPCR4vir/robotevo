# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# just testing a new, generic Evo200

from protocols.evo200_f.evo200_f import *


class Prefill_plate_in_Evo200(Evo200_FLI):
    """
    Prefill one plate with Buffer.
    """

    name = "Prefill one plate with Buffer."
    min_s, max_s = 1, 96/6

    # for now just ignore the variants
    def def_versions(self):
        self.versions = {'No version': self.V_def               }

    def V_def(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 num_of_samples: int         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        this = Path(__file__).parent

        Evo200_FLI.__init__(self,
                            GUI                         = GUI,
                            num_of_samples=num_of_samples or Prefill_plate_in_Evo200.max_s,
                            worktable_template_filename = worktable_template_filename or
                                                          this / 'demo-two.mixes.Evo200example.ewt',
                            output_filename             = output_filename or this / 'scripts' / 'two.mixes',
                            firstTip                    = firstTip,
                            run_name                    = run_name)

    def Run(self):
        self.initialize()                                               # set_EvoMode and set_defaults() from Evo200

        self.check_initial_liquid_level = True
        self.show_runtime_check_list    = True

        num_of_samples = self.num_of_samples
        assert 1 <= num_of_samples <= 96/6 , "In this demo we want to set 6x num_of_samples in a 96 well plate."
        wt           = self.worktable

        self.comment('Prefill a plate with some dilutions of two master mix and Buffer Reagent for {:d} samples.'
                     .format(num_of_samples))

        BufCuvette    = wt.get_labware("BufferCub", labware.Trough_100ml)  # Get Labwares from the work table
        master_mixes_ = wt.get_labware("mixes", labware.Eppendorfrack)

        maxTips       = min(self.n_tips, num_of_samples)

        buf_per_sample =0
        well_v = 100

        dil_mix1_10 = well_v /10                     # to be distribute from original mix1 to mix1_10
        buf_mix1_10 = well_v - dil_mix1_10
        buf_per_sample += buf_mix1_10

        dil_mix2_10 = well_v / 10                    # to be distribute from original mix2 to mix2_10
        buf_mix2_10 = well_v - dil_mix2_10
        buf_per_sample += buf_mix2_10

        dil_mix1_100 = well_v / 10                   # to be transfered from mix1_10 to mix1_100
        buf_mix1_100 = well_v - dil_mix1_100
        buf_per_sample += buf_mix1_100

        dil_mix2_100 = well_v / 10                   # to be transfered from mix2_10 to mix2_100
        buf_mix2_100 = well_v - dil_mix2_100
        buf_per_sample += buf_mix2_100


        # Define the reactives in each labware (Cuvette, eppys, etc.)

        buffer_reag = Reagent("Buffer ",
                              BufCuvette,
                              volpersample = buf_per_sample,
                              # defLiqClass  = 'MN VL',
                              # num_of_samples= num_of_samples
                              )

        mix1 = Reagent("mix1",
                       master_mixes_,
                       volpersample = dil_mix1_10,
                       # defLiqClass  = 'MN VL'
                       )

        mix2 = Reagent("mix2",
                       master_mixes_,
                       volpersample  = dil_mix2_10,
                       # defLiqClass  = 'MN VL'
                       )

        # Show the check_list GUI to the user for possible small changes

        self.check_list()

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        plate_1 = wt.get_labware("plate1", labware.MP96MachereyNagel)
        plate_2 = wt.get_labware("plate2", labware.MP96well)

        # Define place for intermediate reactions
        Reagent.use_minimal_number_of_aliquots = False
        mix1_10 = Reagent(f"mix1, diluted 1:10",
                          plate_1,
                          initial_vol = 0.0,
                          replicas    = num_of_samples,
                          excess      = 0)

        mix2_10 = Reagent(f"mix2, diluted 1:10",
                          plate_1,
                          initial_vol = 0.0,
                          replicas    = num_of_samples,
                          excess      = 0)

        mix1_100 = Reagent(f"mix1, diluted 1:100",
                           plate_2,
                           initial_vol=0.0,
                           replicas=num_of_samples,
                           excess=0)

        mix2_100 = Reagent(f"mix2, diluted 1:100",
                           plate_2,
                           initial_vol=0.0,
                           replicas=num_of_samples,
                           excess=0)

        loc = plate_2.location               # just showing how to move the plate from one site to the next in the carrier
        loc.site -= 1
        carrier = labware.Carrier(self.get_carrier_type("MP 3Pos"), loc.grid, label ="MP 3Pos")
        loc.carrier = carrier
        instructions.transfer_rack(plate_2, loc).exec()                                            # just showing how RoMa works.

        with group("Fill plate with mixes "):

            instructions.userPrompt("Put the plates for Buffer ").exec()

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
    p = Prefill_plate_in_Evo200(num_of_samples= 4,
                                run_name        = "_4s_mix_1_2")

    # \EvoScripts\scripts\temp/VakuumExtraktion_RL_96_str.esc
    # \EvoScripts\scripts\temp/Ko_Platte_17_11_2011.esc

    p.use_version('No version')
    # p.go_first_pos('A01')
    p.Run()
