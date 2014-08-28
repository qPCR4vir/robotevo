__author__ = 'Ariel'

import EvoMode


class WorkTable:
    """ Collection of Racks """

    def __init__(self):
        self.Racks = []
        self.nGrid = 67   # TODO ver max
        self.templateFile = ""

class Rack:
    """ Collection of Labwares places, filled with labwares... """

    def __init__(self, RackName=None):
        self.Labwares = []
        self.width = 1
        self.nSite = 1
        self.allowedLabwaresTypes = []
        self.name = RackName


class Well:
    def __init__(self, labware, Well_Offset):
        assert isinstance(Well_Offset, int)
        self.offset = Well_Offset
        self.vol = 0
        self.selFlag = False


class Labware:
    class Type:
        def __init__(self, name, nRow, nCol=1, maxVol = None):
            self.name = name
            self.nRow = nRow
            self.nCol = nCol
            self.maxVol = maxVol

    class Location:
        def __init__(self, grid=None, site=None, label=None):
            """

            :param grid: int, 1-67.     labware location - carrier grid position
            :param site: int, 0 - 127.  labware location - (site on carrier - 1) !!!!!
            :param label:
            """
            self.grid=grid
            self.site=site
            self.label=label

    class Position:
        def __init__(self, row, col=1):
            self.row=row
            self.col=col


    def __init__(self, type, location=None):
        self.type = type
        self.location = location
        self.Wells = [Well(self,offset) for offset in range(self.offset(self.type.nRow,self.type.nCol)+1)]

    def clearSelection(self):
        for well in self.Wells:
            well.selFlag = False

    def selectAll(self):
        for well in self.Wells:
            well.selFlag = True

    def offset(self, row, col=1):
        if isinstance(row,str):
            return self.offsetFromName(row)
        return row-1 + (col-1)*self.type.nRow

    def offsetFromName(self, wellName):
        row = ord(wellName[0]) - ord('A') + 1
        col = int(wellName[1:])
        return self.offset(row,col)

    def position(self, offset):
        return self.Position( offset % self.type.nCol + 1, offset // self.type.nCol + 1)

    def newOffset(self, pos, offset ):
        return self.offset(pos.row,pos.col) + offset

    def newPosition(self, pos, offset):
        return self.position(self.newOffset(pos,offset))

    def posAtParallelMove(self, step):
        assert step < self.type.nCol * self.type.nRow , "too many steps!!"
        nTips = EvoMode.CurEvo.Tip_tNum
        SubPlateSize = nTips * self.type.nCol
        SubPlate = step // SubPlateSize
        p = self.Position(row=SubPlate*nTips + step%nTips + 1, col=self.type.nCol - (step//nTips) % self.type.nCol )
        return p

    def offsetAtParallelMove(self, step):
        p = self.posAtParallelMove(step)
        return self.offset(p.row, p.col)

    def moveParallel(self, pos, offset): # TODO
        return offset % self.type.nCol + 1, offset // self.type.nCol + 1

    def wellSelectionStr(self):
        """
        :return: See A.15.3, pag. A-122
        file:///C:/Prog/RobotEvo/FreedomEVOwareStandardV2.4SP1-2011.ExtendedDeviceSupportManual.pdf
        this function stores 7 bit per character in the selection string
        the first 2 characters are the number of wells in x direction (columns) in hexadecimal.
        the characters 3 and 4 are the number of wells in y direction (rows) in hexadecimal.
        well are computed in the order back to front, left to right;
        https://docs.python.org/3.4/library/string.html#formatstrings
        """
        X = self.type.nCol
        Y = self.type.nRow
        sel = "{:02X}{:02X}".format (X,Y)
        bitMask=0
        null = ord('0')
        for w in self.Wells:
            bit = w.offset % 7
            bitMask += w.selFlag << bit
            if bit == 6 :
                sel+= chr(null + bitMask)
                bitMask = 0
        if bit != 6:
            sel+= chr(null + bitMask)
        return sel





Trough_100ml  = Labware.Type("Trough 100ml", 8, maxVol=100000)

EppRack16_2mL = Labware.Type("Tube Eppendorf 2mL 16 Pos", 16, maxVol=2000)

EppRack3x16R  = Labware.Type("Tube Eppendorf 3x 16 PosR", 3*16, maxVol=1500)

EppRack3x16   = Labware.Type("Tube Eppendorf 3x 16 Pos", 3*16, maxVol=1500)

TeMag48       = Labware.Type("Tube Eppendorf 48 Pos", 8, 6, maxVol=1500)

CleanerSWS    = Labware.Type("Washstation 2Grid Cleaner short"  , 8, maxVol=100000)
WashCleanerS  = Labware(CleanerSWS, Labware.Location(22,0))

WasteWS       = Labware.Type("Washstation 2Grid Waste"          , 8, maxVol=100000)
WashWaste     = Labware(WasteWS,    Labware.Location(22,1))

CleanerLWS    = Labware.Type("Washstation 2Grid Cleaner long"   , 8, maxVol=100000)
WashCleanerL  = Labware(CleanerLWS, Labware.Location(22,2))

DiTi_Waste    = Labware.Type("Washstation 2Grid DiTi Waste"     , 8, maxVol=100000)
DiTiWaste     = Labware(DiTi_Waste,Labware.Location(22,6))

DiTi_1000ul   = Labware.Type("DiTi 1000ul"     , 8, maxVol=970)




EppRack16 = Labware.Type("Epp 1,5 mL x 16", 16, maxVol=1500)
MP96well = Labware.Type("MP 96 well 0,2 mL", 8,12, maxVol=200)
Tip1000  = Labware.Type("DiTi 96 1000uL", 8,12, maxVol=970)