# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
__author__ = 'Ariel'


__author__ = 'qPCR4vir'

# http://sydney.edu.au/medicine/bosch/facilities/molecular-biology/automation/Manual%20Freedom%20EVOware%202.3%20Research%20Use%20Only.pdf

import logging

from EvoScriPy.Instruction_Base import *
import EvoScriPy.robot
#todo organize the arg in each instruction according to the more common use
#todo implement all the instruction, from all the devices, and from script only (not documented-inverse engineering) !!

class aspirate(Pipetting):
    """ A.15.4.1 Aspirate command (Worklist: Aspirate)  A - 125
    """
    def __init__(self,  tipMask     = None,
                        liquidClass = None,
                        volume      = None,
                        labware     = None,
                        spacing     = 1,
                        wellSelection= None,
                        LoopOptions = def_LoopOp,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        """


        :param liquidClass:
        :param volume:
        :param tipMask: int; selected tips, bit-coded (tip1 = 1, tip8 = 128)
        :param labware: Labware;
        :param spacing: int; tip spacing
        :param wellSelection: str;
        :param LoopOptions: list; of objects of class LoopOption.
        :param RackName:
        :param Well:
        :param arm:
        """
        Pipetting.__init__(self, 'Aspirate',
                            tipMask     = tipMask,
                            liquidClass = liquidClass,
                            volume      = volume,
                            labware     = labware,
                            spacing     = spacing,
                            wellSelection= wellSelection,
                            LoopOptions = LoopOptions,
                            RackName    = RackName,
                            Well        = Well,
                            arm         = arm )

    @staticmethod
    def action():
        return EvoScriPy.robot.Arm.Aspirate

    def validate_arg(self):
        if isinstance(self.liquidClass, tuple):
            assert len(self.liquidClass) == 2
            self.liquidClass = self.liquidClass[0]
        return Pipetting.validate_arg(self)


class dispense(Pipetting):
    """ A.15.4.2 Dispense (Worklist: Dispense)
    """
    def __init__(self,  tipMask     = None,
                        liquidClass = None,
                        volume      = def_vol,
                        labware     = None,
                        spacing     = 1,
                        wellSelection= None,
                        LoopOptions = def_LoopOp,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        Pipetting.__init__(self, 'Dispense',
                            tipMask,
                            liquidClass,
                            volume,
                            labware,
                            spacing,
                            wellSelection,
                            LoopOptions,
                            RackName,
                            Well,
                            arm )

    @staticmethod
    def action():
        return EvoScriPy.robot.Arm.Dispense

    def validate_arg(self):
        if isinstance(self.liquidClass, tuple):
            assert len(self.liquidClass) == 2
            self.liquidClass = self.liquidClass[1]
        return Pipetting.validate_arg(self)


class mix(Pipetting):
    """ A.15.4.3 Mix (Worklist: Mix)
    """

    @staticmethod
    def action():
        return True


    def __init__(self,  tipMask     = None,
                        liquidClass = None,
                        volume      = def_vol,
                        labware     = None,
                        spacing     = 1,
                        wellSelection= None,
                        cycles      = 3,
                        LoopOptions = def_LoopOp,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        Pipetting.__init__(self, 'Mix',
                            tipMask,
                            liquidClass,
                            volume,
                            labware,
                            spacing,
                            wellSelection,
                            LoopOptions,
                            RackName,
                            Well,
                            arm )
        self.cycles = cycles

    def validate_arg(self):
        Pipetting.validate_arg(self)
        self.arg[18:18] = [self.cycles]                 # arg 19
        return True

    def actualize_robot_state(self):
        self.pipette_on_i_robot(aspirate.action())
        self.pipette_on_i_robot(dispense.action())
        pass


class wash_tips(Pipette):                     # TODO revise def values of arg, how to model with iRobot?
    """ A.15.4.4 Wash Tips (Worklist: Wash) pag. A - 128; pag. 15 - 8.
    to flush and wash fixed tips or to flush DITI
adapters using a wash station. It is not intended for flushing DITI tips (DITI tips
should not normally be flushed). Tips should be washed as often as necessary, e.g. after a pipetting sequence and
before taking a new sample. DITI adapters should be flushed after replacing the
DITIs several times to renew the system liquid column in the DITI adapters. This
ensures maximum pipetting accuracy.
    """
    def __init__(self,  tipMask     = None,
                        WashWaste   = None,
                        WashCleaner = None,
                        wasteVol    = 100,
                        wasteDelay  = 50,
                        cleanerVol  = 10,
                        cleanerDelay= 50,
                        Airgap      = 0.0,
                        airgapSpeed = 50,
                        retractSpeed= 100,
                        FastWash    = False,
                        lowVolume   = False,
                        atFrequency = 0,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        """

        :param tipMask:
        :param WashWaste: labware ; the waste you want to use. You must first put a wash station
            with waste unit in the Worktable Editor at the required position.
        :param WashCleaner: labware ; the cleaner you want to use. You must first put a wash
            station with cleaner unit in the Worktable Editor at the required position.
            Choose a shallow cleaner if you only need to clean the ends of the tips.
            Choose a deep cleaner if there is a possibility of contamination along the shaft
            of the tip. The deep cleaner requires a larger volume of system liquid and
            cleaning takes somewhat longer.
            The wash cycle is skipped if you are flushing DITI adapters and Use Cleaner
            is ignored in this case.
        :param wasteVol: int ; volume [in mL !!] of system liquid which should be used to flush the inside of
            the tips. Flushing takes place with the tips positioned above the waste of the
            specified wash station (tip height for fixed tips = Z-dispense; tip height for DITI
            adapters = Z-travel).
        :param wasteDelay:
        :param cleanerVol: int ; Specify the volume of system liquid which should be used to wash the outside
            of the tips. Washing takes place with the tips lowered into the cleaner of the
            specified wash station (tip height = Z-max). The wash cycle is skipped if you
            are flushing DITI adapters and Volume in Cleaner is ignored in this case.
        :param cleanerDelay:
        :param Airgap:
        :param airgapSpeed:
        :param retractSpeed:
        :param FastWash:
        :param lowVolume:
        :param atFrequency:
        :param RackName:
        :param Well:
        :param arm:
        """
        Pipette.__init__(self, 'Wash',
                            tipMask,
                            labware     = WashWaste,
                            RackName    = RackName,
                            Well        = Well,
                            arm         = arm )
        if WashWaste is None:
            self.labware    = self.robot.worktable.def_WashWaste
        self.atFrequency    = atFrequency
        self.lowVolume      = lowVolume
        self.FastWash       = FastWash
        self.retractSpeed   = retractSpeed
        self.airgapSpeed    = airgapSpeed
        self.Airgap         = Airgap
        self.cleanerDelay   = cleanerDelay
        self.cleanerVol     = cleanerVol
        self.wasteDelay     = wasteDelay
        self.wasteVol       = wasteVol
        self.WashCleaner    = WashCleaner or self.robot.worktable.def_WashCleaner
        #self.WashWaste = WashWaste

    def validate_arg(self):
        self.wellSelection = 1
        Pipette.validate_arg(self)
        self.arg[3:-1] = [Integer(self.WashCleaner.location.grid),   # arg 4
                          Integer(self.WashCleaner.location.site),   # arg 5
                          Expression(self.wasteVol),                 # arg 6
                          Integer(self.wasteDelay),
                          Expression(self.cleanerVol),
                          Integer(self.cleanerDelay),
                          FloatingPoint(self.Airgap),
                          Integer(self.airgapSpeed),
                          Integer(self.retractSpeed),
                          Integer(self.FastWash),
                          Integer(self.lowVolume),
                          Integer(self.atFrequency)]
        return True


class getDITI(DITIs):
    def __init__(self,  tipMask, type, options=0, arm= None):
        """ A.15.4.5 Get DITIs (Worklist: GetDITI) ...
            The Get DITIs command is used to pick up DITIs (disposable tips) of the specified
            type from a DITI rack. Freedom EVOware keeps track of their position on the
            worktable and automatically picks up the next available unused DITIs of the
            chosen type.
            When you choose a DITI type in a script command, the pull-down list all of the
            LiHa DITI types which are currently configured in the labware database. When
            you want to pick up a DiTi, Freedom EVOware searches the worktable for a DITI
            rack which contains the DITI type you have specified in the script command.
            To configure Freedom EVOware for a new DITI type, create a new DITI rack or
            duplicate an existing DITI rack and give the new labware a suitable name (e.g.
            “ZipTip”).
            DiTi Index:
            Freedom EVOware automatically assigns a unique numeric index to each
            DITI type. You cannot edit the index manually. The DITI index is used e.g. by
            the Set DITI Type command in worklists and in advanced worklists. The DITI
            index is shown in the Edit Labware dialog box for the DITI labware (Well
            Dimensions tab).
            This function is deprecated in favor of getDITI2 which do not use index
            Currently only use ... ?
        :param label:
        :param tipMask:
        :param type: int, 0-3. DITI index (see 9.4.5 “Labware Types and DITI Types”,  9-32, DITI Index).
        """
        DITIs.__init__(self, "GetDITI", tipMask, options, arm)
        self.type=type # todo Deprecated?? Find the correct rack in the worktable and the current position to pick.

    def validate_arg(self):
        DITIs.validate_arg(self)
        self.arg[1:1] = [Integer(self.type)]     # arg 2 is type -an index-
        return True


class getDITI2(DITIs):
    """ A.15.4.5 Get DITIs (Worklist: GetDITI) pag. A - 129
    It take a labware type or name instead of the labware itself because the real robot take track of the
    next position to pick including the rack and the site (that is - the labware).
    It need a labware type and it know where to pick the next tip.
    """
    def __init__(self,
                 tipMask         = None,
                 DITI_series  :(str, labware_.DITIrackType, labware_.DITIrack, labware_.DITIrackTypeSeries)     = None,
                 options         = 0,
                 arm             = None,
                 AirgapVolume    = 0,
                 AirgapSpeed     = def_AirgapSpeed):
        """

        :param tipMask:
        :param DITI_series: string or labware or labware_.Type? DiTi labware name
        :param options:
        :param arm:
        :param AirgapVolume: int. used to specify a system trailing airgap (STAG) which will be aspirated after
                                  mounting the DITIs. Volume in μl
        :param AirgapSpeed: int. Speed for the airgap in μl/s
        """
        if AirgapSpeed is None:
            AirgapSpeed = def_AirgapSpeed

        DITIs.__init__(self, "GetDITI2", tipMask, options, arm)
        self.DITI_series  = DITI_series                             # to find the rack and the current position to pick.
        self.AirgapSpeed  = AirgapSpeed
        self.AirgapVolume = AirgapVolume

    def validate_arg(self):
        DITIs.validate_arg(self)
        if self.AirgapSpeed is None:
            self.AirgapSpeed = def_AirgapSpeed
        self.DITI_series = self.robot.worktable.get_DITI_series(self.DITI_series)

        self.arg[1:1] = [String1(self.DITI_series.type.name)]                 # arg 2 TODO String1 or Expression?
        self.arg += [Integer(self.AirgapVolume),
                     Integer(self.AirgapSpeed)]                               # arg 5, 6 (3, 4 are grid, site)

        return True

    def actualize_robot_state(self):
        self.validate_arg()
        maxVol = None
        self.tipMask, tips = self.robot.get_tips_executed(self.DITI_series, self.tipMask)   # todo what with ,lastPos=False
        assert not tips

    def exec(self, mode=None):
        self.tipMask = self.robot.getTips_test(self.DITI_series, self.tipMask)  # todo use arm ?
        Pipette.exec(self, mode=mode)


class dropDITI(Pipette):
    """ A.15.4.6 Drop DITIs command (Worklist: DropDITI). pag A - 130 and 15 - 14
     """

    def __init__(self,  tipMask     = None,
                        labware     = None,
                        AirgapVolume= 0,
                        AirgapSpeed = def_AirgapSpeed ,
                        arm         = None): #, conditional=True):
        """
        :param conditional: exec only if there are some tip to droop.
        :param tipMask:
        :param labware: Specify the worktable position for the DITI waste you want to use.
                        You must first put a DITI waste in the Worktable at the required position.
        :param AirgapVolume: floating point, 0 - 100.  airgap in μl which is aspirated after dropping the DITIs
        :param AirgapSpeed: int 1-1000. Speed for the airgap in μl/s
        :param arm:
        """
        Pipette.__init__(self, "DropDITI",  tipMask, labware = labware, arm=arm)
        if self.labware is None:
            self.labware = self.robot.worktable.def_DiTiWaste
#        self.conditional = conditional
        if AirgapSpeed is None:
            AirgapSpeed = def_AirgapSpeed
        self.AirgapSpeed = AirgapSpeed

        self.AirgapVolume = AirgapVolume

    def validate_arg(self):
        self.wellSelection = 1
        Pipette.validate_arg(self)
        if self.AirgapSpeed is None:
            self.AirgapSpeed = def_AirgapSpeed
        self.arg[3:-1] = [FloatingPoint(self.AirgapVolume), self.AirgapSpeed]
        return True

    def exec(self, mode=None):
        self.tipMask = self.robot.drop_tips_test(self.tipMask)  # todo use arm ?
        Pipette.exec(self, mode=mode)

    def actualize_robot_state(self):
        self.tipMask = self.robot.drop_tips_executed(self.tipMask, self.labware)


class set_DITI_Counter(Pipette):            # todo help determining the type,set other labware_.def_LabW,   deprecated???
    """A.15.4.7 Set Diti Position (Worklist: Set_DITI_Counter) pag. 15 - 15
        If you are using DITIs, Freedom EVOware remembers the position in the DITI
    rack of the last DITI which was fetched. When starting a new run, the Get DITIs
    command starts picking up DITIs at the next available position. After loading a
    new DITI rack onto the worktable during script runtime (e.g. using the RoMa), you
    should use the Set DITI Position command in your script to set the DITI Position
    counter to 1. This ensures that the next DITI is fetched from position 1 rather than
    from the middle of the new rack.
    You can specify the next position separately for each of the available DITI types
    (i.e. DITI racks on the worktable).
    Note: If you want to specify the next DITI position manually before the script or
    process is started, use the direct command Set DITI Position (see 5.4.1.3 “Direct
    commands”,  5-10) or create a maintenance script which contains the Set DITI
    Position command (see 6.4.2 “Run Maintenance”,  6-10).
    Note: DiTi handling is automatic in Freedom EVOware Plus.
    This command is only shown in the Control Bar if you are using DiTis on the LiHa.
    Freedom EVOware does not detect the LiHa tip type automatically. If you are
    using DITIs you must configure them manually (see 8.4.2.1 “LiHa (Liquid Handling
    Arm)”,  8-22).
    If your pipetting instrument is fitted with two liquid handling arms, the Set DITI
    Position command will be provided in the Control Bar for both arms. However,
    please note that the same DITI position counter (and the same pool of unused
    DITIs) is used by both arms.
    """

    def __init__(self, type      = None,
                       posInRack = 0,
                       labware   = None ):

        Pipette.__init__(self, "Set_DITI_Counter" , labware = labware, tipMask=True)

        self.type      = type
        self.labware   = labware or self.robot.worktable.def_DiTi_type
        self.posInRack = posInRack

    def validate_arg(self):
        assert isinstance(self.labware, labware_.DITIrack)
        self.arg = [Integer(self.type),
                    String1(self.labware.location.grid),
                    String1(self.labware.location.site),
                    String1(self.posInRack)] # OK extract from Location
        return True

    def actualize_robot_state(self):
        # Robot.Robot.current.worktable.labware_series[self.type]
        self.labware.type.pick_next_rack = self.labware
        self.labware.type.pick_next      = self.labware.offset(self.posInRack)


class set_DITI_Counter2(Pipette):
    """A.15.4.7 Set Diti Position (Worklist: Set_DITI_Counter)     NOT DOCUMENTED
        example: Set_DITI_Counter2("DiTi 1000ul","25","2","5",0);
        last position
    If you have activated the feature Optimize positions when fetching DITIs,
    Freedom EVOware fetches new DITIs either starting from the beginning of the
    DITI rack or starting from the end of the DITI rack, depending on the situation
    (see 8.4.2.1 “LiHa (Liquid Handling Arm)”,  8-22, Optimize positions when
    fetching DITIs). In this case, Freedom EVOware maintains two counters for
    the last used DITI position (for DITIs which are taken from the beginning of the
    rack and for DITIs which are taken from the end of the rack). Check this
    checkbox if you want to set the last used DITI position for the end counter
    instead of for the beginning counter.
    If you have activated the feature Optimize positions when fetching DITIs, after
    loading a new DITI rack onto the worktable during script runtime you should
    use the Set DITI Position command twice in your script, to set the beginning
    counter to 1 and the end counter to 96.
    The Set last position checkbox is inactive (grey) if you have not activated
    Optimize positions when fetching DITIs. If you have previously specified the
    last used DITI position, it will be ignored during script execution
    """

    def __init__(self, labware   = None,
                       posInRack = 0,
                       lastPos   = False  ):

        Pipette.__init__(self, "Set_DITI_Counter2" , labware = labware, tipMask=True)

        self.lastPos   = lastPos                                     # todo implement internally; how??
        self.labware   = labware or self.robot.worktable.def_DiTi_type
        self.posInRack = posInRack

    def validate_arg(self):
        if not isinstance(self.labware, labware_.DITIrack):
            self.labware  = self.robot.worktable.get_DITI_series(self.labware).current
        assert isinstance(self.labware, labware_.DITIrack)

        self.arg = [String1(self.labware.type.name),
                    String1(self.labware.location.grid),
                    String1(self.labware.location.site + 1),
                    String1(self.labware.offset(self.posInRack) + 1),
                    Integer(self.lastPos)]
        return True

    def actualize_robot_state(self):
        self.validate_arg()
        self.robot.worktable.set_current(self.labware)                     # todo really    ??????????
        self.labware.set_DITI_counter(self.posInRack, self.lastPos)


class pickUp_DITIs(Pipette):
    """ A.15.4.8 Pick Up DITIs (Worklist: Pick Up_DITI) pag. A-131 and 15-16
    The Pick Up DITIs command is used to pick up DITIs which have already been
    used and put back into a DITI rack with the Set DITIs Back command. You must
    specify the DITIs you want to pick up.
    """
    def __init__(self,       tipMask     = None,
                             labware     = None,
                             wellSelection= None,
                             LoopOptions = def_LoopOp,
                             type        = None,
                             arm         = None,
                             RackName    = None,
                             Well        = None):

        Pipette.__init__(self, 'PickUp_DITIs',
                             tipMask     = tipMask,
                             labware     = labware,
                             wellSelection= wellSelection,
                             LoopOptions = LoopOptions,
                             RackName    = RackName,
                             Well        = Well,
                             arm         = arm)
        self.labware = labware  or self.robot.worktable.def_DiTi_type
        self.type = type

    def validate_arg(self):
        Pipette.validate_arg(self)
        assert isinstance(self.labware, labware_.DITIrack)

        self.arg[3:4]   = []
        self.arg[-1:-1] = [Integer(self.type)]
        return True

    def actualize_robot_state(self):
        assert isinstance(self.labware, labware_.DITIrack)
        self.tipMask, tips = self.robot.pick_up_tips_executed(self.tipMask, self.labware)
        assert not tips


class pickUp_DITIs2(Pipette):
    """ A.15.4.8 Pick Up DITIs (Worklist: Pick Up_DITI) pag. A-131 and 15-16
                 NOT DOCUMENTED
    The Pick Up DITIs command is used to pick up DITIs which have already been
    used and put back into a DITI rack with the Set DITIs Back command. You must
    specify the DITIs you want to pick up.
    """
    def __init__(self,       tipMask     = None,
                             labware     = None,
                             wellSelection= None,
                             LoopOptions = def_LoopOp,
                             arm         = None,   # last parameter
                             RackName    = None,
                             Well        = None):
        Pipette.__init__(self, 'PickUp_DITIs2',
                             tipMask     = tipMask,
                             labware     = labware,
                             wellSelection= wellSelection,
                             LoopOptions = LoopOptions,
                             RackName    = RackName,
                             Well        = Well,
                             arm         = arm)
        self.type    = type
        self.labware = labware or self.robot.worktable.def_DiTi_type

    def validate_arg(self):
        Pipette.validate_arg(self)
        assert isinstance(self.labware, labware_.DITIrack)

        self.arg[3:4]   = []        # delete arg tip spacing
        self.arg[-1:-1] = [String1(self.labware.type.name)]
        return True

    def actualize_robot_state(self):
        assert isinstance(self.labware, labware_.DITIrack)
        self.tipMask, tips = self.robot.pick_up_tips_executed(self.tipMask, self.labware)
        assert not tips


class set_DITIs_Back(Pipette):
    """ A.15.4.9 Set DITIs Back (Worklist: Set_DITIs_Back)
    return used DITIs to specified positions on a DITI rack for later use.
    This command requires the Lower DITI Eject option.
    """
    def __init__(self,
                 tipMask,
                 labware: labware_.DITIrack,
                 wellSelection      = None,
                 LoopOptions        = def_LoopOp,
                 arm                = None,
                 RackName           = None,
                 Well               = None):

        assert isinstance(labware, labware_.DITIrack)

        Pipette.__init__(self, 'Set_DITIs_Back',
                         tipMask     = tipMask,
                         labware     = labware,
                         wellSelection= wellSelection,
                         LoopOptions = LoopOptions,
                         RackName    = RackName,
                         Well        = Well,
                         arm         = arm)


    def validate_arg(self):
        Pipette.validate_arg(self)
        assert isinstance(self.labware, labware_.DITIrack)

        self.arg[3:4] = []
        return True

    def actualize_robot_state(self):
        self.tipMask = self.robot.set_tips_back_executed(self.tipMask, self.labware)


class pickUp_ZipTip(Pipette): # todo implement !!!
    """ A.15.4.10 Pickup ZipTip (Worklist: PickUp_ZipTip)
    """
    def __init__(self, tipMask = None ):
        Pipette.__init__(self, 'PickUp_ZipTip' )
        assert False, "PickUp_ZipTip not implemented"


class detect_Liquid(Pipetting):    # todo get the results !!!
    """ A.15.4.11 Detect Liquid (Worklist: Detect_Liquid)
    Liquid level detection is one of the options available for aspirating and dispensing
    and can be individually defined for each liquid class. The Detect Liquid command is
    used to carry out liquid level detection without pipetting and reports the liquid volume
    for each of the chosen wells in the labware. The volumes are returned in a set of variables
    DETECTED_VOLUME_x, where x is the tip number.
    """

    @staticmethod
    def action():
        return EvoScriPy.robot.Arm.Detect

    def __init__(self ,      tipMask     = None,                         # arg 1
                             liquidClass = None,                         # arg 2
                             labware     = None,                         # arg 3, 4
                             spacing     = 1,                            # arg 5
                             wellSelection= None,                        # arg 6
                             LoopOptions = None,                         # arg 7, 8, 9, 10
                             arm         = None,                         # arg 11
                             RackName    = None,
                             Well        = None):

        Pipetting.__init__(self, 'Detect_Liquid',
                            tipMask        = tipMask,
                            liquidClass    = liquidClass,
                            labware        = labware,
                            volume         = 0,
                            spacing        = spacing,
                            wellSelection  = wellSelection,
                            LoopOptions    = LoopOptions,
                            RackName       = RackName,
                            Well           = Well,
                            arm            = arm )


class activate_PMP(Instruction):
    """ A.15.4.12 Activate PMP (Worklist: Activate_PMP)
    """
    def __init__(self, tipMask = None ):
        Instruction.__init__(self, "Activate_PMP")
        self.tipMask = tipMask if tipMask is not None else Rbt.tipsMask[self.robot.cur_arm().n_tips]

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg = [Integer(self.tipMask)]
        return True

    def exec(self, mode=None):
        if self.tipMask :
            Instruction.exec(self, mode)


class deactivate_PMP(Instruction):
    """ A.15.4.13 Deactivate PMP (Worklist: Deactivate_PMP)
    """
    def __init__(self, tipMask = None ):
        Instruction.__init__(self, "Deactivate_PMP")
        self.tipMask = tipMask if tipMask is not None else Rbt.tipsMask[self.robot.cur_arm().n_tips]

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg = [Integer(self.tipMask)]
        return True

    def exec(self, mode=None):
        if self.tipMask: Instruction.exec(self, mode)


class moveLiha(Pipette ):
    """ A.15.4.14 Move LiHa (Worklist: MoveLiha   - A - 135)see 15.21 “Move LiHa Command”, 15-33.
    The Move LiHa command is used to move the liquid handling arm (LiHa) from one
    position to another without performing an Aspirate or Dispense operation.
    Type of movement
    Choose X-Move, Y-Move or Z-Move to move only one axis of the LiHa. You
    can then specify the speed of the movement. Z-Move only moves the selected
    tips.
    The options Positioning with global Z-travel, Positioning with local Z-travel and
    Positioning with variable Z-travel move the LiHa to the labware at maximum
    speed. The chosen height for Z-Travel (the tip height which is used during the
    arm movement) only applies to the selected tips. The Z position of the
    unselected tips remains unchanged.
    If you choose Positioning with variable Z-travel, the required Z-Travel height is
    specified using the pre-defined variable LIHA_MOVE_HEIGHT (see
    14.1.4.7 “LIHA_MOVE_HEIGHT”,  14-5).
    Z-Position
    Unless you have chosen X-Move or Y-Move in the Type of Movement field,
    you can specify the Z-Position to which the selected tips should be lowered at
    the end of the LiHa movement. The Z position of the unselected tips remains
    unchanged. Choose the required Z-position and then specify a Z offset in mm
    if required. A positive value for the offset lowers the tips.
    """
        # type of movement:
    pos_global_z_travel = 0  # = positioning with global z-travel
    pos_local_z_travel  = 1  # = positioning with local z-travel
    x_move              = 2  # = x-move
    y_move              = 3  # = y-move
    z_move              = 4  # = z-move

        # z-position after move:
    z_travel        = 0  # = z-travel
    z_dispense      = 1  # = z-dispense
    z_start         = 2  # = z-start
    z_max           = 3  # = z-max
    global_z_travel = 4  # = global z-travel

    def __init__(self,  zMove, zTarget, offset, speed,   # arg 6,7,8,9
                        tipMask     = None,
                        labware     = None,
                        spacing     = 1,
                        wellSelection= None,
                        LoopOptions = def_LoopOp,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        """

        :param zMove: int; type of movement:
                            0 = positioning with global z-travel
                            1 = positioning with local z-travel
                            2 = x-move
                            3 = y-move
                            4 = z-move
        :param zTarget: int; z-position after move:
                            0 = z-travel
                            1 = z-dispense
                            2 = z-start
                            3 = z-max
                            4 = global z-travel
        :param offset: float;  in range (-1000, 1000) offset in mm added to z-position (parameter zTarget)
        :param speed:  float;  in range (0.1, 400)  move speed in mm/s if zMove is x-move, y-move or z-move
        :param tipMask: int; selected tips, bit-coded (tip1 = 1, tip8 = 128)
        :param labware: Labware;
        :param spacing: int; tip spacing
        :param wellSelection: str; bit-coded well selection
        :param LoopOptions: list; of objects of class LoopOption.
        :param RackName:
        :param Well:
        :param arm:
        """
        Pipette.__init__(self,  'MoveLiha' ,
                             tipMask    ,
                             labware     ,
                             spacing    ,
                             wellSelection,
                             LoopOptions,
                             RackName    ,
                             Well      ,
                             arm       )

        self.speed      = speed
        self.offset     = offset
        self.zTarget    = zTarget
        self.zMove      = zMove

    def validate_arg(self):
        Pipette.validate_arg(self)
        self.arg[5:5] = [Integer        (self.zMove),
                         Integer        (self.zTarget),       # arg 6, 7
                         FloatingPoint (self.offset),
                         FloatingPoint (self.speed)]  # arg 8, 9
        return True


class waste(Instruction):
    """ A.15.4.15 Waste (Worklist: Waste)
    """
    # actions
    init_system           = 0
    activate_waste_1      = 1
    activate_waste_2      = 2
    activate_waste_3      = 3
    deactivate_all_wastes = 4
    deactivate_system     = 5
    actions         = range(6)

    def __init__(self, action = init_system ):
        Instruction.__init__(self, "Waste")
        self.action = action

    def validate_arg(self):
        Instruction.validate_arg(self)
        assert self.action in waste.actions
        self.arg= [Integer(self.action)]
        return True


class active_Wash(Instruction):
    """ A.15.4.16 Active WashStation (Worklist: Active_Wash)
    """

    def __init__(self, wait = True, time=None, arm=None   ):
        Instruction.__init__(self, "Active_Wash")
        self.arm = arm if arm is not None else self.robot.cur_arm().index
        self.time = time
        self.wait = wait

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [Integer(self.wait),Integer(self.time),Integer(self.arm)]
        return True


class export(Instruction):
    """ A.15.4.17 Export Data (Worklist: Export)
    """
    lotus  = 1
    dbase  = 2
    excel  = 4
    paradox = 8
    quattro = 16
    text_with_delimiters = 32

    def __init__(self, exportAll = True,
                       formats =  text_with_delimiters,
                       delete = False,
                       compress = False,
                       Raks=None,     # ?????
                       significantStep = 1):
        Instruction.__init__(self, "Export")
        self.exportAll = exportAll
        self.formats = formats
        self.delete = delete
        self.compress = compress
        self.Raks = Raks if Raks is not None else []
        self.significantStep = significantStep


    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [Integer(self.exportAll), Integer(self.formats),
                   Integer(self.delete),    Integer(self.compress)]
        self.arg +=  [Integer(len(self.Raks))]                                         # arg 5
        for rk in self.Raks:
            self.arg += [Integer(rk.location.grid), Integer(rk.location.site)]        # arg 6,7
        self.arg += [Integer( self.significantStep)]                                  # arg 8

        return True


class startTimer(Instruction):
    """ A.15.4.18 Start Timer (Worklist: StartTimer)
    """
    def __init__(self, timer = 1 ):
        """


        :type timer: Expression
        :param timer: expression, 1 - 100. number of timer to re-start. 1-1000?
        """
        Instruction.__init__(self, "StartTimer")
        self.timer = timer

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [Expression(self.timer)]


class waitTimer(Instruction):
    """ A.15.4.19 Wait for Timer (Worklist: WaitTimer)
    """
    def __init__(self, timer =1, timeSpan= None ):
        """

        :param timeSpan: expression, 0.02 - 86400. duration
        :type timer: Expression
        :param timer: expression, 1 - 100. number of timer to re-start. 1-1000?
        """
        Instruction.__init__(self, "WaitTimer")
        self.timeSpan = timeSpan
        self.timer = timer

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [Expression(self.timer),Expression(self.timeSpan)]


class execute(Instruction): # todo declare const
    """ A.15.4.20 Execute Application (Worklist: Execute)
    """
    def __init__(self, application, options, responseVariable, scope =0  ):
        """
        """
        Instruction.__init__(self, "Execute")
        self.scope = scope
        self.responseVariable = responseVariable
        self.options = options
        self.application = application


    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.application),      Integer(self.options),
                   String1(self.responseVariable), Integer(self.scope)]


class comment(Instruction):
    """ A.15.4.21 Comment (Worklist: Comment)
    """
    def __init__(self, text ):
        """
        """
        Instruction.__init__(self, "Comment")
        self.text = text

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.text)]
        return True


class userPrompt(Instruction):    # todo declare const
    """
    A.15.4.22 User Prompt (Worklist: UserPrompt)
    """
    def __init__(self, text:str, sound:int = 1, closeTime:int = -1 ):
        """
        """
        Instruction.__init__(self, "UserPrompt")
        self.closeTime = closeTime
        self.sound = sound
        self.text = text

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.text), Integer(self.sound), Integer(self.closeTime)]
        return True


class variable(Instruction):    # OK declare const
    """ A.15.4.23 Set Variable (Worklist: Variable)
    """
    Numeric     = 0
    String      = 1

    Run         = 0
    Instance    = 1
    Script      = 2

    Fixed_value = 0
    User_query  = 1
    File_import = 2

    def __init__(self, var_name,
                       default,
                       queryFlag    = False,
                       queryString  = "",
                       checkLimits  = False,
                       lowerLimit   = 0.0,
                       upperLimit   = 0.0,
                       type         = 0,
                       scope        = 0,
                       InitMode     = 0,
                       QueryAtStart = False):
        """

        :param var_name: string2 ; name of variable
        :param default: Expression ; value assigned to variable or default value if user query
        :param queryFlag: bool
        :param queryString: String1 ; text shown in user query
        :param checkLimits: bool
        :param lowerLimit:
        :param upperLimit:
        :param type: type of variable; 0 = Numeric; 1 = String
        :param scope: scope of variable (see 6.4.6,  6-12):0 = Run; 1 = Instance; 2 = Script
        :param InitMode: 0 = Fixed value; 1 = User query; 2 = File import;
        :param QueryAtStart: bool ; 1 = Prompt for value at start of script
        """
        Instruction.__init__(self, "Variable")
        self.QueryAtStart = QueryAtStart
        self.InitMode = InitMode
        self.scope = scope
        self.type = type
        self.upperLimit = upperLimit
        self.lowerLimit = lowerLimit
        self.checkLimits = checkLimits
        self.queryString = queryString
        self.var_name = var_name
        self.default = default
        self.queryFlag = queryFlag

    def validate_arg(self):
        Instruction.validate_arg     (self)
        self.arg =  [String2        (self.var_name),
                     Expression     (self.default),
                     Integer        (self.queryFlag)]
        self.arg += [String1        (self.queryString),
                     Integer        (self.checkLimits),
                     FloatingPoint (self.lowerLimit)]
        self.arg += [FloatingPoint (self.upperLimit),
                     Integer        (self.type),
                     Integer        (self.scope)]
        self.arg += [Integer        (self.InitMode),
                     Integer        (self.QueryAtStart)]
        return True


class execute_VBscript(Instruction):
    """ A.15.4.24 Execute VB Script (Worklist: Execute_VBscript)
    """
    def __init__(self, filename, action  = 0 ):
        """

        :param filename: Path and filename of the defined VB script.
        :param action: Use Waits, Continues and Waits_previous defined in subroutine
        """
        Instruction.__init__(self, "Execute_VBscript")
        self.action = action
        self.filename = filename

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.filename), Integer(self.action)]
        return True


class notification(Instruction):    # todo declare const
    """ A.15.4.25 Notification (Worklist: Notification)
    """
    def __init__(self,   receiverGroup,
                         AttachScreen_ShotFlag  = False,
                         emailSubject           = "",
                         emailMessage           = "",
                         action                 = 0   ):
        """

        :param receiverGroup:
        :param AttachScreen_ShotFlag:
        :param emailSubject:
        :param action: 0 = send email now, 1 = send email on error, 2 = stop sending email on error
        """
        Instruction.__init__(self, "Notification")
        self.emailMessage           = emailMessage
        self.emailSubject           = emailSubject
        self.AttachScreen_ShotFlag  = AttachScreen_ShotFlag
        self.action                 = action
        self.receiverGroup          = receiverGroup

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [ Integer(self.AttachScreen_ShotFlag),
                    String1(self.receiverGroup),
                    String1(self.emailSubject),
                    String1(self.emailMessage),
                    Integer(self.action)]
        return True


'''
class Te_MO_Aspirate(Instruction):
    """
    A.15.4.26  Aspirate-Multipip. (only Freedom EVOware Standard)
    Te-MO (Tecan Multi-Pipetting Option). Can pipette to 96 or 384 wells simultaneously.
    the same volume is pipetted by all of the tips.
    """
    def __init__(self,  tipMask     = None,
                        liquidClass = def_liquidClass,
                        volume      = def_vol,
                        labware     = None,
                        spacing     = 1,
                        wellSelection= None,
                        LoopOptions = def_LoopOp,
                        RackName    = None,
                        Well        = None,
                        arm         = None):
        """

        :param tipMask: Number of tips on the Te-MO pipetting head. Only two values: 255 = 96 tip; 65535 = 384 tip head
        :param liquidClass:
        :param volume:
        :param labware:
        :param spacing:
        :param wellSelection:
        :param LoopOptions:
        :param RackName:
        :param Well:
        :param arm:
        """
        Instruction.__init__(self, 'Aspirate')
        self.robot.cur_arm(arm)
        self.tipMask        = tipMask if tipMask is not None else robot.tipsMask[self.robot.cur_arm().n_tips]
        self.labware        =labware
        self.spacing        = spacing
        self.loopOptions    = LoopOptions
        self.RackName       = RackName
        self.Well           = Well
        self.arm = self.robot.cur_arm().index   # current arm can change - keep it here
                            tipMask,
                            liquidClass,
                            volume,
                            labware or labware_.def_LabW,
                            spacing,
                            wellSelection,
                            LoopOptions,
                            RackName,
                            Well,
                            arm )

'''


class RoMa(Instruction):
    """
    15.60 Move RoMa Command
    This command is used to carry out simple RoMa movements without using a
    RoMa vector:
    The parameters of the Move RoMa command are as follows:
         - ROMA-No.
    Choose the RoMa you want to use (1 or 2) if your instrument is fitted with
    more than one.
         - Open Gripper
    This opens the gripper to the specified width (range: 55 to 140 mm).
        Close Gripper
    This closes the gripper to the specified width (range: 55 to 140 mm) using the
    specified force (range: 0 to 249). A Grip Error message will be output if no
    resistance is detected when gripping.
         - Move to home position
    This moves the RoMa to the specified home position.
    After completing a sequence of movements with the RoMa, you should move
    it back to its home (parking) position, out of the way of other objects on the
    worktable (see 9.6.4 “Defining the Home Position for a RoMa”,  9-63).
         - Move relative to current position
    This moves the RoMa relative to its current position. You must then specify
    the relative distances (range: -400 to 400 mm) and whether the RoMa should
    move at a particular speed (range: 0.1 to 400 mm/s) or at maximum speed.
    The movements in A and B are not aligned with the instrument axes, but with
    the current rotator position (angle).
    The movement in A is perpendicular to the gripper. Example #1: If the gripper
    points to the front (angle = 0°) and the A value is positive, then the RoMA will
    move to the left. Example #2: If the gripper points to the left (angle = 90°) and
    the A value is positive, then the RoMA will move to the back.
    The movement in B is in line with the gripper. Example #1: If the gripper points
    to the front (angle = 0°) and the B value is positive, then the RoMA will move
    to the front. Example #2: If the gripper points to the left (angle = 90°) and the B
    value is positive, then the RoMA will move to the left.
    See also 9.4.8.2 “RoMa Coordinate System”,  9-39.

    """
    # action
    open_gripper    = 0
    close_gripper   = 1
    move_to         = 2
    home_position   = 3
    move_relative   = 4 # 3 = move relative to current position

    # xyzMax
    use_xyzSpeed    = 0
    use_max_speed   = 1 # use_maximum speed

    # number of the RoMa performing the action:
    RoMa_1 = 0
    RoMa_2 = 1

    def __init__(self,   action         : int,
                         distance       : float,
                         force          : int,
                         xOffset        : float,
                         yOffset        : float,
                         zOffset        : float,
                         xyzSpeed       : float,
                         xyzMax         : int,
                         romaNo         : int
                 ):
        """

        :type yOffset: object
        :param action: 0 = open gripper, 1 = close,  2 = move to home position, 3 = move relative to current position
        :param distance:    55 - 140,   gripper distance in mm for opening or closing
        :param force:       0 - 249,    force when closing gripper
        :param xOffset:     -400 - 400, x-distance for relative move in mm
        :param yOffset:     -400 - 400, y-distance for relative move in mm
        :param zOffset:     -400 - 400, z-distance for relative move in mm
        :param xyzSpeed:    0.1 - 400,  speed in mm/s
        :param xyzMax:      0 = use xyzSpeed, 1 = use maximum speed
        :param romaNo:   number of the RoMa performing the action: 0 = RoMa 1, 1 = RoMa 2
        """
        Instruction.__init__(self, "RoMa")
        self.action         = action
        self.distance       = distance
        self.force          = force
        self.xOffset        = xOffset
        self.yOffset        = yOffset
        self.zOffset        = zOffset
        self.xyzSpeed       = xyzSpeed
        self.xyzMax         = xyzMax
        self.romaNo         = romaNo

    def actualize_robot_state(self):
        pass                            # todo  and exec()?

    def validate_arg(self):
        Instruction.validate_arg(self)
        assert    0 > self.action   >   3, "RoMa action must be 0,1, 2 or 3, but passed: " + str(self.action)
        assert   55 > self.distance > 140, "RoMa distance must be 55-140, but passed: " + str(self.distance)
        assert    0 > self.force    > 249, "RoMa force must be 0-249, but passed: " + str(self.force)
        assert -400 > self.xOffset  > 400, "RoMa xOffset must be 0-249, but passed: " + str(self.xOffset)
        assert -400 > self.yOffset  > 400, "RoMa yOffset must be 0-249, but passed: " + str(self.yOffset)
        assert -400 > self.zOffset  > 400, "RoMa zOffset must be 0-249, but passed: " + str(self.zOffset)
        assert  0.1 > self.xyzSpeed > 400, "RoMa xyzSpeed must be 0-249, but passed: " + str(self.xyzSpeed)
        assert    0 > self.xyzMax   >   1, "RoMa xyzMax must be 0 or 1, but passed: " + str(self.xyzMax)
        assert    0 > self.romaNo   >   1, "RoMa romaNo must be 0 or 1, but passed: " + str(self.romaNo) # todo ?

        self.arg= [ Integer       (self.action),
                    FloatingPoint(self.distance),
                    Integer       (self.force),
                    FloatingPoint(self.xOffset),
                    FloatingPoint(self.yOffset),
                    FloatingPoint(self.zOffset),
                    FloatingPoint(self.xyzSpeed),
                    Integer       (self.xyzMax),
                    Integer       (self.romaNo)
                    ]
        return True


class vector(Instruction):

    """
    15.61 RoMa Vector Command
    This command executes a RoMa vector, which is a predefined sequence of RoMa
    movements. You can also specify gripper actions at the Safe and End positions.
    See 9.6.1 “Using RoMa Vectors”,  9-59 for more information.
    The RoMa Vector command is intended for special RoMa movements and not for
    moving labware from one position to another - you should use the Transfer
    Labware command instead for this purpose. See also 15.61.1 “Moving labware
    with the RoMa Vector command”,  15-145.
    The parameters of the RoMa Vector command are as follows:
        - RoMa-No.
    Choose the RoMa you want to use (1 or 2) if your instrument is fitted with
    more than one.
        - Use RoMa Vector
    Choose the RoMa vector you want to use for the RoMa movement. The
    popup list shows the RoMa vectors which are currently defined in the
    Freedom EVOware database.
    The digit at the end of the vector name (e.g. Carousel_Narrow_1) indicates
    the RoMa for which the vector was defined (1 or 2). See also 9.6.1 “Using
    RoMa Vectors”,  9-59.
    You can also choose a user-defined vector. User-defined vectors are created
    in the Control Bar (Robot Vectors section).
    Then specify the grid position and carrier site for which the vector is intended.
    The Grid field is protected (gray) if you have chosen a vector for a device
    which is not positioned on the worktable (see Carrier is Device checkbox in
    the carrier definition).
    Tip: If you click on a carrier, the current grid position is shown in the small
    yellow tab at the bottom left.
        - Move along RoMa Vector
    Choose the required direction of the RoMa movement. Click And back if you
    want the RoMa to return to the Safe position after reaching the End position.
        - Gripper action
    Choose the gripper action which should be executed at the Safe position and
    at the End position. The required gripper spacing to pick up and release the
    labware is taken from the Grip Width and Release Width parameters in the
    chosen RoMa vector.
        - Speed
    Choose Maximum if you want the RoMa to move at maximum speed. Choose
    Slow if you want the RoMa to move at the speed specified in the RoMa vector.

    15.61.1 Moving labware with the RoMa Vector command
    If you have scanned the labware barcode and you move the labware with the
    Transfer Labware command, the barcode remains assigned to the labware (i.e.
    the labware data record) at the new location. In addition, pipetting information, if
    any, remains assigned to the labware (see 15.29 “Export Data Command”,  15-
    50).
    This is not the case with the RoMa Vector command. The barcode and the
    pipetting information are no longer available at the new location.
    This also applies analogously to the MCA96 Vector command and the MCA384
    Vector command.
    Proceed as follows if you want to use a Vector command to move barcoded
    labware in special situations:
     After scanning the barcode, assign it to a temporary variable (see
      14.1.11 “Labware Attributes and String Variables”,  14-16).
     Move the labware.
     Re-assign the barcode from the temporary variable to the labware.
    This workaround transfers the barcode but not the pipetting information.
    """


class transfer_rack(Instruction):

    """
    This command is used to transfer labware (e.g. a microplate) from one position to
    another with the plate robot (RoMa).
    If you have scanned the labware barcode and you move the labware with the
    Transfer Labware command, the barcode remains assigned to the labware (i.e.
    the labware data record) at the new location. In addition, pipetting information, if
    any, remains assigned to the labware (see 15.29 “Export Data Command”,  15-
    50).
    Grip and release commands for the RoMa (used to pick up and put down the
    labware) are handled automatically. The required gripper spacing is taken from
    the advanced properties for the respective labware type (see 9.4.2 “Editing
    Labware, Advanced Tab”,  9-22):
    The parameters of the Transfer Labware command are as follows:
        Move with
    Choose the RoMa you want to use (1 or 2) if your instrument is fitted with
    more than one.
        Vector
    Choose the RoMa vector that you want to use to pick up the labware.
    Choose Narrow to pick up the labware on the narrow side; choose Wide to
    pick up the labware on the wide side.
    Choose User defined (Narrow) or (Wide) to pick up the labware on the narrow
    or wide side with a user-defined vector. In this case, you must choose the
    user-defined vector to use for picking up the labware at the source position
    and putting down it at the destination position in the two User Vector pull-down
    lists. User-defined vectors are created in the Control Bar (Robot Vectors
    section). See 5.4.1.4 “Robot Vectors”,  5-11.
    Above all if you did not create the user-defined vector yourself, we
    recommend you to check carefully that the vector moves the RoMa to the
    correct (i.e. intended) source and destination carrier positions before using it
    for pipetting. Tip: Test the RoMa vector in a script using the 3D simulation
    program EVOSim.
    Freedom EVOware will report an error when you complete the Transfer
    Labware command if the narrow or wide RoMa vector has not yet been
    created for the chosen labware type. It is best to create the required RoMa
    vectors in advance (see 9.6.2 “Teach Plate Robot Vector Dialog Box”,  9-60).

        Transfer Labware command, Step 1
    Specify the parameters for the source position:
        - Source position
    Select the current position of the labware by clicking on it in the Worktable
    Editor.
    Grid and Site then show the position you have chosen. The gray (protected)
    field Defined Carrier then shows the type of carrier at the chosen site and the
    gray (protected) field Defined Labware shows the type of labware at the
    chosen site.
    If you want to fetch the labware from a device such as a hotel or barcode
    scanner, click on the device icon. You then need to choose the site and the
    labware type. The list shows labware types which are allowed for the device
    (see 9.5 “Configuring Carriers”,  9-39, “Allowed Labware on this carrier”).

        Transfer Labware command, Step 2
    Specify the parameters for the labware lid. These parameters are only available
    for labware types which can be fitted with a lid:
        - Lid handling
    Check this checkbox if the labware has a lid. Choose Cover at source if you
    want to put on the lid before moving the labware. Choose Uncover at
    destination if you want to remove the lid after moving the labware to the
    destination position (i.e. the lid was already present). In either case, select the
    position for fetching or putting aside the lid by clicking on the site in the
    Worktable Editor. Grid and Site then show the position you have chosen. The
    gray (protected) field Defined Carrier shows the type of carrier on which the lid
    is placed/will be placed. You can only put aside lids on unused carrier sites.

        Transfer Labware command, Step 3
    Specify the parameters for the destination position:
        - Destination Position
    Select the required destination position of the labware by clicking on the site in
    the Worktable Editor.
    The destination site must be suitable for the labware type you are moving (see
    9.5 “Configuring Carriers”,  9-39, “Allowed labware on this carrier”).
    Grid and Site then show the position you have chosen. The gray (protected)
    field Defined Carrier then shows the type of carrier at the chosen site.
    If you want to move the labware to a device such as a hotel or barcode
    scanner, click on the device icon. You then need to choose the site and the
    labware type. The list shows labware types which are allowed for the device
    (see 9.5 “Configuring Carriers”,  9-39, “Allowed Labware on this carrier”).
        - Speed
    Choose Maximum if you want the RoMa to move at maximum speed. Choose
    Taught in vector dialog if you want the RoMa to move at the speed specified in
    the RoMa vector.
        - Move back to Home Position
    Check this checkbox if you want the RoMa to move back to its home (parking)
    position after transferring the labware. See 9.6.4 “Defining the Home Position
    for a RoMa”,  9-63.
    """

    #
    def __init__(self,
                 labware        : labware_.Labware,
                 destination    : labware_.WorkTable.Location,
                 vectorName     : str         = None,
                 backHome       : bool        = True,
                 slow           : bool        = True,
                 lid            : labware_.Labware = None,
                 cover          : int         = 0,         # todo revise !!!!
                 romaNo         : int         = None
                 ):
        """

        :param labware:
        :param destination:
        :param backHome:    move back to home when finished ?
        :param lid:
        :param slow:        use slow speed (as defined in RoMa vector)? (else use maximum speed)
        :param cover:       0 = cover at source , 1 = uncover at destination
        :param vectorName:  name of RoMa vector to use (as in the Freedom EVOware configuration),
                            choose from one of the following:
                                    Narrow
                                    DriveIN_Narrow
                                    DriveIN_Narrow
                                    DriveIN_Wide
        :param romaNo:      number of the RoMa performing the action: 0 = RoMa 1, 1 = RoMa 2
        """
        Instruction.__init__(self, "Transfer_Rack")

        self.labware         = labware
        self.destination     = destination
        self.backHome        = backHome
        self.slow            = slow
        self.cover           = cover
        self.lid             = lid
        self.vectorName      = vectorName
        self.romaNo          = romaNo

    def validate_arg(self):
        Instruction.validate_arg(self)
        assert isinstance(self.labware,                  labware_.Labware)
        assert isinstance(self.labware.type,             labware_.Labware.Type)
        assert isinstance(self.labware.location.carrier, labware_.Carrier)

        assert isinstance(self.destination,          labware_.WorkTable.Location)
        assert isinstance(self.destination.carrier,  labware_.Carrier)

        if self.lid is not None:
            assert isinstance(self.lid,      labware_.WorkTable.Location)
            assert isinstance(self.lid.carrier, labware_.Carrier)

        logging.info("Transafering from " + str(self.labware.location) + " to " + str(self.destination))
        assert self.cover in [0, 1]

        if self.vectorName is None:
            self.vectorName = "Narrow"
        assert self.vectorName in ["Narrow", "DriveIN_Narrow",
                                   "Wide",   "DriveIN_Wide" ],  f"Passed {self.vectorName}"
        if self.romaNo is None:
            self.romaNo = RoMa.RoMa_1
        assert self.romaNo in [RoMa.RoMa_1, RoMa.RoMa_2], f"romaNo must be 0 or 1, but passed: {self.romaNo}"

        self.arg = [Expression(self.labware.location.grid),  # 1. 1-67, carrier grid position, source                            example: "15"
                    Expression(self.destination.grid),       # 2. 1-67. labware location - carrier grid position,  destination   example: "15"
                    Integer   (1 if self.backHome else 0),   # 3. 1 = move back to home when finished                            example: 0
                    Integer   (1 if self.lid  else 0),       # 4. 0 = no lid handling , 1= lid handling                          example: 1
                    Integer   (1 if self.slow else 0),       # 5. 0 = maximum speed , 1 = slow speed (as defined in RoMa vector) example: 0
                    Integer   (self.romaNo),                 # 6. number of the RoMa : 0 = RoMa 1, 1 = RoMa 2                    example: 0
                    Integer   (self.cover),                  # 7. 0 = cover at source , 1 = uncover at destination               example: 0
                    Expression(self.lid.location.grid if self.lid else 0),  # 8. 1-67. lid location - carrier grid position     ??    example: "15"
                    String1   (self.labware.type.name),      # 9. labware type (as in the Freedom EVOware configuration)         example: "96 Well Microplate"
                    String1   (self.vectorName),             # 10. name of RoMa vector to use (as in the Freedom EVOware configuration), example: "Narrow"
                    String1   (""),                          # 11. unused                                                        example: ""
                    String1   (""),                          # 12. unused                                                        example: ""
                    String1   (self.labware.location.carrier.type.name),     # 13. carrier name, source    ?                     example: "MP 3Pos"
                    String1   (self.lid.carrier.type.name if self.lid else ""),  # 14. carrier name, lid     ?                       example: "MP 3Pos"
                    String1   (self.destination.carrier.type.name),          # 15. carrier name, destination    ?                               example: "MP 3Pos"
                    String1   (self.labware.location.site),                  # 16. 0 - 127 labware location - (site on carrier - 1), source     example: "3",
                    String1   (self.lid.location.site if self.lid else ""),  # 17. 0 - 127 labware location - (site on carrier - 1), source     example: "2",
                    String1   (self.destination.site)                        # 18. 0 - 127 labware location - (site on carrier - 1), source     example: "1"
                    ]
        return True

    def actualize_robot_state(self):
        self.validate_arg()
        # if self.lid:
        #     if self.cover:                       # 1 = uncover at destination
        #         self.lid.location
        self.robot.move_labware_executed(self.labware, self.destination)



class subroutine(ScriptONLY):
    """ UNDOCUMENTED
    """
    Waits     =0      # script waits for end of the called script
    Continues =1      # script continues
    Waits_previous= 2 # script waits for a previously started script

    def __init__(self, filename, action  = 0 ):
        """
        """
        Instruction.__init__(self, "Subroutine")
        self.action = action
        self.filename = filename

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.filename), Integer(self.action)]
        return True


class group(ScriptONLY):
    """ UNDOCUMENTED. Begging a group. MANUALLY set the group_end()  !!!!
    """
    def __init__(self, titel ):
        """
        """
        Instruction.__init__(self, "Group")
        self.titel = titel

    def validate_arg(self):
        Instruction.validate_arg(self)
        self.arg= [String1(self.titel)]
        return True


class group_end(ScriptONLY):
    """ UNDOCUMENTED. Begging a group. MANUALLY set the group_end()  !!!!
    """
    def __init__(self ):
        """
        """
        Instruction.__init__(self, "GroupEnd")

    def validate_arg(self):
        Instruction.validate_arg(self)
        return True

