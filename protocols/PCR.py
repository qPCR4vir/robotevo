# Copyright (C) 2018-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2018

from EvoScriPy.protocol_steps import *
import EvoScriPy.instructions as Itr
import EvoScriPy.Labware as Lab
import EvoScriPy.reagent as Rgt      # ??
#from protocols.Evo75_FLI import Evo75_FLI
from protocols.Evo100 import Evo100_FLI

from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p  import PreKingFisher_RNAextNucleoMag_EtOH80p

__author__ = 'Ariel'


class PCRexperiment(Pipeline):
    """ - Sample names import
        - RNA extraction (optional): Evo100, posible pipeline
        - PCR mix:  Evo75, posible primerMix and even Primer preparation
        - PCR samples: Evo100
        - Export to BioRad software of plate info.
        """
    name = "PCR experiment"

    def __init__(self, GUI=None, run_name=None):
        protocols = [Pipeline                              (run_name="Sample names import"),
                     Prefill_plates_VEW1_ElutionBuffer_VEW2(run_name="Prefill"),
                     PreKingFisher_RNAextNucleoMag_EtOH80p (run_name="Lysis"  )    ]

        Pipeline.__init__(self, GUI, protocols, run_name)




class Evo75_FLI(Protocol):
    """ Using the Evo75_FLI_INNT
    """

    def __init__(self,  GUI                 = None,
                        worktable_template_filename='../EvoScripts/Freedom75_FLI_PCR.ewt',
                        output_filename     = None,
                        run_name            = None):

        Protocol.__init__(self, GUI                         = GUI,
                          n_tips= 1,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          run_name                    = run_name)


    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi     = Lab.DiTi_0200ul   # todo revise, this is a type, the others are labwares

        WashCleanerS    = wt.get_labware(Lab.CleanerShallow, "")
        WashWaste       = wt.get_labware(Lab.WasteWash, "")
        WashCleanerL    = wt.get_labware(Lab.CleanerDeep, "")
        DiTiWaste       = wt.get_labware(Lab.DiTi_Waste_plate, "TipWaste")

        # Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.WorkTable.Location(1,2))
        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste


class MixPCR(Evo75_FLI):
    """Implementation of the protocol for RNA extraction using the NucleoMag® VET kit from MACHEREY-NAGEL.
    """

    name = "PreKingFisher for RNA extraction modified NucleoMag MN_Vet kit and EtOH80p Plate preFill"
    versions = {'none'    : not_implemented}

    def __init__(self, GUI=None, run_name=None):
        Evo75_FLI.__init__(self,
                            GUI=GUI,
                            output_filename='../current/' + run_name,
                            run_name=run_name)

    def Run(self):
        self.initialize()                       #  set_defaults ??
        wt           = self.worktable

        Itr.comment('Extracting RNA from {:s} samples with the MN-Vet kit'.format(str(NumOfSamples))).exec()


        #  Get Labwares (Cuvette, eppys, etc.) from the work table

        DiTi1000_1  = wt.get_labware(Lab.DiTi_1000ul, "1000-1")
        DiTi1000_2  = wt.get_labware(Lab.DiTi_1000ul, "1000-2")
        DiTi1000_3  = wt.get_labware(Lab.DiTi_1000ul, "1000-3")

        Reactives   = wt.get_labware(Lab.GreinRack16_2mL, "Reagents")

        #  Set the initial position of the tips

        self.go_first_pos()

        # Set volumen / sample

        SampleVolume        = 200.0
        EtOH80pVolume       = 600.0



        SampleLiqClass = "Serum Asp"  # = TissueHomLiqClass   # SerumLiqClass="Serum Asp preMix3"

        all_samples = range(NumOfSamples)
        maxTips     = min  (self.n_tips, NumOfSamples)
        maxMask     = Rbt.tipsMask[maxTips]


        # Define the reactives in each labware (Cuvette, eppys, etc.)


        VEB             = Rgt.Reagent("VEB - Binding Buffer ",
                                      BindBuf, volpersample=BindingBufferVolume, defLiqClass=B_liquidClass)
        EtOH80p         = Rgt.Reagent("Ethanol 80% ",
                                      wt.get_labware(Lab.Trough_100ml, "7-EtOH80p"),
                                      volpersample=EtOH80pVolume, defLiqClass=B_liquidClass)


        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        Itr.wash_tips(wasteVol=30, FastWash=True).exec()

        Plate_lysis = wt.get_labware(Lab.MP96deepwell, "Plate lysis")  # Plate 12 x 8 ?
        Plate_EtOH  = wt.get_labware(Lab.MP96deepwell, "Plate EtOH")  # Plate 12 x 8 ? MP96well !!
        Samples     = wt.get_labware(Lab.EppRack6x16, "Proben")  # 6x16 = 12 x 8 ?


        # Define samples and the place for temporal reactions
        par = Plate_lysis.parallelOrder(self.n_tips, all_samples)
        for s in all_samples:
            Rgt.Reagent("probe_{:02d}".format(s + 1), Samples, single_use=SampleVolume,
                        wells=s + 1, defLiqClass=SampleLiqClass, excess=0)
            Rgt.Reagent("lysis_{:02d}".format(s + 1), Plate_lysis, initial_vol=0.0, wells=par[s] + 1,
                        excess=0)  # todo revise order !!!

            Rgt.Reagent("EtOH80p_{:02d}".format(s + 1), Plate_EtOH, initial_vol=0.0, wells=par[s] + 1,
                        excess=0)  # todo revise order !!!


        with group("Prefill plate with EtOH80p"):
            with tips(reuse=True, drop=False, drop_last=True):
                spread(reactive=EtOH80p, to_labware_region=Plate_EtOH.selectOnly(all_samples))
        dropTips()
        self.done()




        PanFla_119 = PrimerMix("PanFLA", ID="119", components=[Primer.IDs[320], Primer.IDs[321]])
        WNV_INNT_37 = PrimerMix("WNV_5p", ID="37", components=[Primer.IDs[20], Primer.IDs[21], Primer.IDs[22]])

        Exp_300 = PCRexperiment(300, "PanFLA mosq Grecia")

        samples = ["Pool-1",
                   "Pool-2",
                   "Pool-3",
                   "Pool-4"]

        Exp_300.addReactions(PanFla_119, samples)
        Exp_300.addReactions(WNV_INNT_37, samples)

        Exp_300.pippete_mix()  # Evo75
        Exp_300.pippete_samples()  # Evo100

