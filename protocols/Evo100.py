# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'

from EvoScriPy.protocol_steps import *
import EvoScriPy.reagent as Rgt


class Evo100(Protocol):
    """ Using the Evo100
    """

    def __init__(self,
                 n_tips                       = 4,
                 num_of_samples                = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips= n_tips,
                          num_of_samples= num_of_samples,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)


class Evo100_FLI(Evo100):
    """ Using the Evo100_FLI_INNT
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
