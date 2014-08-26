__author__ = 'elisa.reader'

import EvoMode
import Labware

class LoopOption:
    def __init__(self, name, action, difference):
        self.name=name
        self.action=action
        self.difference=difference

    VaryColumn=0
    VaryRow=1
    VaryWell=2
    VaryRack=3


class Instruction:
    def __init__(self, name):
        self.name = name
        self.arg = []

    def validateArg(self):
        return False

    def __repr__(self):
        self.validateArg()
        return self.name + "(" + ','.join([          ''   if    a is None
                                           else '"'+a+'"' if isinstance(a,str)
                                           else  str(a)       for a in self.arg]) + ")"


def_tipMask=15
def_liquidClass="Water"
def_vol=[0]*12
def_LabW = Labware.Labware(type=Labware.MP96well)
def_LoopOp = []


class Pippet(Instruction):
    LiHa1 = 0
    LiHa2 = 1
    def __init__(self, name, tipMask     = def_tipMask,
                             labware     = def_LabW,
                             spacing     = 1,
                             wellSelection = None,
                             LoopOptions = def_LoopOp,
                             RackName    = None,
                             Well        = None,
                             arm         = LiHa1):
        Instruction.__init__(self, name)
        self.tipMask=tipMask
        self.labware=labware
        self.spacing = spacing
        self.loopOptions = LoopOptions
        self.RackName = RackName
        self.Well = Well
        self.arm = arm
                            # noOfLoopOptions,
                            # loopName,
                            # action,
                            # difference,

    def validateArg(self):
        self.arg  =  [self.tipMask]
        self.arg +=  [self.labware.location.grid, self.labware.location.site, self.spacing, self.labware.wellSelectionStr()]
        self.arg +=  [len(self.loopOptions)]
        for op in self.loopOptions:
            self.arg +=  [op.name, op.action, op.difference ]
        self.arg +=  [self.arm]

        return True


class Pippeting(Pippet):
    def __init__(self, name, tipMask     = def_tipMask,
                             liquidClass = def_liquidClass,
                             volume      = def_vol,
                             labware     = def_LabW,
                             spacing     = 1,
                             wellSelection= None,
                             LoopOptions = def_LoopOp,
                             RackName    = None,
                             Well        = None,
                             arm         = Pippet.LiHa1):
        Pippet.__init__(self, name, tipMask    ,
                             labware     ,
                             spacing    ,
                             wellSelection,
                             LoopOptions,
                             RackName    ,
                             Well      ,
                             arm       )
        self.liquidClass=liquidClass
        self.volume=volume

    def validateArg(self):
        Pippet.validateArg(self)

        if not isinstance(self.volume,list):
            vol=[str(self.volume)]*12
        else:
            d=12-len(self.volume)
            assert (d<=12)
            vol= [str(v) for v in self.volume+[0]*d]

        self.arg[1:1] = [self.liquidClass] + vol
        return True



class aspirate(Pippeting):
    def __init__(self, RackName = None, Well = None):
        Pippeting.__init__(self, 'Aspirate', RackName , Well)


class dispence(Pippeting):
    def __init__(self, RackName = None, Well = None):
        Pippeting.__init__(self, 'Dispence', RackName , Well)


class mix(Pippeting):
    def __init__(self, RackName = None, Well = None):
        Pippeting.__init__(self, 'Mix', RackName , Well)


class wash_tips(Pippet):
    def __init__(self):
        Pippet.__init__(self, "Wash")
        assert False,"Wash() not implemented"


class DITIs(Pippet):
    def __init__(self, name, tipMask, type):
        Pippet.__init__(self, name, tipMask)
        self.type=type
        


def Aspirate( tipMask,
              liquidClass,
              volume,
              grid,
              site,
              spacing,
              wellSelection,
              noOfLoopOptions,
              loopName,
              action,
              difference,
              arm,
              RackName=None,
              Well=None):
    """
    :param difference:
    :param action:
    :param loopName:
    :param site:
    :param spacing:
    :param wellSelection:
    :param noOfLoopOptions:
    :param tipMask: int 0 - 255, selected tips, bit-coded (tip1 = 1, tip8 = 128)
    :param liquidClass: str,
    :param volume: expr[12], 12 expressions which the volume for each tip. 0 for tips which are not used or not fitted.
    :param grid: int, 1 - 67, labware location - carrier grid position
    :param RackName:
    :param Well:
    """
    a = aspirate( RackName , Well)
    a.tipMask       = tipMask
    a.liquidClass   = liquidClass
    a.volume        = volume
    a.labware.location = Labware.Labware.Location(grid,site)

    return a,EvoMode.CurEvo.exec(a)

def Dispence(tipMask,liquidClass,volume,grid, site, spacing, wellSelection,LoopOptions, RackName,Well):
    """
    :param tipMask: int 0 - 255, selected tips, bit-coded (tip1 = 1, tip8 = 128)
    :param liquidClass: str,
    :param volume: expr[12], 12 expressions which the volume for each tip. 0 for tips which are not used or not fitted.
    :param grid: int, 1 - 67, labware location - carrier grid position
    :param RackName:
    :param Well:
    """
    a = dispence( RackName , Well)
    a.tipMask       = tipMask
    a.liquidClass   = liquidClass
    a.volume        = volume
    a.labware.location = Labware.Labware.Location(grid,site)
    a.loopOptions=LoopOptions

    return a,EvoMode.CurEvo.exec(a)





