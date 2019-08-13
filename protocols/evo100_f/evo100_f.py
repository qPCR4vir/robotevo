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


Beads_LC_1      = "MixBeads_1"
Beads_LC_2      = "MixBeads_2"
Te_Mag_LC       = "Te-Mag"          # "Water free" but uncentered
Te_Mag_Centre   = "Te-Mag Centre"   # To Centre after normal aspiration.
Te_Mag_Rest     = "Te-Mag Rest"
Te_Mag_Force_Centre   = "Te-Mag Force Centre"
Te_Mag_RestPlus = "Te-Mag RestPlus"
