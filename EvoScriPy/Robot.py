__author__ = 'qPCR4vir'

#from Instruction_Base import *
#from Instructions import *
import Labware as Lab


tipMask = []  # mask for one tip of index ...
tipsMask = []  # mask for the first tips
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2 ** tip - 1]

def_nTips = 4
nTips = def_nTips


class Robot:
    """ Maintain an intern state.
    Can have more than one arm in a dictionary that map an index with the actual arm.
    One of the arms can be set as "current" and is returned by curArm()
    Most of the changes in state are made by the implementation of the low level instructions, while the protocols can
    "observe" the state to make all kind of optimizations and organizations previous to the actual instruction call
    """
    current=None

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

        def getTips_test(self, tip_mask=-1) -> int:
            """
                    :rtype : int
                    :param tip_mask:
                    :return: the mask that can be used
                    :raise "Tip already in position " + str(i):
                    """
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i)
            return tip_mask

        def getTips(self, rack_type, tip_mask=-1) -> int:
            """     Mount only one kind of tip at a time
                    :rtype : int
                    :param tip_mask:
                    :return: the mask that can be used
                    :raise "Tip already in position " + str(i):
                    """
            assert isinstance(rack_type, Lab.Labware.DITIrack)
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i)
                    self.Tips[i] = Lab.Tip(rack_type)
            return tip_mask

        def getMoreTips_test(self, rack_type, tip_mask=-1) -> int:
            """ Mount only the tips with are not already mounted.
                Mount only one kind of tip at a time, but not necessary the same of the already mounted.
                    :rtype : int
                    :param tip_mask: int
                    :return: the mask that can be used
                    """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        if tp.type is not rack_type:
                            raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i) + \
                                    " and we need " + rack_type.name
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        pass # self.Tips[i] = Lab.Tip(rack_type)
            return tip_mask

        def getMoreTips(self, rack_type, tip_mask=-1) -> int:
            """ Mount only the tips with are not already mounted.
                Mount only one kind of tip at a time, but not necessary the same of the already mounted.
                    :rtype : int
                    :param tip_mask: int
                    :return: the mask that can be used
                    """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        if tp.type is not rack_type:
                            raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i) + \
                                    " and we need " + rack_type.name
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        pass # self.Tips[i] = Lab.Tip(rack_type)
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
                    assert isinstance(tp, Lab.Tip), "No tip in position " + str(i)
                    nv = tp.vol + action * vol[i]
                    if 0 <= nv <= tp.type.maxVol:
                        self.Tips[i].vol = nv
                        continue
                    msg = str(i + 1) + " changing volume from " + str(tp.vol) + " to " + str(nv)
                    if nv < 0:
                        raise BaseException('To few Vol in tip ' + msg)
                    raise BaseException('To much Vol in tip ' + msg)
                else:
                    pass # vol[i] = None
            return vol, tip_mask

    def __init__(self,  index       = None,
                        arms        = None,
                        nTips       = None,
                        workingTips = None,
                        tipsType    = Arm.DiTi,
                        templateFile= None): # index=Pipette.LiHa1
        """

        :param arms:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        assert Robot.current is None
        Robot.current = self
        self.arms = arms              if isinstance(arms, dict     ) else \
                   {arms.index: arms} if isinstance(arms, Robot.Arm) else \
                   {     index: Robot.Arm(nTips or def_nTips, index, workingTips, tipsType)}
        self.set_worktable(templateFile)
        self.def_arm = index  # or Pipette.LiHa1
        self.droptips = True
        self.reusetips = False
        self.preservetips = False
        self.usePreservedtips = False
        self.preservedtips = {} # order:well
        self.last_preserved_tips = None # Lab.DiTi_Rack, offset

    def where_preserve_tips(self, selection)->[Lab.DiTi_Rack]: # with the tips already selected
        if self.last_preserved_tips:
            rack, offset = self.last_preserved_tips
            assert isinstance(rack, Lab.DiTi_Rack)
            if self.usePreservedtips: # re-back DiTi for multiple reuse
                offsets=[]
                where=[]
                for i in selection:
                    well = self.preservedtips[i]
                    assert isinstance(well, Lab.Well)
                    assert well in self.preservedtips, "There are no tip preserved for sample "+str(well)
                    if rack is well.labware:
                        offsets += [well.offset]
                    else:
                        where += [rack.selectOnly(offsets)]
                        rack = well.labware
                        offset = [well.offset]
                where += [rack.selectOnly(offsets)]
                return where
            else:
                continuous, free_wells = rack.find_free_wells(len(selection))
                offsets=[]
                where=[]
                for well in free_wells:
                    assert isinstance(well, Lab.Well)
                    if rack is well.labware:
                        offsets += [well.offset]
                    else:
                        where += [rack.selectOnly(offsets)]
                        rack = well.labware
                        offset = [well.offset]
                where += [rack.selectOnly(offsets)]
                return where

    def set_worktable(self,templateFile):
        w = Lab.WorkTable.curWorkTable
        if not w:
            w = Lab.WorkTable(templateFile)
        else:
            w.parseWorTableFile(templateFile)
        self.worktable = w

    def set_as_current(self):
        Lab.curWorkTable=self.worktable

    # Functions to observe the iRobot status (intern-physical status, or user status with are modificators of future
    # physical actions), or to modify the user status, but not the physical status. It can be used by the protocol
    # instruction and even by the final user.

    def set_dropTips(self, drop=True):
        self.droptips, drop = drop, self.droptips
        return drop

    def reuseTips(self, reuse=True)->bool:
        self.reusetips, reuse = reuse, self.reusetips
        return reuse

    def preserveTips(self, preserve=True)->bool:
        self.preservetips, preserve = preserve, self.preservetips
        return preserve

    def usePreservedTips(self, usePreserved=True)->bool:
        self.usePreservedtips, usePreserved = usePreserved, self.usePreservedtips
        return usePreserved

    def curArm(self, arm=None):
        if arm is not None: self.def_arm = arm
        return self.arms[self.def_arm]

    def getTips_test(self, rack_type, tip_mask=-1) -> int:   # todo REVISE
        if self.reusetips:
            tip_mask = self.curArm().getMoreTips_test(rack_type, tip_mask)
        else:
            # self.dropTips(tip_mask)  # todo REVISE  here ???
            tip_mask = self.curArm().getTips_test(tip_mask)
        return tip_mask

    # function to change the physical status, to model physical actions, or that directly
    # correspond to actions in the hardware. It can be call only from the official low level instructions
    # in the method Itr.actualize_robot_state(self):

    def getTips(self, rack, tip_mask=-1,lastPos=False) -> int:
        if isinstance(rack, Lab.Labware.DITIrack):
            rack = rack.pick_next_rack
        assert isinstance(rack, Lab.DiTi_Rack)
        tip_mask = self.getTips_test(rack.type, tip_mask)
        rack.remove_tips(tip_mask, rack.type, self.worktable, lastPos=lastPos)
        return self.curArm().getTips(rack.type, tip_mask)

    def dropTips(self, TIP_MASK=-1): # todo coordine protocol
        if not self.droptips: return 0
        TIP_MASK = self.curArm().drop(TIP_MASK)
        return TIP_MASK

    def dispense(self, tip, labware, vol=None): # todo implement a coordinate call to arm and lab
        self.curArm().dispense(vol, tipMask[tip])


    def set_tips_back(self, TIP_MASK=-1, labware):
        # todo what if self.droptips: is True ???
        
        pass



