__author__ = 'qPCR4vir'

#from Instruction_Base import *
#from Instructions import *
import Labware as Lab

TeMg_Heat = Lab.Labware(Lab.TeMag48, Lab.Labware.Location(14, 0), "48 Pos Heat")
TeMag = Lab.Labware(Lab.TeMag48, Lab.Labware.Location(14, 1), "48PosMagnet")

tipMask = []  # mask for one tip of index ...
tipsMask = []  # mask for the first tips
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2 ** tip - 1]

def_nTips = 4
nTips = def_nTips
Tip_1000maxVol = Lab.DiTi_1000ul.maxVol
Tip_200maxVol = 190


class Tip:
    def __init__(self, maxVol=1000):
        self.vol = 0
        self.maxVol = maxVol


class Robot:
    """ Maintain an intern state.
    Can have more than one arm in a dictionary that map an index with the actual arm.
    One of the arms can be set as "current" and is returned by curArm()
    Most of the changes in state are made by the implementation of the low level instructions, while the protocols can
    "observe" the state to make all kind of optimizations and organizations previous to the actual instruction call
    """
    class Arm:
        DiTi = 0
        Fixed = 1
        Aspire = 1
        Dispense = -1

        def __init__(self, nTips, index, workingTips=None, tipsType=DiTi): # index=Pipette.LiHa1
            """

            :param nTips:
            :param index: int. for example: index=Pipette.LiHa1
            :param workingTips: some tips maybe broken or permanently unused.
            :param tipsType:
            """
            self.index = index
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips] # todo implement
            self.tipsType = tipsType
            self.nTips = nTips
            self.Tips = [None] * nTips

        def mask_to_getTips(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
            """     Mount only one kind of tip at a time
                    :rtype : int
                    :param tip_mask:
                    :param maxVol: int. the maximum volume allowed in microliters
                    :return: the mask that can be used
                    :raise "Tip already in position " + str(i):
                    """
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "A Tip with max Vol=" + str(tp.maxVol) + " already in position " + str(i)
                    # self.Tips[i] = Tip(maxVol)
            return tip_mask

        def getTips(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
            """     Mount only one kind of tip at a time
                    :rtype : int
                    :param tip_mask:
                    :param maxVol: int. the maximum volume allowed in microliters
                    :return: the mask that can be used
                    :raise "Tip already in position " + str(i):
                    """
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "A Tip with max Vol=" + str(tp.maxVol) + " already in position " + str(i)
                    self.Tips[i] = Tip(maxVol)
            return tip_mask

        def mask_to_getMoreTips(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
            """ Mount only the tips with are not already mounted.
                Mount only one kind of tip at a time, but not necessary the same of the already mounted.
                    :rtype : int
                    :param tip_mask: int
                    :param maxVol: int  max microliter
                    :return: the mask that can be used
                    """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        3 self.Tips[i] = Tip(maxVol)
            return tip_mask

        def getMoreTips(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
            """ Mount only the tips with are not already mounted.
                Mount only one kind of tip at a time, but not necessary the same of the already mounted.
                    :rtype : int
                    :param tip_mask: int
                    :param maxVol: int  max microliter
                    :return: the mask that can be used
                    """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        self.Tips[i] = Tip(maxVol)
            return tip_mask

        def drop(self, tip_mask=-1) -> int:
            """ Drop tips only if needed
            :param tip_mask: int
            :return: the mask that can be used with, is "True" if tips actually ned to be drooped
            :rtype : int
            """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # in position
                        self.Tips[i] = None
                    else:
                        tip_mask ^= (1 << i)  # already drooped
            return tip_mask

        def pipette(self, action, volume, tip_mask=-1) -> (list, int):
            """ Check and actualize the robot Arm state to aspire [vol]s with a tip mask.
                    Using the tip mask will check that you are not trying to use an unmounted tip.
                    vol values for unsettled tip mask are ignored.

                    :rtype : (list, int)
                    :param action: +1:aspire, -1:dispense
                    :param volume: one vol for all tips, or a list of vol
                    :param tip_mask: -1:all tips
                    :return: a lis of vol to pipette, and the mask

                    """
            if isinstance(volume, (float, int)):
                vol = [volume] * self.nTips
            else:
                vol = list(volume)
                d = self.nTips - len(vol)
                vol += [0]*(d if d > 0 else 0 )
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    assert tp is not None, "No tp in position " + str(i)
                    nv = tp.vol + action * vol[i]
                    if 0 < nv < tp.maxVol:
                        self.Tips[i].vol = nv
                        continue
                    msg = str(i + 1) + " changing volume from " + str(tp.vol) + " to " + str(nv)
                    if 0 < nv:
                        raise BaseException('To few Vol in tip ' + msg)
                    raise BaseException('To much Vol in tip ' + msg)
                else:
                    vol[i] = None
            return vol, tip_mask

    def __init__(self, index,arms=None, nTips=None,
                  workingTips=None,
                 tipsType=Arm.DiTi, templateFile=None): # index=Pipette.LiHa1
        """

        :param arms:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        self.arms = arms if isinstance(arms, dict) else \
            {arms.index: arms} if isinstance(arms, Robot.Arm) else \
                {arms.index: Robot.Arm(nTips or def_nTips, index, workingTips, tipsType)}

        self.worktable = Lab.WorkTable(templateFile)
        self.def_arm = index  # or Pipette.LiHa1
        self.droptips = True
        self.reusetips = False
        self.preservetips = False
        self.usePreservedtips = False

    def set_worktable(self,templateFile):
        self.worktable = Lab.WorkTable(templateFile)

    def dropTips(self, drop=True):
        self.droptips, drop = drop, self.droptips
        return drop

    def reuseTips(self, reuse=True):
        self.reusetips, reuse = reuse, self.reusetips
        return reuse

    def preserveTips(self, preserve=True):
        self.preservetips, preserve = preserve, self.preservetips
        return preserve

    def usePreservedTips(self, usePreserved=True):
        self.usePreservedtips, usePreserved = usePreserved, self.usePreservedtips
        return usePreserved

    def curArm(self, arm=None):
        if arm is not None: self.def_arm = arm
        return self.arms[self.def_arm]

    def getTips(self, TIP_MASK=-1, maxVol=Tip_1000maxVol):
        # todo Find the correct rack in the worktable and the current position to pick.
        if self.reusetips:
            TIP_MASK = self.curArm().getMoreTips(TIP_MASK, maxVol)
        else:
            self.dropTips(TIP_MASK)
            TIP_MASK = self.curArm().getTips(TIP_MASK, maxVol)
        return TIP_MASK

    def mask_to_getTips(self, TIP_MASK=-1, maxVol=Tip_1000maxVol):
        if self.reusetips:
            TIP_MASK = self.curArm().mask_to_getMoreTips(TIP_MASK, maxVol)
        else:
            self.dropTips(TIP_MASK)
            TIP_MASK = self.curArm().mask_to_getTips(TIP_MASK, maxVol)
        return TIP_MASK



    def dropTips(self, TIP_MASK=-1): # todo coordine protocol
        if not self.droptips: return 0
        TIP_MASK = self.curArm().drop(TIP_MASK)
        return TIP_MASK

    def dispense(self, tip, labware, vol=None): # todo implement a coordinate call to arm and lab

        self.curArm().dispense(vol, tipMask[tip])

    def aspiremultiTips(self, tips, reactive, vol=None):
        if not isinstance(vol, list):
            vol = [vol] * tips
        mask = tipsMask[tips]
        nTip = reactive.autoselect(tips)
        asp = aspirate(mask, reactive.defLiqClass, vol, reactive.labware)
        curTip = 0
        while curTip < tips:
            nextTip = curTip + nTip
            nextTip = nextTip if nextTip <= tips else tips
            mask = tipsMask[curTip] ^ tipsMask[nextTip]
            self.curArm().aspire(vol, mask)
            asp.tipMask = mask
            asp.exec()
            curTip = nextTip

    def dispensemultiwells(self, tips, liq_class, labware, vol):
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = tipsMask[tips]
        self.curArm().dispense(vol, om)
        dispense(om, liq_class, vol, labware).exec()


    def makePreMix(self, pMix, NumSamples=None):
        NumSamples = NumSamples or React.NumOfSamples

        l = pMix.labware
        msg = "preMix: {:.1f} µL of {:s} into {:s}[grid:{:d} site:{:d} well:{:d}] from {:d} components:".format(
            pMix.minVol(NumSamples), pMix.name, l.label, l.location.grid, l.location.site + 1, pMix.pos + 1,
            len(pMix.components))
        comment(msg).exec()
        nc = len(pMix.components)
        assert nc <= self.curArm().nTips, \
            "Temporally the mix can not contain more than {:d} components.".format(self.curArm().nTips)

        self.getTips(tipsMask[nc])

        for i, react in enumerate(pMix.components):
            l = react.labware
            msg = "   {:d}- {:.1f} µL of {:s} from {:s}[grid:{:d} site:{:d} well:{:d}]".format(
                i + 1, react.minVol(NumSamples), react.name, l.label, l.location.grid, l.location.site + 1,
                react.pos + 1)
            comment(msg).exec()
            mV = self.curArm().Tips[i].maxVol
            r = react.minVol(NumSamples)
            while r > 0:
                dV = r if r < mV else mV
                self.aspire(i, react, dV)
                self.dispense(i, pMix, dV)
                r -= dV

        self.dropTips()

    def spread(self, volume=None, reactive=None, to_labware_region=None, optimize=True, NumSamples=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param volume: if not, volume is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(reactive, React.Reactive), 'A Reactive expected in reactive to spread'
        assert isinstance(to_labware_region, Labware), 'A Labware expected in to_labware_region to spread'

        if NumSamples:
            to_labware_region.selectOnly(range(NumSamples))
        else:
            if not to_labware_region.selected():
                to_labware_region.selectOnly(range(React.NumOfSamples))

        to = to_labware_region.selected()
        if optimize: to = to_labware_region.parallelOrder(to)
        NumSamples = len(to)
        SampleCnt = NumSamples

        volume = volume or reactive.volpersample

        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        maxMultiDisp_N = self.curArm().Tips[0].maxVol // volume  # assume all tips equal

        lf = reactive.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
            .format(v=volume, n=reactive.name, fg=lf.location.grid, fs=lf.location.site, fw=reactive.pos, do=str(to),
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        comment(msg).exec()
        availableDisp = 0

        while SampleCnt:
            if nt > SampleCnt: nt = SampleCnt
            if availableDisp == 0:
                dsp, rst = divmod(SampleCnt, nt)
                if dsp >= maxMultiDisp_N:
                    dsp = maxMultiDisp_N
                    vol = [volume * dsp] * nt
                    availableDisp = dsp
                else:
                    vol = [volume * (dsp + 1)] * rst + [volume * dsp] * (nt - rst)
                    availableDisp = dsp + bool(rst)
                self.aspiremultiTips(nt, reactive, vol)

            curSample = NumSamples - SampleCnt
            sel = to[curSample: curSample + nt]  # todo what if volume > maxVol_tip ?
            self.dispensemultiwells(nt, reactive.defLiqClass, to_labware_region.selectOnly(sel), [volume] * nt)
            availableDisp -= 1
            SampleCnt -= nt
        self.dropTips()

    def transfer(self, from_labware_region, to_labware_region, volume, using_liquid_class,
                 optimizeFrom=True, optimizeTo=True, NumSamples=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param from_reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param volume: if not, volume is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(from_labware_region, Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(to_labware_region, Labware), 'A Labware expected in to_labware_region to transfer'
        assert isinstance(using_liquid_class, tuple)

        if NumSamples:  # todo  select convenient def
            oriSel = range(NumSamples)
            dstSel = range(NumSamples)
        else:
            oriSel = to_labware_region.selected()
            dstSel = from_labware_region.selected()

            if not dstSel:
                if not oriSel:
                    oriSel = range(React.NumOfSamples)
                    dstSel = range(React.NumOfSamples)
                else:
                    dstSel = oriSel
            else:
                if not oriSel:
                    oriSel = dstSel
                else:
                    l = min(len(oriSel), len(dstSel))  # todo transfer the minimun of the selected ???? Best reise error
                    oriSel = oriSel[:l]
                    dstSel = dstSel[:l]
        if optimizeFrom: oriSel = from_labware_region.parallelOrder(oriSel)
        if optimizeTo: dstSel = to_labware_region.parallelOrder(dstSel)

        NumSamples = len(dstSel)
        SampleCnt = NumSamples

        assert isinstance(volume, (int, float))
        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        lf = from_labware_region
        lt = to_labware_region
        msg = "Transfer: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
            .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site, oo=str(oriSel), do=str(dstSel),
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        comment(msg).exec()
        Asp = aspirate(tipsMask[nt], using_liquid_class[0], volume, from_labware_region)
        Dst = dispense(tipsMask[nt], using_liquid_class[1], volume, to_labware_region)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                Asp.tipMask = tipsMask[nt]
                Dst.tipMask = tipsMask[nt]

            self.getTips(tipsMask[nt])  # todo what if volume > maxVol_tip ?
            self.curArm().aspire(volume, tipsMask[nt])
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            Asp.exec()

            Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
            self.curArm().dispense(volume, tipsMask[nt])
            Dst.exec()
            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel

    def waste(self, from_labware_region, using_liquid_class, volume, to_waste_labware=None, optimize=True):

        """

        :param from_labware_region:
        :param using_liquid_class:
        :param volume:
        :param to_waste_labware:
        :param optimize:
        :return:
        """
        to_waste_labware = to_waste_labware or WashWaste
        assert isinstance(from_labware_region, Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(volume, (int, float))
        # todo  select convenient def
        oriSel = from_labware_region.selected()
        if not oriSel:
            oriSel = range(React.NumOfSamples)
        if optimize:
            oriSel = from_labware_region.parallelOrder(oriSel)
        NumSamples = len(oriSel)
        SampleCnt = NumSamples

        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt:
            nt = SampleCnt
        tm = tipsMask[nt]
        self.getTips(tm)

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order:" \
                  .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
        comment(msg).exec()
        Asp = aspirate(tm, using_liquid_class[0], volume, from_labware_region)
        Dst = dispense(tm, using_liquid_class[1], volume, to_waste_labware)
        nt = to_waste_labware.autoselect(maxTips=nt)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                tm = tipsMask[nt]
                Asp.tipMask = tm
                Dst.tipMask = tm

            self.getTips(tm)
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            mV = self.curArm().Tips[0].maxVol
            r = volume
            while r > 0:
                dV = r if r < mV else mV
                r -= dV
                Asp.volume = dV
                self.curArm().aspire(dV, tm)
                Asp.exec()
                Dst.volume = dV
                self.curArm().dispense(dV, tm)
                Dst.exec()

            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        Asp.labware.selectOnly(oriSel)
        return oriSel

    def mix(self, in_labware_region, using_liquid_class, volume, optimize=True):

        """

        :param in_labware_region:
        :param using_liquid_class:
        :param volume:
        :param optimize:
        :return:
        """
        in_labware_region = in_labware_region or WashWaste
        assert isinstance(in_labware_region, Labware), 'A Labware expected in in_labware_region to be mixed'
        assert isinstance(volume, (int, float))
        oriSel = in_labware_region.selected()
        if not oriSel:
            oriSel = range(React.NumOfSamples)
        if optimize:
            oriSel = in_labware_region.parallelOrder(oriSel)
        NumSamples = len(oriSel)
        SampleCnt = NumSamples
        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt:
            nt = SampleCnt

        self.getTips(tipsMask[nt])
        volume = volume * 0.8
        mV = self.curArm().Tips[0].maxVol * 0.8
        volume = volume if volume < mV else mV

        lf = in_labware_region
        msg = "Mix: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order:" \
                  .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
        comment(msg).exec()
        mx = mix(tipsMask[nt], using_liquid_class, volume, in_labware_region)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                mx.tipMask = tipsMask[nt]

            self.getTips(tipsMask[nt])
            mx.labware.selectOnly(oriSel[curSample:curSample + nt])
            mx.exec()

            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        mx.labware.selectOnly(oriSel)
        return oriSel

    def wash_in_TeMag(self, reactive, wells=None, using_liquid_class=None, vol=None):
        if wells is None:
            wells = reactive.labware.selected() or range(React.NumOfSamples)
        if using_liquid_class is None:
            using_liquid_class = (reactive.defLiqClass, reactive.defLiqClass)

        self.spread(reactive=reactive, to_labware_region=TeMag.selectOnly(wells))
        subroutine("avr_MagMix.esc", subroutine.Continues).exec()
        self.mix(TeMag.selectOnly(wells), reactive.defLiqClass, vol or reactive.volpersample)
        subroutine("avr_MagMix.esc", subroutine.Waits_previous).exec()
        self.waste(TeMag.selectOnly(wells), using_liquid_class, vol or reactive.volpersample)


current = None


class ProtocolStep:
    pass


class MakeMix(ProtocolStep):
    pass


class DistrReactive(ProtocolStep):
    pass


class Transfer(ProtocolStep):
    def __init__(self, src, dest, vol):
        pass


class Collect(ProtocolStep):
    def __init__(self, src, dest, vol):
        pass


class Waste(Collect):
    def __init__(self, src, dest, vol):
        pass

