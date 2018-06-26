# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

from EvoScriPy.protocol_steps import *
import EvoScriPy.Reactive as Rtv


__author__ = 'Ariel'



class Evo75_FLI(Protocol):
    """ Using the Evo75_FLI_INNT
    """

    class Parameter (Protocol.Parameter):

        def __init__(self,
                     GUI                            = None,
                     # NumOfSamples                   = 48,
                     worktable_template_filename    = """C:\Prog\robotevo\EvoScripts\wt_templates\Freedom75_FLI_PCR.ewt""",
                     output_filename                = None):

            # self.NumOfSamples = NumOfSamples

            Protocol.Parameter.__init__(self, GUI=GUI,
                                        worktable_template_filename = worktable_template_filename,
                                        output_filename= output_filename
                                        )


    def __init__(self, parameters ):

        # self.NumOfSamples = parameters.NumOfSamples
        # Rtv.NumOfSamples = self.NumOfSamples

        Protocol.__init__(self,
                          1,
                          parameters)

    def set_defaults(self):
        wt = self.worktable

        # todo decide where to put the default labware: in robot or worktable object or the global Lab

        WashCleanerS    = wt.getLabware(Lab.CleanerSWS,""                                  )
        WashWaste       = wt.getLabware(Lab.WasteWS,   ""                                  )
        WashCleanerL    = wt.getLabware(Lab.CleanerLWS,""                                  )
        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste,""                                  )

        # Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.WorkTable.Location(1,2))
        Lab.def_WashWaste   = WashWaste
        Lab.def_WashCleaner = WashCleanerS
        Lab.def_DiTiWaste   = DiTiWaste
        Lab.def_DiTi        = Lab.DiTi_1000ul   # todo revise



