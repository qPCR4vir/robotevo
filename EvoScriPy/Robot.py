__author__ = 'qPCR4vir'

import Instructions

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
                    
            
        def __init__(self, nTips, index=Instructions.Pippet.LiHa1 ,workingTips=None, tipsType=DiTi ):
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

        def drop(self, TIP_MASK=-1):
            if  TIP_MASK==-1:
                self.Tips=[None]* self.nTips
                return
            for i in range(self.nTips):
                if TIP_MASK & (1<<i):
                    self.Tips[i]=None

        def aspire(self, vol, TIP_MASK=-1):
            TIP_MASK= TIP_MASK if TIP_MASK!=-1 else tipsMask[self.nTips]
            for i in range(self.nTips):
                if TIP_MASK & (1<<i):
                    if self.Tips[i]=None

    class ProtocolStep:
        pass

    class makeMix(ProtocolStep):
        pass

    class distrReactive(ProtocolStep):
        pass

    class Transfer(ProtocolStep):
        def __init__(self, src, dest, vol):
            pass

    def __init__(self, arms=None, nTips=def_nTips, index=Instructions.Pippet.LiHa1 , workingTips=None, tipsType=DiTi):
        """

        :param arm:
        :param nTips:
        :param workingTips:
        :param tipsType:
        """
        self.arms =  arms              if isinstance(arms,dict      ) else \
                    {arms.index, arms} if isinstance(arms,Robot.arm ) else \
                    {arms.index, Robot.arm(nTips,index,workingTips,tipsType)}




