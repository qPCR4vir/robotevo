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

        class tip:
            def __init__(self, maxVol=1000)
                    self.vol=0
                    self.maxVol=maxVol
                    
            
        def __init__(self, nTips, workingTips=None, tipsType=DiTi):
            self.workingTips = workingTips if workingTips is not None else tipsMask[nTips]
            self.tipsType = tipsType
            self.nTips=nTips
            self.

        def drop(self, TIP_MASK=-1):
            

