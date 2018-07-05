# Copyright (C) 2018-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2018

from EvoScriPy.protocol_steps import *
import EvoScriPy.Instructions as Itr
import EvoScriPy.Labware as Lab
from protocols.Evo100_FLI import Evo100_FLI
import EvoScriPy.Reactive as Rtv      # ??


__author__ = 'Ariel'


class KingFisher_RNAextNucleoMag_EtOH80p(Evo100_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "RNAextr original NMag MN_Vet kit and EtOH80p preFill for KingFisher"
    versions = {'none'    : not_implemented}

    class Parameter (Evo100_FLI.Parameter):

        def __init__(self, GUI = None):
            Evo100_FLI.Parameter.__init__(self, GUI=GUI,
                                          NumOfSamples=96,
                                          worktable_template_filename = '../EvoScripts/wt_templates/preFisher_RNAext_EtOH.ewt',
                                          output_filename='../current/KingFisher_RNAextNucleoMag_EtOH80p'
                                         )

    def Run(self):
        self.initialize()                       #  set_defaults ??
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Extracting RNA from {:s} samples with the original MN-Vet kit protocol and EtOH prefill'.format(str(NumOfSamples))).exec()


        #  Get Labwares (Cuvette, eppys, etc.) from the work table

        LysBuf      = wt.getLabware(Lab.Trough_100ml,   "2-Vl Lysis Buffer"     )
        BindBuf     = wt.getLabware(Lab.Trough_100ml,   "3-VEB Binding Buffer"  )

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Reactives   = wt.getLabware(Lab.GreinRack16_2mL,"Reactives" )

        #  Set the initial position of the tips

        Itr.set_DITI_Counter2(DiTi1000_1, posInRack=self.parameters.firstTip).exec()

        # Set volumen / sample

        SampleVolume        = 200.0
        LysisBufferVolume   = 180.0       # VL1
        IC2Volume           =   5.0       # ? 4
        BindingBufferVolume = 600.0
        B_BeadsVolume       =  20.0
        ProtKVolume         =  20.0
        cRNAVolume          =   4.0
        IC_MS2Volume        =  20.0
        EtOH80pVolume       = 600.0


        # Liquid classes used for pippetting. Others liquidClass names are defined in "protocol_steps.py"

        SampleLiqClass = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]


        # Define the reactives in each labware (Cuvette, eppys, etc.)

        LysisBuffer     = Rtv.Reactive("VL - Lysis Buffer "              ,
                                       LysBuf,    volpersample=LysisBufferVolume ,defLiqClass=B_liquidClass)
        IC2             = Rtv.Reactive("IC2 - synthetic RNA "              ,
                                       Reactives, pos=11, volpersample=  IC2Volume ,defLiqClass=W_liquidClass)
        VEB             = Rtv.Reactive("VEB - Binding Buffer "           ,
                                       BindBuf,   volpersample=BindingBufferVolume ,defLiqClass=B_liquidClass)
        B_Beads         = Rtv.Reactive("B - Beads " , Reactives, initial_vol=1200,
                                         pos=1, volpersample= B_BeadsVolume , replicas=2, defLiqClass=Beads_LC_2)

        EtOH80p         = Rtv.Reactive("Ethanol 80% "                     ,
                                         wt.getLabware(Lab.Trough_100ml,  "7-EtOH80p"     ),
                                         volpersample=EtOH80pVolume , defLiqClass=B_liquidClass)

        ProtK           = Rtv.Reactive("Proteinase K "                    ,
                                       Reactives, pos=16, volpersample= ProtKVolume , defLiqClass=Small_vol_disp)
        cRNA            = Rtv.Reactive("Carrier RNA "                     ,
                                       Reactives, pos=15, volpersample=  cRNAVolume , defLiqClass=Small_vol_disp)
        IC_MS2          = Rtv.Reactive("IC MS2 phage culture ",
                                       Reactives, pos=14, volpersample= IC_MS2Volume , defLiqClass=Small_vol_disp)
        pK_cRNA_MS2     = Rtv.preMix  ("ProtK+cRNA+IC-MS2 mix "        ,
                                       Reactives, pos=12,   components=[ ProtK, cRNA, IC2 ]
                                         ,defLiqClass=W_liquidClass, replicas=2)

        # Show the CheckList GUI to the user for possible small changes

        self.CheckList()

        Itr.wash_tips(wasteVol=30, FastWash=True).exec()

        Plate_lysis = wt.getLabware(Lab.MP96deepwell,   "Plate VEW1"    )  # Plate 12 x 8 ?
        Plate_EtOH  = wt.getLabware(Lab.MP96deepwell,   "Plate EtOH"    )  # Plate 12 x 8 ? MP96well !!
        Samples     = wt.getLabware(Lab.EppRack6x16,    "Proben"        )  # 6x16 = 12 x 8 ?


        # Define samples and the place for temporal reactions
        for s in all_samples:
            Rtv.Reactive("probe_{:02d}".format(s + 1), Samples, single_use=SampleVolume,
                         pos=s + 1, defLiqClass=SampleLiqClass, excess=0)
            Rtv.Reactive("lysis_{:02d}".format(s + 1), Plate_lysis, initial_vol=0.0, pos=s + 1,
                         excess=0)  # todo revise order !!!

            Rtv.Reactive("EtOH80p_{:02d}".format(s + 1), Plate_EtOH, initial_vol=0.0, pos=s + 1,
                         excess=0)  # todo revise order !!!


        with group("Prefill plate with EtOH80p"):
            with tips(reuse=True, drop=False):
                spread(reactive=EtOH80p, to_labware_region=Plate_EtOH.selectOnly(all_samples))


        with group("Sample Lysis"):
            with tips(tipsMask=maxMask, reuse=True, drop=True):
                pK_cRNA_MS2.make(NumOfSamples)
                spread  (  reactive=pK_cRNA_MS2,   to_labware_region= Plate_lysis.selectOnly(all_samples))
                spread  (  reactive=LysisBuffer,   to_labware_region= Plate_lysis.selectOnly(all_samples))
            with tips(reuse=False, drop=True):
                transfer(  from_labware_region= Samples,
                           to_labware_region=   Plate_lysis,
                           volume=              SampleVolume,
                           using_liquid_class=  (SampleLiqClass,"Serum Disp postMix3"),
                           optimizeFrom         =False,     # optimizeTo= True,           # todo Really ??
                           NumSamples=          NumOfSamples)
            Itr.wash_tips(wasteVol=4, FastWash=True).exec()


            with incubation(minutes=15):
                Itr.userPrompt("Please Schutteln the plates for lysis in pos 1")

        with group("Beads binding"):
            with tips(tipsMask=maxMask, reuse=True, drop=False):
                for p in [40, 50, 60, 65]:
                   mix_reactive(B_Beads, LiqClass=Beads_LC_1, cycles=1, maxTips=maxTips, v_perc=p)

            with tips(reuse=True, drop=True):
                spread( reactive=B_Beads,      to_labware_region=Plate_lysis.selectOnly(all_samples))
                spread( reactive=VEB,          to_labware_region=Plate_lysis.selectOnly(all_samples))

            with incubation(minutes=5):
                Itr.userPrompt("Please Schutteln the plates for lysis in pos 1")

        self.Script.done()
        self.comments_.done()

