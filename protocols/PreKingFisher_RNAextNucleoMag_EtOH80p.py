# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100 import Evo100_FLI
import EvoScriPy.Reagent as Rgt


class PreKingFisher_RNAextNucleoMag_EtOH80p(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "PreKingFisher for RNA extraction modified NucleoMag MN_Vet kit and EtOH80p Plate preFill"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'VL-pKmix prefill'     : self.V_fill_preMix_inactivation,
                         'VL-only prefill'      : self.V_fill_inactivation,
                         'VL-only inactivated'  : self.V_VL_inactivated,
                         'VL-pKmix Inactivated' : self.V_preMix_inactivated,
                         'original samples'     : self.V_original_samples           }

    def V_default(self):
        self.add_samples    = True
        self.add_preMix     = True
        self.add_VL         = True
        self.do_extraction  = True

    def V_original_samples(self):
        self.V_default()

    def V_VL_inactivated(self):
        self.V_default()
        self.add_VL         = False
        self.add_samples    = False

    def V_preMix_inactivated(self):
        self.V_VL_inactivated()
        self.add_preMix     = False

    def V_fill_preMix_inactivation(self):
        self.V_default()
        self.add_samples    = False
        self.do_extraction  = False

    def V_fill_inactivation(self):
        self.V_fill_preMix_inactivation()
        self.add_preMix     = False


    def __init__(self,
                 GUI                            = None,
                 num_of_samples       : int       = None,
                 worktable_template_filename    = None,
                 output_filename                = None,
                 firstTip                       = None,
                 run_name           : str       = ""):

        self.V_default()

        Evo100_FLI.__init__(self,
                            GUI                     = GUI,
                            num_of_samples=num_of_samples or PreKingFisher_RNAextNucleoMag_EtOH80p.max_s,
                            worktable_template_filename
                                                    = worktable_template_filename or
                                                      '../EvoScripts/wt_templates/PreKingFisher_RNAextNucleoMag_EtOH80p.ewt',
                            output_filename         = output_filename or
                                                      '../current/PreKingFisher_RNAextNucleoMag_EtOH80p',
                            firstTip                = firstTip,
                            run_name                = run_name)

    def Run(self):
        self.initialize()                       # set_defaults ??

        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment((self.version + 'for extracting RNA from {:s} samples with the MN-Vet kit')
                                             .format(str(NumOfSamples))).exec()

                                                        # Get Labwares (Cuvette, eppys, etc.) from the work table

        if self.add_VL:
            LysBuf      = wt.get_labware(Lab.Trough_100ml, "2-Vl Lysis Buffer")

        if self.do_extraction:
            BindBuf     = wt.get_labware(Lab.Trough_100ml, "3-VEB Binding Buffer")

        DiTi1000_1  = wt.get_labware(Lab.DiTi_1000ul, "1000-1")
        DiTi1000_2  = wt.get_labware(Lab.DiTi_1000ul, "1000-2")
        DiTi1000_3  = wt.get_labware(Lab.DiTi_1000ul, "1000-3")

        Reagents   = wt.get_labware(Lab.GreinRack16_2mL, "Reactives")

                                                                # Set the initial position of the tips

        self.go_first_pos()

                                                                # Set volumen / sample

        SampleVolume        = 100.0
        LysisBufferVolume   = 100.0                 # VL
        # IC2Volume         =   5.0                 # IC2 ? 4
        IC_MS2Volume        =  10.0                 # MS2
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        BindingBufferVolume = 350.0                 # VEB
        B_BeadsVolume       =  20.0                 # B-Beads
        EtOH80pVolume       = 600.0

        InitLysisVol        =   0.0
        if self.do_extraction:
            if not self.add_samples:    InitLysisVol += SampleVolume
            if not self.add_preMix:     InitLysisVol += ProtKVolume + cRNAVolume + IC_MS2Volume
            if not self.add_VL:         InitLysisVol += LysisBufferVolume

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass = "Serum Asp"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.n_tips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]

                                                        # Define the reactives in each labware (Cuvette, eppys, etc.)

        if self.add_preMix:                             # we need to add ProtK+cRNA+MS2 mix
            ProtK       = Rgt.Reagent("Proteinase K ",
                                      Reagents,
                                      replicas     = 2,
                                      minimize_aliquots=False,
                                      wells= [15, 16],
                                      volpersample = ProtKVolume,
                                      defLiqClass  = Small_vol_disp)

            cRNA        = Rgt.Reagent("Carrier RNA ",
                                      Reagents,
                                      wells= 14,
                                      volpersample  = cRNAVolume,
                                      defLiqClass   = Small_vol_disp)

            IC_MS2      = Rgt.Reagent("IC MS2 phage culture ",
                                      Reagents,
                                      wells= 13,
                                      volpersample  = IC_MS2Volume,
                                      defLiqClass   = Small_vol_disp)

            # IC2         = Rgt.Reagent("IC2 - synthetic RNA " ,  Reagents, pos=13,
            #                           volpersample=  IC2Volume ,defLiqClass=W_liquidClass)

            pK_cRNA_MS2 = Rgt.preMix  ("ProtK+cRNA+IC-MS2 mix "  ,
                                       Reagents,
                                       pos          = 8,
                                       components   = [cRNA, ProtK, IC_MS2] ,
                                       defLiqClass  = W_liquidClass,
                                       excess       = 20)

        if self.add_VL:
            LysisBuffer = Rgt.Reagent("VL - Lysis Buffer ",
                                      LysBuf,
                                      volpersample  = LysisBufferVolume,
                                      defLiqClass   = 'MN VL')

        if self.do_extraction:
            B_Beads         = Rgt.Reagent("B - Beads ",
                                          Reagents,
                                          wells= [1, 2],
                                          initial_vol  = 1200,
                                          volpersample = B_BeadsVolume,
                                          defLiqClass  = Beads_LC_2,
                                          maxFull      = 70)

            BindingBuffer   = Rgt.Reagent("VEB - Binding Buffer ",
                                          BindBuf,
                                          volpersample  = BindingBufferVolume,
                                          defLiqClass   = B_liquidClass)

        EtOH80p         = Rgt.Reagent("Ethanol 80% ",
                                      wt.get_labware(Lab.Trough_100ml, "7-EtOH80p"),
                                      volpersample      =EtOH80pVolume,
                                      defLiqClass       =B_liquidClass)

                                                        # Show the check_list GUI to the user for possible small changes
        self.check_list()
        self.set_EvoMode()

                                                        # Define the Reagents not shown in the check_list GUI
                                                        # Define samples and the place for temporal reactions

        Plate_lysis = wt.get_labware(Lab.MP96deepwell, "Plate lysis")  # Plate 12 x 8 ?
        Plate_EtOH  = wt.get_labware(Lab.MP96deepwell, "Plate EtOH")  # Plate 12 x 8 ? MP96well !!

        if self.version != 'original samples':
           Samples  = wt.get_labware(Lab.EppRack6x16, "Proben")  # 6x16 = 12 x 8 ?


        par = Plate_lysis.parallelOrder(self.n_tips, all_samples)

        for s in all_samples:

            Rgt.Reagent("lysis_{:02d}".format(s + 1),
                        Plate_lysis,
                        initial_vol = InitLysisVol,
                        wells=par[s] + 1,
                        excess      = 0)

            Rgt.Reagent("EtOH80p_{:02d}".format(s + 1),
                        Plate_EtOH,
                        initial_vol = 0.0,
                        wells=par[s] + 1,  # todo revise order !!!
                        excess      = 0)

            if self.add_samples:
                Rgt.Reagent("probe_{:02d}".format(s + 1),
                            Samples,
                            single_use  = SampleVolume,
                            wells=s + 1,
                            defLiqClass = SampleLiqClass,
                            excess      = 0)


        Itr.wash_tips(wasteVol=30, FastWash=True).exec()

        with group("Prefill plate with EtOH80p"):

            with self.tips(reuse=True, drop=False, drop_last=True):
                self.distribute(reagent=EtOH80p, to_labware_region=Plate_EtOH.selectOnly(all_samples))

        with group("Sample Lysis"):

            if self.add_preMix:                                          # add  ProtK+cRNA+MS2 mix

                with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.makePreMix(pK_cRNA_MS2)
                    self.distribute  (reagent=pK_cRNA_MS2, to_labware_region= Plate_lysis.selectOnly(all_samples))

            if self.add_VL:                                             # add  LysisBuffer

                with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.distribute  (reagent=LysisBuffer, to_labware_region= Plate_lysis.selectOnly(all_samples))

            if self.add_samples:                                        # add samples

                Itr.userPrompt("Please make sure the samples are in place").exec()
                with self.tips(reuse=False, drop=True):
                    self.transfer( from_labware_region  = Samples,
                                   to_labware_region    = Plate_lysis,
                                   volume               = SampleVolume,
                                   using_liquid_class   = (SampleLiqClass, "Serum Disp postMix3"),
                                   optimizeFrom         = False,
                                   optimizeTo           = True,           # todo Really ??
                                   NumSamples           = NumOfSamples)

                Itr.wash_tips(wasteVol=4, FastWash=True).exec()

            if self.do_extraction and self.add_preMix:
                Itr.userPrompt("Please Schutteln the plates for lysis in pos 1").exec()
                with incubation(minutes=5):
                    pass

        if self.do_extraction:
            Itr.userPrompt("Please make sure the samples are back in place").exec()

            with group("Beads binding"):

                with self.tips(tipsMask=maxMask, reuse=True, drop=False):
                    for p in [40, 50, 60, 65]:
                        self.mix_reagent(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)

                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=B_Beads, to_labware_region=Plate_lysis.selectOnly(all_samples))

                self.drop_tips()

                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=BindingBuffer, to_labware_region=Plate_lysis.selectOnly(all_samples))

                Itr.userPrompt("Please Schutteln the plates for lysis in pos 1").exec()

        self.drop_tips()
        self.done()


if __name__ == "__main__":

    p = PreKingFisher_RNAextNucleoMag_EtOH80p(num_of_samples= 96,
                                              run_name        = "")

    p.use_version('VL-pKmix Inactivated')
    # p.go_first_pos('A01')
    p.Run()
