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
            :param nTips: the number of possible tips
            :param index: int. for example: index=Pipette.LiHa1
            :param workingTips: some tips maybe broken or permanently unused.
            :param tipsType: DITI or fixed (not implemented)
            """
            self.index = index
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips] # todo implement
            self.tipsType = tipsType
            self.nTips = nTips
            self.Tips = [None] * nTips

        def getTips_test(self, tip_mask=-1) -> int:
            """ Simple test that the asked positions are free for mounting new tips.
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

        def getTips(self, rack_type=None, tip_mask=-1, tips=None) -> int:
            """     Mount only one kind of new tip at a time or just the tips given in the list
            :param rack_type:
            :param tips:
            :rtype : int
            :param tip_mask:
            :return: the mask that can be used
            :raise "Tip already in position " + str(i):
            """
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            n = Lab.count_tips(tip_mask)
            assert n <= self.nTips
            t = 0
            if tips is None:   # deprecated
                assert isinstance(rack_type, Lab.Labware.DITIrack)
                tips = [Lab.Tip(rack_type) for i in range(n)]
            else:
                assert n == len(tips)

            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp is not None:
                        raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i)
                    self.Tips[i] = tips[t]
                    t += 1
            return tip_mask, tips[t:] if t < n else []

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

        def getMoreTips(self, rack_type, tip_mask=-1, tips=None) ->(int, [Lab.Tip]):
            """ Mount only the tips with are not already mounted.
                Mount only one kind of tip at a time, but not necessary the same of the already mounted.
                    :rtype : int
                    :param tip_mask: int
                    :return: the mask that can be used
                    """
            if tip_mask == -1:  tip_mask = tipsMask[self.nTips]
            n = Lab.count_tips(tip_mask)
            assert n <= self.nTips
            t = 0
            if tips is None:   # deprecated
                assert isinstance(rack_type, Lab.Labware.DITIrack)
                tips = [Lab.Tip(rack_type) for i in range(n)]
            else:
                assert n == len(tips)

            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # already in position
                        if tp.type is not tips[t].type:
                            raise "A Tip from rack type " + tp.type.name + " is already in position " + str(i) + \
                                    " and we need " + tips[t].type.name
                        tip_mask ^= (1 << i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                        self.Tips[i] = tips[t]
                        t += 1
            return tip_mask, tips[t:] if t < n else []

        def drop_test(self, tip_mask=-1) -> (int, [int]):
            """ Return the mask and the tips index to be really used.
            :param tip_mask: int
            :return: the mask that can be used with, is "True" if tips actually ned to be drooped
            :rtype : int
            """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            tips_index = []
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # in position
                        tips_index += [i] # tips += [tp]
                        pass # self.Tips[i] = None
                    else:
                        tip_mask ^= (1 << i)  # already drooped
            return tip_mask, tips_index

        def drop(self, tip_mask=-1) -> (int, list):
            """ Drop tips only if needed. Return the mask and the tips really used.
            :param tip_mask: int
            :return: the mask that can be used with, is "True" if tips actually ned to be drooped
            :rtype : int
            """
            if tip_mask == -1:
                tip_mask = tipsMask[self.nTips]
            tips = []
            for i, tp in enumerate(self.Tips):
                if tip_mask & (1 << i):
                    if tp:  # in position
                        tips += [tp]
                        self.Tips[i] = None
                    else:
                        tip_mask ^= (1 << i)  # already drooped
            return tip_mask, tips

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
        # self.preservedtips = {} # order:well
        # self.last_preserved_tips = None # Lab.DITIrack, offset

    def set_worktable(self,templateFile):
        w = Lab.WorkTable.curWorkTable
        if not w:
            w = Lab.WorkTable(templateFile)
        else:
            w.parseWorTableFile(templateFile)
        self.worktable = w

    def set_as_current(self):
        Lab.curWorkTable=self.worktable

    def setUsed(self, tipMask, labware_selection):
        # Deprecated ??????
        mask, tips = self.curArm().drop_test(tipMask)
        assert len(tips, labware_selection.selected())
        for i, w in enumerate(labware_selection.selected_wells()):
            self.curArm().Tips[tips[i]] = Lab.usedTip(self.curArm().Tips[tips[i]], w)


    # Functions to observe the iRobot status (intern-physical status, or user status with are modificators of future
    # physical actions), or to modify the user status, but not the physical status. It can be used by the protocol
    # instruction and even by the final user.

    def where_are_preserved_tips(self, selected_reactive, TIP_MASK, type)->[Lab.DITIrack]:
        """

        :param TIP_MASK:
        :param type:
        :return:  Return a list of racks with the tips-wells already selected.
        """
        TIP_MASK = TIP_MASK if TIP_MASK != -1 else tipsMask[nTips]
        type = type if type else Lab.def_DiTi
        n = Lab.count_tips(TIP_MASK)
        assert n == len(selected_reactive)
        where = []
        for react_offset in selected_reactive:
            assert react_offset in type.preserved_tips
            well_tip = type.preserved_tips[react_offset]
            assert isinstance(well_tip, Lab.Well)
            if well_tip.labware in where:
                well_tip.selFlag = True
            else:
                where += [well_tip.labware]
                well_tip.labware.selectOnly(well_tip.offset)
        return where

    def where_preserve_tips(self, TIP_MASK)->[Lab.DITIrack]:
        """ Return a list of racks with the tips-wells already selected.

        :param selection:
        :return:
        """   # todo this in Labware??

        TIP_MASK = TIP_MASK if TIP_MASK != -1 else tipsMask[nTips]
        types = []
        t_masks = []
        racks = []
        tips = []

        for i, tip in enumerate(self.curArm().Tips):
            if TIP_MASK & (1 << i):
                assert tip, "There are no tip mounted in position " + str(i)
                tips += [tip]
                if tip.type in types:
                    t_masks[types.index(tip.type)] |= (1 << i)
                else:
                    types += [tip.type]
                    t_masks += [(1 << i)]

        assert len(types)==1   # todo temporally assumed only one type of tips
        tpe = types[0]
        m = t_masks[0]

        if not self.usePreservedtips:  # no re-back DiTi for multiple reuse
            assert isinstance(tpe, Lab.Labware.DITIrackType)
            if not tpe.last_preserved_tips:
                tpe.last_preserved_tips = tpe.pick_next_rack.Wells[0]
            w = tpe.last_preserved_tips
            assert isinstance(w, Lab.Well)
            cont = False
            rack = w.labware
            assert isinstance(rack, Lab.DITIrack)
            ip = w.offset
            n = Lab.count_tips(m)
            while n:
                cont, fw = rack.find_free_wells(n, init_pos=ip)
                if cont:
                    racks += [rack]
                    rack.selectOnly([w.offset for w in fw])
                    n -= len(fw)
                    rack = rack.next_rack(self.worktable)
                    ip = 0
            return racks

        for tp in tips:
            assert isinstance(tp, Lab.usedTip)
            react_well = tp.origin
            assert react_well.offset in tp.type.preservedtips, "There are no tip preserved for sample "+str(i)
            tip_well = tp.type.preservedtips[react_well.offset]
            assert isinstance(tip_well, Lab.Well)
            if tip_well.labware in racks:
                tip_well.selFlag = True
            else:
                racks += [ tip_well.labware]
                tip_well.labware.selectOnly(tip_well.offset)
        return racks


    def set_dropTips(self, drop=True)->bool:
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

    # Functions to change the physical status, to model physical actions, or that directly
    # correspond to actions in the hardware.
    # It can be CALL ONLY FROM the official low level INSTRUCTIONS in the method Itr.actualize_robot_state(self):

    def getTips(self, rack, tip_mask=-1,lastPos=False) -> (int, [Lab.Tip]):
        """ To be call from Itr.actualize_robot_state(self): actualize iRobot state (tip mounted and DiTi racks)
        Return the mask with will be really used taking into account the iRobot state, specially, the "reusetips"
        status and the number of tips already mounted.
        If it return mask = 0 no evo-instruction for the real robot will be generated in some cases.

        :param rack: the king of tip.
        :param tip_mask:
        :param lastPos: begging in backward direction?
        :return: int
        """
        if isinstance(rack, Lab.Labware.DITIrackType):
            rack = rack.pick_next_rack
        assert isinstance(rack, Lab.DITIrack)
        tip_mask = self.getTips_test(rack.type, tip_mask)
        tips = rack.remove_tips(tip_mask, rack.type, self.worktable, lastPos=lastPos)
        return self.curArm().getTips(rack.type, tip_mask, tips)

    def dropTips(self, TIP_MASK=-1, waste=None):
        if not self.droptips: return 0

        waste = waste if waste else Lab.def_DiTiWaste
        assert isinstance(waste, Lab.DITIwaste)

        TIP_MASK, tips = self.curArm().drop(TIP_MASK)
        waste.waste(tips)

        return TIP_MASK

    def pipette(self, action, volume, labware_selection, tip_mask=-1) -> (list, int):
        volume, tip_mask = self.curArm().pipette(action, volume, tip_mask)
        w = -1
        # assert isinstance(labware_selection, Lab.Labware)
        wells = labware_selection.selected_wells()
        for i, tp in enumerate(self.curArm().Tips):
                if tip_mask & (1 << i):
                    w += 1
                    dv = action*volume[i]
                    assert wells[w].vol is not None, "Volume of " + wells[w].reactive.name + " not initialized."
                    nv = wells[w].vol - dv
                    assert 0 <= nv <= wells[w].labware.type.maxVol, "Error tryin to change the volume of " + \
                         wells[w].reactive.name + " from " + str(wells[w].vol)  + " to " + str(nv)

                    wells[w].vol = nv
                    if    action == Robot.Arm.Aspire:
                        self.curArm().Tips[i] = Lab.usedTip(tp, wells[w])
                        wells[w].log(dv)
                    elif  action == Robot.Arm.Dispense:
                        assert isinstance(tp, Lab.usedTip)
                        wells[w].log(dv, tp.origin)
        return volume, tip_mask

    def set_tips_back(self, TIP_MASK, labware_selection):
        """ The low level instruction have to be generated already with almost all the information needed.
        Here we don't check any more where we really need to put the tips.
        Be careful by manual creation of low level instructions: they are safe if they are generated
        by protocol instructions (dropTips(), and preserve and usePreserved were previously set).
        :param TIP_MASK:
        :param labware:
        """
        # todo what if self.droptips: is False ???
        TIP_MASK, tips = self.curArm().drop(TIP_MASK)
        labware_selection.set_back(TIP_MASK, tips)
        return TIP_MASK

    def pick_up_tips(self, TIP_MASK, labware_selection) -> int:
        """ The low level instruction have to be generated already with almost all the information needed.
        Here we don't check any more from where we really need to pick the tips
        and assume they are all in the same rack.
        Be careful by manual creation of low level instructions: they are safe if they are generated
        by protocol instructions (dropTips(), and preserve and usePreserved were previously set).
        :param labware_selection:
        :param TIP_MASK:
        """

        TIP_MASK = self.curArm().getTips_test(TIP_MASK)
        tips = labware_selection.pick_up(TIP_MASK)
        return self.curArm().getTips(TIP_MASK, tips)


