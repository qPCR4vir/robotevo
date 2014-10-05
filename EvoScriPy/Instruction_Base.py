__author__ = 'qPCR4vir'
# todo Revise def values: the binding take place at the moment of first import ???
import EvoMode
import Labware as Lab
import Robot as Rbt

supportVirtualRobot = True  # todo explore this idea ! (problems with "asynchronous" and multiple mode)


class EvoTypes:  # TODO improve EvoTypes: string1: "V[~i~]", string2: V[~i~], integer, float, expr[12]
    def __init__(self, data):
        self.data = data

    def __str__(self):  # todo implement exceptions
        return str(self.data)


class string1(EvoTypes):
    def __str__(self):
        return '"' + str(self.data) + '"'


class expression(string1):
    pass


class expr(EvoTypes):
    def __init__(self, dim, data):
        EvoTypes.__init__(self, data)
        self.dim = dim

    def split(self):  # TODO 0 instant "0" ???? ; split - is not an elegant solution
        if isinstance(self.data, list):
            d = self.dim - len(self.data)
            assert (d >= 0)
            return [integer(0) if v is None else expression(v) for v in self.data] + [integer(0)] * d
        else:
            return [integer(0) if self.data is None else expression(self.data)] * self.dim


class string2(EvoTypes):
    pass


class integer(EvoTypes):  # todo implement exceptions
    def __str__(self):
        return str(int(self.data))


class floating_point(EvoTypes):  # todo implement exceptions
    def __str__(self):
        return str(float(self.data))


class LoopOption:
    def __init__(self, name, action, difference):
        """

        :param name: str; name
        :param action: int;
        :param difference: int;
        """
        self.name = name
        self.action = action
        self.difference = difference
    # loop action:
    VaryColumn = 0
    VaryRow = 1
    VaryWell = 2
    VaryRack = 3


class Instruction:
    def __init__(self, name):
        self.name = name
        self.arg = []

    def validateArg(self):
        self.arg = []
        return False

    def allowed(self, mode):
        return True

    def actualize_robot_state(self):
        pass

    def exec(self, mode=None):
        if not mode: mode = EvoMode.current  # todo revise
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
        return not isinstance(mode, EvoMode.AdvancedWorkList)


class Device(Instruction):
    def __init__(self, devicename, commandname):
        Instruction.__init__(self, "FACTS")
        self.commandname = commandname
        self.devicename = devicename

    def validateArg(self):
        Instruction.validateArg(self)
        self.arg += [string1(self.devicename), string1(self.commandname)]
        return False


class T_Mag_Instr(Device):
    """ A.15.10 Advanced Worklist Commands for the Te-MagS
    """
    Dispense    = 0
    Aspirate    = 1
    Resuspension = 2
    Incubation  = 3

    def __init__(self, commandname):
        Device.__init__(self, "Te-MagS", commandname)


def_TipMask     = 15          # todo revise. here? use Robot?
curTipMask      = def_TipMask
def_liquidClass = "Buffer free DITi 1000-AVR" # "AVR-Water free DITi 1000" # "Water free dispense DiTi 1000"
def_vol         = [0]*12
def_LoopOp      = []
def_AirgapSpeed = 300


class Pipette(Instruction):
    LiHa1 = 0
    LiHa2 = 1
    def __init__(self, name, tipMask     = curTipMask,
                             labware     = None,
                             spacing     = 1,           # todo how to use???
                             wellSelection = None,      # todo how to use???
                             LoopOptions = def_LoopOp,  # todo how to model???
                             RackName    = None,        # todo I need to this???
                             Well        = None,        # todo I need to this???
                             arm         = LiHa1):
        """

        :param name: str; Instruction name
        :param tipMask: int; selected tips, bit-coded (tip1 = 1, tip8 = 128)
        :param labware: Labware;
        :param spacing: int; Tip Spacing
                                    The Tip Spacing parameter controls the distance between adjacent pipetting
                                    tips for this command. You can choose a different tip spacing for the source
                                    labware and the destination labware. Tip spacing is only relevant if you want
                                    to use more than one tip. A tip spacing of 1 means that the tips will be spread
                                    to match the distance between adjacent wells in the labware. A tip spacing of
                                    2 will select every other well in the labware. You can only choose values for tip
                                    spacing which are meaningful for the labware geometry.
                                    The liquid handling arm achieves the highest mechanical accuracy when the
                                    tips are not spread. For high-density labware such as 1536-well microplates,
                                    you should choose tip spacing such that the tips are adjacent to one another
                                    (physical tip spacing 9 mm). Accordingly, for 1536-well microplates you should
                                    set tip spacing to 4 (every fourth well).
        :param wellSelection: str; bit-coded well selection
        :param LoopOptions: list; of objects of class LoopOption.
        :param RackName:
        :param Well:
        :param arm:
        """
        Instruction.__init__(self, name)
        self.tipMask=tipMask
        self.labware=labware or Lab.def_LabW
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

    def exec(self, mode=None):
        if self.tipMask: Instruction.exec(self, mode)


class Pipetting(Pipette):
    def __init__(self, name, tipMask     = curTipMask,
                             liquidClass = def_liquidClass,
                             volume      = def_vol,
                             labware     = Lab.def_LabW,
                             spacing     = 1,
                             wellSelection= None,
                             LoopOptions = def_LoopOp,
                             RackName    = None,
                             Well        = None,
                             arm         = Pipette.LiHa1):
        Pipette.__init__(self, name, tipMask    ,
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
        Pipette.validateArg(self)
        nTips = Rbt.Robot.current.curArm().nTips
        self.arg[1:1] = [string1(self.liquidClass)] + expr(nTips, self.volume).split() + [int(0)] * (
            12 - nTips)  # arg 2, 3 - 14
        return True

    def actualize_robot_state(self):
        self.pipette_on_iRobot(self.action())
        pass

    def pipette_on_iRobot(self,action):
        self.volume, self.tipMask = Rbt.Robot.current.curArm().pipette(action, self.volume, self.tipMask )


class DITIs(Instruction):
    def __init__(self, name, tipMask=curTipMask, options=0, arm=Pipette.LiHa1):
        """

        :param name: str, instruction
        :param tipMask:
        :param options: int, 0-1. bit-coded 1 = if diti not fetched try 3 times then go to next position
        :param arm:
        """
        Instruction.__init__(self, name)
        self.options = options
        self.tipMask = tipMask
        self.arm = arm

    def validateArg(self):
        Instruction.validateArg(self)
        self.arg = [integer(self.tipMask)]   # arg 1
        self.arg += [integer(self.options)]  # arg 3 (the arg 2 is type -an index- or labware name)
        self.arg += [integer(self.arm)]      # arg 4
        return True
