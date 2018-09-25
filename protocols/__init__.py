# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# protocols / __init__.py  : author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

"""
Maintain here a list of all available customer protocols
"""

available = []


def registreExecutable(executable_class, parameters):
    available.append((executable_class, parameters))


import protocols.RNAextractionMN_Mag
import protocols.PreKingFisher_RNAextNucleoMag




from EvoScriPy.protocol_steps import Pipeline
from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p  import PreKingFisher_RNAextNucleoMag_EtOH80p

pipeline_PreKingFisher = Pipeline.Parameter(protocols=
                             [[Prefill_plates_VEW1_ElutionBuffer_VEW2.name,                   "Prefill"],
                              [PreKingFisher_RNAextNucleoMag_EtOH80p.name,                      "Lysis"]] )
pipeline_PreKingFisher.run_name = 'PreKingFisher'
registreExecutable(Pipeline, pipeline_PreKingFisher)

from protocols.PCRexperiment import PCRexperiment


available.append(Pipeline)


"""
# todo replace this temporal test
from EvoScriPy.protocol_steps import not_implemented


class PipelineTest (Pipeline):
    name = "Pipeline Test"
    versions = {'VEr1' : not_implemented,
                'VEr2' : not_implemented,
                'V3'   : not_implemented,
                '4'    : not_implemented}

    class Parameter(Pipeline.Parameter):
        # parameters to describe a run of this program

        def __init__(self, GUI=None):
            Pipeline.Parameter.__init__(self, GUI,
                [[Prefill_plates_VEW1_ElutionBuffer_VEW2.Prefill_plates_VEW1_ElutionBuffer_VEW2.name, "Prefill"],
                 [PreKingFisher_RNAextNucleoMag_EtOH80p.PreKingFisher_RNAextNucleoMag_EtOH80p.name,   "Lysis"  ]]  )

#available.append(PipelineTest)


"""






