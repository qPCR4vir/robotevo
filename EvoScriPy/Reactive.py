__author__ = 'qPCR4vir'


import Labware as Lab
# from Robot import current
from Instruction_Base import def_liquidClass

def_react_excess =  4
def_mix_excess   =  8
NumOfSamples     = None

class Reactive:
    def __init__(self, name, labware,  volpersample,
                 pos=None, replicas=None, defLiqClass=None, excess=None, init_vol=None):
        """
        Put a reactive into labware wells, possible with replicates and set the amount to be used for each sample

        :param name:
        :param labware:
        :param volpersample:
        :param pos: if not set (=None) we will try to assign consecutive wells
        :param replicas: def 1
        :param defLiqClass:
        :param excess:
        :param init_vol: is set for each replica. If default (=None) is calculated als minimum.
        """
        ex= def_react_excess if excess is None else excess
        self.excess = 1 + ex/100
        self.defLiqClass = defLiqClass or def_liquidClass
        self.name = name
        self.volpersample = volpersample
        self.labware = labware
        self.Replicas = labware.put(self,pos,replicas)
        self.pos = self.Replicas[0].offset

        for w in  self.Replicas :
             w.vol = init_vol

    def minVol(self, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples or 0
        return self.volpersample * NumSamples * self.excess

    def put_min_vol(self, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples
        V = self.volpersample * self.excess
        replicas=len(self.Replicas)
        for i, w in enumerate(self.Replicas):
            w.vol = V * (NumOfSamples + replicas - (i+1))//replicas

    def autoselect(self,maxTips=1):
        return self.labware.autoselect(self.pos,maxTips,len(self.Replicas))

class preMix(Reactive):
    def __init__(self, name, labware, pos, components, replicas=1, init_vol=None,
                 defLiqClass=None, excess=None):
        ex= def_mix_excess if excess is None else excess
        vol=0
        for react in components:
            vol += react.volpersample
            react.excess =  1 + ex/100      # todo revise! best to calculate at the moment of making?

        if init_vol is None: init_vol = 0
        Reactive.__init__(self,name,labware,vol,pos,replicas,defLiqClass,ex, init_vol=init_vol)
        self.components = components

    def make(self, NumSamples=None):
        if self.Replicas[0].vol is None:
            self.put_min_vol(NumSamples)
        from protocol import makePreMix
        makePreMix(self, NumSamples)

    def compVol(self,index, NumSamples=None):
        NumSamples = NumSamples or NumOfSamples
        return self.components[index].minVol(NumSamples)



