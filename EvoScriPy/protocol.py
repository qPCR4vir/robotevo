__author__ = 'qPCR4vir'

from contextlib import contextmanager

import Robot as Rbt
import Instructions as Itr
import Reactive as Rtv
import Labware as Lab

Water_free = "Water free"  # General. No detect and no track small volumes < 50 µL

B_liquidClass   = Water_free #    or "Buffer free DITi 1000-AVR" ?
W_liquidClass   = Water_free #    or "AVR-Water free DITi 1000"
Std_liquidClass = Water_free #    or "Water free dispense DiTi 1000"
Te_Mag_LC       = "Te-Mag"          # "Water free" but uncentred
Te_Mag_Centre   = "Te-Mag Centre"   # To Centre after normal aspiration.
Te_Mag_Rest     = "Te-Mag Rest"
Te_Mag_Force_Centre   = "Te-Mag Force Centre"
Te_Mag_RestPlus = "Te-Mag RestPlus"

def set_dropTips(drop=True)->bool:
    return Rbt.Robot.current.set_dropTips(drop)

def reuseTips(reuse=True)->bool:
    return Rbt.Robot.current.reuseTips(reuse)

def reuse_tips_and_drop(reuse=True, drop=True)->(bool, bool):
    return set_dropTips(drop), reuseTips(reuse)

def preserveTips(self, preserve=True)->bool:
    return Rbt.Robot.current.preserveTips(preserve)

def usePreservedTips(self, usePreserved=True)->bool:
    return Rbt.Robot.current.usePreservedTips(usePreserved)

def moveTips(zMove, zTarget, offset, speed, TIP_MASK=-1):
    pass # Itr.moveLiha

def getTips(TIP_MASK=-1, type=None, selected_reactive=None):
    robot = Rbt.Robot.current
    assert isinstance(robot, Rbt.Robot)
    #if not Rbt.Robot.reusetips: # and Rbt.Robot.droptips

    if robot.usePreservedtips:
        TIP_MASK = TIP_MASK if TIP_MASK != -1 else Rbt.tipsMask[Rbt.nTips]
        where = robot.where_are_preserved_tips(selected_reactive, TIP_MASK, type)
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
            Itr.pickUp_DITIs(tipsMask, tip_rack).exec()
        assert l == 0
        return

    else:
        type=type or Lab.def_DiTi
        I = Itr.getDITI2(TIP_MASK, type, arm=robot.def_arm)
        I.exec()
        return TIP_MASK # I.tipMask


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
        Itr.dispense(Rbt.tipMask[tip], reactive.defLiqClass, v,
                     w.labware.selectOnly([w.offset])).exec()

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

def make( what, NumSamples=None): # todo coordinate with protocol
        if isinstance(what, Rtv.preMix): makePreMix(what, NumSamples)

def makePreMix( preMix, NumSamples=None):
        NumSamples = NumSamples or Rtv.NumOfSamples
        l = preMix.labware
        msg = "preMix: {:.1f} µL of {:s}".format(preMix.minVol(NumSamples), preMix.name)
        with group(msg):
            msg = " into {:s}[grid:{:d} site:{:d} well:{:d}] from {:d} components:".format(
                l.label, l.location.grid, l.location.site + 1, preMix.pos + 1, len(preMix.components))
            Itr.comment(msg).exec()
            nc = len(preMix.components)
            nr = len(preMix.Replicas)
            nt = Rbt.Robot.current.curArm().nTips
            assert nc <= nt, "Temporally the mix can not contain more than {:d} components.".format(nt)
            dt = nt - nc
            samples_per_replicas = [(NumSamples + nr - (i+1))//nr for i in range(nr)]
            with tips(Rbt.tipsMask[nc]):   # todo want to use preserved ?? selected=??
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
            msg = "{v:.1f} µL total from [grid:{fg:d} site:{fs:d} well:{fw:d}] into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(v=reactive.minVol(), fg=lf.location.grid, fs=lf.location.site+1, fw=reactive.pos+1, do=str([i+1 for i in to]),
                        to=lt.label, tg=lt.location.grid, ts=lt.location.site+1)
            Itr.comment(msg).exec()
            availableDisp = 0
            with tips(Rbt.tipsMask[nt]):  # todo want to use preserved ?? selected=??
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
        lf = from_labware_region
        lt = to_labware_region
        Asp = Itr.aspirate(Rbt.tipsMask[nt], using_liquid_class[0], volume, from_labware_region)
        Dst = Itr.dispense(Rbt.tipsMask[nt], using_liquid_class[1], volume, to_labware_region)
        msg = "Transfer: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg = "[grid:{fg:d} site:{fs:d}] in order {oo:s} into {to:s}[grid:{tg:d} site:{ts:d}] in order {do:s}:" \
                .format(fg=lf.location.grid, fs=lf.location.site+1, oo=str(oriSel), do=str(dstSel),
                        to=lt.label, tg=lt.location.grid, ts=lt.location.site+1)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    Asp.tipMask = Rbt.tipsMask[nt]
                    Dst.tipMask = Rbt.tipsMask[nt]

                sel = oriSel[curSample:curSample + nt]
                with tips(Rbt.tipsMask[nt], selected=sel):  # todo what if volume > maxVol_tip ?
                    Asp.labware.selectOnly(sel)
                    Asp.exec()
                    # Rbt.setUsed(Asp.tipMask, Asp.labware) # todo this in robot.aspire()
                    Dst.labware.selectOnly(sel)
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
        if volume < 0 : volume = 0
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
        tm = Rbt.tipsMask[nt]
        nt = to_waste_labware.autoselect(maxTips=nt)
        mV = Lab.def_DiTi.maxVol      # todo revise !! What tip tp use !

        Rest = 50  # the volume we cannot more aspire with liquid detection, to small, collisions
        RestPlus = 50

        # Asp = Itr.aspirate(tm, using_liquid_class[0], volume, from_labware_region)
        Asp = Itr.aspirate(tm, Te_Mag_LC, volume, from_labware_region)
        Dst = Itr.dispense(tm, using_liquid_class[1], volume, to_waste_labware)
        # Ctr = Itr.moveLiha(Itr.moveLiha.y_move, Itr.moveLiha.z_start, 3.0, 2.0, tm, from_labware_region)
        lf = from_labware_region
        msg = "Waste: {v:.1f} µL of {n:s}".format(v=volume, n=lf.label)
        with group(msg):
            msg = "[grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) + str(oriSel)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    tm = Rbt.tipsMask[nt]
                    Asp.tipMask = tm
                    Dst.tipMask = tm
                    # Ctr.tipMask = tm
                sel = oriSel[curSample:curSample + nt]
                Asp.labware.selectOnly(sel)
                r = volume   # r: Waste_available yet; volume: to be Waste
                with tips(tm, drop=True, preserve=False, selected=sel):
                    while r > Rest:      # dont aspire Rest with these Liq Class (Liq Detect)
                        dV = r if r < mV else mV
                        if dV < Rest: break # ??
                        dV -= Rest       # the last Rest uL have to be aspired with the other Liq Class
                        Asp.volume = dV  #  with Liq Class with Detect: ">> AVR-Serum 1000 <<	365"
                        Dst.volume = dV
                        Asp.liquidClass = Te_Mag_LC # ">> AVR-Serum 1000 <<	365"  # "No Liq Detect"
                        Asp.exec()
                        Asp.volume = 0.5
                        Asp.liquidClass = Te_Mag_Centre
                        Asp.exec()
                        # Ctr.exec()
                        Dst.exec()
                        r -= dV

                    Asp.volume = Rest
                    Asp.liquidClass =  Te_Mag_Rest # ">> AVR-Serum 1000 <<	367" # "No Liq Detect"
                    Asp.exec()
                    # Ctr.exec()
                    Asp.volume = 0.5
                    Asp.liquidClass = Te_Mag_Force_Centre
                    Asp.exec()
                    Asp.volume = RestPlus
                    Asp.liquidClass =  Te_Mag_RestPlus # ">> AVR-Serum 1000 <<	369" # "No Liq Detect"
                    Asp.exec()
                    #Ctr.exec()
                    Asp.volume = 0.5
                    Asp.liquidClass = Te_Mag_Force_Centre
                    Asp.exec()
                    Dst.volume = Rest + RestPlus
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
            msg = "[grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) + str(oriSel)
            Itr.comment(msg).exec()
            while SampleCnt:
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:
                    nt = SampleCnt
                    mx.tipMask = Rbt.tipsMask[nt]

                sel = oriSel[curSample:curSample + nt]
                with tips(Rbt.tipsMask[nt], selected=sel):
                    mx.labware.selectOnly(sel)
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
def tips(tipsMask=None, reuse=None, drop=None, preserve=None, usePreserved=None):
    if reuse        is not None: reuse        = reuseTips       (reuse       )
    if drop         is not None: drop         = set_dropTips    (drop        )
    if preserve     is not None: preserve     = preserveTips    (preserve    )
    if usePreserved is not None: usePreserved = usePreservedTips(usePreserved)

    if tipsMask     is not None: tipsMask     = getTips         (tipsMask)

    yield

    if tipsMask     is not None: tipsMask     = dropTips        (tipsMask)

    if reuse        is not None: reuse        = reuseTips       (reuse       )
    if drop         is not None: drop         = set_dropTips    (drop        )
    if preserve     is not None: preserve     = preserveTips    (preserve    )
    if usePreserved is not None: usePreserved = usePreservedTips(usePreserved)

@contextmanager
def parallel_execution_of(subroutine):
    Itr.subroutine(subroutine, Itr.subroutine.Continues).exec()
    yield
    Itr.subroutine(subroutine, Itr.subroutine.Waits_previous).exec()

@contextmanager
def incubation(minutes, timer=1):
    Itr.startTimer(timer).exec()
    yield
    Itr.waitTimer(timer=timer, timeSpan= 10*60).exec()



@contextmanager
def opening_example(filename):
    f = open(filename) # IOError is untouched by GeneratorContext
    try:
        yield f
    finally:
        f.close() # Ditto for errors here (however unlikely)

# TODO  autom create replicates when preMix > Well.maxVol, and vol > tip.maxVol ? NumCompon > nTips ?
# TODO  implement preserveTips and usePreservedTips !!
# TODO  mix well <B-beads
# TODO  Elution buffer to eppis !!!
# TODO  implement accumulated volume
# TODO  implement actualize vol in reactives in pipette
# TODO  comentar las replicas, como 2x b-beads
# TODO  parse WorkTable. Create "temporal" list of grid/rack/labware, and check with created or create
# TODO  parse WorkTable from the real backup! Create real abjects list (carrie and labware types, and LiqClass
# TODO  implement use only tips filled
# TODO  implement Debugger: prompt and or wait
# TODO  implement with drop(true or false): with reuse and drop(): etc. to restore previous settings   - ok ?!
# TODO  write the total vol to spread.                      - ok ?!
# TODO  actualize liquid classes                            - ok ?!
# TODO  poner IC MS2 mas cerca (intercambiar con b-beads)   - ok ?!
# TODO  test no drop                                        - ok ?!
# TODO  reimplementar rest... for waste                     - ok ?!


