# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# protocols / __init__.py  : author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

"""
Maintain here a list of all available customer protocols
"""

available = []


def registreExecutable(executable):
    available.append(executable)


import protocols.RNAextractionMN_Mag
import protocols.PreKingFisher_RNAextNucleoMag




from EvoScriPy.protocol_steps                         import Pipeline
from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p  import PreKingFisher_RNAextNucleoMag_EtOH80p


pipeline_PreKingFisher = Pipeline ( protocols=  [Prefill_plates_VEW1_ElutionBuffer_VEW2 (run_name = "Prefill"),
                                                 PreKingFisher_RNAextNucleoMag_EtOH80p  (run_name = "Lysis"   ) ],
                                    run_name='PreKingFisher')

registreExecutable(pipeline_PreKingFisher)

from protocols.PCRexperiment import PCRexperiment


available.append(Pipeline())








