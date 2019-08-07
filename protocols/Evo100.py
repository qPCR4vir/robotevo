# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'

from pathlib import Path
from EvoScriPy.protocol_steps import *


class Evo100(Protocol):
    """
    Using the Evo100
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

        self.carrier_file = Path(__file__).parent / 'evo100_f' / 'Carrier.cfg'
