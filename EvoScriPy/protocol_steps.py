# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

from contextlib import contextmanager
import EvoScriPy.Robot as Rbt
import EvoScriPy.Instructions as Itr
import EvoScriPy.Reactive as Rtv
import EvoScriPy.Labware as Lab
import EvoScriPy.EvoMode as EvoMode

__author__ = 'qPCR4vir'


def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')


# output_filename = '../current/AWL'
class Executable:
    """ Each executable need to implement these functions.

    """

    # parameters to describe this program
    name = "undefined"
    versions = {"none": not_implemented}
    isPipeline = False     # todo revise !


    class Parameter:
        # parameters to describe a run of this program

        def __init__(self, GUI       = None,
                           run_name  = None):
            self.GUI      = GUI
            self.run_name = run_name


        def initialize(self):
            if (self.GUI):
                self.GUI.initialize_parameters(self)


    def __init__(self,   parameters = None):

        self.parameters  = parameters or Protocol.Parameter()
        self.initialized = False
        self.Reactives   = []
        Rtv.Reactive.SetReactiveList(self)  # todo Revise !!!

    def set_defaults(self):
        """Set initial values that will not be rest during secondary initializations.
        The "primary initialization" maybe a light one, like defining the list of versions available.
        Here, for example, initialize the list of reactive.
        """
        print('set def in Protocol')

    def options(self):
        """
        :return: the list of different variants or version of the protocol implemented by this protocol
        """
        return self.options_list    # todo revise    versions???

    def initialize(self):
        """It is called "just in case" to ensure we don't go uninitialized in lazy initializing scenarios.
        """
        if not self.initialized:
            self.set_defaults()

    def Run(self):
        '''
        Here we haccesscces to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with getLabware()
        :return:
        '''
        self.initialize()
        self.preCheck()
        self.CheckList()
        self.postCheck()
        self.done()


    def preCheck(self):
        pass

    def CheckList(self):
        pass

    def postCheck(self):
        pass

    def done(self):
        pass


class Protocol (Executable):
    """ Each custom protocol need to implement these functions.

    """

    class Parameter (Executable.Parameter):
        # parameters to describe a run of this program

        def __init__(self, GUI                         = None,
                           worktable_template_filename = None,
                           output_filename             = None,
                           firstTip                    = None):

            self.worktable_template_filename = worktable_template_filename or ""
            self.output_filename             = output_filename or '../current/AWL'
            self.firstTip                    = firstTip if firstTip is not None else ''
            Executable.Parameter.__init__(self, GUI)

    def __init__(self,       # worktable_template_fn ,
                 nTips=4,
                 parameters = None):
        Executable.__init__(self, parameters)
        self.nTips       = nTips
        self.EvoMode     = None
        self.set_EvoMode()


    def init_EvoMode(self):
        self.iRobot = EvoMode.iRobot(Itr.Pipette.LiHa1, nTips=self.nTips)
        self.Script = EvoMode.Script(template=self.parameters.worktable_template_filename,
                                     filename=self.parameters.output_filename + '.esc',
                                     robot=self.iRobot.robot)
        self.comments_ = EvoMode.Comments(filename=self.parameters.output_filename + '.protocol.txt')
        self.EvoMode = EvoMode.multiple([self.iRobot,
                                         self.Script,
                                         EvoMode.AdvancedWorkList(self.parameters.output_filename + '.gwl'),
                                         EvoMode.ScriptBody(self.parameters.output_filename + '.txt'),
                                         EvoMode.StdOut(),
                                         self.comments_
                                         ])
        EvoMode.current = self.EvoMode
        self.worktable = self.iRobot.robot.worktable  # shortcut !!
        self.robot = self.iRobot.robot
        assert (self.iRobot.robot.curArm().nTips == self.nTips )

    def set_EvoMode(self):
        if not self.EvoMode:
            self.init_EvoMode()
        else:
            EvoMode.current = self.EvoMode
        self.iRobot.set_as_current()

    def comments(self):
        return self.comments_.comments

    def Run(self):
        '''
        Here we haccesscces to the "internal robot" self.iRobot, with in turn have access to the used Work Table,
        self.iRobot.worktable from where we can obtain labwares with getLabware()
        :return:
        '''
        self.set_EvoModet()

        self.initialize()
        self.set_EvoMode()

        self.preCheck()
        self.set_EvoMode()

        self.CheckList()
        self.set_EvoMode()

        self.postCheck()
        self.set_EvoMode()

        self.done()

    def CheckList(self):
        self.set_EvoMode()
        if (self.parameters.GUI):
            self.parameters.GUI.CheckList(self)
        self.set_EvoMode()

    def done(self):
        self.EvoMode.done()
        Executable.done(self)

    def go_first_pos(self):
        if self.parameters.firstTip:
            rack, firstTip = self.worktable.get_first_pos(posstr=self.parameters.firstTip)
            Itr.set_DITI_Counter2(labware=rack, posInRack=firstTip).exec()



class Pipeline (Executable):
    """ Each custom Pipeline need to implement these functions.

    """
    name = "Pipeline"
    isPipeline = True

    class Parameter (Executable.Parameter):
        # parameters to describe a run of this program

        def __init__(self, GUI                         = None,
                           protocols                   = None):
            # assert isinstance(protocols, list)
            self.Protocol_classes = protocols or [] #[[Executable, "don't run"]]

            Executable.Parameter.__init__(self, GUI)


    def __init__(self,     parameters = None):
        self.protocol_runs = {}
        Executable.__init__(self, parameters)

    def CheckList(self):
        if (self.parameters.GUI):
            self.parameters.GUI.CheckPipeline(self)

    def RunPi(self):

        for protocol_class, run_name in self.parameters.Protocol_classes:
            print(protocol_class + run_name)



Water_free = "Water free"  # General. No detect and no track small volumes < 50 µL

SerumLiqClass      = "Serum Asp preMix3"
TissueHomLiqClass  = "Serum Asp"


B_liquidClass   = "Water free cuvette"
W_liquidClass   = Water_free #    or "AVR-Water free DITi 1000"
Std_liquidClass = Water_free #    or "Water free dispense DiTi 1000"
Small_vol_disp  = "Water wet"
Beads_LC_1      = "MixBeads_1"
Beads_LC_2      = "MixBeads_2"

Te_Mag_LC       = "Te-Mag"          # "Water free" but uncentred
Te_Mag_Centre   = "Te-Mag Centre"   # To Centre after normal aspiration.
Te_Mag_Rest     = "Te-Mag Rest"
Te_Mag_Force_Centre   = "Te-Mag Force Centre"
Te_Mag_RestPlus = "Te-Mag RestPlus"


def set_dropTips(drop=True)->bool:
    """
    Drops the tips at THE END of the whole action? like after spread of the reactive into various targets
    :param drop:
    :return:
    """
    return Rbt.Robot.current.set_dropTips(drop)


def set_allow_air(allow_air=0.0)->float:
    return Rbt.Robot.current.set_allow_air(allow_air)


def reuseTips(reuse=True)->bool:
    """     Reuse the tips or drop it and take new after each action?
    :param reuse:
    :return:
    """
    return Rbt.Robot.current.reuseTips(reuse)


def reuse_tips_and_drop(reuse=True, drop=True)->(bool, bool):
    return set_dropTips(drop), reuseTips(reuse)

def preserveTips(preserve=True)->bool:
    return Rbt.Robot.current.preserveTips(preserve)

def preserveingTips()->bool:
    return Rbt.Robot.current.preservetips

def usePreservedTips(usePreserved=True)->bool:
    return Rbt.Robot.current.usePreservedTips(usePreserved)

def moveTips(zMove, zTarget, offset, speed, TIP_MASK=-1):
    pass # Itr.moveLiha

def getTips(TIP_MASK=-1, type=None, selected_samples=None):
    robot = Rbt.Robot.current                                                         # todo revice !!!
    assert isinstance(robot, Rbt.Robot)
    mask = TIP_MASK = TIP_MASK if TIP_MASK != -1 else Rbt.tipsMask[robot.curArm().nTips]
    #if not Rbt.Robot.reusetips: # and Rbt.Robot.droptips

    if robot.usePreservedtips:
        with tips(drop=True, preserve=False): # drop tips from previous "buffer" in first pipetting
            dropTips(TIP_MASK)
        where = robot.where_are_preserved_tips(selected_samples, TIP_MASK, type)
        nTips = robot.curArm().nTips
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
        type=type or Lab.def_DiTi
        I = Itr.getDITI2(TIP_MASK, type, arm=robot.def_arm)
        I.exec()
    return mask # todo REVISE !!   I.tipMask


def dropTips(TIP_MASK=-1):

    robot = Rbt.Robot.current
    assert isinstance(robot, Rbt.Robot)
    if robot.preservetips:
        where = robot.where_preserve_tips(TIP_MASK)
        nTips = robot.curArm().nTips
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

def aspire( tip, reactive, vol=None):
    """
    Aspire vol with ONE tip from reactive
    :param self:
    :param tip:
    :param reactive:
    :param vol:
    """
    if vol is None:
        vol = reactive.minVol()
    v = [0] * Rbt.Robot.current.curArm().nTips
    v[tip] = vol
    reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
    Itr.aspirate(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

def dispense( tip, reactive, vol=None): # OK coordinate with robot
    """
    Dispense vol with ONE tip to reactive
    :param tip:
    :param reactive:
    :param vol:
    """
    vol = vol or reactive.minVol()  # really ??
    reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
    v = [0] * Rbt.Robot.current.curArm().nTips
    v[tip] = vol
    Itr.dispense(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()


def mix_reactive(reactive, LiqClass=None, cycles=3, maxTips=1, v_perc=90):
    """

    :param reactive:
    :param LiqClass:
    :param cycles:
    :param maxTips:
    :param v_perc:
    :return:
    """
    assert isinstance(reactive, Rtv.Reactive)
    v_perc /= 100.0
    vol = []
    reactive.autoselect(maxTips)
    for tip, w in enumerate(reactive.labware.selected_wells()):
        v = w.vol * v_perc
        vm = Rbt.Robot.current.curArm().Tips[tip].type.maxVol * 0.9
        vol += [min(v, vm)]
    Itr.mix(Rbt.tipsMask[len(vol)],
            liquidClass=LiqClass,
            volume=vol,
            labware=reactive.labware,
            cycles=cycles).exec()


def multidispense_in_replicas(tip, reactive, vol):
    """ Multi-dispense of the content of ONE tip into the reactive replicas

    :param tip:
    :param reactive:
    :param vol:
    """
    assert isinstance(vol, list)
    re = reactive.Replicas
    assert len(vol) == len(re)
    for v, w in zip(vol, re):
        Itr.dispense(Rbt.tipMask[tip], Rbt.Robot.current.curArm().Tips[tip].origin.reactive.defLiqClass,
                     # reactive.defLiqClass,
                     v, w.labware.selectOnly([w.offset])).exec()

def aspiremultiTips( tips, reactive, vol=None, LiqClass=None):
        if not isinstance(vol, list):
            vol = [vol] * tips
        LiqClass = LiqClass or reactive.defLiqClass

        mask = Rbt.tipsMask[tips]
        nTip = reactive.autoselect(tips)
        asp = Itr.aspirate(mask, LiqClass, vol, reactive.labware)
        curTip = 0
        while curTip < tips:
            nextTip = curTip + nTip
            nextTip = nextTip if nextTip <= tips else tips
            mask = Rbt.tipsMask[curTip] ^ Rbt.tipsMask[nextTip]
            #Rbt.Robot.current.curArm().aspire(vol, mask)
            asp.tipMask = mask
            asp.exec()
            curTip = nextTip

def dispensemultiwells( tips, liq_class, labware, vol):
        """ One dispense of multitip in multiwell with different vol

        :param tips:
        :param liq_class:
        :param labware:
        :param vol:
        """
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = Rbt.tipsMask[tips]
        # Rbt.Robot.current.curArm().dispense(vol, om)
        Itr.dispense(om, liq_class, vol, labware).exec()

def make( what, NumSamples=None): # OK coordinate with protocol
        if isinstance(what, Rtv.preMix): makePreMix(what, NumSamples)

def makePreMix( preMix, NumSamples=None):
        NumSamples = NumSamples or Rtv.NumOfSamples
        l = preMix.labware
        msg = "preMix: {:.1f} µL of {:s}".format(preMix.minVol(NumSamples), preMix.name)
        with group(msg):
            msg += " into {:s}[grid:{:d} site:{:d} well:{:d}] from {:d} components:".format(
                l.label, l.location.grid, l.location.site + 1, preMix.pos + 1, len(preMix.components))
            Itr.comment(msg).exec()
            nc = len(preMix.components)
            nr = len(preMix.Replicas)
            nt = Rbt.Robot.current.curArm().nTips
            assert nc <= nt, "Temporally the mix can not contain more than {:d} components.".format(nt)
            dt = nt - nc
            samples_per_replicas = [(NumSamples + nr - (i+1))//nr for i in range(nr)]
            with tips(Rbt.tipsMask[nc]):   #  want to use preserved ?? selected=??
                for i, react in enumerate(preMix.components):
                    l = react.labware
                    r = react.volpersample*NumSamples*preMix.excess
                    msg = "   {:d}- {:.1f} µL of {:s} from {:s}[grid:{:d} site:{:d} well:{:d}]".format(
                        i + 1, r, react.name, l.label, l.location.grid, l.location.site + 1,
                        react.pos + 1)
                    Itr.comment(msg).exec()
                    mV = Rbt.Robot.current.curArm().Tips[i].type.maxVol # todo what if the tip are different?
                    while r > 0:
                        dV = r if r < mV else mV
                        aspire(i, react, dV)
                        multidispense_in_replicas(i, preMix, [sp/NumSamples * dV for sp in samples_per_replicas])
                        r -= dV


def spread( volume=None, reactive=None, to_labware_region=None, optimize=True, NumSamples=None, using_liquid_class=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param volume: if not, volume is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(reactive, Rtv.Reactive), 'A Reactive expected in reactive to spread'
        assert isinstance(to_labware_region, Lab.Labware), 'A Labware expected in to_labware_region to spread'
        nt = Rbt.Robot.current.curArm().nTips  # the number of tips to be used in each cycle of pippeting

        if NumSamples:
            to_labware_region.selectOnly(range(NumSamples))
        else:
            if not to_labware_region.selected():
                to_labware_region.selectOnly(range(Rtv.NumOfSamples))

        to = to_labware_region.selected()
        if optimize: to = to_labware_region.parallelOrder(nt, to)
        NumSamples = len(to)
        SampleCnt = NumSamples

        volume = volume or reactive.volpersample

        Asp_liquidClass, Dst_liquidClass = (reactive.defLiqClass, reactive.defLiqClass) if using_liquid_class is None else \
                                           (using_liquid_class[0] or reactive.defLiqClass, using_liquid_class[1] or reactive.defLiqClass)


        if nt > SampleCnt: nt = SampleCnt

        lf = reactive.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}".format(v=volume, n=reactive.name)
        with group(msg):
            msg += " ({v:.1f} µL total) from [grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(v=reactive.minVol(), fg=lf.location.grid, fs=lf.location.site+1, fw=reactive.pos+1, do=str([i+1 for i in to]),
                        to=lt.label, tg=lt.location.grid, ts=lt.location.site+1)
            Itr.comment(msg).exec()
            availableDisp = 0
            while SampleCnt:
                if nt > SampleCnt: nt = SampleCnt
                with tips(Rbt.tipsMask[nt], usePreserved=False, preserve=False):  # OK want to use preserved ?? selected=??
                    maxMultiDisp_N = Rbt.Robot.current.curArm().Tips[0].type.maxVol // volume  # assume all tips equal
                    dsp, rst = divmod(SampleCnt, nt)
                    if dsp >= maxMultiDisp_N:
                        dsp = maxMultiDisp_N
                        vol = [volume * dsp] * nt
                        availableDisp = dsp
                    else:
                        vol = [volume * (dsp + 1)] * rst + [volume * dsp] * (nt - rst)
                        availableDisp = dsp + bool(rst)

                    aspiremultiTips(nt, reactive, vol, LiqClass=Asp_liquidClass)

                    while availableDisp:
                        if nt > SampleCnt: nt = SampleCnt
                        curSample = NumSamples - SampleCnt
                        sel = to[curSample: curSample + nt]  # todo what if volume > maxVol_tip ?
                        dispensemultiwells(nt, Dst_liquidClass, to_labware_region.selectOnly(sel), [volume] * nt)
                        availableDisp -= 1
                        SampleCnt -= nt


def transfer( from_labware_region, to_labware_region, volume, using_liquid_class=None,
                 optimizeFrom=True, optimizeTo=True, NumSamples=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param from_reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param volume: if not, volume is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(from_labware_region, Lab.Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(to_labware_region, Lab.Labware), 'A Labware expected in to_labware_region to transfer'
        # assert isinstance(using_liquid_class, tuple)
        nt = Rbt.Robot.current.curArm().nTips  # the number of tips to be used in each cycle of pippeting

        if NumSamples:  # OK?  select convenient def
            oriSel = range(NumSamples)
            dstSel = range(NumSamples)
        else:
            oriSel = to_labware_region.selected()
            dstSel = from_labware_region.selected()

            if not dstSel:
                if not oriSel:
                    oriSel = range(Rtv.NumOfSamples)
                    dstSel = range(Rtv.NumOfSamples)
                else:
                    dstSel = oriSel
            else:
                if not oriSel:
                    oriSel = dstSel
                else:
                    l = min(len(oriSel), len(dstSel))  # todo transfer the minimun of the selected ???? Best reise error
                    oriSel = oriSel[:l]
                    dstSel = dstSel[:l]
        if optimizeFrom: oriSel = from_labware_region.parallelOrder(nt, oriSel)
        if optimizeTo: dstSel = to_labware_region.parallelOrder(nt, dstSel)

        NumSamples = len(dstSel)
        SampleCnt = NumSamples

        assert isinstance(volume, (int, float))
        if nt > SampleCnt: nt = SampleCnt
        lf = from_labware_region
        lt = to_labware_region
        Asp = Itr.aspirate(Rbt.tipsMask[nt], volume=volume, labware=from_labware_region)
        Dst = Itr.dispense(Rbt.tipsMask[nt], volume=volume, labware=to_labware_region)
        msg = "Transfer: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += " [grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg=lf.location.grid, fs=lf.location.site+1, oo=str([i+1 for i in oriSel]),
                        do=str([i+1 for i in dstSel]),  to=lt.label, tg=lt.location.grid, ts=lt.location.site+1)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    Asp.tipMask = Rbt.tipsMask[nt]
                    Dst.tipMask = Rbt.tipsMask[nt]

                src = oriSel[curSample:curSample + nt]
                trg = dstSel[curSample:curSample + nt]
                spl = range(curSample, curSample + nt)

                sw = Asp.labware.selected_wells()

                if isinstance(using_liquid_class, tuple):
                    if using_liquid_class[0]:
                        Asp.liquidClass = using_liquid_class[0]
                    else:
                        Asp.liquidClass = sw[0].reactive.defLiqClass
                    if using_liquid_class[1]:
                        Dst.liquidClass = using_liquid_class[1]
                    else:
                        Dst.liquidClass = sw[0].reactive.defLiqClass
                else:
                    Asp.liquidClass = sw[0].reactive.defLiqClass
                    Dst.liquidClass = sw[0].reactive.defLiqClass

                with tips(Rbt.tipsMask[nt], selected_samples=spl):  # todo what if volume > maxVol_tip ?
                    Asp.labware.selectOnly(src)
                    Asp.exec()
                    Dst.labware.selectOnly(trg)
                    Dst.exec()
                    for s, d in zip(Asp.labware.selected_wells(), Dst.labware.selected_wells()):
                        d.track = s.track
                SampleCnt -= nt
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel


def waste( from_labware_region=None, using_liquid_class=None, volume=None, to_waste_labware=None, optimize=True):

    """

    :param from_labware_region:
    :param using_liquid_class:
    :param volume:
    :param to_waste_labware:
    :param optimize:
    :return:
    """
    to_waste_labware = to_waste_labware or Lab.def_WashWaste
    assert isinstance(from_labware_region, Lab.Labware), 'A Labware expected in from_labware_region to transfer'
    if not volume or volume< 0.0 : volume = 0.0
    assert isinstance(volume, (int, float))
    oriSel = from_labware_region.selected()
    nt = Rbt.Robot.current.curArm().nTips  # the number of tips to be used in each cycle of pippeting
    if not oriSel:
        oriSel = range(Rtv.NumOfSamples)
    if optimize:
        oriSel = from_labware_region.parallelOrder(nt, oriSel)
    NumSamples = len(oriSel)
    SampleCnt = NumSamples

    if nt > SampleCnt:
        nt = SampleCnt
    tm = Rbt.tipsMask[nt]
    nt = to_waste_labware.autoselect(maxTips=nt)
    mV = Lab.def_DiTi.maxVol      # todo revise !! What tip tp use !

    Rest = 50  # the volume we cannot more aspire with liquid detection, to small, collisions
    RestPlus = 50
    CtrVol = 0.5

    if volume:
        v = volume
    else:
        v = from_labware_region.Wells[oriSel[0]].vol

    Asp = Itr.aspirate(tm, Te_Mag_LC, volume, from_labware_region)
    # Asp = Itr.aspirate(tm, using_liquid_class[0], volume, from_labware_region)
    Dst = Itr.dispense(tm, using_liquid_class, volume, to_waste_labware)
    # Ctr = Itr.moveLiha(Itr.moveLiha.y_move, Itr.moveLiha.z_start, 3.0, 2.0, tm, from_labware_region)

    lf = from_labware_region
    msg = "Waste: {v:.1f} µL of {n:s}".format(v=v, n=lf.label)
    with group(msg):
        msg += " [grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) \
                                 + str([i+1 for i in oriSel])
        Itr.comment(msg).exec()
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                tm = Rbt.tipsMask[nt]
                Asp.tipMask = tm
                Dst.tipMask = tm

            sel = oriSel[curSample:curSample + nt]
            spl = range(curSample, curSample + nt)
            Asp.labware.selectOnly(sel)

            if volume:
                r = volume   # r: Waste_available yet; volume: to be Waste
            else:
                vols = [w.vol for w in Asp.labware.selected_wells()]
                r_min, r_max = min(vols), max(vols)
                assert r_min == r_max
                r = r_max

            if not using_liquid_class:
                    if sel:
                        Dst.liquidClass = Asp.labware.selected_wells()[0].reactive.defLiqClass

            with tips(tm, drop=True, preserve=False, selected_samples=spl):
                while r > Rest:      # dont aspire Rest with these Liq Class (Liq Detect)
                    dV = r if r < mV else mV
                    if dV < Rest: break # ??
                    dV -= Rest       # the last Rest uL have to be aspired with the other Liq Class
                    Asp.volume = dV  #  with Liq Class with Detect: ">> AVR-Serum 1000 <<	365"
                    Dst.volume = dV
                    Asp.liquidClass = Te_Mag_LC # ">> AVR-Serum 1000 <<	365"  # "No Liq Detect"
                    Asp.exec()
                    Asp.volume = CtrVol
                    Asp.liquidClass = Te_Mag_Centre


                    with tips(allow_air=CtrVol):
                        Asp.exec()
                        if dV + Rest + RestPlus + 2*CtrVol > mV:
                            Dst.exec()
                            r -= dV
                            Dst.volume = 0
                        else:
                            break

                Asp.volume = Rest
                Asp.liquidClass =  Te_Mag_Rest # ">> AVR-Serum 1000 <<	367" # "No Liq Detect"
                with tips(allow_air=Rest):
                        Asp.exec()
                Asp.volume = CtrVol
                Asp.liquidClass = Te_Mag_Force_Centre
                with tips(allow_air=CtrVol):
                        Asp.exec()
                Asp.volume = RestPlus
                Asp.liquidClass =  Te_Mag_RestPlus # ">> AVR-Serum 1000 <<	369" # "No Liq Detect"
                with tips(allow_air=RestPlus):
                        Asp.exec()
                #Ctr.exec()
                Asp.volume = CtrVol
                Asp.liquidClass = Te_Mag_Force_Centre
                Dst.volume += Rest + RestPlus
                with tips(allow_air=CtrVol):
                        Asp.exec()
                with tips(allow_air=Rest + RestPlus):
                        Dst.exec()

            SampleCnt -= nt
        Asp.labware.selectOnly(oriSel)
    Itr.wash_tips(wasteVol=4).exec()
    return oriSel


def mix( in_labware_region, using_liquid_class=None, volume=None, optimize=True):

    """
    Mix each of the reactive in the selected region of the labware
    :param in_labware_region:
    :param using_liquid_class:
    :param volume:
    :param optimize:
    :return:
    """
    mix_p = 0.9
    in_labware_region = in_labware_region or Lab.WashWaste
    assert isinstance(in_labware_region, Lab.Labware), 'A Labware expected in in_labware_region to be mixed'
    if not volume or volume< 0.0 : volume = 0.0
    assert isinstance(volume, (int, float))
    oriSel = in_labware_region.selected()
    nt = Rbt.Robot.current.curArm().nTips  # the number of tips to be used in each cycle of pippeting
    if not oriSel:
        oriSel = range(Rtv.NumOfSamples)
    if optimize:
        oriSel = in_labware_region.parallelOrder( nt, oriSel)
    NumSamples = len(oriSel)
    SampleCnt = NumSamples
    if nt > SampleCnt:
        nt = SampleCnt
    # mV = Rbt.Robot.current.curArm().Tips[0].type.maxVol * 0.8
    mV = Lab.def_DiTi.maxVol * mix_p    # What tip tp use !
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
            spl = range(curSample, curSample + nt)
            with tips(Rbt.tipsMask[nt], selected_samples=spl):
                mV = Rbt.Robot.current.curArm().Tips[0].type.maxVol * mix_p
                mx.labware.selectOnly(sel)
                if not using_liquid_class:
                    if sel:
                        mx.liquidClass = mx.labware.selected_wells()[0].reactive.defLiqClass
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
def group(titel, mode=None):
    Itr.group(titel).exec(mode)
    yield
    Itr.group_end().exec(mode)


@contextmanager
def tips(tipsMask=None, reuse=None,     drop=None,
                        preserve=None,  usePreserved=None, selected_samples=None,
                        allow_air=None, drop_first=False,   drop_last=False):
    '''

    :param tipsMask:
    :param reuse: Reuse the tips or drop it and take new BEFORE each individual action
    :param drop: Drops the tips AFTER each individual action? like after one aspiration and spread of the reactive into various target
    :param preserve:
    :param usePreserved:
    :param selected_samples:
    :param allow_air:
    :param drop_first: Reuse the tips or drop it and take new once BEFORE the whole action
    :param drop_last: Drops the tips at THE END of the whole action
    :return:
    '''

    if drop_first:  dropTips()
    if reuse        is not None: reuse_old          = reuseTips       (reuse       )
    if drop         is not None: drop_old           = set_dropTips    (drop        )
    if preserve     is not None: preserve_old       = preserveTips    (preserve    )
    if usePreserved is not None: usePreserved_old   = usePreservedTips(usePreserved)
    if allow_air    is not None: allow_air_old      = set_allow_air   (allow_air  )

    if tipsMask     is not None: tipsMask_old     = getTips         (tipsMask, selected_samples=selected_samples)

    yield

    if tipsMask     is not None: tipsMask     = dropTips        (tipsMask_old)

    if reuse        is not None: reuse        = reuseTips       (reuse_old       )
    if drop         is not None: drop         = set_dropTips    (drop_old        )
    if preserve     is not None: preserve     = preserveTips    (preserve_old    )
    if usePreserved is not None: usePreserved = usePreservedTips(usePreserved_old)
    if allow_air    is not None: allow_air    = set_allow_air   (allow_air_old   )
    if drop_last:   dropTips()

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
        Itr.variable("repetitions", repeat, queryString="How many time repeat the subroutine?",
                      type=Itr.variable.Numeric).exec()
        Itr.variable("subroutine",subroutine, queryString="The subroutine path",
                      type=Itr.variable.String).exec()
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

# TODO  autom create replicates when preMix > Well.maxVol, and vol > tip.maxVol ? NumCompon > nTips ?
# OK  implement preserveTips and usePreservedTips !!
# OK  mix well <B-beads
# TODO  Elution buffer to eppis !!!
# OK  implement accumulated volume
# OK  implement actualize vol in reactives in pipette
# TODO  comentar las replicas, como 2x b-beads
# OK  parse WorkTable. Create "temporal" list of grid/rack/labware, and check with created or create
# TODO  parse WorkTable from the real backup! Create real abjects list (carrie and labware types, and LiqClass
# OK?  implement use only tips filled
# TODO  implement Debugger: prompt and or wait
# OK  implement with drop(true or false): with reuse and drop(): etc. to restore previous settings   - ok ?!
# OK  write the total vol to spread.                      - ok ?!
# TODO  actualize liquid classes                            - ok ?!
# TODO  poner IC MS2 mas cerca (intercambiar con b-beads)   - ok ?!
# OK  test no drop                                        - ok ?!
# OK  reimplementar rest... for waste                     - ok ?!


