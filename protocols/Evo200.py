# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo200 (Protocol):
    """Using the Evo200"""

    def __init__(self,
                 n_tips                         = 8,
                 num_of_samples                 = None,
                 GUI                            = None,
                 worktable_template_filename    = None,
                 output_filename                = None,
                 firstTip                       = None,
                 run_name                       = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips                      = n_tips,
                          num_of_samples              = num_of_samples,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)

    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi     = lab.DiTi_1000ul  # DiTi_0200ul  # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware(lab.CleanerSWS, "Cleaner1")
        WashWaste       = wt.get_labware(lab.WasteWS,    "Waste")
        WashCleanerL    = wt.get_labware(lab.CleanerLWS, "Cleaner2")
        DiTiWaste       = wt.get_labware(lab.DiTi_Waste, "DiTi Waste")

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste
