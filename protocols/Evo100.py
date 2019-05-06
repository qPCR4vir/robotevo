# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'

from EvoScriPy.protocol_steps import *
import EvoScriPy.Reagent as Rtv


class Evo100(Protocol):
    """ Using the Evo100
    """

    def __init__(self,
                     GUI                            = None,
                     worktable_template_filename    = None,
                     output_filename                = None,
                     run_name                       = None):


        Protocol.__init__(self, GUI                         = GUI,
                                nTips                       = 4,
                                worktable_template_filename = worktable_template_filename,
                                output_filename             = output_filename,
                                run_name                    = run_name)


    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi       = Lab.DiTi_1000ul   # todo revise, this is a type, the others are labwares

        WashCleanerS    = wt.getLabware(Lab.CleanerSWS, ""                                  )
        WashWaste       = wt.getLabware(Lab.WasteWS,    ""                                  )
        WashCleanerL    = wt.getLabware(Lab.CleanerLWS, ""                                  )
        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste, ""                                  )

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste


class Evo100_FLI(Evo100):
    """ Using the Evo100_FLI_INNT
    """
    min_s, max_s = 1, 48

    def __init__(self,
                     GUI                            = None,
                     NumOfSamples                   = max_s,
                     worktable_template_filename    = None,
                     output_filename                = None,
                     run_name                       = None):


        Protocol.__init__(self, GUI                         = GUI,
                                nTips                       = 4,
                                worktable_template_filename = worktable_template_filename,
                                output_filename             = output_filename,
                                run_name                    = run_name)

        self.NumOfSamples = int(NumOfSamples)  # if NumOfSamples is not None else  Evo100_FLI.max_s)
        Rtv.NumOfSamples = self.NumOfSamples

    def set_defaults(self):
        Evo100.set_defaults(self)

    def makePreMix( self, preMix, force_replies=False, NumSamples=None):
        Protocol.makePreMix(self, preMix, NumSamples=NumSamples or self.NumOfSamples, force_replies=force_replies)
