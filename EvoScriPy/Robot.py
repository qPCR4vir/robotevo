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

        def getTips_test(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
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

        def getMoreTips_test(self, tip_mask=-1, maxVol=Tip_1000maxVol) -> int:
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
                        pass # self.Tips[i] = Tip(maxVol)
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
                    if 0 <= nv <= tp.maxVol:
                        self.Tips[i].vol = nv
                        continue
                    msg = str(i + 1) + " changing volume from " + str(tp.vol) + " to " + str(nv)
                    if nv < 0:
                        raise BaseException('To few Vol in tip ' + msg)
                    raise BaseException('To much Vol in tip ' + msg)
                else:
                    pass # vol[i] = None
            return vol, tip_mask

    def __init__(self, index=None,arms=None, nTips=None,
                  workingTips=None,
                 tipsType=Arm.DiTi, templateFile=None): # index=Pipette.LiHa1
        """

        :param arms:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        self.arms = arms              if isinstance(arms, dict     ) else \
                   {arms.index: arms} if isinstance(arms, Robot.Arm) else \
                   {     index: Robot.Arm(nTips or def_nTips, index, workingTips, tipsType)}

        self.worktable = Lab.WorkTable(templateFile)
        self.def_arm = index  # or Pipette.LiHa1
        self.droptips = True
        self.reusetips = False
        self.preservetips = False
        self.usePreservedtips = False

    def set_worktable(self,templateFile):
        self.worktable = Lab.WorkTable(templateFile)

    def set_dropTips(self, drop=True):
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

        return self.curArm().getTips(self.getTips_test(TIP_MASK, maxVol))

    def getTips_test(self, TIP_MASK=-1, maxVol=Tip_1000maxVol):
        if self.reusetips:
            TIP_MASK = self.curArm().getMoreTips_test(TIP_MASK, maxVol)
        else:
            self.dropTips(TIP_MASK)
            TIP_MASK = self.curArm().getMoreTips_test(TIP_MASK, maxVol)
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

current = None


