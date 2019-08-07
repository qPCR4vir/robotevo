# Copyright (C) 2019-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2019-2019
__author__ = 'Ariel'

# Tutorial

from   EvoScriPy.protocol_steps import *
import EvoScriPy.instructions   as     Itr
import EvoScriPy.labware        as     Lab
from protocols.Evo200 import Evo200


class Tutorial_LL(Evo200):
    """
    Created n wells with 100 uL of mix1 diluted 1:10. A diluent is provided.
    A reagent "mix1" is diluted (distributed) in n wells 1:10.
    The final volume of each dilution is vf=100 uL.

    There are many ways to achieve that. Here is one:
    - Calculate how much to distribute from mix1 to each Dil_10. v= vf/10 and from diluent vd.
    - Create well mix1 in an Eppendorf Tube 1,5 mL for v uL per "sample".
    - Create wells diluent in a cubette 100 mL for vd uL per "sample".
    - Generate check list
    - Create n Dil_10_i wells ( i from 0 to n-1 )
    - Distribute mix1
    - Distribute diluent

    """

    name = "Tutorial_LL. Dilutions."
    min_s, max_s = 1, 96                  # all dilutions in one 96 well plate

    def def_versions(self):               # for now just ignore the variants
        self.versions = {'No version': self.V_def               }

    def V_def(self):
        pass

    def __init__(self,
                 GUI                         = None,
                 num_of_samples: int           = 8,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name: str               = ""):

        this = Path(__file__).parent

        Evo200.__init__(self,
                        GUI                         = GUI,
                        num_of_samples              = num_of_samples or Tutorial_LL.max_s,
                        worktable_template_filename = worktable_template_filename or
                                                      this.parent / 'tutorial_HL' / 'tutorial_hl_dilution.ewt',
                        output_filename             = output_filename or this / 'scripts' / 'dilutions_LL',
                        firstTip                    = firstTip,
                        run_name                    = run_name)

    def Run(self):
        self.initialize()           # if needed calls Executable.initialize() and set_EvoMode
                                    # which calls GUI.update_parameters() and set_defaults() from Evo200

        self.show_runtime_check_list    = True

        n = self.num_of_samples
        assert 1 <= n <= Tutorial_LL.max_s , "In this demo we want to set dilutions in a 96 well plate."
        wt = self.worktable

        Itr.comment('Dilute 1:10 mix1 in {:d} wells.'.format(n)).exec()

        # Get Labwares (Cuvette, eppys, etc.) from the work table    -----------------------------------------------
        diluent_cuvette   = wt.get_labware(Lab.Trough_100ml, "BufferCub")
        assert isinstance(diluent_cuvette, Lab.Cuvette)

        mixes             = wt.get_labware(Lab.Eppendorfrack, "mixes")
        assert isinstance(mixes, Lab.Labware)

        vf = 100                                      # The final volume of every dilution, uL
        v  = vf /10                                   # uL to be distribute from original mix1 to each Dil_10
        vd = vf - v                                   # uL to be distribute from diluent to each Dil_10
        excess = 1.04                                 # 4%

        diluent = diluent_cuvette.Wells[0:8]          # Define the wells in each labware (Cuvette, eppys, etc.) ---
        diluent[0].vol = vd * n * excess              # set the initial volume needed - connected wells

        mix1     = mixes.Wells[0]                     # just one 1,5 mL tube
        mix1.vol = v * n * excess


        Itr.userPrompt("Put diluent in "+str(diluent[0]) ).exec()  # Show the check_list   -------------------------
        Itr.userPrompt("Put mix1 in " + str(mix1)).exec()

        Itr.wash_tips(wasteVol=5, FastWash=True).exec()

        plate = wt.get_labware(labw_type="96 Well Microplate", label="plate")
        assert isinstance(plate, Lab.Labware)

        dilution = plate.Wells[:n]                                 # Define place for temporal reactions  ----------

        with group("Fill dilutions"):

            Itr.userPrompt("Put the plate for dilutions in " + str(plate.location)).exec()

            arm = self.robot.curArm(Itr.Pipette.LiHa1)
            m_tips = arm.nTips

            n_tips = min(n, m_tips)                                                 # distribute mix1 --------------
            self.pick_up_tip(TIP_MASK = robot.tipsMask[n_tips],                       # using 200 uL tips
                             tip_type = "DiTi 200 ul",
                             arm      = arm)

            dil_left = n
            while dil_left:
                n_tips = min(dil_left, m_tips)
                maxMultiDisp_N = arm.Tips[0].type.maxVol // v
                dsp, rst = divmod(dil_left, n_tips)
                if dsp >= maxMultiDisp_N:
                    dsp = maxMultiDisp_N
                    vol = [v * dsp] * n_tips                                        # equal volume with each tips
                    availableDisp = dsp
                else:
                    vol = [v * (dsp + 1)] * rst + [v * dsp] * (n_tips - rst)
                    availableDisp = dsp + bool(rst)

                for tip in range(n_tips):
                    self.aspirate(arm=arm, TIP_MASK=robot.tipMask[tip], volume=vol, from_wells=mix1)

                while availableDisp:
                    n_tips = min(n_tips, dil_left)
                    curSample = n - dil_left
                    sel = dilution[curSample: curSample + n_tips]
                    self.dispense(arm      = arm,
                                  TIP_MASK = robot.tipsMask[n_tips],
                                  volume   = v,
                                  to_wells = sel)
                    availableDisp -= 1
                    dil_left -= n_tips

            self.drop_tip()

            n_tips = min(n, m_tips, len(diluent))                                    # distribute diluent ----------
            self.pick_up_tip(TIP_MASK = robot.tipsMask[n_tips],                        # using 1000 uL tips
                             tip_type = "DiTi 1000ul",
                             arm      = arm)

            dil_left = n
            while dil_left:
                n_tips = min(dil_left, m_tips, len(diluent))
                maxMultiDisp_N = arm.Tips[0].type.maxVol // vd
                dsp, rst = divmod(dil_left, n_tips)
                if dsp >= maxMultiDisp_N:
                    dsp = maxMultiDisp_N
                    vol = [vd * dsp] * n_tips       # equal volume with each tips
                    availableDisp = dsp
                else:
                    vol = [vd * (dsp + 1)] * rst + [vd * dsp] * (n_tips - rst)
                    availableDisp = dsp + bool(rst)

                self.aspirate(arm=arm, TIP_MASK=robot.tipsMask[n_tips], volume=vol, from_wells=diluent)

                while availableDisp:
                    n_tips = min(n_tips, dil_left)
                    curSample = n - dil_left
                    sel = dilution[curSample: curSample + n_tips]
                    self.dispense(arm      = arm,
                                  TIP_MASK = robot.tipsMask[n_tips],
                                  volume   = vd,
                                  to_wells = sel)
                    availableDisp -= 1
                    dil_left -= n_tips

            self.drop_tip()

        self.done()


if __name__ == "__main__":
    p = Tutorial_LL(num_of_samples= 42,
                    run_name        = "_42s")

    p.use_version('No version')
    p.Run()
