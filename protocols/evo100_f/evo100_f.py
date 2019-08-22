# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo100_FLI(Protocol):
    """
    Using the Evo100_FLI_INNT
    """
    min_s, max_s = 1, 48
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
                          n_tips                      = 4,
                          num_of_samples              = num_of_samples or Evo100_FLI.max_s,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

    def liquid_classes(self):
        if Evo100_FLI._liquid_classes is None:
            Evo100_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

            # the liquid classes are static members of this robot-specific protocol class
            # (only one copy shared for all objects of this class).
            # But just for convenience of typing we want protocol objects to have
            # a self. object member which reference that liquid class.

        all = Evo100_FLI._liquid_classes.all

        self.Beads_LC_1          = all["MixBeads_1"]
        self.Beads_LC_2          = all["MixBeads_2"]
        self.Te_Mag_LC           = all["Te-Mag"]         # "Water free" but uncentered
        self.Te_Mag_Centre       = all["Te-Mag Centre"]  # To Centre after normal aspiration.
        self.Te_Mag_Rest         = all["Te-Mag Rest"]
        self.Te_Mag_Force_Centre = all["Te-Mag Force Centre"]
        self.Te_Mag_RestPlus     = all["Te-Mag RestPlus"]
        self.Water_free          = all["Water free"]     # General. No detect and no track small volumes < 50 µL

        self.SerumLiqClass      = all["Serum Disp postMix3"]  # or "MN Virus Sample"
        self.TissueHomLiqClass  = all["Serum Asp"]

        self.B_liquidClass      = all["Water free cuvette"]
        self.W_liquidClass      = self.Water_free                           # or "AVR-Water free DITi 1000"
        self.Std_liquidClass    = self.Water_free                           # or "Water free dispense DiTi 1000"
        self.Small_vol_disp     = all["Water wet"]        # or "Water free Low Volume"  ??

        return Evo100_FLI._liquid_classes

    def carrier_types(self):
        if Evo100_FLI._carrier_types is None:
            Evo100_FLI._carrier_types = labware.Carrier.Types(self.carrier_file)

            self.allow_labware("DiTi 3Pos", ['DiTi 1000ul',
                                             '96 Well Microplate',
                                             '96 Well DeepWell square'], widht_in_grids = 6)
            self.allow_labware("MP 3Pos", ['DiTi 1000ul',
                                           '96 Well Microplate',
                                           '96 Well DeepWell square'], widht_in_grids = 6)

            self.allow_labware("Trough 3Pos 25+100ml", 'Trough 100ml', widht_in_grids = 1)
            self.allow_labware("Washstation 2Grid Trough DiTi", ['Washstation 2Grid Cleaner short',
                                                                 'Washstation 2Grid Cleaner long',
                                                                 'Washstation 2Grid Waste',
                                                                 'Washstation 2Grid DiTi Waste',
                                                                 'Trough 100ml'], widht_in_grids = 2)
            self.allow_labware("Tube Eppendorf 16 Sites", ['Tube Greinerconic 2mL 16 Pos',
                                                           'Tube Eppendorf 1 Pos',
                                                           'Tube Eppendorf 2mL 1 Pos',
                                                           'Tube Greiner conic 2mL 1 Pos',
                                                           'Tube Eppendorf 2mL 16 Pos'], widht_in_grids = 1)
            self.allow_labware("Tube Eppendorf 3x16=48 Pos", ['Tube Eppendorf 3x 16 PosR',
                                                              'Tube Eppendorf 3x 16 Pos'], widht_in_grids = 3)
            self.allow_labware("Tube Eppendorf 6x16=96 Pos", ['Tube Eppendorf 6x 16 Pos'], widht_in_grids = 6)
            self.allow_labware("Te-MagS portrait", 'Tube Eppendorf 48 Pos', widht_in_grids = 6)  # ?

        return Evo100_FLI._carrier_types

    def set_defaults(self):

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

