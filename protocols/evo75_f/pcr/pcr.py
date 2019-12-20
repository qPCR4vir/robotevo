# Copyright (C) 2018-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2018-2019
__author__ = 'Ariel'
# this is

from EvoScriPy.protocol_steps import *
from EvoScriPy.reagent import *
from protocols.evo75_f.evo75_f import Evo75_FLI


class PCR(Evo75_FLI):
    """

    """

    name = "PCR"
    min_s, max_s = 1, 96

    def def_versions(self):
        self.versions = {'3 plate': self.V_3_plate,
                         '2 plate': self.V_2_plate,
                         '1 plate': self.V_1_plate}

    def V_1_plate(self):        self.num_plates = 1
    def V_2_plate(self):        self.num_plates = 2
    def V_3_plate(self):        self.num_plates = 3

    def __init__(self,
                 GUI=None,
                 run_name=None,
                 output_filename=None,
                 exp_file=None,
                 page=None,
                 cell_rows=6,
                 sample_line=6,
                 worktable=None,
                 primers_file=None):

        self.sample_line = sample_line
        self.cell_rows = cell_rows
        self.page = page
        self.exp_file = exp_file
        this = Path(__file__).parent

        Evo75_FLI.__init__(self,
                           GUI                         = GUI,
                           num_of_samples              = PCR.max_s,
                           worktable_template_filename = worktable or (this / '../Freedom75_FLI_PCR.ewt'),
                           output_filename             = output_filename or this / 'scripts' / 'PCR',
                           run_name                    = run_name)

        # call all the "DB" things not directly used.
        file = primers_file or Path('PCR.xlsx')
        Primer.load_excel_list(file_name=file)
        PrimerMix.load_excel_list(file_name=file)

    def run(self):

        sheet0 = ExpSheet(
            file_name=Path('K:\\AG RealtimePCR\\Ariel\\Exp 424. WESSV.MID.NewRNAbis-4. AVRvsSAfr.PanFlav-224.Ute.xlsx'),
            page='Druken (2)',
            cell_rows=3,
            sample_line=3)

        sheet1 = ExpSheet(file_name=Path(
            'C:\\Users\\Ariel\\Documents\\Exp\\PCR\\'
            'Exp 308. WNV.ZKU.10-1 10-10. WN-INNT-133, WN.Hoff, PanFlav.116.pltd.xlsx'),
            page='Druken (3)',
            cell_rows=6,
            sample_line=6)

        sheet2 = ExpSheet(file_name=Path('PCR.xlsx'), page='PCR-SYBR', cell_rows=4, sample_line=3)
        sheet3 = ExpSheet(file_name=Path('PCR.xlsx'), page='PCR-1plex', cell_rows=3, sample_line=3)
        sheet4 = ExpSheet(file_name=Path('PCR.xlsx'), page='Exp 308', cell_rows=6, sample_line=6)
        sheet5 = ExpSheet(file_name=Path('PCR.xlsx'), page='Exp 424', cell_rows=3, sample_line=3)

        exp = PCRexperiment().load_excel_list(sheet5)

        self.initialize()

        num_of_samples = self.num_of_samples
        wt = self.worktable

        self.comment('PCR {:d} plates for {:d} samples.'
                     .format(self.num_plates, num_of_samples))

        # Get Labwares (Cuvette, eppys, etc.) from the work table
        pcr_plates = [wt.get_labware("PCR" + str(i + 1)) for i in range(self.num_plates)]
        kit_rack = [wt.get_labware(rack) for rack in ["PCRkits+MMix", "PrimerMix"]]
        mmix_rack = [wt.get_labware(rack) for rack in ["PrimerMix", "PCRkits+MMix", "Primers-5"]]
        primer_mix_rack = mmix_rack + [wt.get_labware(rack) for rack in ["Primers-4", "Primers-3"]]
        primer_rack = [wt.get_labware(rack) for rack in ["Primers-1", "Primers-2", "Primers-3",
                                                         "Primers-4", "Primers-5"]]

        self.set_first_tip()                      # Set the initial position of the tips

        # Set volume / sample

        # Define the reagents in each labware (Cuvette, eppys, etc.)
        Reagent('Quantitect-SYBR RT-PCR Master Mix', labware='PCRkits+MMix', num_of_aliquots=2, concentration=2)
        Reagent('Quantitect-Probe RT-PCR Master Mix', labware='PCRkits+MMix', num_of_aliquots=2, concentration=2)
        h2o = Reagent('H2O', labware='BufferTubes', num_of_aliquots=5, minimize_aliquots=False)
        te100x = Reagent('TE 100x', labware='BufferTubes', num_of_aliquots=1, concentration=100)
        Reagent('TE 1x', labware='BufferTubes', num_of_aliquots=1)
        Reagent('TE 0,1 x', labware='BufferTubes', num_of_aliquots=1)

        TE_10x_fixed = MixReagent('TE 10x fixed', labware='BufferTubes', num_of_aliquots=1, min_vol=5000,
                   components=[MixComponentReagent(te100x, volume=500),
                               MixComponentReagent(h2o, volume=4500)])
        TE_1x_fixed = MixReagent('TE 1x fixed', labware='BufferTubes', num_of_aliquots=1, min_vol=5000,
                                 components=[MixComponentReagent(TE_10x_fixed, volume=500),
                                             MixComponentReagent(h2o, volume=4500)])

        te10x = Dilution('TE 10x dil', labware='BufferTubes', num_of_aliquots=1, min_vol=5000,
                         components=[DilutionComponentReagent(te100x, dilution=10)], diluent=h2o)
        te1x = Dilution('TE 1x dil', labware='BufferTubes', num_of_aliquots=1, min_vol=5000,
                        components=[DilutionComponentReagent(te10x, dilution=10)], diluent=h2o)

        expr = PCRexperimentRtic(exp,
                                 plates=pcr_plates[0],
                                 kit_rack=kit_rack,
                                 mmix_rack=mmix_rack,
                                 primer_mix_rack=primer_mix_rack,
                                 primer_rack=primer_rack,
                                 protocol=self)
        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        expr.dilute_primers()

        with self.tips():  # todo add tip_type="DiTi 1000ul" to the worktable !!
            TE_10x_fixed.make(self)
            TE_1x_fixed.make(self)
            te10x.make(self, volume=15000)
            te1x.make(self, volume=15000)

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        # Define place for intermediate reactions

        self.done()


if __name__ == "__main__":
    # from pathlib import Path
    # import logging
    this = Path(__file__).parent
    logging.basicConfig(filename=(this / 'scripts' / 'log.txt'), filemode='w', level=logging.DEBUG)

    wt1 = this / '../Freedom75_FLI_PCR.ewt'
    wt2 = this / '../Freedom75_FLI_PCR2x3Pr.ewt'
    wt3 = this / '../Freedom75_FLI_PCR5xPr.ewt'
    pf1 = Path('C:\Prog\exp\PCR fli.xlsx')
    pf2 = Path('K:\\AG RealtimePCR\\Ariel\\PCR fli.xlsx')
    pf3 = Path('PCR.xlsx')

    p = PCR(run_name='1 plate', worktable=wt3, primers_file=pf3)

    p.use_version('1 plate')
    p.run()
