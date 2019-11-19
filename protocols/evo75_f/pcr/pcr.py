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
                 sample_line=6):

        self.sample_line = sample_line
        self.cell_rows = cell_rows
        self.page = page
        self.exp_file = exp_file
        this = Path(__file__).parent

        Evo75_FLI.__init__(self,
                           GUI                         = GUI,
                           num_of_samples              = PCR.max_s,
                           worktable_template_filename = this / '../Freedom75_FLI_PCR.ewt',
                           output_filename             = output_filename or this / 'scripts' / 'PCR',
                           run_name                    = run_name)

        # call all the "DB" things not directly used.

        Primer.load_excel_list()
        PrimerMix.load_excel_list()

    def run(self):
        self.initialize()

        num_of_samples = self.num_of_samples
        wt           = self.worktable

        self.comment('PCR {:d} plates for {:d} samples.'
                     .format(self.num_plates, num_of_samples))

                                                       # Get Labwares (Cuvette, eppys, etc.) from the work table

        self.set_first_tip()                      #  Set the initial position of the tips

        # Set volumen / sample


        # Define the reactives in each labware (Cuvette, eppys, etc.)


        # exp_file = 'K:\AG RealtimePCR\Ariel\Exp 424. WESSV.MID.NewRNAbis-4. AVRvsSAfr.PanFlav-224.Ute.xlsx'
        # page ='Druken (2)'

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

        exp = PCRexperiment().load_excel_list(sheet0)
        pcr_plates = [wt.get_labware("PCR" + str(i + 1)) for i in range(self.num_plates)]
        eppis_rack = wt.get_labware("MM + Primer")
        exp = PCRexperimentRtic(exp, pcr_plates[0], eppis_rack, self)
        # Show the check_list GUI to the user for possible small changes

        self.check_list()
        self.set_EvoMode()

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()


        # Define place for intermediate reactions


        self.done()


if __name__ == "__main__":
    # from pathlib import Path
    # import logging
    this = Path(__file__).parent
    logging.basicConfig(filename=(this / 'scripts' / 'log.txt'), filemode='w', level=logging.DEBUG)

    p = PCR(run_name='1 plate')

    p.use_version('1 plate')
    p.run()
