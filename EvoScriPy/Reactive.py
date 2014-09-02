__author__ = 'qPCR4vir'

import Labware

class Reactive:
    def __init__(self, name, labware, pos, volpersample):
        self.name = name
        self.labware = labware
        self.pos = labware.offset(pos)
        self.volpersample = volpersample
        self.labware.Wells[self.pos].reactive=self


class preMix(Reactive):
    def __init__(self, name, labware, pos, components):
        self.components = components
        for react in components:



