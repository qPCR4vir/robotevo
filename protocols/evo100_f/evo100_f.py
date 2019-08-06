# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from protocols.Evo100 import Evo100
import EvoScriPy.reagent as Rgt


class Evo100_FLI(Evo100):
    """
    Using the Evo100_FLI_INNT
    """
    min_s, max_s = 1, 48

    def __init__(self,
                 num_of_samples                = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):


        Evo100.__init__(self,
                        GUI                         = GUI,
                        n_tips= 4,
                        num_of_samples=num_of_samples or Evo100_FLI.max_s,
                        worktable_template_filename = worktable_template_filename,
                        output_filename             = output_filename,
                        firstTip                    = firstTip,
                        run_name                    = run_name)

        # self.carrier_file = 'Carrier.cfg'