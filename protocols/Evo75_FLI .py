# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *



class Evo75_FLI(Protocol):
    """ Using the Evo75_FLI_INNT
    """

    def __init__(self,  GUI                 = None,
                        worktable_template_filename='../EvoScripts/Freedom75_FLI_PCR.ewt',
                        output_filename     = None,
                        run_name            = None):

        Protocol.__init__(self, GUI                         = GUI,
                                nTips                       = 1,
                                worktable_template_filename = worktable_template_filename,
                                output_filename             = output_filename,
                                run_name                    = run_name)


    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi     = Lab.DiTi_0200ul   # todo revise, this is a type, the others are labwares

        WashCleanerS    = wt.getLabware(Lab.CleanerShallow, ""                             )
        WashWaste       = wt.getLabware(Lab.WasteWash,   ""                                )
        WashCleanerL    = wt.getLabware(Lab.CleanerDeep, ""                                )
        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste_plate, "TipWaste"                   )

        # Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.WorkTable.Location(1,2))
        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste