# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# protocols / __init__.py  : author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

"""
Maintain here a list of all available customer protocols
"""

available = []
available_classes = {}


def registreExecutable(executable):
    available.append(executable)
    available_classes[executable.name] = executable.__class__


from protocols.RNAextractionMN_Mag_Vet                import RNAextr_MN_Vet_Kit
from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
from protocols.Prefill_plates_LysisBuffer             import Prefill_plates_LysisBuffer
from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p  import PreKingFisher_RNAextNucleoMag_EtOH80p
from protocols.Prefill_plates_LysisBuffer_and_ProtKpreMix  import Prefill_plates_LysisBuffer_and_ProtKpreMix
#from protocols.PreKingFisher_RNAextNucleoMag          import PreKingFisher_RNAextNucleoMag
from EvoScriPy.protocol_steps                         import Pipeline


available.append(Prefill_plates_VEW1_ElutionBuffer_VEW2      ())
available.append(Prefill_plates_LysisBuffer                  ())
available.append(Prefill_plates_LysisBuffer_and_ProtKpreMix  ())
available.append(PreKingFisher_RNAextNucleoMag_EtOH80p       ())
available.append(RNAextr_MN_Vet_Kit                          ())
#available.append(PreKingFisher_RNAextNucleoMag          ())




pipeline_PreKingFisher = Pipeline ( protocols=  [Prefill_plates_VEW1_ElutionBuffer_VEW2 (run_name = "Prefill"),
                                                 PreKingFisher_RNAextNucleoMag_EtOH80p  (run_name = "Lysis"   ) ],
                                    run_name='PreKingFisher')

registreExecutable(pipeline_PreKingFisher)

from protocols.PCR import PCRexperiment
available.append(PCRexperiment())

available.append(Pipeline())






