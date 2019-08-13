# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo75_FLI(Protocol):
    """
    Using the Evo75_FLI_INNT
    """

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                       GUI                         = GUI,
                       n_tips                      = 1,
                       num_of_samples              = num_of_samples,
                       worktable_template_filename = worktable_template_filename,
                       output_filename             = output_filename,
                       firstTip                    = firstTip,
                       run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = Path(__file__).parent / 'Carrier.cfg'
