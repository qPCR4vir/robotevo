# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

from EvoScriPy.protocol_steps import *
import EvoScriPy.Reactive as Rtv


__author__ = 'Ariel'



class Evo200_generic (Protocol):
    """ Using the Evo200
    """
    min_s, max_s = 1, 96

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

        self.NumOfSamples = int(NumOfSamples)# if NumOfSamples is not None else  Evo200.max_s)
        Rtv.NumOfSamples  = self.NumOfSamples



    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi       = Lab.DiTi_1000ul   # todo revise, this is a type, the others are labwares

        WashCleanerS    = wt.getLabware(Lab.CleanerSWS, ""                                  )
        WashWaste       = wt.getLabware(Lab.WasteWS,    ""                                  )
        WashCleanerL    = wt.getLabware(Lab.CleanerLWS, ""                                  )
        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste, ""                                  )

        # Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.WorkTable.Location(1,2))
        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste



    def makePreMix( self, preMix, force_replies=False, NumSamples=None):

        Protocol.makePreMix(self, preMix,
                                  NumSamples    = NumSamples or self.NumOfSamples,
                                  force_replies = force_replies                    )