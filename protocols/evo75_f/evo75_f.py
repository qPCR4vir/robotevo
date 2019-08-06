# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from protocols.Evo75 import Evo75


class Evo75_FLI(Evo75):
    """
    Using the Evo75_FLI_INNT
    """

    def __init__(self,
                 num_of_samples                = None,
                 GUI                         = None,
                 worktable_template_filename = '../EvoScripts/Freedom75_FLI_PCR.ewt',
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):


        Evo100.__init__(self,
                        GUI                         = GUI,
                        nTips                       = 1,
                        num_of_samples= num_of_samples,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

        self.carrier_file = 'Carrier.cfg'
