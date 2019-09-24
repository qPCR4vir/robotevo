# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019


"""
Principal API: Protocol steps
=======================================

All these functions are member of the base class :py:class:`Protocol`, from which all user protocols are derived.

High level functions:
^^^^^^^^^^^^^^^^^^^^

These are the functions you will use in "every day" protocol programming.
They allow you to specify the kind of tips to use and them command the operations you need on your reagents,
samples, reactions, etc., almost directly as it states in the steps of your "hand written" original laboratory protocol.

  - :py:meth:`~Protocol.tips`: how to use tips during the involved instructions.
  - :py:meth:`~Protocol.distribute`: some volume of reagent into the wells of the target labware
  - :py:meth:`~Protocol.transfer`: from some wells into equal number of target wells
  - :py:meth:`~Protocol.mix`: mix by pipetting the content of wells
  - :py:meth:`~Protocol.mix_reagent`: mix every aliquot by pipetting
  - :py:meth:`~Protocol.make_pre_mix`
  - :py:meth:`~Protocol.get_tips`
  - :py:meth:`~Protocol.drop_tips`
  - :py:meth:`~Protocol.set_first_tip`
  - :py:meth:`~Protocol.check_reagents_levels`
  - :py:meth:`~Protocol.check_reagent_level`
  - :py:meth:`~Protocol.show_check_list`
  - :py:meth:`~Protocol.comment`
  - :py:meth:`~Protocol.user_prompt`


Advanced functions.
^^^^^^^^^^^^^^^^^^

Are you doing some advanced protocol development that cannot be efficiently or clearly expressed
using the previous High level functions? Then, you may use the following functions.

Atomic functions
-----------------------------------------------------------

These are functions aimed to isolate what a physical robot would make at once: pick some tips,
aspirate some liquid, etc.
They are simple to understand, but are harder to use in "every day" protocol programming.
They may be a great tool to set up your robot and to get an initial familiarization with all the system.
Keep in mind that it is now your responsibility to know what robot/protocol "state" are ignored by these new functions.
For example, before `aspirate` you will need to mount "by yourself" the tips in the correct position of the used arm,
because `aspirate` ignores the higher level with :py:meth:`~Protocol.tips`.
But don't worry, **RobotEvo** still keeps track of the "internal" robot state and will throw errors
informing you about most logical mistakes
(like in the previous example forgetting to mount the tips).
In some cases these functions may be used to construct new high lever functions.

  - :py:meth:`~Protocol.pick_up_tip`
  - :py:meth:`~Protocol.drop_tip`
  - :py:meth:`~Protocol.aspirate`
  - :py:meth:`~Protocol.dispense`


Protocol-structure or state functions
-----------------------------------------------------------

Related to initialization:

  - :py:meth:`~Executable.def_versions`
  - :py:meth:`~Executable.set_paths`
  - :py:meth:`~Executable.init_EvoMode`
  - :py:meth:`~Executable.set_defaults`
  - :py:meth:`~Protocol.liquid_classes`
  - :py:meth:`~Protocol.carrier_types`
  - :py:meth:`~Protocol.allow_labware`
  - :py:meth:`~Protocol.labware_types`


Related to execution order:

  - :py:meth:`~Executable.use_version`
  - :py:meth:`~Executable.initialize`
  - :py:meth:`~Executable.run`
  - :py:meth:`~Executable.pre_check`
  - :py:meth:`~Executable.check_list`
  - :py:meth:`~Executable.post_check`
  - :py:meth:`~Executable.done`


Related to state:

  - :py:meth:`~Protocol.get_liquid_class`
  - :py:meth:`~Protocol.get_carrier_type`
  - :py:meth:`~Protocol.get_labware_type`
  - :py:meth:`~Protocol.set_EvoMode`
  - :py:meth:`~Protocol.set_drop_tips`
  - :py:meth:`~Protocol.set_allow_air`
  - :py:meth:`~Protocol.reuse_tips`
  - :py:meth:`~Protocol.reuse_tips_and_drop`
  - :py:meth:`~Protocol.preserve_tips`
  - :py:meth:`~Protocol.preserveing_tips`
  - :py:meth:`~Protocol.use_preserved_tips`


Other intermediate level functions:
--------------------------

  - :py:meth:`~Protocol.aspirate_one`
  - :py:meth:`~Protocol.dispense_one`
  - :py:meth:`~Protocol._dispensemultiwells`
  - :py:meth:`~Protocol._aspirate_multi_tips`
  - :py:meth:`~Protocol._multidispense_in_replicas`
  - :py:meth:`~Protocol.comments`

-----------------------------------------


"""

__author__ = 'qPCR4vir'


from pathlib import Path
from contextlib import contextmanager
import logging

import EvoScriPy.robot as robot
import EvoScriPy.instructions as instructions
from EvoScriPy.reagent import Reagent, preMix
import EvoScriPy.labware as labware
import EvoScriPy.evo_mode as mode

base_dir = Path(__file__).parent.parent


def not_implemented():
    logging.error('This protocols have yet to be implemented.')


# output_filename = '../current/AWL'
class Executable:
    """
    Each executable will need to implement these methods.

    """

    # parameters to describe this program
    name = "undefined"

    def def_versions(self):
        """
        Override this  function to define a 'dictionary' of the versions for your Executable,
        with a name as key and a method as value,
        which will initialize the Executable to effectively execute that version.
        You don't need to call this function. It will be used internally during initialization of your
        derived class.
        """
        self.versions = {"none": not_implemented}

    def use_version(self, version: str):
        """
        Select the version to be execute

        :param str version: the name of the desired version
        """
        assert version in self.versions, \
            version + " is not a valid version. Valid versions are: " + str(self.versions.keys())
        self.version = version
        self.versions[version]()

    def __init__(self, GUI=None, run_name=None):

        self.GUI         = GUI
        self.run_name    = run_name
        self.pipeline    = None
        self.initialized = False
        self.reagents    = []
        self.versions    = {"none": not_implemented}
        self.def_versions()
        self.version     = next(iter(self.versions))

        self.set_paths()
        Reagent.set_reagent_list(self)

    def set_paths(self):
        # todo: make private
        self.root_directory = Path(__file__).parent

    def set_defaults(self):
        """
        Set initial values that will not be rest during secondary initializations.
        The "primary initialization" maybe a light one, like defining the list of versions available.
        Here, for example, initialize the list of reagents.
        # todo: make private
        """
        logging.debug('set def in Executable')

    def initialize(self):
        """
        It is called "just in case" to ensure we don't go uninitialized in lazy initializing scenarios.
        """
        if not self.initialized:
            if self.GUI:
                self.GUI.update_parameters()
            self.initialized = True
            self.set_defaults()

    def run(self):
        """
        Here we have accesses to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with get_labware().
        Overwrite this function and dont call this basic function. This basic function is provided only as an example
        of "boiled-plate" code

        """

        self.initialize()
        self.pre_check()
        self.check_list()
        self.post_check()
        self.done()

    def pre_check(self):
        pass

    def check_list(self):
        pass

    def post_check(self):
        pass

    def done(self):
        pass


class Protocol (Executable):
    """
    Base class from which each custom protocol need to be derived, directly
    or from one of already derived. For example from the already adapted to some
    generic type robot like Evo200 or from an even more especially adapted like Evo100_FLI.
    Each newly derived protocol have to optionally override some of the following functions,
    especially .run().

    - High level API:
    - App-Structure API:
    - Context-options modifiers:
    - Lower lever API & "private" functions:
    - Atomic API:

    """
    name = ""
    min_s, max_s = 1, 96

    def __init__(self,
                 n_tips                      = 4,
                 num_of_samples              = max_s,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 first_tip                   = None,
                 run_name                    = None,
                 tips_type                   = None):
        """

        :param n_tips:
        :param num_of_samples:
        :param GUI:
        :param worktable_template_filename:
        :param output_filename:
        :param first_tip:
        :param run_name:
        :param tips_type:
        """
        evo_scripts = Path(__file__).parent.parent / 'EvoScripts' / 'scripts'
        output = output_filename or evo_scripts
        assert isinstance(output, Path)
        output_filename = output.parent / (output.name + (run_name or ""))

        self.worktable_template_filename = worktable_template_filename or ""
        self.carrier_file                = None
        self.output_filename             = output_filename
        self.first_tip                    = first_tip
        self.n_tips                      = n_tips
        self.EvoMode                     = None      # mode.multiple
        self.iRobot                      = None      # mode.iRobot
        self.Script                      = None      # mode.Script
        self.comments_                   = None      # mode.Comments
        self.worktable                   = None
        self.robot                       = None
        self.num_of_samples              = int(num_of_samples or Protocol.max_s)
        self.check_initial_liquid_level  = False
        self.def_DiTi_check_liquid_level = None
        self.show_runtime_check_list     = False
        self.tips_type                   = tips_type

        Reagent.set_reagent_list(self)

        Executable.__init__(self, GUI=GUI, run_name=run_name)

    # -------------------------------------------------------- High level API ------------------------------------------

    @contextmanager
    def tips(self,
             tips_mask   = None, tip_type      = None,
             reuse       = None, drop          = None,
             preserve    = None, use_preserved = None,
             drop_first  =False, drop_last     = False,
             allow_air   = None, selected_samples: labware.Labware  = None):
        """
        A contextmanager function which will manage how tips will be used during execution of the dependant instructions

        :param tips_mask:
        :param tip_type:         the type of the tips to be used
        :param bool reuse:       Reuse the tips already mounted? or drop and take new BEFORE each individual action
        :param bool drop:        Drops the tips AFTER each individual action?
                                 like after one aspiration and distribute of the reagent into various targets
        :param bool preserve:    puts the tip back into a free place in some rack of the same type
        :param use_preserved:    pick the tips back from the previously preserved
        :param selected_samples:
        :param allow_air:
        :param bool drop_first:  Reuse the tips or drop it and take new once BEFORE the whole action
        :param bool drop_last:   Drops the tips at THE END of the whole action

        """

        if selected_samples is not None:
            assert isinstance(selected_samples, labware.Labware)      # todo set some current?

        if drop_first:
            droping = self.set_drop_tips(True)
            self.drop_tips()
            self.set_drop_tips(droping)

        if reuse         is not None: reuse_old          = self.reuse_tips       (reuse)
        if drop          is not None: drop_old           = self.set_drop_tips    (drop)
        if preserve      is not None: preserve_old       = self.preserve_tips    (preserve)
        if use_preserved is not None: use_preserved_old  = self.use_preserved_tips(use_preserved)
        if allow_air     is not None: allow_air_old      = self.set_allow_air    (allow_air)
        if tip_type      is not None: tip_type_old       = self.worktable.set_def_DiTi(tip_type)

        if tips_mask     is not None:
            tips_mask_old = self.get_tips(tips_mask, selected_samples=selected_samples, tip_type=tip_type)

        yield

        if tips_mask     is not None: tips_mask     = self.drop_tips        (tips_mask_old)
        if tip_type      is not None: tip_type      = self.worktable.set_def_DiTi(tip_type_old)
        if reuse         is not None: reuse         = self.reuse_tips       (reuse_old)
        if drop          is not None: drop          = self.set_drop_tips    (drop_old)
        if preserve      is not None: preserve      = self.preserve_tips    (preserve_old)
        if use_preserved is not None: use_preserved = self.use_preserved_tips(use_preserved_old)
        if allow_air     is not None: allow_air     = self.set_allow_air    (allow_air_old)
        if drop_last:
            droping = self.set_drop_tips(True)
            self.drop_tips()
            self.set_drop_tips(droping)

    def distribute(self,
                   volume            : float        = None,
                   reagent           : Reagent      = None,
                   to_labware_region : labware.Labware  = None,
                   optimize          : bool         = True,
                   num_samples       : int          = None,
                   using_liquid_class: (str, tuple) = None,
                   TIP_MASK          : int          = None,        # todo ?? introduce use of this.
                   num_tips          : int          = None):
        """



        :param volume:            if not, volume is set from the default of the source reagent
        :param reagent:           Reagent to distribute
        :param to_labware_region: Labware in which the destine well are selected
        :param optimize:          minimize zigzag of multi pipetting
        :param num_samples:        Priorized   !!!! If true reset the selection
        :param using_liquid_class:
        :param TIP_MASK:
        :param num_tips:          the number of tips to be used in each cycle of pipetting = all

        To distribute a reagent into some wells.
        This is a high level function with works with the concept of "reagent". This a a concept introduced by
        RobotEvo that don't exist in EVOware and other similar software. It encapsulated the name, wells occupied by
        each of the aliquots of the reagent, the volume corresponding to one sample (if any) and the current volume
        in each aliquot. This function can use multiple of those aliquots to distribute the reagent to the target
        wells using multiple tips (the maximum will be used if `num_tips` is not set).

        By default a number of wells equal to the number of samples set in the protocol will be auto selected in the
        target labware `to_labware_region`, but this selection can be set explicitly (setting `well.selFlag=True`,
        for example by calling `to_labware_region.selectOnly(self, sel_idx_list)`). If `num_samples` is set
        it will rewrite (reset) the selected wells in the target `to_labware_region`.

        Please, carefully indicate whether to use "parallel optimization" in the pipetting order
        by setting `optimize`. (very important unless you are using a full column
        pipetting arm). Check that the created script don't have conflicts in
        the order of the samples and the "geometry" of the labware areas (selection of wells)
        during each pipetting step. This is ease to "see" in the EVOware visual script editor. The generated
        .protocol.txt can also be used to check this. RobotEvo will detect
        some errors, but currently not all, assuming the areas are relatively "regular".

        The same volume will be transfer to each well. It will be dispensed in only one pass: muss fit
        into the current tips
        If the liquid classes (LC) to be used are not explicitly passed the default LC of the reagent
        will be used. The generated .esc and .gwl can also be used to check this.

        A human readable comment will be automatically added to the script with the details of this operation.

        """
        assert isinstance(reagent, Reagent), 'A Reagent expected in reagent to distribute'
        assert isinstance(to_labware_region, labware.Labware), 'A Labware expected in to_labware_region to distribute'

        # todo allow wellselection here
        # allow tip mask continue y calcule num of tips

        if num_tips is None:
            num_tips = self.robot.cur_arm().n_tips  # the number of tips to be used in each cycle of pipetting = all

        if num_samples:
            to_labware_region.selectOnly(range(num_samples))
        else:
            if not to_labware_region.selected():
                to_labware_region.selectOnly(range(self.num_of_samples))

        to = to_labware_region.selected()        # list of offset of selected wells
        if optimize:
            to = to_labware_region.parallelOrder(num_tips, to)

        num_samples = len(to)
        sample_cnt = num_samples

        volume = volume or reagent.volpersample

        asp_liquid_class, dst_liquid_class = (reagent.def_liq_class, reagent.def_liq_class) if using_liquid_class is None else \
                                  (using_liquid_class[0] or reagent.def_liq_class, using_liquid_class[1] or reagent.def_liq_class)

        lf = reagent.labware
        lt = to_labware_region
        msg = "Distribute: {v:.1f} µL of {n:s}".format(v=volume, n=reagent.name)
        with group(msg):
            msg += " ({v:.1f} µL total) from [grid:{fg:d} site:{fs:d} {fw:s} " \
                   "into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                        .format(v  = reagent.min_vol(),
                                fg = lf.location.grid,
                                fs = lf.location.site+1,
                                fw = str([str(well) for well in reagent.Replicas]),
                                do = str([i+1 for i in to]),
                                to = lt.label,
                                tg = lt.location.grid,
                                ts = lt.location.site+1)
            instructions.comment(msg).exec()
            available_disp = 0
            while sample_cnt:
                num_tips = min(num_tips, sample_cnt)

                with self.tips(robot.mask_tips[num_tips], use_preserved=False, preserve=False):
                    # todo a function returning max vol in arm tips
                    max_multi_disp_n = self.robot.cur_arm().Tips[0].type.max_vol // volume  # assume all tips equal
                    assert max_multi_disp_n > 0
                    dsp, rst = divmod(sample_cnt, num_tips)
                    if dsp >= max_multi_disp_n:
                        dsp = max_multi_disp_n
                        vol = [volume * dsp] * num_tips
                        available_disp = dsp
                    else:
                        vol = [volume * (dsp + 1)] * rst + [volume * dsp] * (num_tips - rst)
                        available_disp = dsp + bool(rst)

                    self._aspirate_multi_tips(reagent, num_tips, vol, liq_class=asp_liquid_class)

                    while available_disp:

                        if num_tips > sample_cnt:
                            num_tips = sample_cnt

                        cur_sample = num_samples - sample_cnt
                        sel = to[cur_sample: cur_sample + num_tips]  # todo what if volume > maxVol_tip ?

                        self._dispensemultiwells(num_tips,
                                                 dst_liquid_class,
                                                 to_labware_region.selectOnly(sel),
                                                 [volume] * num_tips)
                        available_disp -= 1
                        sample_cnt -= num_tips

    def transfer(self,
                 from_labware_region: labware.Labware,  # todo take list of "samples"
                 to_labware_region  : labware.Labware,  # todo take list
                 volume             : (int, float),
                 using_liquid_class : (str, tuple)  = None,
                 optimize_from      : bool          = True,
                 optimize_to        : bool          = True,
                 num_samples        : int           = None) -> (labware.Labware, labware.Labware):
        """

        :param Labware from_labware_region:   Labware in which the source wells are located and possibly selected
        :param Labware to_labware_region:     Labware in which the target wells are located and possibly selected
        :param float volume:   if not, volume is set from the default of the source reagent
        :param using_liquid_class:    LC or tuple (LC to aspirate, LC to dispense)
        :param bool optimize_from:    use from_labware_region.parallelOrder() to aspirate?
        :param bool optimize_to:      use to_labware_region.parallelOrder() to aspirate?
        :param int num_samples:       Prioritized. If used reset the well selection
        :return: a tuple of the labwares used as origin and target with the involved wells selected.

        To transfer reagents (typically samples or intermediary reactions) from some wells in the source labware to
        the same number of wells in the target labware using the current LiHa arm with maximum number of tips
        (of type: `self.worktable.def_DiTi_type`,
        which can be set 'with self. :py:meth:`~Protocol.tips` (tip_type = myTipsRackType)').
        # todo: count for 'broken' tips

        The number of "samples" may be explicitly indicated in which case will be assumed to begin from the
        first well of the labware. Alternatively the wells in the source or target or in both may be
        previously directly "selected" (setting `well.selFlag=True`, for example by calling
        `from_labware_region.selectOnly(self, sel_idx_list)`), in which case transfer the minimum length selected.
        If no source wells are selected this function will auto select the protocol's `self.num_of_samples` number
        of wells in the source and target labwares.
        Please, carefully indicate whether to use "parallel optimization" in the pipetting order for both source and
        target by setting `optimizeFrom` and `optimizeTo`. (very important unless you are using a full column
        pipetting arm). Check that the created script don't have conflicts in
        the order of the samples and the "geometry" of the labware areas (selection of wells)
        during each pipetting step. This is ease to "see" in the EVOware visual script editor. The generated
        .protocol.txt can also be used to check this. RobotEvo will detect
        some errors, but currently not all, assuming the areas are relatively "regular".

        The same volume will be transfer from each well. It will be aspirated/dispensed in only one pass: muss fit
        into the current tips
        todo ?! If no `volume` is indicated then the volume expected to be in the first selected well will be used.

        If the liquid classes (LC) to be used are not explicitly passed the default LC in the first well of the current
        pipetting step will be used. The generated .esc and .gwl can also be used to check this.

        A human readable comment will be automatically added to the script with the details of this operation.

        Warning: modify the selection of wells in both source and target labware to reflect the wells actually used


        """
        assert isinstance(from_labware_region, labware.Labware), 'Labware expected in from_labware_region to transfer'
        assert isinstance(to_labware_region,   labware.Labware), 'Labware expected in to_labware_region to transfer'
        # assert isinstance(using_liquid_class, tuple)
        nt = self.robot.cur_arm().n_tips                  # the number of tips to be used in each cycle of pippeting

        if num_samples:                                  # select convenient def
            ori_sel = range(num_samples)
            dst_sel = range(num_samples)
        else:
            ori_sel = from_labware_region.selected()
            dst_sel = to_labware_region.selected()

            if not dst_sel:
                if not ori_sel:
                    ori_sel = range(self.num_of_samples)
                    dst_sel = range(self.num_of_samples)
                else:
                    dst_sel = ori_sel  # todo ??
            else:
                if not ori_sel:
                    ori_sel = dst_sel  # todo ??
                else:
                    n_wells = min(len(ori_sel), len(dst_sel))   # transfer the minimum of the selected
                    ori_sel = ori_sel[:n_wells]                 # todo Best reise an error ??
                    dst_sel = dst_sel[:n_wells]

        if optimize_from: ori_sel = from_labware_region.parallelOrder(nt, ori_sel)   # a list of well offset s
        if optimize_to  : dst_sel = to_labware_region.parallelOrder  (nt, dst_sel)

        num_samples = len(dst_sel)
        sample_cnt = num_samples

        assert isinstance(volume, (int, float))

        # todo revise !!!
        assert 0 < volume <= self.worktable.def_DiTi_type.max_vol, \
            "Invalid volumen to transfer ("+str(volume)+") with tips " + self.worktable.def_DiTi_type

        nt = min(sample_cnt, nt)
        lf = from_labware_region
        lt = to_labware_region

        asp = instructions.aspirate(robot.mask_tips[nt], volume=volume, labware=from_labware_region)
        dst = instructions.dispense(robot.mask_tips[nt], volume=volume, labware=to_labware_region)
        msg = "Transfer: {v:.1f} µL from {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += " [grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg =lf.location.grid,
                        fs =lf.location.site+1,
                        oo =str([i+1 for i in ori_sel]),
                        do =str([i+1 for i in dst_sel]),
                        to =lt.label,
                        tg =lt.location.grid,
                        ts =lt.location.site+1)
            instructions.comment(msg).exec()
            while sample_cnt:                                # loop wells (samples)
                cur_sample = num_samples - sample_cnt
                if nt > sample_cnt:                          # only a few samples left
                    nt = sample_cnt                          # don't use all tips
                    tm = robot.mask_tips[nt]                   # todo count for broken tips
                    asp.tipMask = tm
                    dst.tipMask = tm

                src = ori_sel[cur_sample:cur_sample + nt]      # only the next nt wells
                trg = dst_sel[cur_sample:cur_sample + nt]
                spl = range(cur_sample, cur_sample + nt)

                sw = asp.labware.selected_wells()

                if isinstance(using_liquid_class, tuple):
                    if using_liquid_class[0]:
                        asp.liquidClass = using_liquid_class[0]
                    else:
                        asp.liquidClass = sw[0].reagent.def_liq_class
                    if using_liquid_class[1]:
                        dst.liquidClass = using_liquid_class[1]
                    else:
                        dst.liquidClass = sw[0].reagent.def_liq_class
                else:
                    asp.liquidClass = sw[0].reagent.def_liq_class
                    dst.liquidClass = sw[0].reagent.def_liq_class

                asp.labware.selectOnly(src)
                dst.labware.selectOnly(trg)
                with self.tips(robot.mask_tips[nt], selected_samples=asp.labware):  # todo what if volume > maxVol_tip ?
                    asp.exec()                                           # <---- low level aspirate
                    dst.exec()                                           # <---- low level dispense
                    for s, d in zip(asp.labware.selected_wells(), dst.labware.selected_wells()):
                        d.track = s                                     # todo revise !! and .actions []
                        d.actions += s.actions                          # ????
                sample_cnt -= nt
        asp.labware.selectOnly(ori_sel)
        dst.labware.selectOnly(dst_sel)
        return ori_sel, dst_sel

    def aspirate_one(self, tip, reagent, vol=None, offset = None):
        """
        Aspirate vol with ONE tip from reagent

        :param self:
        :param tip:
        :param reagent:
        :param vol:
        :param offset:
        """
        if vol is None:
            vol = reagent.min_vol()    # todo: revise !!

        v = [0] * self.robot.cur_arm().n_tips
        v[tip] = vol
        reagent.autoselect(offset = offset)                                         # reagent.labware.selectOnly([reagent.pos])
        instructions.aspirate(robot.mask_tip[tip], reagent.def_liq_class, v, reagent.labware).exec()

    def dispense_one(self, tip, reagent, vol=None):                     # OK coordinate with robot
        """
        Dispense vol with ONE tip to reagent

        :param tip:
        :param reagent:
        :param vol:
        """
        vol = vol or reagent.min_vol()                                # really ??   # todo: revise !!
        reagent.autoselect()                                         # reagent.labware.selectOnly([reagent.pos])
        v = [0] * self.robot.cur_arm().n_tips
        v[tip] = vol
        instructions.dispense(robot.mask_tip[tip], reagent.def_liq_class, v, reagent.labware).exec()

    def mix(self,
            in_labware_region : labware.Labware,
            using_liquid_class: str        = None,
            volume            : float      = None,
            optimize          : bool       = True):

        """
        Mix the reagents in each of the wells selected `in_labware_region`, `using_liquid_class` and `volume`

        :param in_labware_region:
        :param using_liquid_class:
        :param volume:
        :param optimize:
        """
        mix_p = 0.9
        in_labware_region = in_labware_region or self.worktable.def_WashWaste    # todo ???????????
        assert isinstance(in_labware_region, labware.Labware), 'A Labware expected in in_labware_region to be mixed'
        if not volume or volume < 0.0:
            volume = 0.0
        assert isinstance(volume, (int, float))
        ori_sel = in_labware_region.selected()
        nt = self.robot.cur_arm().n_tips  # the number of tips to be used in each cycle of pippeting
        if not ori_sel:
            ori_sel = range(self.num_of_samples)
        if optimize:
            ori_sel = in_labware_region.parallelOrder(nt, ori_sel)
        num_samples = len(ori_sel)
        sample_cnt = num_samples
        if nt > sample_cnt:
            nt = sample_cnt
        # mV = robot.Robot.current.cur_arm().Tips[0].type.max_vol * 0.8
        max_vol = self.worktable.def_DiTi_type.max_vol * mix_p    # What tip tp use !
        if volume:
            v = volume
        else:
            v = in_labware_region.Wells[ori_sel[0]].vol
        v = v * mix_p
        v = v if v < max_vol else max_vol

        lf = in_labware_region
        mx = instructions.mix(robot.mask_tips[nt], using_liquid_class, volume, in_labware_region)
        msg = "Mix: {v:.1f} µL of {n:s}".format(v=v, n=lf.label)
        with group(msg):
            msg += " [grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) \
                                        + str([i+1 for i in ori_sel])
            instructions.comment(msg).exec()
            while sample_cnt:
                cur_sample = num_samples - sample_cnt
                if nt > sample_cnt:
                    nt = sample_cnt
                    mx.tipMask = robot.mask_tips[nt]

                sel = ori_sel[cur_sample:cur_sample + nt]
                mx.labware.selectOnly(sel)
                with self.tips(robot.mask_tips[nt], selected_samples = mx.labware):
                    max_vol = self.robot.cur_arm().Tips[0].type.max_vol * mix_p
                    if not using_liquid_class:
                        if sel:
                            mx.liquidClass = mx.labware.selected_wells()[0].reagent.def_liq_class
                    if volume:
                        r = volume   # r: Waste_available yet; volume: to be Waste
                    else:
                        vols = [w.vol for w in mx.labware.selected_wells()]
                        r_min, r_max = min(vols), max(vols)
                        assert r_min == r_max
                        r = r_max
                    r = r * mix_p
                    r = r if r < max_vol else max_vol
                    mx.volume = r
                    mx.exec()
                sample_cnt -= nt
        mx.labware.selectOnly(ori_sel)
        return ori_sel

    def mix_reagent(self,
                    reagent  : Reagent,
                    liq_class: str  = None,
                    cycles   : int  = 3,
                    maxTips  : int  = 1,
                    v_perc   : int  = 90):
        """
        Select all possible replica of the given reagent and mix using the given % of the current vol in EACH well
        or the max vol for the tip. Use the given "liquid class" or the reagent default.

        :param reagent:
        :param liq_class:
        :param cycles:
        :param maxTips:
        :param v_perc:  % of the current vol in EACH well to mix
        """
        assert isinstance(reagent, Reagent)
        liq_class = liq_class or reagent.def_liq_class
        v_perc /= 100.0
        vol = []
        reagent.autoselect(maxTips)
        for tip, w in enumerate(reagent.labware.selected_wells()):
            v = w.vol * v_perc
            vm = self.robot.cur_arm().Tips[tip].type.max_vol * 0.9
            vol += [min(v, vm)]

        instructions.mix(robot.mask_tips[len(vol)],
                         liquidClass =liq_class,
                         volume      =vol,
                         labware     =reagent.labware,
                         cycles      =cycles).exec()

    def make_pre_mix(self,
                     pre_mix: preMix,
                     num_samples: int = None,
                     force_replies: bool = False):
        """
        A preMix is just that: a premix of reagents (aka - components)
        which have been already defined to add some vol per sample.
        Uses one new tip per component.
        It calculates and checks self the minimum and maximum number of replica of the resulting preMix

        :param preMix pre_mix: what to make, a predefined preMix
        :param int num_samples:
        :param bool force_replies: use all the preMix predefined replicas

        """

        assert isinstance(pre_mix, preMix)
        mxn_tips    = self.robot.cur_arm().n_tips  # max number of Tips
        ncomp       = len(pre_mix.components)
        nt          = min(mxn_tips, ncomp)
        num_samples = num_samples or self.num_of_samples
        labw        = pre_mix.labware
        t_vol       = pre_mix.min_vol(num_samples)
        mxnrepl     = len(pre_mix.Replicas)                        # max number of replies
        mnnrepl     = pre_mix.min_num_of_replica(num_samples)       # min number of replies
        assert mxnrepl >= mnnrepl, 'Please choose at least {:d} replies for {:s}'.format(mnnrepl, pre_mix.name)
        nrepl       = mxnrepl if force_replies else mnnrepl
        if nrepl < mxnrepl:
            logging.warning("The last {:d} replies of {:s} will not be used.".format(mxnrepl - nrepl, pre_mix.name))
            pre_mix.Replicas = pre_mix.Replicas[:nrepl]

        msg = "preMix: {:.1f} µL of {:s}".format(t_vol, pre_mix.name)
        with group(msg):
            msg += " into grid:{:d} site:{:d} {:s} from {:d} components:"\
                                .format(labw.location.grid,
                                        labw.location.site + 1,
                                        str([str(well) for well in pre_mix.Replicas]),
                                        ncomp)
            instructions.comment(msg).exec()
            samples_per_replicas = [(num_samples + nrepl - (ridx + 1)) // nrepl for ridx in range(nrepl)]
            with self.tips(robot.mask_tips[nt]):   # want to use preserved ?? selected=??
                tip = -1
                ctips = nt
                for ridx, reagent_component in enumerate(pre_mix.components):       # iterate reagent components
                    labw = reagent_component.labware
                    v_per_sample = reagent_component.volpersample * pre_mix.excess       # vol we need for each sample
                    reagent_vol = v_per_sample * num_samples                 # the total vol we need of this reagent component
                    msg = "   {idx:d}- {v:.1f} µL from grid:{g:d} site:{st:d}:{w:s}"\
                                 .format(idx = ridx + 1,
                                         v   = reagent_vol,
                                         g   = labw.location.grid,
                                         st  = labw.location.site + 1,
                                         w   = str([str(well) for well in reagent_component.Replicas]))
                    instructions.comment(msg).exec()
                    tip += 1  # use the next tip
                    if tip >= nt:
                        ctips = min(nt, ncomp - ridx)                    # how many tips to use for the next gruop
                        tips_type = self.robot.cur_arm().Tips[0].type    # only the 0 ??
                        self.drop_tips(robot.mask_tips[ctips])
                        self.get_tips(robot.mask_tips[ctips], tips_type)
                        tip = 0
                    max_vol = self.robot.cur_arm().Tips[tip].type.max_vol
                    # aspirate/dispense multiple times if rVol don't fit in the tip (mV)
                    # but also if there is not sufficient reacgent in the current component replica
                    current_comp_repl = 0
                    while reagent_vol > 0:
                        while reagent_component.Replicas[current_comp_repl].vol < 1:      # todo define min vol
                            current_comp_repl += 1
                        d_v = min(reagent_vol, max_vol, reagent_component.Replicas[current_comp_repl].vol)

                        self.aspirate_one(tip,
                                          reagent_component,
                                          d_v,
                                          offset=reagent_component.Replicas[current_comp_repl].offset)

                        self._multidispense_in_replicas(ridx, pre_mix, [sp / num_samples * d_v for sp in samples_per_replicas])
                        reagent_vol -= d_v
                self.mix_reagent(pre_mix, maxTips=ctips)

    def get_tips(self,
                 TIP_MASK         = None,
                 tip_type         = None,
                 selected_samples = None):
        """
        It will decide to get new tips or to pick back the preserved tips for the selected samples

        :param TIP_MASK:
        :param tip_type:
        :param selected_samples:
        :return: the TIP_MASK used
        """
        if self.robot.cur_arm().tips_type == self.robot.cur_arm().Fixed:          # todo call protocol wash ??
            return TIP_MASK

        mask = TIP_MASK = TIP_MASK if TIP_MASK is not None else robot.mask_tips[self.robot.cur_arm().n_tips]

        if self.robot.usePreservedtips:
            with self.tips(drop=True, preserve=False):    # drop tips from previous "buffer" in first pipetting
                self.drop_tips(TIP_MASK)
            where = self.robot.where_are_preserved_tips(selected_samples, TIP_MASK, tip_type)
            n_tips = self.robot.cur_arm().n_tips

            for tip_rack in where:
                instr_mask = 0
                tips_in_rack = len(tip_rack.selected())
                for idx in range(n_tips):
                    if not tips_in_rack:
                        break
                    tip = (1 << idx)
                    if TIP_MASK & tip:
                        instr_mask |= tip
                        TIP_MASK ^= tip
                        tips_in_rack -= 1
                instructions.pickUp_DITIs2(instr_mask, tip_rack).exec()
            assert tips_in_rack == 0
        else:
            tip_type = tip_type or self.worktable.def_DiTi_type
            instructions.getDITI2(TIP_MASK, tip_type, arm=self.robot.def_arm).exec()
        return mask                                    # todo REVISE !!   I.mask_tip?

    def drop_tips(self, TIP_MASK=None):
        """
        It will decide to really drop the tips or to put it back in some DiTi rack

        :param TIP_MASK:
        """
        if self.robot.preservetips:
            where = self.robot.where_preserve_tips(TIP_MASK)
            n_tips = self.robot.cur_arm().n_tips
            for tip_rack in where:
                tips_mask = 0
                tips_in_rack = len(tip_rack.selected())
                assert tips_in_rack, "A rack with no selected tip-wells was returned from robot.where_preserve_tips(TIP_MASK)"

                for i in range(n_tips):
                    if not tips_in_rack:
                        break
                    b = (1 << i)
                    if TIP_MASK & b:
                        tips_mask |= b
                        TIP_MASK ^= b
                        tips_in_rack -= 1

                instructions.set_DITIs_Back(tips_mask, tip_rack).exec()
            assert tips_in_rack == 0
            return
        # if not robot.Robot.current.droptips: return 0
        # TIP_MASK = robot.Robot.current.cur_arm().drop(TIP_MASK)
        # if TIP_MASK:# todo is this a correct solution or it is best to do a double check? To force drop?

        instructions.dropDITI(TIP_MASK).exec()

        # return TIP_MASK

    def set_first_tip(self, first_tip: (int, str) = None, tip_type: (str, labware.DITIrackType) = None):
        """
        Optionally set the Protocol.first_tip, a position in rack, like 42 or 'B06'
        (optionally including the rack self referenced with a number, like '2-B06', were 2 will be the second
        rack in the worktable series of the default tip type). Currently, for a more precise set, use directly:

            instructions.set_DITI_Counter2(labware=rack, posInRack=first_tip).exec()

        """
        if first_tip is not None:
            self.first_tip = first_tip                                       # just keep it

        if self.first_tip is not None and self.worktable is not None:        # set in wt
            rack, first_tip = self.worktable.set_first_pos(posstr=self.first_tip, labw_type_name=tip_type)
            instructions.set_DITI_Counter2(labware=rack, posInRack=first_tip).exec()

    def consolidate(self):              # todo
        """
        Volumes going to the same destination well are combined within the same tip,
        so that multiple aspirates can be combined to a single dispense.
        If there are multiple destination wells, the pipette will never combine their volumes into the same tip.
        :return:
        """
        pass

    # App-Structure API ---------------------------------------------------------------------------------------
    def run(self):
        """
        Here we have accesses to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with get_labware()
        """
        self.set_EvoMode()

        self.initialize()
        self.set_EvoMode()

        self.pre_check()
        self.set_EvoMode()

        self.check_list()
        self.set_EvoMode()

        self.post_check()
        self.set_EvoMode()

        self.done()

    def check_list(self):
        """
        Tipically
        """
        self.set_EvoMode()
        if self.GUI:
            self.GUI.check_list()
        self.set_EvoMode()
        Reagent.set_reagent_list(self)
        if self.show_runtime_check_list:
            self.show_check_list()
        if self.check_initial_liquid_level:
            self.check_reagents_levels()

    def check_reagent_level(self, reagent, liq_class=None):
        """
        Select all possible replica of the given reagent and detect the liquid level,
        contrasting it with the current (expected) volumen in EACH well.
        Use the given liquid class or the reagent default.

        :param reagent:
        :param liq_class:

        """
        assert isinstance(reagent, Reagent)
        liq_class = liq_class or reagent.def_liq_class

        tips = 1 if isinstance(reagent.labware, labware.Cuvette) else self.robot.cur_arm().n_tips
        reagent.autoselect(tips)              # todo use even more tips? see self._aspirate_multi_tips
        vol = [w.vol for w in reagent.labware.selected_wells()]
        instructions.comment(f"Check: {str([str(well) for well in reagent.labware.selected_wells()]) }").exec()

        with self.tips(tip_type     = self.def_DiTi_check_liquid_level,
                       reuse        = False,
                       tips_mask= robot.mask_tips[len(vol)]):

            instructions.detect_Liquid(robot.mask_tips[len(vol)],
                                       liquidClass =liq_class,
                                       labware     =reagent.labware).exec()

        instructions.userPrompt("").exec()

    def check_reagents_levels(self):
        """
        Will emit a liquid level detection on every well occupied by all the reagents defined so fort.
        Will be executed at the end of self.check_list() but only if self.check_initial_liquid_level is True
        """
        for reagent in self.worktable.reagents.values():
            if reagent.include_in_check:
                reagent_msg = f"Check {reagent.name}in {str([str(well) for well in reagent.Replicas])}"
                logging.info(reagent_msg)
                self.check_reagent_level(reagent)

    def show_check_list(self):
        """
        Will show a user prompt with a check list to set all defined reagents:
        Name, position in the worktable, wells and initial volume (on every well occupied by all
        the reagents defined so fort.
        Will be executed at the end of self.check_list() but only if self.show_runtime_check_list is True
        """
        prompt_msg = ""
        for reagent in self.worktable.reagents.values():
            if reagent.include_in_check:
                reagent_msg = f"Check {reagent.name} in {str([str(well) for well in reagent.Replicas])}"
                logging.info(reagent_msg)
                prompt_msg += reagent_msg + ""

        self.user_prompt(prompt_msg)

    def done(self):
        self.EvoMode.done()
        Executable.done(self)

    def set_paths(self):
        Executable.set_paths(self)
        self.root_directory = Path(__file__).parent

    def liquid_classes(self):
        return None

    def get_liquid_class(self, name:str):
        return self.liquid_classes().all[name]

    def carrier_types(self):
        return None

    def get_carrier_type(self, carrier:(str, int)):
        if isinstance(carrier, str):
            return self.carrier_types().by_name[carrier]
        return self.carrier_types().by_index[carrier]

    def allow_labware(self, carrier_type, labwares, widht_in_grids = None):
        carrier_t = self.get_carrier_type(carrier_type)
        if isinstance(labwares, list):
            carrier_t.allowed_labwares_types.extend(labwares)
        else:
            carrier_t.allowed_labwares_types.append(labwares)
        if widht_in_grids is not None:
            carrier_t.widht_in_grids = widht_in_grids

    def labware_types(self):
        return None

    def get_labware_type(self, name:str):
        return self.labware_types().all[name]

    def initialize(self):
        self.liquid_classes()
        self.carrier_types()
        self.labware_types()
        self.set_EvoMode()
        if not self.initialized:
            Executable.initialize(self)
        Reagent.set_reagent_list(self)
        if self.def_DiTi_check_liquid_level is None:
            self.def_DiTi_check_liquid_level = self.worktable.def_DiTi_type

    def set_defaults(self):
        # wt = self.worktable
        pass

    def set_EvoMode(self):
        if not self.EvoMode:
            self.init_EvoMode()
        else:
            mode.current = self.EvoMode
        self.iRobot.set_as_current()
        Reagent.set_reagent_list(self)

    def init_EvoMode(self):
        logging.debug("Setting Evo Modes")

        script_dir = self.output_filename.parent
        script_name = self.output_filename.name
        script = script_dir / (script_name + '.esc')
        assert isinstance(script, Path)

        self.iRobot = mode.iRobot(instructions.Pipette.LiHa1, tips_type=self.tips_type, n_tips=self.n_tips)
        self.Script = mode.Script(template       = self.worktable_template_filename,
                                  robot_protocol = self,
                                  filename       = script,
                                  robot          = self.iRobot.robot)
        self.comments_ = mode.Comments(filename= script.with_suffix('.protocol.txt'))

        self.EvoMode = mode.Multiple([self.Script,
                                      mode.AdvancedWorkList(script.with_suffix('.gwl')),
                                      mode.ScriptBody(script.with_suffix('.txt')),
                                      mode.StdOut(),
                                      self.comments_,
                                      self.iRobot ])
        mode.current = self.EvoMode
        self.worktable  = self.iRobot.robot.worktable  # shortcut !!
        self.robot      = self.iRobot.robot
        self.robot.liquid_clases = self.liquid_classes()
        assert (self.iRobot.robot.cur_arm().n_tips == self.n_tips)

    def comments(self):
        return self.comments_.comments

    # Context-options modifiers ---------------------------------------------------------------------------
    def set_drop_tips(self, drop=True)->bool:
        """
        Drops the tips at THE END of the whole action? like after distribution of a reagent into various targets
        :param drop:
        :return:
        """
        return self.robot.set_drop_tips(drop)

    def set_allow_air(self, allow_air=0.0)->float:
        return self.robot.set_allow_air(allow_air)

    def reuse_tips(self, reuse=True)->bool:
        """
        Reuse the tips or drop it and take new after each action?

        :param bool reuse:
        :return:
        """
        return self.robot.reuse_tips(reuse)

    def reuse_tips_and_drop(self, reuse=True, drop=True)->(bool, bool):
        return self.set_drop_tips(drop), self.reuse_tips(reuse)

    def preserve_tips(self, preserve=True)->bool:
        return self.robot.preserve_tips(preserve)

    def preserveing_tips(self)->bool:
        return self.robot.preservetips

    def use_preserved_tips(self, usePreserved=True)->bool:
        return self.robot.use_preserved_tips(usePreserved)

    def move_tips(self, z_move, z_target, offset, speed, TIP_MASK=None):
        pass # instructions.moveLiha

    # Lower lever API & "private" functions -------------------------------------------------------------
    def _multidispense_in_replicas(self, tip     : int,
                                         reagent : Reagent,
                                         vol     : list) :
        """ Multi-dispense of the content of ONE tip into the reagent replicas

        :param tip:
        :param reagent:
        :param vol:
        """
        assert isinstance(vol, list)
        re = reagent.Replicas
        assert len(vol) <= len(re)
        for v, w in zip(vol, re):                              # zip continues until the shortest iterable is exhausted
            instructions.dispense(robot.mask_tip[tip], self.robot.cur_arm().Tips[tip].origin.reagent.def_liq_class,
                                  # reagent.def_liq_class,
                                  v, w.labware.selectOnly([w.offset])).exec()

    def _aspirate_multi_tips(self, reagent  : Reagent,
                                   tips     : int           = None,
                                   vol      : (float, list) = None,
                                   liq_class: str           = None):
        """
        Intermediate-level function. Aspirate with multiple tips from multiple wells with different volume.
        Example: you want to aspirate 8 different volume of a reagent into 8 tips, but the reagent
        have only 3 replicas (only 3 wells contain the reagent). This call will generate the instructions to
        fill the tips 3 by 3 with the correct volume. Assumes the tips are mounted in the current arm.

        :param tips     : number of tips beginning from #1 to use
        :param reagent  : reagent to aspirate, with some number of wells in use
        :param vol:
        :param liq_class:
        """
        max_tips = self.robot.cur_arm().n_tips

        if isinstance(vol, list):
            if tips is None:
                tips = len(vol)
            else:
                assert tips == len(vol), f"Number of tips {tips} != number of desired volume ({len(vol)})."
        else:
            if tips is None:
                tips =max_tips

            vol = [vol] * tips

        assert tips <= max_tips, f"Too many tips selected: {tips}. The maximum is {max_tips}."

        liq_class = liq_class or reagent.def_liq_class

        mask = robot.mask_tips[tips]                                 # as if we could use so many tips
        n_wells = reagent.autoselect(tips)                           # the total number of available wells to aspirate from
        asp = instructions.aspirate(mask, liq_class, vol, reagent.labware)
        cur_tip = 0
        while cur_tip < tips:                                        # todo what to do with used tips?
            next_tip = cur_tip + n_wells                             # add tips, one for each well
            next_tip = next_tip if next_tip <= tips else tips        # but not too much
            mask = robot.mask_tips[cur_tip] ^ robot.mask_tips[next_tip]   # now use only the last tips added

            asp.tipMask = mask
            asp.exec()                                           # will call robot.cur_arm().aspirated(vol, mask)  ???
            cur_tip = next_tip

    def _dispensemultiwells(self, tips : int, liq_class, labware : labware.Labware, vol : (float, list)):
        """
        Intermediate-level function. One dispense from multiple tips in multiple wells with different volume

        :param tips: number of tips to use                        # todo ?
        :param liq_class:
        :param labware:
        :param vol:
        """
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = robot.mask_tips[tips]

        instructions.dispense(om, liq_class, vol, labware).exec()          # will call robot.cur_arm().dispensed(vol, om)  ??

    def make(self,  what, NumSamples=None): # OK coordinate with protocol
            if isinstance(what, preMix): self.make_pre_mix(what, NumSamples)

    # Atomic API ----------------------------------------------------------------------------------------
    def pick_up_tip(self, TIP_MASK     : int        = None,
                          tip_type     :(str, labware.DITIrackType, labware.DITIrack, labware.DITIrackTypeSeries)= None,
                          arm          : robot.Arm  = None,
                          airgap_volume: float      = 0,
                          airgap_speed : int        = None):
        """
        Atomic operation. Get new tips. It take a labware type or name instead of the labware itself (DiTi rack)
        because the real robot take track of the next position to pick, including the rack and the site (the labware).
        It only need a labware type (tip type) and it know where to pick the next tip. Example:

            self.pick_up_tip('DiTi 200 ul')  # will pick a 200 ul tip with every tip arm.

        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.mask_tip[index] and Robot.mask_tips[index])
        :param tip_type: if None the worktable default DiTi will be used.
        :param arm:      Uses the default Arm (pipette) if None
        :param airgap_speed:  int 1-1000. Speed for the airgap in μl/s
        :param airgap_volume: 0 - 100.  Airgap in μl which is aspirated after dropping the DITIs

        """

        # not needed here, just to illustrate how is processed
        DITI_series = self.robot.worktable.get_DITI_series(tip_type)

        instructions.getDITI2(TIP_MASK, DITI_series, arm=arm, AirgapVolume=airgap_volume, AirgapSpeed=airgap_speed).exec()

    def drop_tip(self,  TIP_MASK     : int             = None,
                        DITI_waste   : labware.Labware = None,
                        arm          : robot.Arm       = None,
                        airgap_volume: float           = 0,
                        airgap_speed : int             = None):
        """
        :param TIP_MASK:     Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                             If None all tips are used. (see Robot.mask_tip[index] and Robot.mask_tips[index])
        :param DITI_waste:   Specify the worktable position for the DITI waste you want to use.
                             You must first put a DITI waste in the Worktable at the required position.
        :param arm:          Uses the default Arm (pipette) if None
        :param airgap_speed:  int 1-1000. Speed for the airgap in μl/s
        :param airgap_volume: 0 - 100.  Airgap in μl which is aspirated after dropping the DITIs
        """
        instructions.dropDITI(TIP_MASK, labware=DITI_waste, AirgapVolume=airgap_volume, AirgapSpeed=airgap_speed, arm=arm).exec()

    def aspirate(self,   arm        : robot.Arm         = None,
                         TIP_MASK   : int               = None,
                         volume     : (float, list)     = None,
                         from_wells : [labware.Well]    = None,
                         liq_class  : str               = None):
        """
        Atomic operation. Use arm (pipette) with masked (selected) tips to aspirate volume from wells.
        :param arm:      Uses the default Arm (pipette) if None
        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.mask_tip[index] and Robot.mask_tips[index])
        :param volume:   One (the same) for each tip or a list specifying the volume for each tip.
        :param from_wells: list of wells to aspirate from.
        :param liq_class: the name of the Liquid class, as it appears in your own EVOware database.
                          instructions.def_liquidClass if None
        """

        instructions.aspirate(arm=arm, tipMask=TIP_MASK, liquidClass=liq_class, volume=volume, wellSelection=from_wells).exec()

    def dispense(self,
                 arm        : robot.Arm         = None,
                 TIP_MASK   : int               = None,
                 volume     : (float, list)     = None,
                 to_wells   : [labware.Well]    = None,
                 liq_class  : str               = None):
        """
        Atomic operation. Use arm (pipette) with masked (selected) tips to dispense volume to wells.

        :param arm:      Uses the default Arm (pipette) if None
        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.mask_tip[index] and Robot.mask_tips[index])
        :param volume:   One (the same) for each tip or a list specifying the volume for each tip.
        :param to_wells: list of wells to aspirate from.
        :param liq_class: the name of the Liquid class, as it appears in your own EVOware database.
                          instructions.def_liquidClass if None
        """

        instructions.dispense(arm=arm, tipMask=TIP_MASK, liquidClass=liq_class, volume=volume, wellSelection=to_wells).exec()

    def atomic_mix(self):       # todo
        pass

    def delay(self):            # todo
        pass

    def user_prompt(self, text:str, sound:bool = True, close_time:int = -1 ):
        """
        Interrupt pippeting to popup a message box to the operator.

        :param text: the text in the box
        :param sound: Should add an acustic signal?
        :param close_time: time to wait for automatic closing the box: the operator can "manually"
        close this box at any time, and this will be the only way to close it if the default -1 is used,
         which cause no automatic closing.
        """
        instructions.userPrompt(text, sound=int(sound), closeTime=close_time).exec()

    def comment(self, text:str):
        """
        Add a text comment in the generated script
        :param text:
        """
        instructions.comment(text).exec()

class Pipeline (Executable):
    """ Each custom Pipeline need to implement these functions.

    """
    name = "Pipeline"

    def __init__(self,  GUI        = None,
                        protocols  = None,
                        run_name   = None):
        # assert isinstance(protocols, list)
        Executable.__init__(self, GUI=GUI, run_name  = run_name)

        self.protocols = protocols or []
        self.protocol_runs = {}
        for protocol in self.protocols:
            protocol.pipeline = self

    def check_list(self):
        if self.GUI:
            self.GUI.CheckPipeline(self)

    def run_pi(self):

        for protocol in self.protocols:
            logging.info(protocol.name + protocol.run_name)


@contextmanager
def group(titel, emode=None):
    instructions.group(titel).exec(emode)
    yield
    instructions.group_end().exec(emode)


@contextmanager
def parallel_execution_of(subroutine, repeat=1):
    # todo improve this idea: execute repeatably one after other and only at end wait.
    # for rep in range(repeat):
    if repeat == 1:
        instructions.subroutine(subroutine, instructions.subroutine.Continues).exec()
        yield
        instructions.subroutine(subroutine, instructions.subroutine.Waits_previous).exec()
    else:
        # rep_sub = br"C:\Prog\robotevo\EvoScriPy\repeat_subroutine.esc" .decode(mode.Mode.encoding)
        instructions.variable("repetitions",
                              repeat,
                              queryString="How many time repeat the subroutine?",
                              type=instructions.variable.Numeric
                              ).exec()

        instructions.variable("subroutine",
                              subroutine,
                              queryString="The subroutine path",
                              type=instructions.variable.String
                              ).exec()

        instructions.subroutine(robot.rep_sub, instructions.subroutine.Continues).exec()
        yield
        instructions.subroutine(robot.rep_sub, instructions.subroutine.Waits_previous).exec()


@contextmanager
def incubation(minutes, timer=1):
    instructions.startTimer(timer).exec()
    yield
    instructions.waitTimer(timer=timer, timeSpan=minutes * 60).exec()



# TODO  implement Debugger: prompt and or wait



