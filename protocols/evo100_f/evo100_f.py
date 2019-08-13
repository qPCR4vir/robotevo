# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *
from protocols.Evo100 import Evo100


class Evo100_FLI(Evo100):
    """
    Using the Evo100_FLI_INNT
    """
    min_s, max_s = 1, 48
    _liquid_classes = None

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Evo100.__init__(self,
                        GUI                         = GUI,
                        n_tips                      = 4,
                        num_of_samples              = num_of_samples or Evo100_FLI.max_s,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def set_paths(self):
        Evo100.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

    def set_defaults(self):
        self.Beads_LC_1         = self.liquid_classes().all["MixBeads_1"]
        self.Beads_LC_2         = self.liquid_classes().all["MixBeads_2"]
        self.Te_Mag_LC          = self.liquid_classes().all["Te-Mag"]         # "Water free" but uncentered
        self.Te_Mag_Centre      = self.liquid_classes().all["Te-Mag Centre"]  # To Centre after normal aspiration.
        self.Te_Mag_Rest        = self.liquid_classes().all["Te-Mag Rest"]
        self.Te_Mag_Force_Centre = self.liquid_classes().all["Te-Mag Force Centre"]
        self.Te_Mag_RestPlus    = self.liquid_classes().all["Te-Mag RestPlus"]
        self.Water_free         = self.liquid_classes().all["Water free"]  # General. No detect and no track small volumes < 50 µL

        # self.SerumLiqClass      = self.liquid_classes().all["Serum Asp preMix3"]  # or "MN Virus Sample"
        self.TissueHomLiqClass  = self.liquid_classes().all["Serum Asp"]

        self.B_liquidClass      = self.liquid_classes().all["Water free cuvette"]
        self.W_liquidClass      = self.Water_free                           # or "AVR-Water free DITi 1000"
        self.Std_liquidClass    = self.Water_free                           # or "Water free dispense DiTi 1000"
        self.Small_vol_disp     = self.liquid_classes().all["Water wet"]    # or "Water free Low Volume"  ??

        wt = self.worktable

        wt.def_DiTi_type       = labware.DiTi_1000ul                 # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware("", labware.CleanerSWS)
        WashWaste       = wt.get_labware("", labware.WasteWS)
        WashCleanerL    = wt.get_labware("", labware.CleanerLWS)
        DiTiWaste       = wt.get_labware("", labware.DiTi_Waste)

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste

        Reagent("Liquid waste", wt.def_WashWaste).include_in_check = False

    def liquid_classes(self):
        if Evo100_FLI._liquid_classes is None:
            Evo100_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

        return Evo100_FLI._liquid_classes


