__author__ = 'qPCR4vir'


from Labware import *
# from Robot import curRobot


def_react_excess =  4
def_mix_excess   =  8
NumOfSamples     = None

class Reactive:
    def __init__(self, name, labware,  volpersample,
                 pos=0, replys=1, defLiqClass=None, excess=None):
        ex= def_react_excess if excess is None else excess
        self.excess = 1 + ex/100
        self.defLiqClass = defLiqClass
        self.replys = replys
        self.name = name
        self.labware = labware
        self.pos = labware.offset(pos)
        self.volpersample = volpersample
        self.labware.Wells[self.pos].reactive=self

    def minVol(self, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples
        return self.volpersample * NumSamples * self.excess

    def autoselect(self,maxTips=1):
        return self.labware.autoselect(self.pos,maxTips,self.replys)

class preMix(Reactive):
    def __init__(self, name, labware, pos, components, replys=1,
                 defLiqClass=None, excess=None):
        ex= def_mix_excess if excess is None else excess
        vol=0
        for react in components:
            vol += react.volpersample
            react.excess =  1 + ex/100      # todo revise! best to calculate at the moment of making?
        Reactive.__init__(self,name,labware,vol,pos,replys,defLiqClass,ex)
        self.components = components

    def make(self, NumSamples=None):
        from Robot import curRobot
        curRobot.make(self, NumSamples)

    def compVol(self,index, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples
        return self.components[index].minVol(NumSamples)



