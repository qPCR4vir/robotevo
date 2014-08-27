__author__ = 'Ariel'

import EvoMode
import Labware
from Instruction_Base import *
from Instructions import *


def Aspirate( tipMask,
              liquidClass,
              volume,
              grid,
              site,
              spacing,
              wellSelection,
              noOfLoopOptions,
              #loopName,
              #action,
              #difference,
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

    return a, EvoMode.CurEvo.exec(a)

def Dispence(tipMask,liquidClass,volume,grid, site, spacing, wellSelection,
             #LoopOptions,
             RackName,Well):
    """
    :param tipMask: int 0 - 255, selected tips, bit-coded (tip1 = 1, tip8 = 128)
    :param liquidClass: str,
    :param volume: expr[12], 12 expressions which the volume for each tip. 0 for tips which are not used or not fitted.
    :param grid: int, 1 - 67, labware location - carrier grid position
    :param RackName:
    :param Well:
    """
    a = dispense( RackName , Well)
    a.tipMask       = tipMask
    a.liquidClass   = liquidClass
    a.volume        = volume
    a.labware.location = Labware.Labware.Location(grid,site)
    #a.loopOptions=LoopOptions

    return a, a.exec()


