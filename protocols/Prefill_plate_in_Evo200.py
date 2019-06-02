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
import EvoScriPy.Reagent        as     Rtv

from protocols.Evo200 import Evo200


class Prefill_plate_in_Evo200(Evo200):
    """
    Prefill one plate with Buffer.
    """

    name = "Prefill one plate with Buffer."
    min_s, max_s = 1, 96

    # for now just ignore the variants
    def def_versions(self):
        self.versions = { # '3 plate': self.V_3_plate,
                          # '2 plate': self.V_2_plate,
                         '1 plate': self.V_1_plate                         }

    def V_1_plate(self):
        self.num_plates = 1

    def V_2_plate(self):
        self.num_plates = 2

    def V_3_plate(self):
        self.num_plates = 3

    def __init__(self,
                 GUI                         = None,
                 NumOfSamples: int           = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        Evo200.__init__(self,
                        GUI                         = GUI,
                        NumOfSamples                = NumOfSamples or Prefill_plate_in_Evo200.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      '../EvoScripts/wt_templates/Evo200example.ewt',
                        output_filename             = output_filename or '../current/pp200n',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()    # if needed calls Executable.initialize() and set_EvoMode
                             # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.check_initial_liquid_level = True

        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill {:d} plates with Buffer Reagent for {:d} samples.'\
                       .format(self.num_plates,
                               NumOfSamples     )).exec()

                                                            # Get Labwares (Cuvette, eppys, etc.) from the work table
        BufCuvette = wt.getLabware(Lab.Trough_100ml, "RA4")

        self.go_first_pos()                                                     #  Set the initial position of the tips

                                                                                  # Set volumen / sample
        BufferVolume   = 100.0       # VL1 or VL

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

                                                        # Define the reactives in each labware (Cuvette, eppys, etc.)

        buffer_reag = Rtv.Reagent("Buffer ",
                                  BufCuvette,
                                  volpersample = BufferVolume,
                                  #defLiqClass  = 'MN VL',
                                  num_of_samples= self.num_plates * NumOfSamples)

        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        Plat = wt.getLabware(Lab.MP96MachereyNagel, "Filterplatte")

        assert isinstance(Plat, Lab.Labware)



        # Define place for temporal reactions
        for s in all_samples:
            Rtv.Reagent(f"lysis_{s + 1:02d}",
                        Plat,
                        initial_vol =0.0,
                        pos         =s + 1,
                        excess      =0)

        loc = Plat.location               # just showing how to move the plate from one site to the next in the carrier
        loc.site += 1
        car = Lab.Carrier(Lab.Carrier.Type("MP 3Pos", nSite=3), loc.grid, label = "MP 3Pos")
        loc.rack = car
        Itr.transfer_rack(Plat, loc ).exec()                                              # just showing how RoMa works.

        with group("Prefill plates with Buffer "):

            Itr.userPrompt("Put the plates for Buffer ").exec()

            with self.tips(reuse=True, drop=False):
                self.spread(reagent=buffer_reag, to_labware_region=Plat.selectOnly(all_samples))
            self.dropTips()

        self.done()


if __name__ == "__main__":
    p = Prefill_plate_in_Evo200(NumOfSamples    = 96,
                                run_name        = "_96s_1 plate")

    # \EvoScripts\scripts\temp/VakuumExtraktion_RL_96_str.esc
    # \EvoScripts\scripts\temp/Ko_Platte_17_11_2011.esc

    p.use_version('1 plate')
    # p.go_first_pos('A01')
    p.Run()
