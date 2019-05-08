# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'qPCR4vir'

from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2 as Prt

p = Prt (NumOfSamples    = 96,
         output_filename = '../current/tests/Prefill_plates_VEW1_ElutionBuffer_VEW2',
         run_name        = "_test_96s")
p.Run()

p = Prt (NumOfSamples    = 6,
         output_filename = '../current/tests/Prefill_plates_VEW1_ElutionBuffer_VEW2',
         run_name        = "_test_6s")
p.Run()


#from protocols.Prefill_plate_in_Evo200                import Prefill_plate_in_Evo200
#from protocols.RNAextractionMN_Mag_Vet                import RNAextr_MN_Vet_Kit
#from protocols.Prefill_plates_LysisBuffer             import Prefill_plates_LysisBuffer
#from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p  import PreKingFisher_RNAextNucleoMag_EtOH80p
#from protocols.Prefill_plates_LysisBuffer_and_ProtKpreMix  import Prefill_plates_LysisBuffer_and_ProtKpreMix
#from EvoScriPy.protocol_steps                         import Pipeline
#from protocols.PCR                                    import PCRexperiment

