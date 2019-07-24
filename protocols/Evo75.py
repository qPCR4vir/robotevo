# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *

class Evo75(Protocol):
    """ Using the Evo75
    """

    def __init__(self,
                 n_tips                       = 1,
                 NumOfSamples                = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips= n_tips,
                          NumOfSamples                = NumOfSamples,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)

    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi     = Lab.DiTi_0200ul                   # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware(Lab.CleanerShallow, "")
        WashWaste       = wt.get_labware(Lab.WasteWash, "")
        WashCleanerL    = wt.get_labware(Lab.CleanerDeep, "")
        DiTiWaste       = wt.get_labware(Lab.DiTi_Waste_plate, "TipWaste")

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste


class Evo75_FLI(Evo75):
    """ Using the Evo75_FLI_INNT
    """

    def __init__(   self,
                    NumOfSamples                = None,
                    GUI                         = None,
                    worktable_template_filename = '../EvoScripts/Freedom75_FLI_PCR.ewt',
                    output_filename             = None,
                    firstTip                    = None,
                    run_name                    = None):


        Evo100.__init__(self,
                        GUI                         = GUI,
                        nTips                       = 1,
                        NumOfSamples                = NumOfSamples,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

