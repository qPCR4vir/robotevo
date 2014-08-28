__author__ = 'Ariel'
""" A.15.10 Advanced Worklist Commands for the Te-MagS """

import EvoMode
import Labware
from Instruction_Base import *



class Te_MagS_MoveToPosition(T_Mag_Instr):
    """
    A.15.10.1 MoveToPosition (Worklist: Te-MagS_MoveToPosition)
    """
    def __init__(self,  position, z_pos=31, needs_allwd_lw=0, allowed_labware="" ):
        T_Mag_Instr.__init__(self, "Te-MagS_MoveToPosition"  )
        self.allowed_labware = allowed_labware
        self.needs_allwd_lw = needs_allwd_lw
        self.z_pos = z_pos
        self.position = position

    def validateArg(self):
        T_Mag_Instr.validateArg(self)
        assert self.needs_allwd_lw == 0
        assert self.allowed_labware == ""

        pos = int(self.position)
        if pos == T_Mag_Instr.Aspirate:
            pos = "{:d} {:d}".format( pos, int(self.z_pos) )

        self.arg += [ string1(pos), string1(self.needs_allwd_lw), string1(self.allowed_labware) ]
        return True


