# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'

"""
Implement the 
"""

# todo Revise def values: the binding take place at the moment of first import ???
import EvoScriPy.evo_mode
import EvoScriPy.labware as lab
import EvoScriPy.robot as robot

def_vol         = [0]*12
def_LoopOp      = []
def_AirgapSpeed = 300


class EvoTypes:  # OK improve EvoTypes: string1: "V[~i~]", string2: V[~i~], integer, float, expr[12]
    def __init__(self, data):
        self.data = data

    def __str__(self):  # todo implement exceptions
        return str(self.data)


class string1(EvoTypes):
    def __str__(self):
        s = "{:.2f}".format(self.data) if isinstance(self.data, float) else str(self.data)
        return '"' + s + '"'


class expression(string1):
    pass


class expr(EvoTypes):
    def __init__(self, dim, data):
        EvoTypes.__init__(self, data)
        self.dim = dim

    def split(self):  # OK 0 instant "0" ???? ; split - is not an elegant solution
        if isinstance(self.data, list):
            d = self.dim - len(self.data)
            assert (d >= 0)
            return [integer(0) if v is None else expression(v) for v in self.data] + [integer(0)] * d
        else:
            return [integer(0) if self.data is None else expression(self.data)] * self.dim


class string2(EvoTypes):
    pass


class integer(EvoTypes):  #  implement exceptions ?
    def __str__(self):
        return str(int(self.data))


class floating_point(EvoTypes):  #  implement exceptions ?
    def __str__(self):
        return "{:.2f}".format(float(self.data))


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
        self.robot = robot.Robot.current

    def validateArg(self):
        self.arg = []
        return False

    def allowed(self, mode):
        return True

    def actualize_robot_state(self):
        pass

    def exec(self, mode=None):
        if mode is None: mode = EvoScriPy.evo_mode.current  # todo revise
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
        return not isinstance(mode, EvoScriPy.evo_mode.AdvancedWorkList)


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
    """ A.15.10 Advanced Worklist Commands for the Te-MagS. pag. A - 198, pag. 16 - 100
        The Magnetic Bead Separator option (also called Te-MagS) is a magnetic bead
    separator with an optional heating function. It uses a commercially-available liquid
    containing microscopic magnetic beads to rapidly isolate bio-molecules (e.g.
    DNA, RNA, proteins etc.) or whole cells from various crude mixtures by means of
    magnetic forces. The magnetic beads are pulled through the liquid in the tubes
    using magnets and collect the required substance as they move.
    """

    def __init__(self, commandname):
        Device.__init__(self, "Te-MagS", commandname)


class Pipette(Instruction):
    LiHa1 = 0
    LiHa2 = 1

    def __init__(self,
                 name,
                 tipMask                    = None,
                 labware      : lab.Labware = None,
                 spacing                    = 1,           # todo how to use in actualize_robot_state, validateArg ?
                 wellSelection              = None,        # todo    use???
                 LoopOptions                = None,        # todo how to model???
                 RackName                   = None,        # todo I need to this???
                 Well                       = None,        # todo I need to this???
                 arm                        = LiHa1):      # set this as def
        """
        Set labware to match wells.

        :param name: str; Instruction name
        :param tipMask: int; selected tips, bit-coded (tip1 = 1, tip8 = 128)
        :param labware: Labware; grid 1-67, site 0-127, the labware with the selected wells
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
        :param wellSelection: str; list of wells. Converted to bit-coded well selection to be used.
        :param LoopOptions: list; of objects of class LoopOption.
        :param RackName:
        :param Well:
        :param arm:
        """
        Instruction.__init__(self, name)

        self.arm                = arm
        self.tipMask            = tipMask
        self.labware            = labware
        self.wellSelection      = wellSelection
        self.spacing            = spacing
        self.loopOptions        = LoopOptions
        self.RackName           = RackName
        self.Well               = Well
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
        Instruction.validateArg(self)

        self.arm = self.robot.curArm(self.arm)

        max_tip_mask = robot.tipsMask[self.arm.nTips]
        if self.tipMask is None:
            self.tipMask = max_tip_mask
        assert 0 <= self.tipMask <= max_tip_mask; "Invalid tip mask"

        if self.loopOptions is None:
            self.loopOptions = def_LoopOp

        well_selection_str = None                                      # Set selected wells to match labware selection.
        if self.wellSelection is None:                                 # only labware selection.
            assert isinstance(self.labware, lab.Labware)
            assert len(self.labware.selected_wells()) > 0, "No well selected for pipetting in " + str(self.labware) + "."
            well_selection_str = self.labware.wellSelectionStr()       # use them
        else:
            if not isinstance(self.wellSelection, list):
                self.wellSelection = [self.wellSelection]
            if len(self.wellSelection) == 0:
                assert isinstance(self.labware, lab.Labware)
                assert len(self.labware.selected_wells()) > 0, "No well selected to pipette."
                well_selection_str = self.labware.wellSelectionStr()
            else:
                w0 = self.wellSelection[0]
                if isinstance(w0, lab.Well):
                    if self.labware is None:
                        self.labware = w0.labware
                    assert w0.labware is self.labware, "Using a well from another labware"
                assert isinstance(self.labware, lab.Labware)
                self.labware.selectOnly(self.wellSelection)
                well_selection_str = self.labware.wellSelectionStr(self.wellSelection)



        self.arg  =  [integer(self.tipMask)]                                                    # arg 1
        self.arg +=  [integer(self.labware.location.grid),                                      # arg 2
                      integer(self.labware.location.site),                                      # arg 3
                      integer(self.spacing),                                                    # arg 4
                      string1(well_selection_str) ]                                             # arg 5
        self.arg +=  [integer(len(self.loopOptions))]                                           # arg 6
        for op in self.loopOptions:
            self.arg +=  [string1(op.name),
                          integer(op.action),
                          integer(op.difference) ]                                              # arg 7, 8, 9
        self.arg +=  [integer(self.arm.index)]                                                  # arg 10

        return True

    def exec(self, mode=None):
        if not self.tipMask:
            self.validateArg()
        if self.tipMask:
            Instruction.exec(self, mode)


class Pipetting(Pipette):

    @staticmethod
    def action():
        return False

    def __init__(self, name, tipMask     = None,
                             liquidClass = None,
                             volume      = None,
                             labware     = None,                                # todo ??????
                             spacing     = 1,
                             wellSelection= None,
                             LoopOptions = None,
                             RackName    = None,
                             Well        = None,
                             arm         = None):

        Pipette.__init__(self, name,
                             tipMask     = tipMask,
                             labware     = labware,
                             spacing     = spacing,
                             wellSelection= wellSelection,
                             LoopOptions = LoopOptions,
                             RackName    = RackName,
                             Well        = Well,
                             arm         = arm       )

        self.liquidClass = liquidClass                                     # todo reagent.LC ?
        self.volume      = volume if volume is not None else def_vol

    def validateArg(self):
        Pipette.validateArg(self)
        if isinstance(self.liquidClass  , str):
            self.liquidClass   = self.robot.liquid_clases.all[self.liquidClass  ]
        # todo use LiqC of the reagents in wells ?
        assert isinstance(self.liquidClass  .name, str), "Set the liquid class to be used (for the reagent?)"

        self.arg[1:1] =   [string1(self.liquidClass)]                              # arg 2

        nTips = self.robot.curArm().nTips
        if self.action():
            self.arg[2:2] =  expr   (nTips, self.volume).split()   \
                           + [int    (0)] * (12 - nTips)                           # arg 3 - 14 todo integer(0) ?
        return True

    def actualize_robot_state(self):
        self.validateArg()
        self.pipette_on_iRobot(self.action())
        pass

    def pipette_on_iRobot(self,action):
        # print("pipette_on_iRobot called with mask= " + str(self.tipMask))
        self.volume, self.tipMask = self.robot.pipette_executed(action, self.volume,
                                                                self.labware, self.tipMask)
        # print("pipette_on_iRobot return= " + str(self.tipMask))


class DITIs(Instruction):
    def __init__(self, name, tipMask=None, options=0, arm=Pipette.LiHa1):
        """

        :param name: str, instruction
        :param tipMask:
        :param options: int, 0-1. bit-coded 1 = if diti not fetched try 3 times then go to next position
        :param arm:
        """
        Instruction.__init__(self, name)
        self.arm     = self.robot.curArm(arm)
        self.options = options
        self.tipMask = tipMask if tipMask is not None else robot.tipsMask[self.robot.curArm().nTips]


    def validateArg(self):
        Instruction.validateArg(self)

        self.arm = self.robot.curArm(self.arm)

        assert self.arm.tips_type == self.arm.DiTi

        self.arg  = [integer(self.tipMask)]  # arg 1
        self.arg += [integer(self.options)]  # arg 3 (the arg 2 is type -an index- or labware name)
        self.arg += [integer(self.arm.index)]      # arg 4
        return True

    def exec(self, mode=None):
        if self.tipMask: Instruction.exec(self, mode)
