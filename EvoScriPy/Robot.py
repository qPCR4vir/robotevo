__author__ = 'qPCR4vir'

from Instructions import *
from Labware import WorkTable
import Reactive

tipMask = []  # mask for one tip of index ...
tipsMask = []  # mask for the first tips
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2 ** tip - 1]

def_nTips = 4


class Tip:
    def __init__(self, maxVol=1000):
        self.vol = 0
        self.maxVol = maxVol


class Robot:
    class Arm:
        DiTi = 0
        Fixed = 1

        def __init__(self, nTips, index=Pippet.LiHa1, workingTips=None, tipsType=DiTi):
            """

            :param nTips:
            :param index:
            :param workingTips:
            :param tipsType:
            """
            self.index = index
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips]
            self.tipsType = tipsType
            self.nTips = nTips
            self.Tips = [None] * nTips


        def getTips(self, tip_mask=-1, maxVol=1000):
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "Tip already in position " + str(i)
                    self.Tips[i] = Tip(maxVol)
            return tip_mask

        def getMoreTips(self, tip_mask=-1, maxVol=1000):
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        self.Tips[i] = Tip(maxVol)
            return tip_mask

        def drop(self, tip_mask=-1):
            """
            :rtype : True if actually ned to be drooped
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

        def aspire(self, vol, tip_mask=-1):  # todo more checks
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tip in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    assert tip is not None, "No tip in position " + str(i)
                    nv = tip.vol + vol[i]
                    if nv > tip.maxVol:
                        raise BaseException(
                            'To much Vol in tip ' + str(i + 1) + ' V=' + str(tip.vol) + '+' + str(vol[i]))
                    self.Tips[i].vol = nv

        def dispense(self, vol, tip_mask=-1):  # todo more checks
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tip in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tip is None:
                        raise "No tip in position " + str(i)
                    nv = tip.vol - vol[i]
                    assert nv >= 0, 'To few Vol in tip ' + str(i + 1) + ' V=' + str(tip.vol) + '-' + str(vol[i])
                    self.Tips[i].vol = nv


    class ProtocolStep:
        pass

    class makeMix(ProtocolStep):
        pass

    class distrReactive(ProtocolStep):
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


    def __init__(self, arms=None, nTips=def_nTips,
                 index=Pippet.LiHa1, workingTips=None,
                 tipsType=Arm.DiTi, templateFile=None):
        """

        :param arm:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        self.arms = arms if isinstance(arms, dict) else \
            {arms.index: arms} if isinstance(arms, Robot.Arm) else \
                {arms.index: Robot.Arm(nTips, index, workingTips, tipsType)}

        self.worktable = WorkTable(templateFile)
        self.def_arm = index
        self.droptips = True
        self.reusetips = False
        self.preservetips = False
        self.usePreservedtips = False

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

    def getTips(self, TIP_MASK=-1, maxVol=1000):
        if self.reusetips:
            TIP_MASK = self.curArm().getMoreTips(TIP_MASK, maxVol)
        else:
            self.dropTips(TIP_MASK)
            TIP_MASK = self.curArm().getTips(TIP_MASK, maxVol)
        if TIP_MASK:
            getDITI2(TIP_MASK, arm=self.def_arm).exec()
        return TIP_MASK

    def dropTips(self, TIP_MASK=-1):
        if not self.droptips: return 0
        TIP_MASK = self.curArm().drop(TIP_MASK)
        if TIP_MASK:
            dropDITI(TIP_MASK).exec()
        return TIP_MASK

    def make(self, what, NumSamples=None):
        if isinstance(what, Reactive.preMix): self.makePreMix(what, NumSamples)

    def aspire(self, tip, reactive, vol=None):
        if vol is None:
            vol = reactive.minVol()
        v = [0] * self.curArm().nTips
        v[tip] = vol
        reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
        self.curArm().aspire(v, tipMask[tip])
        aspirate(tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

    def dispense(self, tip, reactive, vol=None):
        vol = vol or reactive.minVol()  # really ??
        reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
        v = [0] * self.curArm().nTips
        v[tip] = vol
        self.curArm().dispense(v, tipMask[tip])
        dispense(tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

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
        NumSamples = NumSamples or Reactive.NumOfSamples

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
            self.aspire(i, react, react.minVol(NumSamples))
            self.dispense(i, pMix, react.minVol(NumSamples))

        self.dropTips()

    def spread(self, from_reactive, to_labware_region, Disp_V=None, optimize=True, NumSamples=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param from_reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param Disp_V: if not, Disp_V is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(from_reactive, Reactive.Reactive), 'A Reactive expected in from_reactive to spread'
        assert isinstance(to_labware_region, Labware.Labware), 'A Labware expected in to_labware_region to spread'

        if NumSamples:
            to_labware_region.selectOnly(range(NumSamples))
        else:
            if not to_labware_region.selected():
                to_labware_region.selectOnly(range(Reactive.NumOfSamples))

        to = to_labware_region.selected()
        NumSamples = len(to)
        SampleCnt = NumSamples

        Disp_V = Disp_V or from_reactive.volpersample

        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        maxMultiDisp_N = self.curArm().Tips[0].maxVol // Disp_V  # assume all tips equal

        lf = from_reactive.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}]:" \
            .format(v=Disp_V, n=from_reactive.name, fg=lf.location.grid, fs=lf.location.site, fw=from_reactive.pos,
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        comment(msg).exec()
        availableDisp = 0

        while SampleCnt:
            if nt > SampleCnt: nt = SampleCnt
            if availableDisp == 0:
                dsp, rst = divmod(SampleCnt, nt)
                if dsp >= maxMultiDisp_N:
                    dsp = maxMultiDisp_N
                    vol = [Disp_V * dsp] * nt
                    availableDisp = dsp
                else:
                    vol = [Disp_V * (dsp + 1)] * rst + [Disp_V * dsp] * (nt - rst)
                    availableDisp = dsp + bool(rst)
                self.aspiremultiTips(nt, from_reactive, vol)

            curSample = NumSamples - SampleCnt
            sel = [to_labware_region.offsetAtParallelMove(to[sample]) for sample in range(curSample, curSample + nt)]
            self.dispensemultiwells(nt, from_reactive.defLiqClass, to_labware_region.selectOnly(sel), [Disp_V] * nt)
            availableDisp -= 1
            SampleCnt -= nt
        self.dropTips()

    def transfer(self, from_labware_region, to_labware_region, Disp_V, LC,
                 optimizeFrom=True, optimizeTo=True, NumSamples=None):
        """


        :param NumSamples: Priorized   !!!! If true reset the selection
        :param from_reactive: Reactive to spread
        :param to_labware_region: Labware in which the destine well are selected
        :param Disp_V: if not, Disp_V is set from the default of the source reactive
        :param optimize: minimize zigzag of multipippeting
        """
        assert isinstance(from_labware_region, Labware.Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(to_labware_region, Labware.Labware), 'A Labware expected in to_labware_region to transfer'
        assert isinstance(LC, tuple)

        if NumSamples:  # todo  select convenient def
            oriSel = range(NumSamples)
            dstSel = range(NumSamples)
        else:
            oriSel = to_labware_region.selected()
            dstSel = from_labware_region.selected()

            if not dstSel:
                if not oriSel:
                    oriSel = range(Reactive.NumOfSamples)
                    dstSel = range(Reactive.NumOfSamples)
                else:
                    dstSel = oriSel
            else:
                if not oriSel:
                    oriSel = dstSel
                else:
                    l = min(len(oriSel, dstSel))  # todo transfer the minimun of the selected ???? Best reise error
                    oriSel = oriSel[:l]
                    dstSel = dstSel[:l]
        if optimizeFrom: oriSel = from_labware_region.parallelOrder(oriSel)
        if optimizeTo: dstSel = to_labware_region.parallelOrder(dstSel)

        NumSamples = len(dstSel)
        SampleCnt = NumSamples

        assert isinstance(Disp_V, (int, float))
        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        lf = from_labware_region
        lt = to_labware_region
        msg = "Transfer: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] into {to:s}[grid:{tg:d} site:{ts:d}]:" \
            .format(v=Disp_V, n=lf.label, fg=lf.location.grid, fs=lf.location.site,
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        comment(msg).exec()
        Asp = aspirate(tipsMask[nt], LC[0], Disp_V, from_labware_region)
        Dst = dispense(tipsMask[nt], LC[1], Disp_V, to_labware_region)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                Asp.tipMask = tipsMask[nt]
                Dst.tipMask = tipsMask[nt]

            self.getTips(tipsMask[nt])
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            Asp.exec()

            Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
            Dst.exec()
            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel

    def waste(self, from_labware_region, LC, vol, optimize=True):
        assert isinstance(from_labware_region, Labware.Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(vol, (int, float))
        # todo  select convenient def
        oriSel = from_labware_region.selected()
        if optimize: oriSel = from_labware_region.parallelOrder(oriSel)
        to_waste = BioWaste    !!!! ver
        NumSamples = len(oriSel)
        SampleCnt = NumSamples

        assert isinstance(vol, (int, float))
        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}]:" \
            .format(v=vol, n=lf.label, fg=lf.location.grid, fs=lf.location.site)
        comment(msg).exec()
        Asp = aspirate(tipsMask[nt], LC[0], vol, from_labware_region)
        Dst = dispense(tipsMask[nt], LC[1], vol, to_waste)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                Asp.tipMask = tipsMask[nt]
                Dst.tipMask = tipsMask[nt]

            self.getTips(tipsMask[nt])
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            Asp.exec()

            Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
            Dst.exec()
            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel


    def mix(self, from_labware_region, LC, vol, optimize=True):
        assert isinstance(from_labware_region, Labware.Labware), 'A Labware expected in from_labware_region to transfer'
        assert isinstance(vol, (int, float))
        # todo  select convenient def
        oriSel = from_labware_region.selected()
        if optimize: oriSel = from_labware_region.parallelOrder(oriSel)
        to_waste = BioWaste    !!!! ver
        NumSamples = len(oriSel)
        SampleCnt = NumSamples

        assert isinstance(vol, (int, float))
        nt = self.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        self.getTips(tipsMask[nt])

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}]:" \
            .format(v=vol, n=lf.label, fg=lf.location.grid, fs=lf.location.site)
        comment(msg).exec()
        Asp = aspirate(tipsMask[nt], LC[0], vol, from_labware_region)
        Dst = dispense(tipsMask[nt], LC[1], vol, to_waste)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                Asp.tipMask = tipsMask[nt]
                Dst.tipMask = tipsMask[nt]

            self.getTips(tipsMask[nt])
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            Asp.exec()

            Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
            Dst.exec()
            self.dropTips()

            SampleCnt -= nt
        self.dropTips()
        Asp.labware.selectOnly(oriSel)
        Dst.labware.selectOnly(dstSel)
        return oriSel, dstSel


curRobot = None


