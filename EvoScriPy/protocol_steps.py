# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from contextlib import contextmanager
import EvoScriPy.Robot as Rbt
import EvoScriPy.Instructions as Itr
import EvoScriPy.Reagent as Rtv
import EvoScriPy.Labware as Lab
import EvoScriPy.EvoMode as EvoMode


def not_implemented():
    print('This protocols have yet to be implemented.')


# output_filename = '../current/AWL'
class Executable:
    """ Each executable need to implement these functions.

    """

    # parameters to describe this program
    name = "undefined"

    def def_versions(self):
        self.versions = {"none": not_implemented}

    def use_version(self, version : str):
        assert version in self.versions, \
            version + " is not a valid version. Valid versions are: " + str(self.versions.keys())
        self.version = version
        self.versions[version]()


    def __init__(self,  GUI       = None,
                        run_name  = None):

        self.GUI         = GUI
        self.run_name    = run_name
        self.pipeline    = None
        self.initialized = False
        self.reagents    = []
        self.versions    = {"none": not_implemented}
        self.def_versions()

        self.version     = next(iter(self.versions))
        Rtv.Reagent.SetReactiveList(self)  # todo Revise !!!

    def set_defaults(self):
        """Set initial values that will not be rest during secondary initializations.
        The "primary initialization" maybe a light one, like defining the list of versions available.
        Here, for example, initialize the list of reactive.
        """
        print('set def in Executable')

    def initialize(self):
        """It is called "just in case" to ensure we don't go uninitialized in lazy initializing scenarios.
        """
        if not self.initialized:
            if self.GUI:
                self.GUI.update_parameters()
            self.initialized = True
            self.set_defaults()

    def Run(self):
        """
        Here we have accesses to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with getLabware()
        :return:
        """

        self.initialize()
        self.preCheck()
        self.check_list()
        self.postCheck()
        self.done()

    def preCheck(self):
        pass

    def check_list(self):
        pass

    def postCheck(self):
        pass

    def done(self):
        pass


class Protocol (Executable):
    """
    Base class from which each custom protocol need to be derived, directly
    or from one of already derived. For example from the already adapted to some
    generic type robot like Evo200 or from an even more especially adapted like Evo100_FLI.
    Each newly derived protocol have to optionally override some of the following functions,
    especially .Run().

    """
    name = ""
    min_s, max_s = 1, 96

    def __init__(   self,
                    nTips                       = 4,
                    NumOfSamples                = max_s,
                    GUI                         = None,
                    worktable_template_filename = None,
                    output_filename             = None,
                    firstTip                    = None,
                    run_name                    = None):

        self.worktable_template_filename = worktable_template_filename or ""
        self.output_filename             = (output_filename or '../current/AWL') + (run_name or "")
        self.firstTip                    = firstTip
        self.nTips                       = nTips
        self.EvoMode                     = None      # EvoMode.multiple
        self.iRobot                      = None      # EvoMode.iRobot
        self.Script                      = None      # EvoMode.Script
        self.comments_                   = None      # EvoMode.Comments
        self.worktable                   = None
        self.robot                       = None
        self.NumOfSamples                = int(NumOfSamples or Protocol.max_s)
        self.check_initial_liquid_level  = False
        self.def_DiTi_check_liquid_level = None

        Rtv.Reagent.SetReactiveList(self)

        Executable.__init__(self, GUI=GUI, run_name  = run_name)

    def set_defaults(self):
        wt = self.worktable

        wt.def_DiTi       = Lab.DiTi_1000ul                 # this is a type, the others are labwares

        WashCleanerS    = wt.getLabware(Lab.CleanerSWS, ""     )
        WashWaste       = wt.getLabware(Lab.WasteWS,    ""     )
        WashCleanerL    = wt.getLabware(Lab.CleanerLWS, ""     )
        DiTiWaste       = wt.getLabware(Lab.DiTi_Waste, ""     )

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste

        Rtv.Reagent("Liquid waste", wt.def_WashWaste)

    def initialize(self):
        self.set_EvoMode()
        if not self.initialized:
            Executable.initialize(self)
        Rtv.Reagent.SetReactiveList(self)
        if self.def_DiTi_check_liquid_level is None:
            self.def_DiTi_check_liquid_level = self.worktable.def_DiTi


    def set_EvoMode(self):
        if not self.EvoMode:
            self.init_EvoMode()
        else:
            EvoMode.current = self.EvoMode
        self.iRobot.set_as_current()
        Rtv.Reagent.SetReactiveList(self)

    def init_EvoMode(self):
        self.iRobot = EvoMode.iRobot(Itr.Pipette.LiHa1, nTips=self.nTips)
        self.Script = EvoMode.Script(template=self.worktable_template_filename,
                                     filename=self.output_filename + '.esc',
                                     robot=self.iRobot.robot)
        self.comments_ = EvoMode.Comments(filename=self.output_filename + '.protocol.txt')
        self.EvoMode = EvoMode.multiple([self.iRobot,
                                         self.Script,
                                         EvoMode.AdvancedWorkList(self.output_filename + '.gwl'),
                                         EvoMode.ScriptBody(self.output_filename + '.txt'),
                                         EvoMode.StdOut(),
                                         self.comments_
                                         ])
        EvoMode.current = self.EvoMode
        self.worktable  = self.iRobot.robot.worktable  # shortcut !!
        self.robot      = self.iRobot.robot
        assert (self.iRobot.robot.curArm().nTips == self.nTips )

    def comments(self):
        return self.comments_.comments

    def Run(self):
        '''
        Here we have accesses to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with getLabware()
        :return:
        '''
        self.set_EvoMode()

        self.initialize()
        self.set_EvoMode()

        self.preCheck()
        self.set_EvoMode()

        self.check_list()
        self.set_EvoMode()

        self.postCheck()
        self.set_EvoMode()

        self.done()

    def check_list(self):
        """
        Tipically
        """
        self.set_EvoMode()
        if (self.GUI):
            self.GUI.check_list()
        self.set_EvoMode()
        Rtv.Reagent.SetReactiveList(self)
        if self.check_initial_liquid_level:
            self.check_reagents_levels()

    def check_reagent_level(self, reagent, LiqClass=None):
        """
        Select all possible replica of the given reagent and detect the liquid level,
        contrasting it with the current (expected) volumen in EACH well.
        Use the given liquid class or the reagent default.
        :param reagent:
        :param LiqClass:

        """
        assert isinstance(reagent, Rtv.Reagent)
        LiqClass = LiqClass or reagent.defLiqClass


        reagent.autoselect(self.robot.curArm().nTips)              # todo use even more tips? see self._aspirate_multi_tips
        vol = [w.vol for w in reagent.labware.selected_wells()]
        Itr.comment(f"Check: {str([str(well) for well in reagent.labware.selected_wells()] ) }").exec()

        with self.tips(tip_type     = self.def_DiTi_check_liquid_level,
                       reuse        = False,
                       tipsMask     = Rbt.tipsMask[len(vol)]):

            Itr.detect_Liquid(Rbt.tipsMask[len(vol)],
                              liquidClass =LiqClass,
                              labware     =reagent.labware).exec()

        Itr.userPrompt("").exec()

    def check_reagents_levels(self):
        """
        Will emit a liquid level detection on every well occupied by all the reagents defined so fort.
        Will be executed at the end of self.check_list() but only if self.check_initial_liquid_level is True
        """

        for reagent in self.worktable.reagents:
            print(f"Check {reagent.name}in {str([str(well) for well in reagent.Replicas])}")
            self.check_reagent_level(reagent)

    def done(self):
        self.EvoMode.done()
        Executable.done(self)

    def go_first_pos(self, first_tip: (int, str) = None):
        """
        Optionally set the Protocol.firstTip, a position in rack, like 42 or 'B06'
        (optionally including the rack self referenced with a number, like '2-B06', were 2 will be the second
        rack in the wortable series ofdefault tip type). Currently, for a more precise set, use directly the
        Itr.set_DITI_Counter2(labware=rack, posInRack=firstTip).exec()
        """
        if first_tip is not None:
            self.firstTip = first_tip                                       # just keep it

        if self.firstTip is not None and self.worktable is not None:        # set in wt
            rack, firstTip = self.worktable.set_first_pos(posstr=self.firstTip)
            Itr.set_DITI_Counter2(labware=rack, posInRack=firstTip).exec()

    def set_dropTips(self, drop=True)->bool:
        """
        Drops the tips at THE END of the whole action? like after spread of the reactive into various targets
        :param drop:
        :return:
        """
        return self.robot.set_dropTips(drop)

    def set_allow_air(self, allow_air=0.0)->float:
        return self.robot.set_allow_air(allow_air)

    def reuseTips(self, reuse=True)->bool:
        """     Reuse the tips or drop it and take new after each action?
        :param reuse:
        :return:
        """
        return self.robot.reuseTips(reuse)

    def reuse_tips_and_drop(self, reuse=True, drop=True)->(bool, bool):
        return self.set_dropTips(drop), self.reuseTips(reuse)

    def preserveTips(self, preserve=True)->bool:
        return self.robot.preserveTips(preserve)

    def preserveingTips(self)->bool:
        return self.robot.preservetips

    def usePreservedTips(self, usePreserved=True)->bool:
        return self.robot.usePreservedTips(usePreserved)

    def moveTips(self, zMove, zTarget, offset, speed, TIP_MASK=-1):
        pass # Itr.moveLiha

    def getTips(self, TIP_MASK         = -1,
                      tip_type         = None,
                      selected_samples = None ):  # todo TIP_MASK=None
        """
        It will decide to get new tips or to pick back the preserved tips for the selected samples
        :param TIP_MASK:
        :param tip_type:
        :param selected_samples:
        :return:
        """
        mask = TIP_MASK = TIP_MASK if TIP_MASK != -1 else Rbt.tipsMask[self.robot.curArm().nTips]

        if self.robot.usePreservedtips:
            with self.tips(drop=True, preserve=False):    # drop tips from previous "buffer" in first pipetting
                self.dropTips(TIP_MASK)
            where = self.robot.where_are_preserved_tips(selected_samples, TIP_MASK, tip_type)
            nTips = self.robot.curArm().nTips

            for tip_rack in where:
                tipsMask = 0
                tips_in_rack = len(tip_rack.selected())
                for idx in range(nTips):
                    if not tips_in_rack: break
                    tip = (1 << idx)
                    if TIP_MASK & tip:
                        tipsMask |= tip
                        TIP_MASK ^= tip
                        tips_in_rack -= 1
                Itr.pickUp_DITIs2(tipsMask, tip_rack).exec()
            assert tips_in_rack == 0
        else:
            tip_type= tip_type or self.worktable.def_DiTi
            I = Itr.getDITI2(TIP_MASK, tip_type, arm=self.robot.def_arm)
            I.exec()
        return mask                                    # todo REVISE !!   I.tipMask

    def dropTips(self, TIP_MASK=-1):
        """
        It will decide to really drop the tips or to put it back in some DiTi rack
        :param TIP_MASK:
        :return:
        """
        if self.robot.preservetips:
            where = self.robot.where_preserve_tips(TIP_MASK)
            nTips = self.robot.curArm().nTips
            for tip_rack in where:
                tipsMask = 0
                l = len(tip_rack.selected())
                for i in range(nTips):
                    if not l: break
                    b = (1 << i)
                    if TIP_MASK & b:
                        tipsMask |= b
                        TIP_MASK ^= b
                        l -= 1
                Itr.set_DITIs_Back(tipsMask, tip_rack).exec()
            assert l == 0
            return
        #if not Rbt.Robot.current.droptips: return 0
        #TIP_MASK = Rbt.Robot.current.curArm().drop(TIP_MASK)
        #if TIP_MASK:# todo is this a correct solution or it is best to do a double check? To force drop?
        Itr.dropDITI(TIP_MASK).exec()
        #return TIP_MASK

    def aspire(self,  tip, reactive, vol=None, offset = None):
        """
        Aspirate vol with ONE tip from reactive
        :param self:
        :param tip:
        :param reactive:
        :param vol:
        """
        if vol is None:       vol = reactive.minVol()    # todo: revise !!

        v = [0] * self.robot.curArm().nTips
        v[tip] = vol
        reactive.autoselect(offset = offset)                                         # reactive.labware.selectOnly([reactive.pos])
        Itr.aspirate(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

    def dispense(self,  tip, reactive, vol=None):                     # OK coordinate with robot
        """
        Dispense vol with ONE tip to reactive
        :param tip:
        :param reactive:
        :param vol:
        """
        vol = vol or reactive.minVol()                                # really ??   # todo: revise !!
        reactive.autoselect()                                         # reactive.labware.selectOnly([reactive.pos])
        v = [0] * self.robot.curArm().nTips
        v[tip] = vol
        Itr.dispense(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

    def mix_reagent(self,   reagent   : Rtv.Reagent,
                            LiqClass  : str  = None,
                            cycles    : int  = 3,
                            maxTips   : int  = 1,
                            v_perc    : int  = 90   ):
        """
        Select all possible replica of the given reagent and mix using the given % of the current vol in EACH well
        or the max vol for the tip. Use the given "liquid class" or the reagent default.
        :param reagent:
        :param LiqClass:
        :param cycles:
        :param maxTips:
        :param v_perc:  % of the current vol in EACH well to mix
        :return:
        """
        assert isinstance(reagent, Rtv.Reagent)
        LiqClass = LiqClass or reagent.defLiqClass
        v_perc /= 100.0
        vol = []
        reagent.autoselect(maxTips)
        for tip, w in enumerate(reagent.labware.selected_wells()):
            v = w.vol * v_perc
            vm = self.robot.curArm().Tips[tip].type.maxVol * 0.9
            vol += [min(v, vm)]

        Itr.mix(Rbt.tipsMask[len(vol)],
                liquidClass =LiqClass,
                volume      =vol,
                labware     =reagent.labware,
                cycles      =cycles).exec()

    def _multidispense_in_replicas(self, tip     : int,
                                   reagent : Rtv.Reagent,
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
            Itr.dispense(Rbt.tipMask[tip], self.robot.curArm().Tips[tip].origin.reagent.defLiqClass,
                         # reagent.defLiqClass,
                         v, w.labware.selectOnly([w.offset])).exec()

    def _aspirate_multi_tips(self, reagent  : Rtv.Reagent,
                                   tips     : int           = None,
                                   vol      : (float, list) = None,
                                   LiqClass : str           = None):
        """
        Intermediate-level function. Aspirate with multiple tips from multiple wells with different volume.
        Example: you want to aspirate 8 different volume of a reagent into 8 tips, but the reagent
        have only 3 replicas (only 3 wells contain the reagent). This call will generate the instructions to
        fill the tips 3 by 3 with the correct volume. Assumes the tips are mounted in the current arm.

        :param tips     : number of tips beginning from #1 to use
        :param reagent  : reagent to aspirate, with some number of wells in use
        :param vol:
        :param LiqClass:
        """
        max_tips = self.robot.curArm().nTips

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

        LiqClass = LiqClass or reagent.defLiqClass

        mask = Rbt.tipsMask[tips]                                 # as if we could use so many tips
        n_wells = reagent.autoselect(tips)                        # the total number of available wells to aspirate from
        asp = Itr.aspirate(mask, LiqClass, vol, reagent.labware)
        curTip = 0
        while curTip < tips:                                      # todo what to do with used tips?
            nextTip = curTip + n_wells                            # add tips, one for each well
            nextTip = nextTip if nextTip <= tips else tips        # but not too much
            mask = Rbt.tipsMask[curTip] ^ Rbt.tipsMask[nextTip]   # now use only the last tips added

            asp.tipMask = mask
            asp.exec()                                           # will call robot.curArm().aspirated(vol, mask)  ???
            curTip = nextTip

    def _dispensemultiwells(self, tips : int, liq_class, labware : Lab.Labware, vol : (float, list)):
        """
        Intermediate-level function. One dispense from multiple tips in multiple wells with different volume

        :param tips: number of tips to use                        # todo ?
        :param liq_class:
        :param labware:
        :param vol:
        """
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = Rbt.tipsMask[tips]

        Itr.dispense(om, liq_class, vol, labware).exec()          # will call robot.curArm().dispensed(vol, om)  ??

    def make(self,  what, NumSamples=None): # OK coordinate with protocol
            if isinstance(what, Rtv.preMix): self.makePreMix(what, NumSamples)

    def makePreMix(self,  preMix        : Rtv.preMix,
                          NumSamples    : int       = None,
                          force_replies : bool      = False):
        """
        A preMix is just that: a premix of reagents (aka - components)
        which have been already defined to add some vol per sample.
        Uses one new tip per component.
        It calculates and checks self the minimum and maximum number of replica of the resulting preMix
        :param preMix    : what to make, a predefined preMix
        :param NumSamples:
        :param force_replies: use all the preMix predefined replicas
        :return:
        """

        assert isinstance(preMix, Rtv.preMix)
        robot       = self.robot
        mxnTips     = robot.curArm().nTips  # max number of Tips
        ncomp       = len(preMix.components)
        nt          = min(mxnTips, ncomp)
        NumSamples  = NumSamples or self.NumOfSamples
        labw        = preMix.labware
        tVol        = preMix.minVol(NumSamples)
        mxnrepl     = len(preMix.Replicas)                        # max number of replies
        mnnrepl     = preMix.min_num_of_replica(NumSamples)       # min number of replies
        assert mxnrepl >= mnnrepl, 'Please choose at least {:d} replies for {:s}'.format(mnnrepl, preMix.name)
        nrepl       = mxnrepl if force_replies else mnnrepl
        if nrepl < mxnrepl:
            print("WARNING !!! The last {:d} replies of {:s} will not be used.".format(mxnrepl-nrepl, preMix.name))
            preMix.Replicas = preMix.Replicas[:nrepl]

        msg = "preMix: {:.1f} µL of {:s}".format(tVol, preMix.name)
        with group(msg):
            msg += " into grid:{:d} site:{:d} {:s} from {:d} components:"\
                                .format( labw.location.grid,
                                         labw.location.site + 1,
                                         str([str(well) for well in preMix.Replicas]) ,
                                         ncomp                        )
            Itr.comment(msg).exec()
            samples_per_replicas = [(NumSamples + nrepl - (ridx+1))//nrepl for ridx in range(nrepl)]
            with self.tips(Rbt.tipsMask[nt]):   #  want to use preserved ?? selected=??
                tip = -1
                ctips = nt
                for ridx, react in enumerate(preMix.components):       # iterate reactive components
                    labw = react.labware
                    sVol = react.volpersample*preMix.excess       # vol we need for each sample
                    rVol = sVol*NumSamples                        # the total vol we need of this reagent component
                    msg = "   {idx:d}- {v:.1f} µL from grid:{g:d} site:{st:d}:{w:s}"\
                                .format( idx = ridx + 1,
                                         v   = rVol,
                                         g   = labw.location.grid,
                                         st  = labw.location.site + 1,
                                         w   = str([str(well) for well in react.Replicas])   )
                    Itr.comment(msg).exec()
                    tip += 1  # use the next tip
                    if tip >= nt:
                        ctips = min(nt, ncomp - ridx) # how many tips to use for the next gruop
                        tipsType = robot.curArm().Tips[0].type    # only the 0 ??
                        self.dropTips(Rbt.tipsMask[ctips])
                        self.getTips(Rbt.tipsMask[ctips], tipsType)
                        tip = 0
                    mV = robot.curArm().Tips[tip].type.maxVol
                    # aspire/dispense multiple times if rVol don't fit in the tip (mV)
                    # but also if there is not sufficient reactive in the current component replica
                    current_comp_repl = 0
                    while rVol > 0:
                        while (react.Replicas[current_comp_repl].vol < 1):      # todo define sinevoll min vol
                            current_comp_repl +=1
                        dV = min (rVol, mV, react.Replicas[current_comp_repl].vol)
                        self.aspire(tip, react, dV, offset=react.Replicas[current_comp_repl].offset)
                        self._multidispense_in_replicas(ridx, preMix, [sp / NumSamples * dV for sp in samples_per_replicas])
                        rVol -= dV
                self.mix_reagent(preMix, maxTips=ctips)

    def spread(self,
               volume            : float        = None,
               reagent           : Rtv.Reagent  = None,
               to_labware_region : Lab.Labware  = None,
               optimize          : bool         = True,
               NumSamples        : int          = None,
               using_liquid_class: (str, tuple) = None,
               TIP_MASK          : int          = None,
               num_tips          : int          = None):
        """
        To spread a reagent into some wells.
        This is a high level function with works with the concept of "reagent". This a a concept introduced by
        RobotEvo that don't exist in EVOware and other similar software. It encapsulated the name, wells occupied by
        each of the aliquots of the reagent, the volume corresponding to one sample (if any) and the current volume
        in each aliquot. This function can use multiple of those aliquots to spread the reagent to the target
        wells using multiple tips (the maximum will be used if `num_tips` is not set).

        By default a number of wells equal to the number of samples set in the protocol will be auto selected in the
        target labware `to_labware_region`, but this selection can be set explicitly (setting `well.selFlag=True`,
        for example by calling `to_labware_region.selectOnly(self, sel_idx_list)`). If `NumSamples` is set
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

        :param NumSamples       : Priorized   !!!! If true reset the selection
        :param reagent          : Reagent to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param volume           : if not, volume is set from the default of the source reactive
        :param optimize         : minimize zigzag of multi pipetting
        :param num_tips         : the number of tips to be used in each cycle of pipetting = all
        """
        assert isinstance(reagent, Rtv.Reagent), 'A Reagent expected in reagent to spread'
        assert isinstance(to_labware_region, Lab.Labware), 'A Labware expected in to_labware_region to spread'

        if num_tips is None:
            num_tips = self.robot.curArm().nTips  # the number of tips to be used in each cycle of pipetting = all

        if NumSamples:
            to_labware_region.selectOnly(range(NumSamples))
        else:
            if not to_labware_region.selected():
                to_labware_region.selectOnly(range(self.NumOfSamples))

        to = to_labware_region.selected()        # list of offset of selected wells
        if optimize: to = to_labware_region.parallelOrder(num_tips, to)
        NumSamples = len(to)
        SampleCnt = NumSamples

        volume = volume or reagent.volpersample

        Asp_liquidClass, Dst_liquidClass = (reagent.defLiqClass, reagent.defLiqClass) if using_liquid_class is None else \
                                           (using_liquid_class[0] or reagent.defLiqClass, using_liquid_class[1] or reagent.defLiqClass)


        lf = reagent.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}".format(v=volume, n=reagent.name)
        with group(msg):
            msg += " ({v:.1f} µL total) from [grid:{fg:d} site:{fs:d} {fw:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                        .format(v  = reagent.minVol(),
                                fg = lf.location.grid,
                                fs = lf.location.site+1,
                                fw = str([str(well) for well in reagent.Replicas]),
                                do = str([i+1 for i in to]),
                                to = lt.label,
                                tg = lt.location.grid,
                                ts = lt.location.site+1)
            Itr.comment(msg).exec()
            availableDisp = 0
            while SampleCnt:
                if num_tips > SampleCnt: num_tips = SampleCnt
                with self.tips(Rbt.tipsMask[num_tips], usePreserved=False, preserve=False):  # OK want to use preserved ?? selected=??
                    maxMultiDisp_N = self.robot.curArm().Tips[0].type.maxVol // volume  # assume all tips equal
                    dsp, rst = divmod(SampleCnt, num_tips)
                    if dsp >= maxMultiDisp_N:
                        dsp = maxMultiDisp_N
                        vol = [volume * dsp] * num_tips
                        availableDisp = dsp
                    else:
                        vol = [volume * (dsp + 1)] * rst + [volume * dsp] * (num_tips - rst)
                        availableDisp = dsp + bool(rst)

                    self._aspirate_multi_tips(reagent, num_tips, vol, LiqClass=Asp_liquidClass)

                    while availableDisp:
                        if num_tips > SampleCnt: num_tips = SampleCnt
                        curSample = NumSamples - SampleCnt
                        sel = to[curSample: curSample + num_tips]  # todo what if volume > maxVol_tip ?
                        self._dispensemultiwells(num_tips, Dst_liquidClass, to_labware_region.selectOnly(sel), [volume] * num_tips)
                        availableDisp -= 1
                        SampleCnt -= num_tips


    def transfer(self,
                 from_labware_region: Lab.Labware,
                 to_labware_region  : Lab.Labware,
                 volume             : (int, float),
                 using_liquid_class : (str,tuple)   = None,
                 optimizeFrom       : bool          = True,
                 optimizeTo         : bool          = True,
                 NumSamples         : int           = None) -> object:
        """
        To transfer reagents (typically samples or intermediary reactions) from some wells in the source labware to
        the same number of wells in the target labware using the current LiHa arm with maximum number of tips
        (of type: `self.worktable.def_DiTi`, which can be set `with self.tips(tip_type = myTipsRackType)`).
        # todo: count for 'broken' tips

        The number of "samples" may be explicitly indicated in which case will be assumed to begin from the
        first well of the labware. Alternatively the wells in the source or target or in both may be
        previously directly "selected" (setting `well.selFlag=True`, for example by calling
        `from_labware_region.selectOnly(self, sel_idx_list)`), in which case transfer the minimum length selected.
        If no source wells are selected this function will auto select the protocol's `self.NumOfSamples` number
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


        :param from_labware_region  : Labware in which the source wells are located and possibly selected
        :param to_labware_region    : Labware in which the target wells are located and possibly selected
        :param volume               : if not, volume is set from the default of the source reactive
        :param using_liquid_class   : LC or tuple (LC to aspirate, LC to dispense)
        :param optimizeFrom         : bool - use from_labware_region.parallelOrder(...) to aspirate
        :param optimizeTo           : bool - use to_labware_region.parallelOrder(...) to aspirate
        :param NumSamples           : Prioritized. If used reset the well selection
        :return:
        """
        assert isinstance(from_labware_region, Lab.Labware), 'Labware expected in from_labware_region to transfer'
        assert isinstance(to_labware_region,   Lab.Labware), 'Labware expected in to_labware_region to transfer'
        # assert isinstance(using_liquid_class, tuple)
        nt = self.robot.curArm().nTips                  # the number of tips to be used in each cycle of pippeting

        if NumSamples:                                  # select convenient def
            oriSel = range(NumSamples)
            dstSel = range(NumSamples)
        else:
            oriSel = to_labware_region.selected()
            dstSel = from_labware_region.selected()

            if not dstSel:
                if not oriSel:
                    oriSel = range(self.NumOfSamples)
                    dstSel = range(self.NumOfSamples)
                else:
                    dstSel = oriSel
            else:
                if not oriSel:
                    oriSel = dstSel
                else:
                    l = min(len(oriSel), len(dstSel))   # transfer the minimum of the selected
                    oriSel = oriSel[:l]                 # todo Best reise an error ??
                    dstSel = dstSel[:l]
        if optimizeFrom: oriSel = from_labware_region.parallelOrder(nt, oriSel)   # a list of well offset s
        if optimizeTo  :   dstSel = to_labware_region.parallelOrder  (nt, dstSel)

        NumSamples = len(dstSel)
        SampleCnt = NumSamples

        assert isinstance(volume, (int, float))
        assert 0 < volume <= self.worktable.def_DiTi.maxVol, \
            "Invalid volumen to transfer ("+str(volume)+") with tips " + self.worktable.def_DiTi

        nt = min(SampleCnt, nt)
        lf = from_labware_region
        lt = to_labware_region

        Asp = Itr.aspirate(Rbt.tipsMask[nt], volume=volume, labware=from_labware_region)
        Dst = Itr.dispense(Rbt.tipsMask[nt], volume=volume, labware=to_labware_region)
        msg = "Transfer: {v:.1f} µL from {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += " [grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg =lf.location.grid,
                        fs =lf.location.site+1,
                        oo =str([i+1 for i in oriSel]),
                        do =str([i+1 for i in dstSel]),
                        to =lt.label,
                        tg =lt.location.grid,
                        ts =lt.location.site+1)
            Itr.comment(msg).exec()
            while SampleCnt:                                # loop wells (samples)
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:                          # only a few samples left
                    nt = SampleCnt                          # don't use all tips
                    tm = Rbt.tipsMask[nt]                   # todo count for broken tips
                    Asp.tipMask = tm
                    Dst.tipMask = tm

                src = oriSel[curSample:curSample + nt]      # only the next nt wells
                trg = dstSel[curSample:curSample + nt]
                spl = range(curSample, curSample + nt)

                sw = Asp.labware.selected_wells()

                if isinstance(using_liquid_class, tuple):
                    if using_liquid_class[0]:
                        Asp.liquidClass = using_liquid_class[0]
                    else:
                        Asp.liquidClass = sw[0].reagent.defLiqClass
                    if using_liquid_class[1]:
                        Dst.liquidClass = using_liquid_class[1]
                    else:
                        Dst.liquidClass = sw[0].reagent.defLiqClass
                else:
                    Asp.liquidClass = sw[0].reagent.defLiqClass
                    Dst.liquidClass = sw[0].reagent.defLiqClass

                Asp.labware.selectOnly(src)
                Dst.labware.selectOnly(trg)
                with self.tips(Rbt.tipsMask[nt], selected_samples=Asp.labware):  # todo what if volume > maxVol_tip ?
                    Asp.exec()                                           # <---- low level aspirate
                    Dst.exec()                                           # <---- low level dispense
                    for s, d in zip(Asp.labware.selected_wells(), Dst.labware.selected_wells()):
                        d.track = s                                     # todo revise !! and .actions []
                        d.actions += s.actions                          # ????
                SampleCnt -= nt
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel


    def waste(self,  from_labware_region : Lab.Labware      = None,
                     using_liquid_class  : str              = None,
                     volume              : float            = None,     # todo accept a list ??
                     to_waste_labware    : Lab.CuvetteType  = None,
                     optimize            : bool             = True):    # todo: set default as False ??

        """
        Use this function as a final step of a `in-well` pellet wash procedure (magnetically or by centrifuge created).
        Waste a `volume` from each of the selected wells `from_labware_region` (source labware wells)
        `to_waste_labware` using the current LiHa arm with maximum number of tips (of type: `self.worktable.def_DiTi`,
        which can be set `with self.tips(tip_type = myTipsRackType)`). # todo: count for 'broken' tips
        If no source wells are selected this function will auto select a `self.NumOfSamples` number
        of wells in the source labware.
        If no destination is indicated, `self.worktable.def_WashWaste` will be used.
        The same volume will be wasted from each well (todo: revise this, waste all from EACH well?).
        If no `volume` is indicated then the volume expected to be in the first selected well will be used.
        todo: current hack to be resolved: using an special liquid class that aspirate from a side to avoid a pellet
        expected to be in the opposite side. The user must specify an equivalent class, or we need to introduce a
        kind of `Protocol.def_Waste_liqClass`.
        Aspirate and waste repeatedly with allowed volume until only an small rest are in wells and then change the LC
        to one without liquid detection - liquid level trace. (this rest depends on the well geometry - todo: make it
        a function parameter?). This avoid collision with the button of the well.

        A human readable comment will be automatically added to the script with the details of this operation.

        Warning: modify the selection of wells in both source and target labware

        :param from_labware_region: source labware possibly with selected wells
        :param using_liquid_class:
        :param volume:              is None the volume expected to be in the first selected well will be used
        :param to_waste_labware:    to_waste_labware or self.worktable.def_WashWaste
        :param optimize:            use optimized order of wells - relevant only if re-using tips
        """

        to_waste_labware = to_waste_labware or self.worktable.def_WashWaste
        assert isinstance(from_labware_region, Lab.Labware), \
          'A Labware is expected in from_labware_region to waste from, but "' + str(from_labware_region) + '" was used.'

        if not volume or volume < 0.0 :
            volume = 0.0
        assert isinstance(volume, (int, float))

        oriSel = from_labware_region.selected()         # list of the selected well offset
        nt = self.robot.curArm().nTips                  # the number of tips to be used in each cycle of pipetting

        if not oriSel:
            oriSel = range(self.NumOfSamples)
        if optimize:                                    # todo: if None reuse self.optimize (to be created !!)
            oriSel = from_labware_region.parallelOrder(nt, oriSel)

        NumSamples = len(oriSel)                        # oriSel used to calculate number of "samples"
        SampleCnt = NumSamples                          # the number of selected wells

        if nt > SampleCnt:                              # very few wells selected (less than tips)
            nt = SampleCnt
        tm = Rbt.tipsMask[nt]                           # todo: count for 'broken' tips
        nt = to_waste_labware.autoselect(maxTips=nt)
        mV = self.worktable.def_DiTi.maxVol

        Rest = 50                    # the volume we cannot further aspirate with liquid detection, to small, collisions
        RestPlus = 50
        CtrVol = 0.5

        # all wells with equal volume. todo: waste all vol from EACH well?. v: just for msg
        v = volume if volume else from_labware_region.Wells[oriSel[0]].vol

        Asp = Itr.aspirate(tm, Te_Mag_LC, volume, from_labware_region)                 # todo: revert this LC temp hack
        # Asp = Itr.aspirate(tm, using_liquid_class[0], volume, from_labware_region)

        Dst = Itr.dispense(tm, using_liquid_class, volume, to_waste_labware)
        # Ctr = Itr.moveLiha(Itr.moveLiha.y_move, Itr.moveLiha.z_start, 3.0, 2.0, tm, from_labware_region)

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL from {n:s}".format(v=v, n=lf.label)
        with group(msg):

            msg += " in [grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) \
                  + str([i+1 for i in oriSel])
            Itr.comment(msg).exec()

            while SampleCnt:                                # loop wells (samples)
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:                          # only a few samples left
                    nt = SampleCnt                          # don't use all tips
                    tm = Rbt.tipsMask[nt]
                    Asp.tipMask = tm
                    Dst.tipMask = tm

                sel = oriSel[curSample:curSample + nt]      # select the next nt (number of used tips) wells
                Asp.labware.selectOnly(sel)

                if volume:                                                  # volume: to be Waste
                    r = volume                                              # r: Waste_available yet
                else:
                    vols = [w.vol for w in Asp.labware.selected_wells()]    # todo priorize this vols !!
                    r_min, r_max = min(vols), max(vols)
                    assert r_min == r_max, "Currently we assumed equal volumen in all wells, but got: " + str(vols)
                    r = r_max

                if not using_liquid_class:
                    if sel:
                        Dst.liquidClass = Asp.labware.selected_wells()[0].reagent.defLiqClass

                with self.tips(tm, drop=True, preserve=False, selected_samples=Asp.labware):

                    # aspirate and waste repeatedly with allowed volume until only Rest uL are in wells
                    while r > Rest:                     # don't aspirate Rest with these Liq Class (Liq Detect)
                        dV = min (r, mV)                # don't aspirate more than the max for that tip type
                        if dV < Rest:
                            break                       # ??  mV < Rest
                        dV -= Rest                      # the last Rest uL have to be aspired with the other Liq Class
                        Asp.volume = dV                 # with Liq Class with Detect: ">> AVR-Serum 1000 <<	365"
                        Dst.volume = dV
                        Asp.liquidClass = Te_Mag_LC     # ">> AVR-Serum 1000 <<	365"  # "No Liq Detect"
                        Asp.exec()                      # <---- low level, direct aspirate here !!
                        Asp.volume = CtrVol             # ?? minimal, 'fake' vol ?
                        Asp.liquidClass = Te_Mag_Centre # just to go to the center

                        with self.tips(allow_air=CtrVol):
                            Asp.exec()
                            if dV + Rest + RestPlus + 2*CtrVol > mV:
                                Dst.exec()              # dispense if there is no capacity for further aspirations
                                r -= dV
                                Dst.volume = 0
                            else:
                                break

                    # now waste the Rest with a LC with no liquid level detection, avoiding collisions
                    Asp.volume = Rest                   # force aspirate Rest, which may be more than rests in well
                    Asp.liquidClass =  Te_Mag_Rest      # ">> AVR-Serum 1000 <<	367" # "No Liq Detect"
                    with self.tips(    allow_air = Rest ):
                            Asp.exec()
                    Asp.volume = CtrVol
                    Asp.liquidClass = Te_Mag_Force_Centre
                    with self.tips(    allow_air = Rest + CtrVol ):
                            Asp.exec()
                    Asp.volume = RestPlus
                    Asp.liquidClass =  Te_Mag_RestPlus  # ">> AVR-Serum 1000 <<	369" # "No Liq Detect"
                    with self.tips(    allow_air = RestPlus + Rest + CtrVol ):
                            Asp.exec()
                    # Ctr.exec()
                    Asp.volume = CtrVol
                    Asp.liquidClass = Te_Mag_Force_Centre
                    Dst.volume += Rest + RestPlus
                    with self.tips(    allow_air = CtrVol + RestPlus + Rest + CtrVol ):
                            Asp.exec()
                    with self.tips(    allow_air = CtrVol + RestPlus + Rest + CtrVol ):
                            Dst.exec()

                SampleCnt -= nt
            Asp.labware.selectOnly(oriSel)
        Itr.wash_tips(wasteVol=4).exec()
        return oriSel


    def mix(self,  in_labware_region  : Lab.Labware,
                   using_liquid_class : str        = None,
                   volume             : float      = None,
                   optimize           : bool       = True):

        """
        Mix the reagents in each of the wells selected `in_labware_region`, `using_liquid_class` and `volume`
        :param in_labware_region:
        :param using_liquid_class:
        :param volume:
        :param optimize:
        :return:
        """
        mix_p = 0.9
        in_labware_region = in_labware_region or self.worktable.def_WashWaste    # todo ???????????
        assert isinstance(in_labware_region, Lab.Labware), 'A Labware expected in in_labware_region to be mixed'
        if not volume or volume< 0.0 : volume = 0.0
        assert isinstance(volume, (int, float))
        oriSel = in_labware_region.selected()
        nt = self.robot.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if not oriSel:
            oriSel = range(self.NumOfSamples)
        if optimize:
            oriSel = in_labware_region.parallelOrder( nt, oriSel)
        NumSamples = len(oriSel)
        SampleCnt = NumSamples
        if nt > SampleCnt:
            nt = SampleCnt
        # mV = Rbt.Robot.current.curArm().Tips[0].type.maxVol * 0.8
        mV = self.worktable.def_DiTi.maxVol * mix_p    # What tip tp use !
        if volume:
            v = volume
        else:
            v = in_labware_region.Wells[oriSel[0]].vol
        v = v * mix_p
        v = v if v < mV else mV

        lf = in_labware_region
        mx = Itr.mix(Rbt.tipsMask[nt], using_liquid_class, volume, in_labware_region)
        msg = "Mix: {v:.1f} µL of {n:s}".format(v=v, n=lf.label)
        with group(msg):
            msg += " [grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) \
                                        + str([i+1 for i in oriSel])
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    mx.tipMask = Rbt.tipsMask[nt]

                sel = oriSel[curSample:curSample + nt]
                mx.labware.selectOnly(sel)
                with self.tips(Rbt.tipsMask[nt], selected_samples = mx.labware):
                    mV = self.robot.curArm().Tips[0].type.maxVol * mix_p
                    if not using_liquid_class:
                        if sel:
                            mx.liquidClass = mx.labware.selected_wells()[0].reagent.defLiqClass
                    if volume:
                        r = volume   # r: Waste_available yet; volume: to be Waste
                    else:
                        vols = [w.vol for w in mx.labware.selected_wells()]
                        r_min, r_max = min(vols), max(vols)
                        assert r_min == r_max
                        r = r_max
                    r = r * mix_p
                    r = r if r < mV else mV
                    mx.volume = r
                    mx.exec()
                SampleCnt -= nt
        mx.labware.selectOnly(oriSel)
        return oriSel

    @contextmanager
    def tips(self,  tipsMask    = None, tip_type     = None,
                    reuse       = None, drop         = None,
                    preserve    = None, usePreserved = None,  selected_samples : Lab.Labware  = None,
                    allow_air   = None, drop_first   = False, drop_last          = False   ):
        '''

        :param tipsMask     :
        :param reuse        : Reuse the tips or drop it and take new BEFORE each individual action
        :param drop         : Drops the tips AFTER each individual action,
                              like after one aspiration and spread of the reactive into various target
        :param preserve     : puts the tip back into a free place in some rackt of the same type
        :param usePreserved : pick the tips from the preserved
        :param selected_samples:
        :param allow_air    :
        :param drop_first   : Reuse the tips or drop it and take new once BEFORE the whole action
        :param drop_last    : Drops the tips at THE END of the whole action
        :return:
        '''

        if selected_samples is not None:
            assert isinstance(selected_samples, Lab.Labware )      # todo set some current?

        if drop_first:  self.dropTips()
        if reuse        is not None: reuse_old          = self.reuseTips       (reuse       )
        if drop         is not None: drop_old           = self.set_dropTips    (drop        )
        if preserve     is not None: preserve_old       = self.preserveTips    (preserve    )
        if usePreserved is not None: usePreserved_old   = self.usePreservedTips(usePreserved)
        if allow_air    is not None: allow_air_old      = self.set_allow_air   (allow_air   )
        if tip_type     is not None: tip_type_old       = self.worktable.set_def_DiTi(tip_type)

        if tipsMask     is not None:
            tipsMask_old     = self.getTips    (tipsMask, selected_samples=selected_samples, tip_type=tip_type)

        yield

        if tipsMask     is not None: tipsMask     = self.dropTips        (tipsMask_old)
        if tip_type     is not None: tip_type     = self.worktable.set_def_DiTi(tip_type_old)
        if reuse        is not None: reuse        = self.reuseTips       (reuse_old       )
        if drop         is not None: drop         = self.set_dropTips    (drop_old        )
        if preserve     is not None: preserve     = self.preserveTips    (preserve_old    )
        if usePreserved is not None: usePreserved = self.usePreservedTips(usePreserved_old)
        if allow_air    is not None: allow_air    = self.set_allow_air   (allow_air_old   )
        if drop_last:   self.dropTips()


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
        if (self.GUI):
            self.GUI.CheckPipeline(self)

    def RunPi(self):

        for protocol in self.protocols:
            print(protocol.name + protocol.run_name)



Water_free = "Water free"  # General. No detect and no track small volumes < 50 µL

SerumLiqClass      = "Serum Asp preMix3"   # or "MN Virus Sample"
TissueHomLiqClass  = "Serum Asp"


B_liquidClass   = "Water free cuvette"
W_liquidClass   = Water_free      #    or "AVR-Water free DITi 1000"
Std_liquidClass = Water_free      #    or "Water free dispense DiTi 1000"
Small_vol_disp  = "Water wet"     #    or "Water free Low Volume"  ??
Beads_LC_1      = "MixBeads_1"
Beads_LC_2      = "MixBeads_2"

Te_Mag_LC       = "Te-Mag"          # "Water free" but uncentered
Te_Mag_Centre   = "Te-Mag Centre"   # To Centre after normal aspiration.
Te_Mag_Rest     = "Te-Mag Rest"
Te_Mag_Force_Centre   = "Te-Mag Force Centre"
Te_Mag_RestPlus = "Te-Mag RestPlus"



@contextmanager
def group(titel, mode=None):
    Itr.group(titel).exec(mode)
    yield
    Itr.group_end().exec(mode)



@contextmanager
def parallel_execution_of(subroutine, repeat=1):
    # todo improve this idea: execute repeatably one after other and only at end wait.
    # for rep in range(repeat):
    if repeat == 1:
        Itr.subroutine(subroutine, Itr.subroutine.Continues).exec()
        yield
        Itr.subroutine(subroutine, Itr.subroutine.Waits_previous).exec()
    else:
        # rep_sub = br"C:\Prog\robotevo\EvoScriPy\repeat_subroutine.esc" .decode(EvoMode.Mode.encoding)
        Itr.variable("repetitions",
                     repeat,
                     queryString="How many time repeat the subroutine?",
                     type=Itr.variable.Numeric
                     ).exec()

        Itr.variable("subroutine",
                     subroutine,
                     queryString="The subroutine path",
                     type=Itr.variable.String
                     ).exec()

        Itr.subroutine(Rbt.rep_sub, Itr.subroutine.Continues).exec()
        yield
        Itr.subroutine(Rbt.rep_sub, Itr.subroutine.Waits_previous).exec()

@contextmanager
def incubation(minutes, timer=1):
    Itr.startTimer(timer).exec()
    yield
    Itr.waitTimer(timer=timer, timeSpan= minutes*60).exec()


@contextmanager
def opening_example(filename):
    f = open(filename) # IOError is untouched by GeneratorContext
    try:
        yield f
    finally:
        f.close() # Ditto for errors here (however unlikely)

# OK  autom create replicates when preMix > Well.maxVol, and vol > tip.maxVol ? NumCompon > nTips ?
# OK  implement preserveTips and usePreservedTips !!
# OK  mix well <B-beads
# OK  Elution buffer to eppis !!!
# OK  implement accumulated volume
# OK  implement actualize vol in reactives in pipette
# OK  comentar las replicas, como 2x b-beads
# OK  parse WorkTable. Create "temporal" list of grid/rack/labware, and check with created or create
# OK  parse WorkTable from the real backup! Create real abjects list (carrie and labware types, and LiqClass
# OK?  implement use only tips filled
# TODO  implement Debugger: prompt and or wait
# OK  implement with drop(true or false): with reuse and drop(): etc. to restore previous settings   - ok ?!
# OK  write the total vol to spread.                      - ok ?!
# OK  actualize liquid classes                            - ok ?!
# OK  poner IC MS2 mas cerca (intercambiar con b-beads)   - ok ?!
# OK  test no drop                                        - ok ?!
# OK  reimplementar rest... for waste                     - ok ?!


