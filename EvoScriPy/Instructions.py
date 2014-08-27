__author__ = 'elisa.reader'

import EvoMode
import Labware
from Instruction_Base import *

class aspirate(Pippeting):
    """ A.15.4.1 Aspirate command (Worklist: Aspirate)  A - 125
    """
    def __init__(self,  tipMask     = def_tipMask,
                        liquidClass = def_liquidClass,
                        volume      = def_vol,
                        labware     = def_LabW,
                        spacing     = 1,
                        wellSelection= None,       # TODO implement
                        LoopOptions = def_LoopOp,
                        RackName    = None,        # TODO implement
                        Well        = None,        # TODO implement
                        arm         = Pippet.LiHa1):
        Pippeting.__init__(self, 'Aspirate',
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

class dispence(Pippeting):
    """ A.15.4.2 Dispense (Worklist: Dispense)
    """
    def __init__(self,  tipMask     = def_tipMask,
                        liquidClass = def_liquidClass,
                        volume      = def_vol,
                        labware     = def_LabW,
                        spacing     = 1,
                        wellSelection= None,       # TODO implement
                        LoopOptions = def_LoopOp,
                        RackName    = None,        # TODO implement
                        Well        = None,        # TODO implement
                        arm         = Pippet.LiHa1):
        Pippeting.__init__(self, 'Dispence',
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

class mix(Pippeting):
    """ A.15.4.3 Mix (Worklist: Mix)
    """
    def __init__(self,  tipMask     = def_tipMask,
                        liquidClass = def_liquidClass,
                        volume      = def_vol,
                        labware     = def_LabW,
                        spacing     = 1,
                        wellSelection= None,       # TODO implement
                        cycles      = 3,
                        LoopOptions = def_LoopOp,
                        RackName    = None,        # TODO implement
                        Well        = None,        # TODO implement
                        arm         = Pippet.LiHa1):
        Pippeting.__init__(self, 'Mix',
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

    def validateArg(self):
        Pippeting.validateArg(self)
        self.arg[18:18] = [self.cycles]                 # arg 19
        return True


class wash_tips(Pippet):                     # TODO implement Arg 7-15
    """ A.15.4.4 Wash Tips (Worklist: Wash)
    """
    def __init__(self,  tipMask     = def_tipMask,
                        WashWaste   = def_WashWaste,
                        WashCleaner = def_WashCleaner,
                        wasteVol    = 100,
                        RackName    = None,        # TODO implement
                        Well        = None,        # TODO implement
                        arm         = Pippet.LiHa1):
        Pippet.__init__(self, 'Wash',
                            tipMask,
                            labware=WashWaste,
                            RackName,
                            Well,
                            arm )
        self.wasteVol = wasteVol
        self.WashCleaner = WashCleaner
        #self.WashWaste = WashWaste

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[3:-1] = [self.WashCleaner.location.grid,   # arg 4
                          self.WashCleaner.location.site,   # arg 5
                          str(self.wasteVol)                # arg 6
                          ]
        return True

    def __init__(self):
        Pippet.__init__(self, "Wash")
        assert False,"Wash() not implemented"

class getDITI(DITIs):
    def __init__(self,  tipMask, type, options=0, arm= Pippet.LiHa1):
        """
        :param label:
        :param tipMask:
        :param type: int, 0-3. DITI index (see 9.4.5 “Labware Types and DITI Types”,  9-32, DITI Index).
        """
        DITIs.__init__(self, "GetDITI", tipMask, options, arm)
        self.type=type

    def validateArg(self):
        DITIs.validateArg(self)
        self.arg[1:1] = [self.type]
        return True

class getDITI2(DITIs):
    def __init__(self,  tipMask, LabwareName, options=0, arm= Pippet.LiHa1, AirgapVolume=0, AirgapSpeed=None ):
        """

        :param label:
        :param tipMask:
        :param LabwareName:
        :param options:
        :param arm:
        :param AirgapVolume: int. used to specify a system trailing airgap (STAG) which will be aspirated after
                                  mounting the DITIs. Volume in μl
        :param AirgapSpeed: int. Speed for the airgap in μl/s
        """
        DITIs.__init__(self, "GetDITI2", tipMask, options, arm)
        self.LabwareName = LabwareName
        self.AirgapSpeed = AirgapSpeed
        self.AirgapVolume = AirgapVolume

    def validateArg(self):
        DITIs.validateArg(self)
        self.arg[1:1] = [str(self.LabwareName)]
        self.arg += [self.AirgapVolume,self.AirgapSpeed]

        return True

class dropDITI(Pippet):
    """ A.15.4.6 Drop DITIs command (Worklist: DropDITI) """
    def __init__(self,  AirgapVolume=0, AirgapSpeed=None , arm= Pippet.LiHa1):
        Pippet.__init__(self, "DropDITI",  arm=arm)
        self.AirgapSpeed = AirgapSpeed
        self.AirgapVolume = AirgapVolume

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[3:-1] = [self.AirgapVolume,self.AirgapSpeed]
        return True

class set_DITI_Counter(Pippet):
    """A.15.4.7 Set Diti Position (Worklist: Set_DITI_Counter)"""
    def __init__(self, type, posInRack  ):
        Pippet.__init__(self, "Set_DITI_Counter" )
        self.type = type
        self.posInRack = posInRack

    def validateArg(self):
        self.arg = [self.type, str(self.labware.location.grid),
                               str(self.labware.location.site), str(self.posInRack)]
        return True

class pickUp_DITIs(Pippet):
    """ A.15.4.8 Pick Up DITIs (Worklist: Pick Up_DITI)
    """
    def __init__(self, type ):
        Pippet.__init__(self, 'PickUp_DITIs' )
        self.type = type

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[4:5] = []
        self.arg[-1:-1] = [self.type]
        return True

class set_DITIs_Back(Pippet):
    """ A.15.4.9 Set DITIs Back (Worklist: Set_DITIs_Back)
    """
    def __init__(self ):
        Pippet.__init__(self, 'Set_DITIs_Back' )

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[4:5] = []
        return True

class PickUp_ZipTip(Pippet):
    """ A.15.4.10 Pickup ZipTip (Worklist: PickUp_ZipTip)
    """
    def __init__(self ):
        Pippet.__init__(self, 'PickUp_ZipTip' )
        assert False, "PickUp_ZipTip not implemented"


class detect_Liquid(Pippeting):
    """ A.15.4.11 Detect Liquid (Worklist: Detect_Liquid)
    """
    def __init__(self ):
        Pippeting.__init__(self, 'Detect_Liquid' )

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[1:1] = [str(self.liquidClass)]
        return True

class moveLiha(Pippet ):
    """ A.15.4.14 Move LiHa (Worklist: MoveLiha   - A - 135)
    """
    def __init__(self, zMove, zTarget, offset, speed  ):
        Pippet.__init__(self, 'MoveLiha' )
        self.speed = speed
        self.offset = offset
        self.zTarget = zTarget
        self.zMove = zMove

    def validateArg(self):
        Pippet.validateArg(self)
        self.arg[5:5] = [ self.zMove, self.zTarget, self.offset, self.speed]
        return True




