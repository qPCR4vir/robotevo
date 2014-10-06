__author__ = 'qPCR4vir'

from contextlib import contextmanager

import Robot as Rbt
import Instructions as Itr
import Reactive as Rtv
import Labware as Lab

def getTips(TIP_MASK=-1, type=None):
    type=type or Lab.def_DiTi
    # TIP_MASK = Rbt.Robot.current.mask_to_getTips(TIP_MASK,maxVol)
    Itr.getDITI2(TIP_MASK, type, arm=Rbt.Robot.current.def_arm).exec()
    # return TIP_MASK

def dropTips(TIP_MASK=-1): # todo is this a correct solution or it is best to do a double check? To force drop?
        #if not Rbt.Robot.current.droptips: return 0
        #TIP_MASK = Rbt.Robot.current.curArm().drop(TIP_MASK)
        #if TIP_MASK:
        Itr.dropDITI(TIP_MASK).exec()
        #return TIP_MASK

def moveTips(zMove, zTarget, offset, speed, TIP_MASK=-1):
    pass # Itr.moveLiha

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
        # Rbt.Robot.current.curArm().aspire(v, Rbt.tipMask[tip])
        Itr.aspirate(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

def dispense( tip, reactive, vol=None): # todo coordinate with robot
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
        # Rbt.Robot.current.curArm().dispense(v, Rbt.tipMask[tip])
        Itr.dispense(Rbt.tipMask[tip], reactive.defLiqClass, v, reactive.labware).exec()

def aspiremultiTips( tips, reactive, vol=None):
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
            #Rbt.Robot.current.curArm().aspire(vol, mask)
            asp.tipMask = mask
            asp.exec()
            curTip = nextTip

def dispensemultiwells( tips, liq_class, labware, vol):
        if not isinstance(vol, list):
            vol = [vol] * tips
        om = Rbt.tipsMask[tips]
        # Rbt.Robot.current.curArm().dispense(vol, om)
        Itr.dispense(om, liq_class, vol, labware).exec()

def make( what, NumSamples=None): # todo coordinate with protocol
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
            assert nc <= Rbt.Robot.current.curArm().nTips, \
                "Temporally the mix can not contain more than {:d} components.".format(Rbt.Robot.current.curArm().nTips)

            with tips(Rbt.tipsMask[nc]):

                for i, react in enumerate(preMix.components):
                    l = react.labware
                    msg = "   {:d}- {:.1f} µL of {:s} from {:s}[grid:{:d} site:{:d} well:{:d}]".format(
                        i + 1, react.minVol(NumSamples), react.name, l.label, l.location.grid, l.location.site + 1,
                        react.pos + 1)
                    Itr.comment(msg).exec()
                    mV = Rbt.Robot.current.curArm().Tips[i].type.maxVol # todo what if the tip are different?
                    r = react.minVol(NumSamples)
                    while r > 0:
                        dV = r if r < mV else mV
                        aspire(i, react, dV)
                        dispense(i, preMix, dV)
                        r -= dV

def spread( volume=None, reactive=None, to_labware_region=None, optimize=True, NumSamples=None):
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

        if nt > SampleCnt: nt = SampleCnt

        lf = reactive.labware
        lt = to_labware_region
        msg = "Spread: {v:.1f} µL of {n:s}".format(v=volume, n=reactive.name)
        with group(msg):
            msg += "[grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg=lf.location.grid, fs=lf.location.site, fw=reactive.pos, do=str(to),
                        to=lt.label, tg=lt.location.grid, ts=lt.location.site)
            Itr.comment(msg).exec()
            availableDisp = 0
            with tips(Rbt.tipsMask[nt]):
                maxMultiDisp_N = Rbt.Robot.current.curArm().Tips[0].type.maxVol // volume  # assume all tips equal
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
                        aspiremultiTips(nt, reactive, vol)

                    curSample = NumSamples - SampleCnt
                    sel = to[curSample: curSample + nt]  # todo what if volume > maxVol_tip ?
                    dispensemultiwells(nt, reactive.defLiqClass, to_labware_region.selectOnly(sel), [volume] * nt)
                    availableDisp -= 1
                    SampleCnt -= nt

def transfer( from_labware_region, to_labware_region, volume, using_liquid_class,
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
        assert isinstance(using_liquid_class, tuple)
        nt = Rbt.Robot.current.curArm().nTips  # the number of tips to be used in each cycle of pippeting

        if NumSamples:  # todo  select convenient def
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

        dropTips(Rbt.tipsMask[nt])

        lf = from_labware_region
        lt = to_labware_region
        Asp = Itr.aspirate(Rbt.tipsMask[nt], using_liquid_class[0], volume, from_labware_region)
        Dst = Itr.dispense(Rbt.tipsMask[nt], using_liquid_class[1], volume, to_labware_region)
        msg = "Transfer: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += "[grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg=lf.location.grid, fs=lf.location.site, oo=str(oriSel), do=str(dstSel),
                        to=lt.label, tg=lt.location.grid, ts=lt.location.site)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    Asp.tipMask = Rbt.tipsMask[nt]
                    Dst.tipMask = Rbt.tipsMask[nt]

                with tips(Rbt.tipsMask[nt]):  # todo what if volume > maxVol_tip ?
                    Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
                    Asp.exec()
                    Dst.labware.selectOnly(dstSel[curSample:curSample + nt])
                    Dst.exec()
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
        assert isinstance(volume, (int, float))
        # todo  select convenient def
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
        lf = from_labware_region
        tm = Rbt.tipsMask[nt]
        Asp = Itr.aspirate(tm, using_liquid_class[0], volume, from_labware_region)
        Dst = Itr.dispense(tm, using_liquid_class[1], volume, to_waste_labware)
        Ctr = Itr.moveLiha(Itr.moveLiha.y_move, Itr.moveLiha.z_start, 3.0, 2.0, tm, from_labware_region)
        nt = to_waste_labware.autoselect(maxTips=nt)
        mV = Lab.def_DiTi.maxVol      # todo revise !! What tip tp use !
        # mV = Rbt.Robot.current.curArm().Tips[0].type.maxVol * 0.8
        msg = "Waste: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += "[grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    tm = Rbt.tipsMask[nt]
                    Asp.tipMask = tm
                    Dst.tipMask = tm
                    Ctr.tipMask = tm
                Asp.labware.selectOnly(oriSel[curSample:curSample + nt])
                r = volume
                with tips(tm):
                    while r > 0:
                        dV = r if r < mV else mV
                        r -= dV
                        Asp.volume = dV
                        Dst.volume = dV
                        Asp.exec()
                        Ctr.exec()
                        Dst.exec()
                SampleCnt -= nt
            Asp.labware.selectOnly(oriSel)
        return oriSel

def mix( in_labware_region, using_liquid_class, volume, optimize=True):

        """

        :param in_labware_region:
        :param using_liquid_class:
        :param volume:
        :param optimize:
        :return:
        """
        in_labware_region = in_labware_region or Lab.WashWaste
        assert isinstance(in_labware_region, Lab.Labware), 'A Labware expected in in_labware_region to be mixed'
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
        volume = volume * 0.8
        mV = Lab.def_DiTi.maxVol * 0.8    # todo revise !! What tip tp use !
        # mV = Rbt.Robot.current.curArm().Tips[0].type.maxVol * 0.8
        volume = volume if volume < mV else mV

        lf = in_labware_region
        mx = Itr.mix(Rbt.tipsMask[nt], using_liquid_class, volume, in_labware_region)
        msg = "Mix: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg += "[grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site) + str(oriSel)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    mx.tipMask = Rbt.tipsMask[nt]

                with tips(Rbt.tipsMask[nt]):
                    mx.labware.selectOnly(oriSel[curSample:curSample + nt])
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
def tips(tipsMask):
    getTips(tipsMask)
    yield
    dropTips(tipsMask)

@contextmanager
def parallel_execution_of(subroutine):
    getTips(tipsMask)
    yield
    dropTips(tipsMask)


@contextmanager
def opening_example(filename):
    f = open(filename) # IOError is untouched by GeneratorContext
    try:
        yield f
    finally:
        f.close() # Ditto for errors here (however unlikely)

