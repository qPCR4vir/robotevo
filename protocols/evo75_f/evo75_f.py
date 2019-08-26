# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo75_FLI(Protocol):
    """
    Using the Evo75_FLI_INNT
    """
    min_s, max_s = 1, 96
    _liquid_classes = None
    _carrier_types = None
    _labware_types = None

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips                      = 1,
                          num_of_samples              = num_of_samples,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = Path(__file__).parent / 'Carrier.cfg'


def liquid_classes(self):
    if Evo75_FLI._liquid_classes is None:
        Evo75_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

            # the liquid classes are static members of this robot-specific protocol class
            # (only one copy shared for all objects of this class).
            # But just for convenience of typing we want protocol objects to have
            # a self. object member which reference that liquid class.

        all = Evo75_FLI._liquid_classes.all

        self.Water_free_d     = all["Water free dispense"]
        self.Water_wet        = all["Water wet contact"]
        self.Water_free       = all["Water free"]     # General. No detect and no track small volumes < 50 µL

        self.SerumLiqClass    = all["Serum free dispense"]

        self.B_liquidClass    = self.Water_free_d
        self.W_liquidClass    = self.Water_free
        self.Std_liquidClass  = self.Water_free
        self.Small_vol_disp   = all["Water wet"]

    return Evo75_FLI._liquid_classes


def carrier_types(self):
    if Evo75_FLI._carrier_types is None:
        Evo75_FLI._carrier_types = labware.Carrier.Types(self.carrier_file)

        # self.allow_labware()

    return Evo75_FLI._carrier_types


def set_defaults(self):
    wt = self.worktable

    # todo take from original robot evo75_f (here from evo100_f) !!!

    wt.def_DiTi_type = labware.DiTi_200ul  # this is a type, the others are labwares

    WashCleanerS = wt.get_labware("", labware.CleanerSWS)
    WashWaste    = wt.get_labware("", labware.WasteWS)
    WashCleanerL = wt.get_labware("", labware.CleanerLWS)
    DiTiWaste    = wt.get_labware("", labware.DiTi_Waste)

    wt.def_WashWaste   = WashWaste
    wt.def_WashCleaner = WashCleanerS
    wt.def_DiTiWaste   = DiTiWaste

    Reagent("Liquid waste", wt.def_WashWaste).include_in_check = False

