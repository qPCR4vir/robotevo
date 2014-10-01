__author__ = 'qPCR4vir'

import Robot as Rbt
from Robot import current as robot
import Instruction_Base as I_b
import Instructions as Itr
import Reactive as Rtv

def getTips( TIP_MASK=-1, maxVol=Rbt.Tip_1000maxVol):

    Itr.getDITI2(robot.mask_to_getTips(TIP_MASK,maxVol), arm=robot.def_arm).exec()
    return TIP_MASK

def dropTips(self, TIP_MASK=-1): # todo coordine robot
        if not robot.droptips: return 0
        TIP_MASK = robot.curArm().drop(TIP_MASK)
        if TIP_MASK:
            Itr.dropDITI(TIP_MASK).exec()
        return TIP_MASK

def aspire(self, tip, reactive, vol=None):
        """
        Aspire vol with ONE tip from reactive
        :param self:
        :param tip:
        :param reactive:
        :param vol:
        """
        if vol is None:
            vol = reactive.minVol()
        v = [0] * robot.curArm().nTips
        v[tip] = vol
        reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
        # robot.curArm().aspire(v, Rbt.tipMask[tip])
        Itr.aspirate(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

def dispense(self, tip, reactive, vol=None): # todo coordinate with robot
        vol = vol or reactive.minVol()  # really ??
        reactive.autoselect()  # reactive.labware.selectOnly([reactive.pos])
        v = [0] * robot.curArm().nTips
        v[tip] = vol
        robot.curArm().dispense(v, Rbt.tipMask[tip])
        Itr.dispense(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

def aspiremultiTips(self, tips, reactive, vol=None):
        if not isinstance(vol, list):
            vol = [vol] * tips
        mask = Rbt.tipsMask[tips]
        nTip = reactive.autoselect(tips)
        asp = Itr.aspirate(mask, reactive.defLiqClass, vol, reactive.labware)
        curTip = 0
        while curTip < tips:
            nextTip = curTip + nTip
            nextTip = nextTip if nextTip <= tips else tips
            mask = Rbt.tipsMask[curTip] ^ Rbt.tipsMask[nextTip]
            robot.curArm().aspire(vol, mask)
            asp.tipMask = mask
            asp.exec()
            curTip = nextTip

def dispensemultiwells(self, tips, liq_class, labware, vol):
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = Rbt.tipsMask[tips]
        robot.curArm().dispense(vol, om)
        dispense(om, liq_class, vol, labware).exec()

def make(self, what, NumSamples=None): # todo coordinate with protocol
        if isinstance(what, Rtv.preMix): self.makePreMix(what, NumSamples)

def makePreMix( preMix, NumSamples=None):
        NumSamples = NumSamples or Rtv.NumOfSamples

        l = preMix.labware
        msg = "preMix: {:.1f} µL of {:s} into {:s}[grid:{:d} site:{:d} well:{:d}] from {:d} components:".format(
            preMix.minVol(NumSamples), preMix.name, l.label, l.location.grid, l.location.site + 1, preMix.pos + 1,
            len(preMix.components))
        Itr.comment(msg).exec()
        nc = len(preMix.components)
        assert nc <= robot.curArm().nTips, \
            "Temporally the mix can not contain more than {:d} components.".format(robot.curArm().nTips)

        getTips(Rbt.tipsMask[nc])

        for i, react in enumerate(preMix.components):
            l = react.labware
            msg = "   {:d}- {:.1f} µL of {:s} from {:s}[grid:{:d} site:{:d} well:{:d}]".format(
                i + 1, react.minVol(NumSamples), react.name, l.label, l.location.grid, l.location.site + 1,
                react.pos + 1)
            Itr.comment(msg).exec()
            mV = robot.curArm().Tips[i].maxVol # todo what if the tip are different?
            r = react.minVol(NumSamples)
            while r > 0:
                dV = r if r < mV else mV
                aspire(i, react, dV)
                dispense(i, preMix, dV)
                r -= dV

        dropTips()

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

        nt = robot.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        robot.getTips(Rbt.tipsMask[nt])

        maxMultiDisp_N = robot.curArm().Tips[0].maxVol // volume  # assume all tips equal

        lf = reactive.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
            .format(v=volume, n=reactive.name, fg=lf.location.grid, fs=lf.location.site, fw=reactive.pos, do=str(to),
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        Itr.comment(msg).exec()
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
                robot.aspiremultiTips(nt, reactive, vol)

            curSample = NumSamples - SampleCnt
            sel = to[curSample: curSample + nt]  # todo what if volume > maxVol_tip ?
            robot.dispensemultiwells(nt, reactive.defLiqClass, to_labware_region.selectOnly(sel), [volume] * nt)
            availableDisp -= 1
            SampleCnt -= nt
        robot.dropTips()

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
        nt = robot.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt: nt = SampleCnt

        robot.getTips(Rbt.tipsMask[nt])

        lf = from_labware_region
        lt = to_labware_region
        msg = "Transfer: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
            .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site, oo=str(oriSel), do=str(dstSel),
                    to=lt.label, tg=lt.location.grid, ts=lt.location.site)
        comment(msg).exec()
        Asp = aspirate(Rbt.tipsMask[nt], using_liquid_class[0], volume, from_labware_region)
        Dst = dispense(Rbt.tipsMask[nt], using_liquid_class[1], volume, to_labware_region)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                Asp.tipMask = Rbt.tipsMask[nt]
                Dst.tipMask = Rbt.tipsMask[nt]

            robot.getTips(Rbt.tipsMask[nt])  # todo what if volume > maxVol_tip ?
            robot.curArm().aspire(volume, Rbt.tipsMask[nt])
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            Asp.exec()

            Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
            robot.curArm().dispense(volume, Rbt.tipsMask[nt])
            Dst.exec()
            robot.dropTips()

            SampleCnt -= nt
        robot.dropTips()
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

        nt = robot.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt:
            nt = SampleCnt
        tm = Rbt.tipsMask[nt]
        robot.getTips(tm)

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order:" \
                  .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
        Itr.comment(msg).exec()
        Asp = Itr.aspirate(tm, using_liquid_class[0], volume, from_labware_region)
        Dst = Itr.dispense(tm, using_liquid_class[1], volume, to_waste_labware)
        nt = to_waste_labware.autoselect(maxTips=nt)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                tm = Rbt.tipsMask[nt]
                Asp.tipMask = tm
                Dst.tipMask = tm

            robot.getTips(tm)
            Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
            mV = robot.curArm().Tips[0].maxVol
            r = volume
            while r > 0:
                dV = r if r < mV else mV
                r -= dV
                Asp.volume = dV
                robot.curArm().aspire(dV, tm)
                Asp.exec()
                Dst.volume = dV
                robot.curArm().dispense(dV, tm)
                Dst.exec()

            robot.dropTips()

            SampleCnt -= nt
        robot.dropTips()
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
        nt = robot.curArm().nTips  # the number of tips to be used in each cycle of pippeting
        if nt > SampleCnt:
            nt = SampleCnt

        robot.getTips(Rbt.tipsMask[nt])
        volume = volume * 0.8
        mV = robot.curArm().Tips[0].maxVol * 0.8
        volume = volume if volume < mV else mV

        lf = in_labware_region
        msg = "Mix: {v:.1f} µL of {n:s}[grid:{fg:d} site:{fs:d}] in order:" \
                  .format(v=volume, n=lf.label, fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
        comment(msg).exec()
        mx = mix(Rbt.tipsMask[nt], using_liquid_class, volume, in_labware_region)
        while SampleCnt:
            curSample = NumSamples - SampleCnt
            if nt > SampleCnt:
                nt = SampleCnt
                mx.tipMask = Rbt.tipsMask[nt]

            robot.getTips(Rbt.tipsMask[nt])
            mx.labware.selectOnly(oriSel[curSample:curSample + nt])
            mx.exec()

            robot.dropTips()

            SampleCnt -= nt
        robot.dropTips()
        mx.labware.selectOnly(oriSel)
        return oriSel

def wash_in_TeMag(self, reactive, wells=None, using_liquid_class=None, vol=None):
        if wells is None:
            wells = reactive.labware.selected() or range(React.NumOfSamples)
        if using_liquid_class is None:
            using_liquid_class = (reactive.defLiqClass, reactive.defLiqClass)

        robot.spread(reactive=reactive, to_labware_region=Itr.TeMag.selectOnly(wells))
        Itr.subroutine("avr_MagMix.esc", Itr.subroutine.Continues).exec()
        robot.mix(Itr.TeMag.selectOnly(wells), reactive.defLiqClass, vol or reactive.volpersample)
        Itr.subroutine("avr_MagMix.esc", Itr.subroutine.Waits_previous).exec()
        robot.waste(Itr.TeMag.selectOnly(wells), using_liquid_class, vol or reactive.volpersample)
