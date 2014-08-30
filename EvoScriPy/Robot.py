__author__ = 'qPCR4vir'

tipMask=[]
tipsMask=[]
for tip in range(13):
    tipMask += [1 << tip]
    tipsMask += [2**tip - 1]



class Robot:
    class arm:
        DiTi=0
        Fixed=1
        def __init__(self, nTips, workingTips=None, tipsType=DiTi):
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips]
            self.tipsType = tipsType
            self.nTips=nTips
            self.mountedTips=0
            self.mountedTipsType=1000

        def drop(self, TIP_MASK=-1):


