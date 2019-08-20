# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'qPCR4vir'

from pathlib import Path
test_dir = Path(__file__).parent / 'tests'

from protocols.hello_world.hello_world import HelloWorld as Prt

p = Prt(output_filename=test_dir / 'hello_world')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2 as Prt

p = Prt (num_of_samples    = 96,
         output_filename = test_dir / 'Prefill_plates_VEW1_ElutionBuffer_VEW2',
         run_name        = "_test_96s")
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'Prefill_plates_VEW1_ElutionBuffer_VEW2',
         run_name        = "_test_6s")
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p.PreKingFisher_RNAextNucleoMag_EtOH80p import PreKingFisher_RNAextNucleoMag_EtOH80p as Prt

p = Prt (num_of_samples    = 96,
         output_filename = test_dir / 'PreKingFisher_RNAextNucleoMag_EtOH80p',
         run_name        = "_test_96s_VL-pKmix prefill")
p.use_version('VL-pKmix prefill')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'PreKingFisher_RNAextNucleoMag_EtOH80p',
         run_name        = "_test_6s_VL-pKmix prefill")
p.use_version('VL-pKmix prefill')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.RNAextractionMN_Mag_Vet.RNAextractionMN_Mag_Vet import RNAextr_MN_Vet_Kit as Prt

p = Prt (num_of_samples    = 48,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_48s_VL-only prefill")
p.use_version('VL-only prefill')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_6s_VL-only prefill")
p.use_version('VL-only prefill')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 48,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_48s_VL-pKmix prefill")
p.use_version('VL-pKmix prefill')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_6s_VL-pKmix prefill")
p.use_version('VL-pKmix prefill')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 48,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_48s_VL-only inactivated")
p.use_version('VL-only inactivated')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_6s_VL-only inactivated")
p.use_version('VL-only inactivated')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 48,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_48s_VL-pKmix Inactivated")
p.use_version('VL-pKmix Inactivated')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_6s_VL-pKmix Inactivated")
p.use_version('VL-pKmix Inactivated')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 48,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_48s_original samples")
p.use_version('original samples')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples    = 6,
         output_filename = test_dir / 'RNAext_MNVet_TeMag',
         run_name        = "_test_6s_original samples")
p.use_version('original samples')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.Prefill_plate_in_Evo200.Prefill_plate_in_Evo200 import Prefill_plate_in_Evo200 as Prt

p = Prt(num_of_samples  = 4,
        output_filename = test_dir / 'demo-two.mixes',
        run_name        = "_test_4s_mix_1_2")
p.use_version('No version')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.tutorial_HL.tutorial_HL import Tutorial_HL as Prt

p = Prt (num_of_samples              = 6,
         output_filename             = test_dir / 'Tutorial_HLevel',
         run_name                    = "_6s")
p.use_version('No version')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples              = 46,
         output_filename             = test_dir / 'Tutorial_HLevel',
         run_name                    = "_46s")
p.use_version('No version')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.tutorial_LL.tutorial_LL import Tutorial_LL as Prt

p = Prt (num_of_samples              = 6,
         output_filename             = test_dir / 'Tutorial_LLevel_atomic',
         run_name                    = "_6s")
p.use_version('No version')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (num_of_samples              = 46,
         output_filename             = test_dir / 'Tutorial_LLevel_atomic',
         run_name                    = "_46s")
p.use_version('No version')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()


from protocols.Prefill_plates_LysisBuffer.Prefill_plates_LysisBuffer import Prefill_plates_LysisBuffer as Prt

p = Prt(run_name="_1_plate")
p.use_version('1 plate')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

p = Prt (run_name="_3_plate")
p.use_version('3 plate')
p.set_first_tip('A01')
print("\n\n************ " + str(p.output_filename) + " **************\n")
p.Run()

#from protocols.Prefill_plates_LysisBuffer_and_ProtKpreMix  import Prefill_plates_LysisBuffer_and_ProtKpreMix
