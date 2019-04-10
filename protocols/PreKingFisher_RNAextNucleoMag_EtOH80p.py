# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'


from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100_FLI import Evo100_FLI
import EvoScriPy.Reactive as Rtv


class PreKingFisher_RNAextNucleoMag_EtOH80p(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "PreKingFisher for RNA extraction modified NucleoMag MN_Vet kit and EtOH80p Plate preFill"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'prefill inactivation': self.V_fill_inactivation,
                         'in-VL inactivated'   : self.V_VL_inactivated,
                         'pre Inactivated'     : self.V_inactivated,
                         'original samples'    : self.V_original_samples                }

    def V_VL_inactivated(self):
        pass

    def V_original_samples(self):
        pass

    def V_inactivated(self):
        pass

    def V_fill_inactivation(self):
        pass

    def __init__(self, GUI = None,  run_name = None):

        Evo100_FLI.__init__(   self,
                               GUI                         = GUI,
                               NumOfSamples                = PreKingFisher_RNAextNucleoMag_EtOH80p.max_s,
                               worktable_template_filename = '../EvoScripts/wt_templates/PreKingFisher_RNAextNucleoMag_EtOH80p.ewt',
                               output_filename             = '../current/PreKingFisher_RNAextNucleoMag_EtOH80p',
                               run_name                    = run_name)

    def Run(self):
        self.set_EvoMode()
        self.initialize()                       # set_defaults ??
        Rtv.NumOfSamples = self.NumOfSamples
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()

                                                              # Get Labwares (Cuvette, eppys, etc.) from the work table

        LysBuf      = wt.getLabware(Lab.Trough_100ml,   "2-Vl Lysis Buffer"     )
        BindBuf     = wt.getLabware(Lab.Trough_100ml,   "3-VEB Binding Buffer"  )

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Reactives   = wt.getLabware(Lab.GreinRack16_2mL, "Reactives" )

                                                              #  Set the initial position of the tips

        self.go_first_pos()

                                                              # Set volumen / sample

        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        LysisBufferVolume   = 100.0                 # VL1 or VL
        IC_MS2Volume        =  10.0                 # IC2
        IC2Volume           =   5.0                 # ? 4
        BindingBufferVolume = 350.0                 # VEB
        B_BeadsVolume       =  20.0                 # B-Beads
        EtOH80pVolume       = 600.0
        SampleVolume        = 100.0
        InitLysisVol        = 0.0

        if self.version == 'in-VL inactivated':
            InitLysisVol  = SampleVolume + LysisBufferVolume

        elif self.version == 'pre Inactivated':
            InitLysisVol  = SampleVolume + ProtKVolume + cRNAVolume + IC_MS2Volume + LysisBufferVolume

                                                        # Liquid classes used for pippetting.
                                                        # Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]


        # Define the reactives in each labware (Cuvette, eppys, etc.)

        if self.version != 'pre Inactivated':             # we need to add ProtK+cRNA+MS2 mix
            ProtK       = Rtv.Reactive("Proteinase K ",
                                       Reactives,
                                       replicas     = 2,
                                       pos          = [15, 16],
                                       volpersample = ProtKVolume  ,
                                       defLiqClass  = Small_vol_disp)

            cRNA        = Rtv.Reactive("Carrier RNA "         , Reactives, pos=14,  volpersample=  cRNAVolume  , defLiqClass=Small_vol_disp)
            IC_MS2      = Rtv.Reactive("IC MS2 phage culture ", Reactives, pos=13,  volpersample= IC_MS2Volume , defLiqClass=Small_vol_disp)

            # IC2         = Rtv.Reactive("IC2 - synthetic RNA " ,  Reactives, pos=13, volpersample=  IC2Volume ,defLiqClass=W_liquidClass)

            pK_cRNA_MS2 = Rtv.preMix  ("ProtK+cRNA+IC-MS2 mix "  ,
                                           Reactives,
                                           pos=8,
                                           components=[  cRNA, ProtK, IC_MS2] ,
                                           defLiqClass=W_liquidClass,
                                           excess=20)

            if self.version != 'in-VL inactivated':
                LysisBuffer     = Rtv.Reactive("VL - Lysis Buffer " , LysBuf,  volpersample=LysisBufferVolume , defLiqClass='MN VL')



        B_Beads         = Rtv.Reactive("B - Beads " ,
                                       Reactives,
                                       pos          = [1,2],
                                       initial_vol  = 1200,
                                       volpersample = B_BeadsVolume ,
                                       defLiqClass  = Beads_LC_2,
                                       maxFull      = 70)

        VEB             = Rtv.Reactive("VEB - Binding Buffer " ,  BindBuf,   volpersample=BindingBufferVolume , defLiqClass=B_liquidClass)

        EtOH80p         = Rtv.Reactive("Ethanol 80% " , wt.getLabware(Lab.Trough_100ml,  "7-EtOH80p"     ),  volpersample=EtOH80pVolume , defLiqClass=B_liquidClass)


        # Show the CheckList GUI to the user for possible small changes

        self.CheckList()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=30, FastWash=True).exec()

        Plate_lysis = wt.getLabware(Lab.MP96deepwell,   "Plate lysis"   )  # Plate 12 x 8 ?
        Plate_EtOH  = wt.getLabware(Lab.MP96deepwell,   "Plate EtOH"    )  # Plate 12 x 8 ? MP96well !!

        if self.version != 'original samples':
           Samples  = wt.getLabware(Lab.EppRack6x16,    "Proben"        )  # 6x16 = 12 x 8 ?


        # Define samples and the place for temporal reactions
        par = Plate_lysis.parallelOrder(self.nTips, all_samples)

        for s in all_samples:

            if self.version == 'original samples':
                Rtv.Reactive("probe_{:02d}".format(s + 1), Samples, single_use=SampleVolume,
                             pos=s + 1, defLiqClass=SampleLiqClass, excess=0)

            Rtv.Reactive("lysis_{:02d}".format(s + 1), Plate_lysis, initial_vol=InitLysisVol, pos=s + 1,
                         excess=0)

            Rtv.Reactive("EtOH80p_{:02d}".format(s + 1), Plate_EtOH, initial_vol=0.0, pos=par[s] + 1,
                         excess=0)  # todo revise order !!!


        with group("Prefill plate with EtOH80p"):
            with self.tips(reuse=True, drop=False, drop_last=True):
                self.spread(reactive=EtOH80p, to_labware_region=Plate_EtOH.selectOnly(all_samples))


        with group("Sample Lysis"):
            if self.version != 'pre Inactivated':                            #  add  ProtK+cRNA+MS2 mix

                with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                    self.makePreMix(pK_cRNA_MS2)
                    self.spread  (  reactive=pK_cRNA_MS2,   to_labware_region= Plate_lysis.selectOnly(all_samples))


                if self.version != 'in-VL inactivated':                      # add  LysisBuffer

                    with self.tips(tipsMask=maxMask, reuse=True, drop=False, drop_last=True):
                        self.spread  (  reactive=LysisBuffer,   to_labware_region= Plate_lysis.selectOnly(all_samples))


            if self.version == 'original samples':                       # add samples

                Itr.userPrompt("Please make sure the samples are in place").exec()
                with self.tips(reuse=False, drop=True):
                    self.transfer(  from_labware_region= Samples,
                               to_labware_region=   Plate_lysis,
                               volume=              SampleVolume,
                               using_liquid_class=  (SampleLiqClass, "Serum Disp postMix3"),
                               optimizeFrom         = False,
                               optimizeTo           = False,           # todo Really ??
                               NumSamples           = NumOfSamples)
                Itr.wash_tips(wasteVol=4, FastWash=True).exec()

            if self.version != 'pre Inactivated':
                Itr.userPrompt("Please Schutteln the plates for lysis in pos 1").exec()
                with incubation(minutes=5): pass

        if self.version != 'prefill inactivation':
            Itr.userPrompt("Please make sure the samples are back in place").exec()

        with group("Beads binding"):
            with self.tips(tipsMask=maxMask, reuse=True, drop=False):
                for p in [40, 50, 60, 65]:
                    self.mix_reactive(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)
            with self.tips(reuse=True, drop=False):
                self.spread( reactive=B_Beads,      to_labware_region=Plate_lysis.selectOnly(all_samples))
            self.dropTips()

            with self.tips(reuse=True, drop=False):
                self.spread( reactive=VEB,          to_labware_region=Plate_lysis.selectOnly(all_samples))

            Itr.userPrompt("Please Schutteln the plates for lysis in pos 1").exec()

        self.dropTips()
        self.done()

