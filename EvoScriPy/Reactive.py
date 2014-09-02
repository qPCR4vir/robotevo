__author__ = 'qPCR4vir'

from Labware import *
from Instructions import *

class Reactive:
    def __init__(self, name, labware,  volpersample,pos=0, replys=1, defLiqClass=def_liquidClass):
        self.defLiqClass = defLiqClass
        self.replys = replys
        self.name = name
        self.labware = labware
        self.pos = labware.offset(pos)
        self.volpersample = volpersample
        self.labware.Wells[self.pos].reactive=self

    def minVol(self, NumSamples=None):
        if not NumSamples:
            global NumOfSamples
            NumSamples=NumOfSamples
        return self.volpersample * NumSamples



class preMix(Reactive):
    def __init__(self, name, labware, pos, components, defLiqClass=def_liquidClass):
        vol=0
        for react in components:
            vol += react.volpersample
        Reactive.__init__(self,name,labware,vol,pos,defLiqClass)
        self.components = components

    def make(self):
        for react in self.components:
            aspirate(1,)





