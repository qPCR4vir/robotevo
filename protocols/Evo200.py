# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *
import EvoScriPy.Reagent as Rtv



class Evo200 (Protocol):
    """ Using the Evo200
    """
    min_s, max_s = 1, 96   # ??

    def __init__(self,
                     GUI                            = None,
                     NumOfSamples                   = max_s,
                     worktable_template_filename    = None,
                     output_filename                = None,
                     run_name                       = None):


        Protocol.__init__(self, GUI                         = GUI,
                                nTips                       = 8,
                                worktable_template_filename = worktable_template_filename,
                                output_filename             = output_filename,
                                run_name                    = run_name)

        self.NumOfSamples = int(NumOfSamples)         # if NumOfSamples is not None else  Evo200.max_s)
        Rtv.NumOfSamples  = self.NumOfSamples         # ?



    def set_defaults(self):
        wt = self.worktable

        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste, ""                                  )

        wt.def_DiTi        = Lab.DiTi_1000ul   # todo revise, this is a type, the others are labwares
        wt.def_DiTiWaste   = DiTiWaste

        """
        WashCleanerS    = wt.getLabware(Lab.CleanerSWS, ""                                  )
        WashWaste       = wt.getLabware(Lab.WasteWS,    ""                                  )
        WashCleanerL    = wt.getLabware(Lab.CleanerLWS, ""                                  )

        # Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.WorkTable.Location(1,2))
        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        """


    def makePreMix( self, preMix, force_replies=False, NumSamples=None):

        Protocol.makePreMix(self, preMix,
                                  NumSamples    = NumSamples or self.NumOfSamples,
                                  force_replies = force_replies                    )