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
    _liquid_classes = None

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                        GUI                         = GUI,
                        n_tips                      = 8,
                        num_of_samples              = num_of_samples,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

    def liquid_classes(self):
        return None

        if Evo200_FLI._liquid_classes is None:
            Evo200_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

        return Evo200_FLI._liquid_classes

    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi_type       = labware.DiTi_1000ul                 # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware("Cleaner1", labware.CleanerSWS)
        WashWaste       = wt.get_labware("Waste", labware.WasteWS)
        WashCleanerL    = wt.get_labware("Cleaner2", labware.CleanerLWS)
        DiTiWaste       = wt.get_labware("DiTi Waste", labware.DiTi_Waste)

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste

        Reagent("Liquid waste", wt.def_WashWaste).include_in_check = False

