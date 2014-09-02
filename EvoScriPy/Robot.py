__author__ = 'qPCR4vir'

from Instruction_Base import Pippet
from Labware import WorkTable

tipMask=[]     # mask for one tip of index ...
tipsMask=[0]   # mask for the first tips
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2**tip - 1]

def_nTips=4

class Robot:
    class arm:
        DiTi=0
        Fixed=1

        class tip:
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


        def get(self, TIP_MASK=-1, maxVol=1000):
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tp in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tp != None: raise "Tip already in position "+str(i)
                    self.Tips[i] = tip(maxVol)

        def drop(self, TIP_MASK=-1):
            if  TIP_MASK==-1:
                self.Tips=[None]* self.nTips
                return
            for i in range(self.nTips):
                if TIP_MASK & (1<<i):
                    self.Tips[i]=None

        def aspire(self, vol, TIP_MASK=-1): # todo more checks
            if TIP_MASK == -1:  TIP_MASK = tipsMask[self.nTips]
            for i,tip in enumerate(self.Tips):
                if TIP_MASK & (1<<i):
                    if tip == None: raise "No tip in position "+str(i)
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
                    {arms.index, arms} if isinstance(arms,Robot.arm ) else \
                    {arms.index, Robot.arm(nTips,index,workingTips,tipsType)}

        self.worktable=WorkTable(templateFile)

curRobot=None


