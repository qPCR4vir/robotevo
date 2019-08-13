# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *
from protocols.Evo200 import Evo200


class Evo200_FLI (Evo200):
    """
    Using the Evo200_FLI
    """

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Evo200.__init__(self,
                        GUI                         = GUI,
                        n_tips                      = 8,
                        num_of_samples              = num_of_samples,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def set_paths(self):
        Evo200.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

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


