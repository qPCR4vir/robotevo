__author__ = 'qPCR4vir'

from Instructions import *
from Labware import WorkTable
import Reactive

tipMask=[]     # mask for one tip of index ...
tipsMask=[]   # mask for the first tips
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2**tip - 1]

def_nTips=4

class Tip:
    def __init__(self, maxVol=1000):
        self.vol = 0
        self.maxVol = maxVol

class Robot:


     class arm:
        DiTi=0
        Fixed=1

        class Tip:
            def __init__(self, maxVol=1000):
                self.vol = 0
                self.maxVol = maxVol


        def __init__(self, nTips, index=Pippet.LiHa1 ,workingTips=None, tipsType=DiTi ):
            """

            :param nTips:
            :param index:
            :param workingTips:
            :param tipsType:
            """
            self.index = index
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips]
            self.tipsType = tipsType
            self.nTips=nTips
            self.Tips=[None]* nTips


        def getTips(self, TIP_MASK=-1, maxVol=1000):
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tp in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tp != None: raise "Tip already in position "+str(i)
                    self.Tips[i] =  Tip(maxVol)
            return TIP_MASK

        def getMoreTips(self, TIP_MASK=-1, maxVol=1000):
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tp in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tp:                  # already in position
                        TIP_MASK ^= (1<<i)  # todo raise if dif maxVol? or if vol not 0?
                    else:
                       self.Tips[i] = Tip(maxVol)
            return TIP_MASK

        def drop(self, TIP_MASK=-1):
            """
            :rtype : True if actually ned to be drooped
            """
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tp in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tp:                  #   in position
                        self.Tips[i] = None
                    else:
                        TIP_MASK ^= (1<<i)  # already drooped
            return TIP_MASK

        def aspire(self, vol, TIP_MASK=-1): # todo more checks
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tip in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    assert tip is not None, "No tip in position "+str(i)
                    nv = tip.vol + vol[i]
                    if nv > tip.maxVol: raise 'To much Vol in tip '+str(i)
                    tip.vol = nv

        def dispense(self, vol, TIP_MASK=-1): # todo more checks
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tip in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tip == None: raise "No tip in position "+str(i)
                    tip.vol += vol[i]


     class ProtocolStep:
        pass

     class makeMix(ProtocolStep):
        pass

     class distrReactive(ProtocolStep):
        pass

     class Transfer(ProtocolStep):
        def __init__(self, src, dest, vol):
            pass

     def __init__(self, arms=None, nTips=def_nTips,
                 index=Pippet.LiHa1 , workingTips=None,
                 tipsType=arm.DiTi, templateFile=None):
        """

        :param arm:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        self.arms =  arms              if isinstance(arms,dict      ) else \
                    {arms.index: arms} if isinstance(arms,Robot.arm ) else \
                    {arms.index: Robot.arm(nTips,index,workingTips,tipsType)}

        self.worktable=WorkTable(templateFile)
        self.def_arm=index
        self.droptips=True
        self.reusetips=False
        self.preservetips=False
        self.usePreservedtips=False
     def dropTips(self,drop=True):
        self.droptips, drop =  drop, self.droptips
        return drop
     def reuseTips(self,reuse=True):
        self.reusetips, reuse = reuse, self.reusetips
        return reuse
     def preserveTips(self,preserve=True):
        self.preservetips, preserve = preserve, self.preservetips
        return preserve
     def usePreservedTips(self,usePreserved=True):
        self.usePreservedtips, usePreserved = usePreserved, self.usePreservedtips
        return usePreserved
     def curArm(self,arm=None):
        if arm is not None: self.def_arm=arm
        return self.arms[self.def_arm]

     def getTips(self, TIP_MASK=-1, maxVol=1000):
        if self.reusetips:
            TIP_MASK = self.curArm().getMoreTips(TIP_MASK,maxVol)
        else:
            self.dropTips(TIP_MASK)
            TIP_MASK = self.curArm().getTips(TIP_MASK,maxVol)
        if TIP_MASK:
            getDITI2(TIP_MASK,arm=self.def_arm).exec()
        return TIP_MASK

     def dropTips(self, TIP_MASK=-1):
        if not self.droptips: return 0
        TIP_MASK = self.curArm().drop(TIP_MASK)
        if TIP_MASK:
            dropDITI(TIP_MASK).exec()
        return TIP_MASK

     def make(self,what):
        if isinstance(what,Reactive.preMix): self.makePreMix(what)

     def aspire(self, tip, reactive, vol=None):
        if vol is None:
            vol=reactive.minVol()
        v=[0]*self.arms[self.def_arm].nTips
        v[tip]=vol
        reactive.labware.selectOnly([reactive.pos])
        self.arms[self.def_arm].aspire(v,tipMask[tip])
        aspirate(tipMask[tip],reactive.defLiqClass,v,reactive.labware).exec()

     def dispense(self, tip, reactive, vol=None):
        if vol is None:
            vol=reactive.minVol()     # really ??
        reactive.labware.selectOnly([reactive.pos])
        v=[0]*self.arms[self.def_arm].nTips
        v[tip]=vol
        self.arms[self.def_arm].dispense(v,tipMask[tip])
        dispense(tipMask[tip],reactive.defLiqClass,v,reactive.labware).exec()

     def makePreMix(self, pMix):
        nc=len(pMix.components)
        assert nc <= self.arms[self.def_arm].nTips, \
            "Temporally the mix can not contain more than {:d} components.".format(self.arms[self.def_arm].nTips)
        self.getTips(tipsMask[nc])
        for i,react in enumerate(pMix.components):
            self.aspire(i,react)
            self.dispense(i,pMix,react.minVol())
        self.dropTips()








curRobot=None


