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


class Prefill_plates_VEW1_ElutionBuffer_VEW2(Evo100_FLI):
    """
    Prefill plates with VEW1, Elution buffer and VEW2 for the
    Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL
    with washes in the Fischer Robot.
    """

    name = "Prefill plates with VEW1, Elution buffer and VEW2 for KingFisher"
    versions = {'none'    : not_implemented}

    class Parameter (Evo100_FLI.Parameter):

        def __init__(self, GUI = None):

            self.NumOfSamples = 96
            Evo100_FLI.Parameter.__init__(self, GUI=GUI,
                                          NumOfSamples=96,
                                          worktable_template_filename = '../EvoScripts/wt_templates/preFisher_RNAext.ewt',
                                          output_filename='../current/Prefill_plates_VEW1_ElutionBuffer_VEW2'
                                         )


    def Run(self):
        self.initialize()                       #  set_defaults ??
        NumOfSamples = self.NumOfSamples
        wt           = self.worktable

        Itr.comment('Prefill plates with VEW1, Elution buffer and VEW2 for {:s} samples.'.format(str(NumOfSamples))).exec()


        #  Get Labwares (Cuvette, eppys, etc.) from the work table

        ElutBuf     = wt.getLabware(Lab.Trough_100ml,   "1-VEL-ElutionBuffer"   )

        DiTi1000_1  = wt.getLabware(Lab.DiTi_1000ul,    "1000-1")
        DiTi1000_2  = wt.getLabware(Lab.DiTi_1000ul,    "1000-2")
        DiTi1000_3  = wt.getLabware(Lab.DiTi_1000ul,    "1000-3")

        Plate_VEW1  = wt.getLabware(Lab.MP96deepwell,   "Plate VEW1"    )  # Plate 12 x 8 ?
        Plate_VEW2  = wt.getLabware(Lab.MP96deepwell,   "Plate VEW2"    )  # Plate 12 x 8 ?
        Plate_Eluat = wt.getLabware(Lab.MP96well,      "Plate ElutB"    )  # Plate 12 x 8 ? MP96well !!


        #  Set the initial position of the tips

        Itr.set_DITI_Counter2(DiTi1000_1, posInRack=self.parameters.firstTip).exec()

        # Set volumen / sample

        VEW1Volume          = 600.0
        VEW2Volume          = 600.0
        ElutionBufferVolume = 100.0


        # Liquid classes used for pippetting. Others liquidClass names are defined in "protocol_steps.py"

        # SampleLiqClass = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"


        all_samples = range(NumOfSamples)
        maxTips     = min  (self.nTips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]


        # Define the reactives in each labware (Cuvette, eppys, etc.)

        VEW1            = Rtv.Reactive("VEW1 - Wash Buffer "              ,
                                         wt.getLabware(Lab.Trough_100ml,  "4-VEW1 Wash Buffe"),
                                         volpersample=VEW1Volume    , defLiqClass=B_liquidClass)
        VEW2            = Rtv.Reactive("VEW2 - WashBuffer "               ,
                                         wt.getLabware(Lab.Trough_100ml,  "5-VEW2-WashBuffer" ),
                                         volpersample=VEW2Volume    , defLiqClass=B_liquidClass)
        ElutionBuffer   = Rtv.Reactive("Elution Buffer "                  ,
                                       ElutBuf,     volpersample=ElutionBufferVolume , defLiqClass="Eluat")

        # Show the CheckList GUI to the user for posible small changes

        self.CheckList()

        Itr.wash_tips(wasteVol=30, FastWash=True).exec()

        # Define samples and the place for temporal reactions
        for s in all_samples:
            Rtv.Reactive("VEW1_{:02d}".format(s + 1), Plate_VEW1, initial_vol=0.0, pos=s + 1,
                         excess=0)  # todo revise order !!!
            Rtv.Reactive("VEW2_{:02d}".format(s + 1), Plate_VEW2, initial_vol=0.0, pos=s + 1,
                         excess=0)  # todo revise order !!!


        with group("Prefill plates with VEW1, VEW2, EtOH and Elution buffer"):

            Itr.userPrompt("Put the plates for VEW1, VEW2 and EtOH in that order")

            with tips(reuse=True, drop=False):
                spread(reactive=VEW1, to_labware_region=Plate_VEW1.selectOnly(all_samples))

            with tips(reuse=True, drop=False):
                spread(reactive=ElutionBuffer, to_labware_region=Plate_Eluat.selectOnly(all_samples))

            with tips(reuse=True, drop=False):
                spread(reactive=VEW2, to_labware_region=Plate_VEW2.selectOnly(all_samples))

        self.done()
