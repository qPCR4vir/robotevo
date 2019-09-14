# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# Tutorial

from EvoScriPy.protocol_steps import *
from protocols.evo200_f.evo200_f import Evo200_FLI


class Tutorial_LL(Evo200_FLI):
    """
    Created n wells with 100 uL of mix1 diluted 1:10. A diluent is provided.
    A reagent "mix1" is diluted (distributed) in n wells 1:10.
    The final volume of each dilution is vf=100 uL.

    There are many ways to achieve that. Here is one:
    - Calculate how much to distribute from mix1 to each dilution_10. v= vf/10 and from diluent vd.
    - Create well mix1 in an Eppendorf Tube 1,5 mL for v uL per "sample".
    - Create wells diluent in a cubette 100 mL for vd uL per "sample".
    - Generate check list
    - Create n dilution_10_i wells ( i from 0 to n-1 )
    - Distribute mix1
    - Distribute diluent

    """

    name = "Tutorial_LL. Dilutions."
    min_s, max_s = 1, 96                  # all dilutions in one 96 well plate

    def def_versions(self):               # for now just ignore the variants
        self.versions = {'No version': self.v_def}

    def v_def(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 num_of_samples: int         = 8,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        this = Path(__file__).parent

        Evo200_FLI.__init__(self,
                            GUI                         = GUI,
                            num_of_samples              = num_of_samples or Tutorial_LL.max_s,
                            worktable_template_filename = worktable_template_filename or
                                                          this.parent / 'tutorial_HL' / 'tutorial_hl_dilution.ewt',
                            output_filename             = output_filename or this / 'scripts' / 'dilutions_LL',
                            firstTip                    = firstTip,
                            run_name                    = run_name)

    def run(self):
        self.initialize()           # if needed calls Executable.initialize() and set_EvoMode
                                    # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        n = self.num_of_samples
        assert 1 <= n <= Tutorial_LL.max_s, "In this demo we want to set dilutions in a 96 well plate."
        wt = self.worktable

        instructions.comment('Dilute 1:10 mix1 in {:d} wells.'.format(n)).exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table    -----------------------------------------------
        diluent_cuvette   = wt.get_labware("BufferCub", labware.Trough_100ml)
        assert isinstance(diluent_cuvette, labware.Cuvette)

        mixes_eppis             = wt.get_labware("mixes", labware.Eppendorfrack)
        assert isinstance(mixes_eppis, labware.Labware)

        vf = 100                                      # The final volume of every dilution, uL
        v  = vf / 10                                   # uL to be distribute from original mix1 to each dilution_10
        vd = vf - v                                   # uL to be distribute from diluent to each dilution_10
        excess = 1.04                                 # 4%

        diluent_wells = diluent_cuvette.Wells[0:8]          # Define the wells in each labware (Cuvette, eppys, etc.) ---
        diluent_wells[0].vol = vd * n * excess              # set the initial volume needed - connected wells

        mix1     = mixes_eppis.Wells[0]                     # just one 1,5 mL tube
        mix1.vol = v * n * excess

        self.user_prompt("Put diluent in "+str(diluent_wells[0]))        # Show the check_list   -------------------------
        self.user_prompt("Put mix1 in " + str(mix1))

        instructions.wash_tips(wasteVol=5, FastWash=True).exec()

        plate = wt.get_labware(label="plate", labw_type="96 Well Microplate")
        assert isinstance(plate, labware.Labware)

        dilution_wells = plate.Wells[:n]                                 # Define place for intermediate mixes  ----------

        with group("Fill dilutions"):

            self.user_prompt("Put the plate for dilutions in " + str(plate.location))

            arm = self.robot.cur_arm(instructions.Pipette.LiHa1)
            m_tips = arm.n_tips

            n_tips = min(n, m_tips)                                                 # distribute mix1 --------------
            self.pick_up_tip(TIP_MASK = robot.mask_tips[n_tips],                       # using 200 uL tips
                             tip_type = "DiTi 200 ul",
                             arm      = arm)

            dilution_left = n
            while dilution_left:
                n_tips = min(dilution_left, m_tips)
                max_multi_disp_n = arm.Tips[0].type.max_vol // v
                dsp, rst = divmod(dilution_left, n_tips)
                if dsp >= max_multi_disp_n:
                    dsp = max_multi_disp_n
                    vol = [v * dsp] * n_tips                                        # equal volume with each tips
                    available_disp = dsp
                else:
                    vol = [v * (dsp + 1)] * rst + [v * dsp] * (n_tips - rst)
                    available_disp = dsp + bool(rst)

                for tip in range(n_tips):
                    self.aspirate(arm=arm, TIP_MASK=robot.mask_tip[tip], volume=vol,
                                  from_wells=mix1, liq_class=self.Water_free)

                while available_disp:
                    n_tips = min(n_tips, dilution_left)
                    cur_sample = n - dilution_left
                    sel = dilution_wells[cur_sample: cur_sample + n_tips]
                    self.dispense(arm      = arm,
                                  TIP_MASK = robot.mask_tips[n_tips],
                                  volume   = v,
                                  to_wells = sel,
                                  liq_class=self.Water_free)
                    available_disp -= 1
                    dilution_left -= n_tips

            self.drop_tip()

            n_tips = min(n, m_tips, len(diluent_wells))                                    # distribute diluent ----------
            self.pick_up_tip(TIP_MASK = robot.mask_tips[n_tips],                        # using 1000 uL tips
                             tip_type = "DiTi 1000ul",
                             arm      = arm)

            dilution_left = n
            while dilution_left:
                n_tips = min(dilution_left, m_tips, len(diluent_wells))
                max_multi_disp_n = arm.Tips[0].type.max_vol // vd
                dsp, rst = divmod(dilution_left, n_tips)
                if dsp >= max_multi_disp_n:
                    dsp = max_multi_disp_n
                    vol = [vd * dsp] * n_tips       # equal volume with each tips
                    available_disp = dsp
                else:
                    vol = [vd * (dsp + 1)] * rst + [vd * dsp] * (n_tips - rst)
                    available_disp = dsp + bool(rst)

                self.aspirate(arm=arm, TIP_MASK=robot.mask_tips[n_tips], volume=vol,
                              from_wells=diluent_wells, liq_class=self.Water_free)

                while available_disp:
                    n_tips = min(n_tips, dilution_left)
                    cur_sample = n - dilution_left
                    sel = dilution_wells[cur_sample: cur_sample + n_tips]
                    self.dispense(arm      = arm,
                                  TIP_MASK = robot.mask_tips[n_tips],
                                  volume   = vd,
                                  to_wells = sel,
                                  liq_class=self.Water_free)
                    available_disp -= 1
                    dilution_left -= n_tips

            self.drop_tip()

        self.done()


if __name__ == "__main__":
    p = Tutorial_LL(num_of_samples= 42, run_name        = "_42s")

    p.use_version('No version')
    p.run()
