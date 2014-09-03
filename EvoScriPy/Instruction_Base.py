__author__ = 'qPCR4vir'
#todo Revise def values: the binding take place at the moment of first import ???
import EvoMode
import Labware

supportVirtualRobot=True  # todo explore this idea ! (problems with "asynchronous" and multiEvo mode)

class EvoTypes: # TODO improve EvoTypes: string1: "V[~i~]", string2: V[~i~], integer, float, expr[12]
    def __init__(self, data):
        self.data = data
    #def __eq__(self, other):

    def __str__(self): # todo implement exceptions
        return str(self.data)

class string1(EvoTypes):
    #def __init__(self, data):
    #   EvoTypes.__init__(self,data)

    def __str__(self):
        return '"'+ str(self.data) + '"'

class expression(string1):
    pass

class expr(EvoTypes):
    def __init__(self, dim, data):
        self.dim = dim
        self.data = data

    def split(self):  #TODO 0 instant "0" ???? ; split - is not an elegant solution
        if isinstance(self.data,list):
            d=self.dim-len(self.data)
            assert (d>=0)
            return [expression(v) for v in self.data+[0]*d]
        else:
            return [expression(self.data)]*self.dim

class string2(EvoTypes):
    pass

class integer(EvoTypes):   # todo implement exceptions
    def __str__(self):
        return str(int(self.data))

class floating_point(EvoTypes):
    def __str__(self):
        return str(float(self.data))


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

    def allowed(self, mode):
        return True

    def exec(self, mode=None):
        if not mode: mode=EvoMode.CurEvo
        if not self.allowed(mode):
            return
        mode.exec(self)

    def __str__(self):
        self.validateArg()
        return self.name + "(" + ','.join([          ''   if    a is None
                                           else '"'+a+'"' if isinstance(a,str)
                                           else  str(a)       for a in self.arg]) + ");"

class ScriptONLY(Instruction):
    def allowed(self, mode):
        return not isinstance(mode,EvoMode.AdvancedWorkList)

class Device(Instruction):
    def __init__(self, devicename, commandname):
        Instruction.__init__(self, "FACTS")
        self.commandname = commandname
        self.devicename = devicename

    def validateArg(self):
        Instruction.validateArg(self)
        self.arg += [string1(self.devicename),string1(self.commandname)]
        return False

class T_Mag_Instr(Device):
    """ A.15.10 Advanced Worklist Commands for the Te-MagS
    """
    Dispense    = 0
    Aspirate    = 1
    Resuspension = 2
    Incubation  = 3

    def __init__(self,  commandname):
        Device.__init__(self, "Te-MagS", commandname )



def_TipMask     = 15          # todo revise. here? use Robot?
curTipMask      = def_TipMask
def_liquidClass = "Buffer free DITi 1000-AVR" # "AVR-Water free DITi 1000" # "Water free dispense DiTi 1000"
def_vol         = [0]*12
def_LabW        = Labware.Labware(type=Labware.MP96well,location=Labware.Labware.Location(1,1))
def_LoopOp      = []
def_WashWaste   = Labware.WashWaste
def_WashCleaner = Labware.WashCleanerS
def_DiTiWaste   = Labware.DiTiWaste
def_AirgapSpeed = 300

class Pippet(Instruction):
    LiHa1 = 0
    LiHa2 = 1
    def __init__(self, name, tipMask     = curTipMask,
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
        """
        Evoware visual script generator enforce a compatibility between the arguments tipMask and well selection.
        If they are not compatible the robot crash.
        :return:

        """
        self.arg  =  [integer(self.tipMask)]                                                    # arg 1
        self.arg +=  [integer(self.labware.location.grid), integer(self.labware.location.site), # arg 2, 3
                      integer(self.spacing),         string1( self.labware.wellSelectionStr()) ]# arg 4, 5
        self.arg +=  [integer(len(self.loopOptions))]                                           # arg 6
        for op in self.loopOptions:
            self.arg +=  [string1(op.name), integer(op.action), integer(op.difference) ]        # arg 7, 8, 9
        self.arg +=  [integer(self.arm)]                                                        # arg 10

        return True

class Pippeting(Pippet):
    def __init__(self, name, tipMask     = curTipMask,
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

        self.arg[1:1] = [string1(self.liquidClass)] + expr(4,self.volume).split() + [int(0)]*8         # arg 2, 3 - 14
        return True

class DITIs(Instruction):
    def __init__(self, name, tipMask= curTipMask,  options=0, arm= Pippet.LiHa1):
        """

        :param name: str, instruction
        :param tipMask:
        :param options: int, 0-1. bit-coded 1 = if diti not fetched try 3 times then go to next position
        :param arm:
        """
        Instruction.__init__(self, name )
        self.options = options
        self.tipMask=tipMask
        self.arm = arm

    def validateArg(self):
        Instruction.validateArg(self)
        self.arg  =  [integer(self.tipMask)]                                                    # arg 1
        self.arg += [integer(self.options)]
        self.arg +=  [integer(self.arm)]                                                        # arg 10
        return True
