# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo200_FLI (Protocol):
    """
    Using the Evo200_FLI
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
                 first_tip                   = None,
                 run_name                    = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips                      = 8,
                          num_of_samples              = num_of_samples or Evo200_FLI.max_s,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          first_tip= first_tip,
                          run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

    def liquid_classes(self):
        if Evo200_FLI._liquid_classes is None:
            Evo200_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

            # the liquid classes are static members of this robot-specific protocol class
            # (only one copy shared for all objects of this class).
            # But just for convenience of typing we want protocol objects to have
            # a self. object member which reference that liquid class.

        all = Evo200_FLI._liquid_classes.all

        self.Water_free          = all["Water free"]     # General. No detect and no track small volumes < 50 µL

        self.SerumLiqClass      = all["Serum Disp postMix3"]  # or "MN Virus Sample"
        self.TissueHomLiqClass  = all["Serum Asp"]

        self.B_liquidClass      = all["Water free cuvette"]
        self.W_liquidClass      = self.Water_free
        self.Std_liquidClass    = self.Water_free
        self.Small_vol_disp     = all["Water wet"]

        return Evo200_FLI._liquid_classes

    def carrier_types(self):
        if Evo200_FLI._carrier_types is None:
            Evo200_FLI._carrier_types = labware.Carrier.Types(self.carrier_file)
            self.allow_labware("DiTi 3Pos", ['DiTi 1000ul',
                                             '96 Well Microplate',
                                             '96 Well DeepWell square'])
            self.allow_labware("MP 3Pos", ['DiTi 1000ul',
                                           '96 Well Microplate',
                                           '96 Well DeepWell square',
                                           "DiTi 200 ul"])
            self.allow_labware("AntiCOntaminationFlyway", "AntiCOntamination")
            self.allow_labware("Tube Eppendorf 16 Pos", "Sampletubes Eppendorfrack")
            self.allow_labware("Washstation 2Grid Trough DiTi", ['Washstation 2Grid Cleaner short',
                                                                 'Washstation 2Grid Cleaner long',
                                                                 'Washstation 2Grid Waste',
                                                                 'Washstation 2Grid DiTi Waste',
                                                                 'Trough 100ml'])
            self.allow_labware("Tube 16 mm 10 Pos", "Tube Falcon 15ml 12 Pos")
            self.allow_labware("Agowa MaxiSep 7200", "96 Well Separation Plate")
            self.allow_labware("Te-VacS", "96 Well Macherey-Nagel Plate")
            self.allow_labware("MP 3Pos Cooled", "FilterplateaufElutionplate flach")
            self.allow_labware("MP 3Pos Cooled", "96 Well 8er Macherey-Nagel flach")
            self.allow_labware("Trough 3Pos 25+100ml", "Trough 100ml")
            self.allow_labware("MP 3Pos Cooled", "96 Well Microplate")
            #self.allow_labware()

        return Evo200_FLI._carrier_types

    def set_defaults(self):
        wt = self.worktable

        # todo take from original robot evo200_f (here from evo100_f) !!!

        self.Water_free_d = self.get_liquid_class("Water free dispense")
        self.Water_wet = self.get_liquid_class("Water wet contact")

        self.Water_free = self.get_liquid_class("Water free")
        self.SerumLiqClass = self.get_liquid_class("Serum Disp postMix3")  # or "MN Virus Sample"
        self.TissueHomLiqClass = self.get_liquid_class("Serum Asp")

        self.B_liquidClass = self.get_liquid_class("Water free cuvette")
        self.W_liquidClass = self.Water_free  # or "AVR-Water free DITi 1000"
        self.Std_liquidClass = self.Water_free  # or "Water free dispense DiTi 1000"
        self.Small_vol_disp = self.get_liquid_class("Water wet")  # or "Water free Low Volume"  ??

        wt.def_DiTi_type       = labware.DiTi_1000ul                 # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware("Cleaner1", labware.CleanerSWS)
        WashWaste       = wt.get_labware("Waste", labware.WasteWS)
        WashCleanerL    = wt.get_labware("Cleaner2", labware.CleanerLWS)
        DiTiWaste       = wt.get_labware("DiTi Waste", labware.DiTi_Waste)

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste

        Reagent("Liquid waste", wt.def_WashWaste).include_in_check = False

