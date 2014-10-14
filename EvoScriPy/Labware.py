__author__ = 'qPCR4vir'

import EvoMode

def_LabW        = None
def_WashWaste   = None
def_WashCleaner = None
def_DiTiWaste   = None

def count_tips(TIP_MASK)->int:
    n = 0
    while TIP_MASK:
        n += (TIP_MASK & 1)
        TIP_MASK = TIP_MASK >> 1
    return n

class Tip:    # todo play with this idea
    def __init__(self, rack_type):
        assert isinstance(rack_type, Labware.DITIrackType)
        self.vol = 0
        self.type = rack_type

class usedTip(Tip):
    def __init__(self, tip, origin=None):
        Tip.__init__(self, tip.type)
        self.vol = tip.vol
        self.origin = origin


class WorkTable:  # todo Implement !, parse WT from export file, template and scripts *.txt, *.ewt, *.est, *.esc
    """ Collection of Racks.Types and Labware.Types and pos of instances """

    curWorkTable = None

    def __init__(self, templateFile=None):
        assert WorkTable.curWorkTable is None
        WorkTable.curWorkTable = self
        self.labTypes = {}  # typeName:labwares. The type mountain a list of labware (with locations)
        self.Racks = []
        self.nGrid = 67  # max
        self.grid = [None] * 67
        if isinstance(templateFile, list):
            self.template = templateFile
        else:
            self.template = self.parseWorTableFile(templateFile)



    def parseWorTableFile(self, templateFile):
        if not templateFile: return []
        templList = []
        with open(templateFile, 'r', encoding='Latin-1') as tmpl:
            for line in tmpl:  # todo do the real complete parse
                templList += [line]
                if line.startswith("--{ RPG }--"): break
        self.template = templList
        return templList

    def addLabware(self, labware):
        """

        :param labware:
        :raise "This WT have only " + self.nGrid + " grid.":
        """
        if labware.location.grid >= self.nGrid:
            raise "This WT have only " + str(self.nGrid) + " grid."

        if labware.type.name not in self.labTypes:
            self.labTypes[labware.type.name] = []
        self.labTypes[labware.type.name] += [labware]

class Carrier:
    """ Collection of Labwares sites, filled with labwares... """

    class Type:
        def __init__(self, name, width=1, nSite=1):
            self.width = width
            self.nSite = nSite
            self.allowedLabwaresTypes = []
            self.name = name

    def __init__(self, RackType, grid, label="", worktable=WorkTable.curWorkTable):
        self.site = grid
        self.type = RackType
        self.labwares = [None] * self.nSite
        self.label = label

    def addLabware(self, labware, site):
        if labware.type.name not in self.allowedLabwaresTypes:
            raise "Labware not allowed"

        if site >= self.Type.nSite:
            raise "This rack " + self.Type.name + ":" + self.label + " have only " + self.Type.nSite + " sites."

        if self.labwares[site] is not None:
            print("Warning: you replaced an existed labware")

        self.labwares[site] = labware
        if labware.location.grid != self.grid:
            if labware.location.grid is not None:
                print("Warning, original grid changed to that of the Rack.")
            labware.location.grid = self.grid

class Well:
    def __init__(self, labware, Well_Offset):
        self.labware = labware
        assert isinstance(Well_Offset, int)
        self.offset = Well_Offset
        self.vol = 0.0
        self.selFlag = False
        self.reactive = None
        self.label = ""
        self.actions = []

    def log(self, vol, origin=None):
        self.actions += (vol, origin if origin else self)

    def select(self, sel=True):
        self.selFlag = sel

banned_well = Well(None,0)

class Labware:
    class Type:
        def __init__(self, name, nRow, nCol=1, maxVol=None, conectedWells=False):
            self.conectedWells = conectedWells
            self.name = name
            self.nRow = nRow
            self.nCol = nCol
            self.maxVol = maxVol

    class DITIrackType(Type):
        def __init__(self, name, nRow=8, nCol=12, maxVol=None, portrait=False):
            if portrait: nCol, nRow = nRow, nCol # todo revise !
            Labware.Type.__init__(self, name, nRow, nCol, maxVol, conectedWells=False)
            self.pick_next      = 0
            self.pick_next_back = nRow*nCol-1
            self.pick_next_rack = None  # labware (DITIrackType or grid,site)
            self.preserved_tips = {} # order:well ??? sample order:tip well ??sample offset:tip well
            self.last_preserved_tips = None  # a tip Well in a DiTi rack

    class Cuvette(Type):        pass
    class Te_Mag (Type):        pass

    def __init__(self, type, location, label=None, worktable=None):
        self.type = type
        self.label = label
        self.location = location
        self.Wells = [Well(self, offset) for offset in range(self.offset(self.type.nRow, self.type.nCol) + 1)]
        worktable = worktable or WorkTable.curWorkTable
        assert isinstance(worktable, WorkTable)
        worktable.addLabware(self)
        if location.rack:
            location.rack.addLabware(self, location.rack_site)

    class Location:
        def __init__(self, grid=None, site=None, rack=None, rack_site=None):
            """


            :param grid: int, 1-67.   worktable grid. Carrier grid position
            :param site: int, 0 - 127. Site on carrier (on RAck?)lab location - (site on carrier - 1) !!!!!
            :param label:
            :param rack:
            :param rack_site:
            """

            self.rack = rack
            assert 1 <= grid <= 67
            site -= 1
            assert 0 <= site <= 127
            self.grid = grid
            self.site = site
            self.rack_site = rack_site

    class Position:
        def __init__(self, row, col=1):
            self.row = row
            self.col = col

    def autoselect(self, offset=0, maxTips=1, replys=1): #todo make this "virtual". Implement cuvette
        """

        :param offset:
        :param maxTips:
        :param replys:
        :return:
        """
        nWells = self.type.nCol * self.type.nRow
        assert nWells > offset, "Can not select to far"  # todo better msg
        if self.type.conectedWells:
            if nWells < maxTips: maxTips = nWells
            self.selectOnly(range((nWells - maxTips) // 2, (nWells - maxTips) // 2 + maxTips))
            return maxTips
        else:
            if maxTips > replys: maxTips = replys
            self.selectOnly(range(offset, offset + maxTips))
            return maxTips

    def offset(self, row, col=1):
        if isinstance(row, Labware.Position):
            col = row.col
            row = row.row
        if isinstance(row, str):
            return self.offsetFromName(row)
        return row - 1 + (col - 1) * self.type.nRow

    def offsetFromName(self, wellName):
        row = ord(wellName[0]) - ord('A') + 1
        col = int(wellName[1:])
        return self.offset(row, col)

    def position(self, offset):
        return self.Position(offset % self.type.nCol + 1, offset // self.type.nCol + 1)

    def find_free_wells(self, n=1, init_pos=0)-> (bool, [Well]):
        continuous = True
        free_wells = []
        for i in range(init_pos, len(self.Wells) - n+1):
            if any(w.reactive for w in self.Wells[i:i + n]): continue
            return continuous, self.Wells[i:i + n]
        for w in self.Wells[init_pos:]:
            if w.reactive: continue
            free_wells += [w]
            if len(free_wells) == n: break
        continuous = all((free_wells[i].offset+1 == free_wells[i+1].offset)
                            for i in range(len(free_wells)-1))
        return continuous, free_wells

    def put(self, reactive, pos=None, replicas=None)->list:
        """ Put a reactive with replicas in the given wells position of this labware,
        and return a list of the wells used

        :param reactive:
        :param pos:
        :param replicas:
        :return:
        """
        if pos is None:  # find self where to put the replicas of this reactive
            replicas = replicas or 1  # default one replica
            continuous, pos = self.find_free_wells(replicas)
            assert replicas == len(pos)  # replicas = len(pos)  # todo What to do?
        elif isinstance(pos, list):
            if replicas is None:  # put one replica on each of the given position
                replicas = len(pos)
            else:
                assert (replicas == len(pos))
        else:
            replicas = replicas or 1  # put one replica beginning from the given position
            if isinstance(pos, Well):
                # assert pos.labware is self, "Trying to put the reactive in another labware?"
                pos = pos.labware.Wells[pos.offset: pos.offset + replicas]
                # pos = self.Wells[pos.offset: pos.offset + replicas]
            else:
                pos = self.offset(pos)
                pos = self.Wells[pos: pos + replicas]
                # pos = self.offset(pos) + 1
                # pos = range(pos, pos + replicas)

        Replicas = []
        for w in pos:
            w = w if isinstance(w, Well) else self.Wells[self.offset(w)]
            assert not w.reactive, self.label + ": Can not put " + reactive.name + " in position " + str(
                w.offset + 1) + " already occupied by " + w.reactive.name
            w.reactive = reactive
            # w.labware = self
            Replicas += [w]
        return Replicas

    def clearSelection(self):
        for well in self.Wells:
            well.selFlag = False
        return self

    def selected(self):
        return [well.offset for well in self.Wells if well.selFlag]

    def selected_wells(self):
        return [well for well in self.Wells if well.selFlag]

    def selectAll(self):
        for well in self.Wells:
            well.selFlag = True
        return self

    def selectOnly(self, sel_idx_list):
        self.clearSelection()
        self.select(sel_idx_list)
        return self

    def select(self, sel_idx_list):
        for i in sel_idx_list:
            self.Wells[i].selFlag = True
        return self

    def newOffset(self, pos, offset):
        return self.offset(pos.row, pos.col) + offset

    def newPosition(self, pos, offset):
        return self.position(self.newOffset(pos, offset))

    def posAtParallelMove(self, step, nTips):
        nR, nC = self.type.nRow, self.type.nCol
        assert step < nC * nR, "too many steps!!"
        SubPlateSize = nTips * nC
        SubPlate = step // SubPlateSize
        tN_semiCol = step // nTips
        parit = (SubPlate) % 2
        pos_semiCol = nC * parit + (tN_semiCol % nC) * (-1) ** parit + 1 - parit

        p = self.Position(row=SubPlate * nTips + step % nTips + 1, col=pos_semiCol)

        msg = "error in calculation of parallel row {:d}>{:d}".format(p.row, nR)
        assert 0 < p.row <= nR, msg
        msg = "error in calculation of parallel col {:d}>{:d}".format(p.col, nC)
        assert 0 < p.col <= nC, msg
        return p

    def parallelOrder(self, nTips, original=None):
        original = original or self.selected()
        assert original
        if isinstance(original, int):
            assert 0 < original <= len(self.Wells)
            original = range(original)
        assert isinstance(original, (list, range))
        return [self.offset(self.posAtParallelMove(offset, nTips)) for offset in original]

    def offsetAtParallelMove(self, step, nTips):
        p = self.posAtParallelMove(step, nTips)
        return self.offset(p.row, p.col)

    def moveParallel(self, pos, offset):  # TODO
        return offset % self.type.nCol + 1, offset // self.type.nCol + 1

    def wellSelectionStr(self):
        """
        :return: See A.15.3, pag. A-122
        file:///C:/Prog/RobotEvo/FreedomEVOwareStandardV2.4SP1-2011.ExtendedDeviceSupportManual.pdf
        Many of the advanced worklist commands have a parameter called wellSelection.
        wellSelection is a string which specifies the wells (tips) which should be used for
        the command.
        Characters 1 and 2 of the string specify the number of wells in the x-direction in
        hexadecimal. Characters 3 and 4 of the the string specify the number of wells in
        the y-direction in hexadecimal. For example, 12 x 8 (96 wells) = 0C08.
        All following characters are used for the well selection, whereby each character
        specifies the well selection for a group of 7 adjacent wells using a specially
        adapted bitmap system. Only 7 bits are used per byte [RANGE 0-127 !!!] instead of 8 to avoid screen
        and printer font compatibility problems. Using the 7-bit system, 14 characters are
        needed to represent the well selection for 96 wells (plus characters 1 to 4, total of
        18 characters) and 55 characters are needed to represent the well selection for
        384 wells (total of 59 characters).
        In addition, since most ANSI characters below ANSI 32 are non-printable (nonhuman-
        readable), decimal 48 (ANSI value for “0”) is added to the value
        [RANGE 48-175 !!! 144 have undefined Unicode !!!]  of the
        bitmap to make it easier to read, send by eMail etc. The following shows some
        examples for character 5 of the well selection string for a 96-well microplate in
        landcape orientation.
        Character 5 is responsible for the first group of 7 wells

        this function stores 7 bit per character in the selection string
        the first 2 characters are the number of wells in x direction (columns) in hexadecimal.
        the characters 3 and 4 are the number of wells in y direction (rows) in hexadecimal.
        well are computed in the order back to front, left to right;
        https://docs.python.org/3.4/library/string.html#formatstrings
        """
        X = self.type.nCol
        Y = self.type.nRow
        sel = bytearray()  # sel=sel.encode('ascii')
        bitMask = 0
        null = 48  # ord('0')
        bit = 0
        for w in self.Wells:
            bit = w.offset % 7
            if w.selFlag: bitMask |= (1 << bit)
            if bit == 6:
                sel.append(null + bitMask)
                bitMask = 0
        if bit != 6:
            sel.append(null + bitMask)
        return "{:02X}{:02X}".format(X, Y) + sel.decode(EvoMode.Mode.encoding)

class DiTi_Rack (Labware):
    def __init__(self, type, location, label=None, worktable=WorkTable.curWorkTable):
        assert isinstance(type, Labware.DITIrackType)
        Labware.__init__(self, type, location, label=label, worktable=worktable)
        self.fill()
        if type.pick_next_rack is None: # update an iRobot state !! Only initialization, please!
            type.pick_next_rack = self
            # type.last_preserved_tips = ?

    def fill(self, beg=1, end=None):   # todo it belong to Robot ??
        if isinstance(beg, list): assert end is None
        else:
            beg = self.offset(beg)
            end = self.offset(end or self.type.nRow*self.type.nCol-1)
            r = range(beg, end+1)
        for w in self.Wells:
            w.reactive = None
            # w.labware = None   #   hummm ??
        for w in r:
            self.Wells[w].reactive = Tip(self.type)   # How we can actualize the "counters"? Using Instructions
            # self.Wells[w].labware = self    #   hummm ??

    def find_new_tips(self, TIP_MASK, lastPos=False)->(bool, list):
        return self.find_tips(TIP_MASK, self.type, lastPos)

    @staticmethod
    def find_tips(TIP_MASK, rack_type, lastPos=False)->(bool, list):
        """

        :param TIP_MASK:
        :param rack_type:
        :param lastPos:
        :return:
        """
        assert isinstance(rack_type, Labware.DITIrackType)
        n = count_tips(TIP_MASK)
        rack = rack_type.pick_next_rack
        r = rack.Wells[rack_type.pick_next,
                       rack_type.pick_next_back+1,
                       -1 if lastPos else 1]
        continuous = True
        try_in_next_rack = 2        # hummm !
        tips = []
        while (try_in_next_rack):
            try_in_next_rack -= 1
            # todo do we really need a correspondence mask - wells??

            for i in range(len(r)-n+1):
                if all(isinstance(w.reactive, Tip) for w in r[i:i + n]):
                    return continuous, tips + r[i:i + n]

            continuous = False
            for w in r:
                if isinstance(w.reactive, Tip):
                    tip = w.reactive
                    assert tip.type is rack_type
                    tips += [w]
                    n -= 1
                    if n==0:
                        return continuous, tips
            # we need to find in other rack
            next_rack = rack_type.pick_next_rack.next_rack()
            assert next_rack is not rack_type.pick_next_rack
            r = next_rack.Wells[0,
                                rack_type.nCol*rack_type.nRow,
                                -1 if lastPos else 1]

    def remove_tips(self, TIP_MASK,
                          labware,
                          worktable=WorkTable.curWorkTable,
                          lastPos=False):
        """
        A response to a getTips: the tips have to be removed from the rack
        and only after that can appear mounted in the robot arm to pipette.
        The tips are removed at the "current" position, the position where
        begin the fresh tips, with is maintained internally by the robot and
        is unknown to the user
        :param TIP_MASK:
        :param labware:
        :param worktable:
        :param lastPos:
        :return:
        """
        n = count_tips(TIP_MASK)# todo do we really need a correspondence mask - wells??
        tp = labware
        tp = tp if isinstance(tp, Labware.Type) else tp.type
        return self._remove_tip(n, tp, worktable, lastPos)

    def _remove_tip(self, n, tp, worktable=WorkTable.curWorkTable, lastPos=False):
        #  return removed tips and set it in the arm
        assert isinstance(tp, Labware.DITIrackType)
        beg, end, rack = tp.pick_next, tp.pick_next_back, tp.pick_next_rack
        assert isinstance(rack, DiTi_Rack)
        rest = end - beg + 1
        i, d = [end, -1] if lastPos else [beg, 1]
        tips = []
        while n:
            assert rack.Wells[i].reactive.type is tp
            tips += [rack.Wells[i].reactive]
            rack.Wells[i].reactive = None
            print ("Pick tip "+str(i+1)+" from site "+str(rack.location.site+1)
                   + " of rack " + rack.label)
            n -= 1
            rest -= 1
            if rest:
                self.set_next_to_next_rack(worktable)
                return tips + self._remove_tip(n, tp, worktable, lastPos)
            i+=d
            if lastPos:  tp.pick_next_back -= 1
            else:        tp.pick_next      += 1
        return tips

    def next_rack(self, worktable=WorkTable.curWorkTable):
        tp = self.type
        assert isinstance(worktable, WorkTable)
        racks = worktable.labTypes[tp.name]
        assert isinstance(racks,list)
        i = racks.index(self)
        i = i+1
        if i == len (racks):
            i = 0
        # if racks[i] is self: return None
        return racks[i]


    def set_next_to_next_rack(self, worktable=WorkTable.curWorkTable):
        rack = self.next_rack(worktable)
        assert isinstance(rack, DiTi_Rack)
        print ("WARNING !!!! USER PROMPT: Fill Rack " + rack.label)
        assert self is not rack
        rack.fill()
        tp = self.type
        tp.pick_next = 0
        tp.pick_next_back = tp.nCol * tp.nRow -1
        tp.pick_next_rack = rack

    def set_back(self, TIP_MASK, tips):
        """ Low level. Part of the job have been already done: tips is a list of the tips in
        the robot arm, passed here just to prevent a call and a link back to the robot.
        And the rack self hat already the target tip-wells selected.

        :param TIP_MASK:
        :param labware_selection:
        :param tips:
        """
        n = count_tips(TIP_MASK)
        assert n == len(self.selected()), "Too much or too few wells selected to put tip back"
        for i, w in enumerate(self.selected_wells()):
            assert w.reactive is not Tip, ("Another tip " + w.reactive.type.name +
                            "is already in position " + str(self.position(i)) + " of " + self.label)
            tp = tips[i]
            assert isinstance(tp, usedTip)
            w.reactive = tp
            self.type.preserved_tips[tp.origin.offset] = w
            self.type.last_preserved_tips = w

    def pick_up(self, TIP_MASK)->[usedTip]:
        """ Low level. Part of the job have been already done: the rack self hat
        already the source tip-wells selected. We need to return these tips.

        :param TIP_MASK:
        """
        n = count_tips(TIP_MASK)
        assert n == len(self.selected()), "Too much or too few wells selected to pick up tips"
        tips = []
        for i, w in enumerate(self.selected_wells()):
            assert isinstance(w.reactive, usedTip), ("No tip " + w.reactive.type.name +
                            "were found in position " + str(self.position(i)) + " of " + self.label)
            tips[i] = w.reactive
            w.reactive = None
            #self.type.preserved_tips[tp.origin.offset] = w # tp.origin.offset



Trough_100ml    = Labware.Type("Trough 100ml",                      8,      maxVol=100000, conectedWells=True)
EppRack16_2mL   = Labware.Type("Tube Eppendorf 2mL 16 Pos",         16,     maxVol=2000)
GreinRack16_2mL = Labware.Type("Tube Greinerconic 2mL 16 Pos",      16,     maxVol=2000)
EppRack3x16R    = Labware.Type("Tube Eppendorf 3x 16 PosR",         16, 3,  maxVol=1500)
EppRack3x16     = Labware.Type("Tube Eppendorf 3x 16 Pos",          16, 3,  maxVol=1500)
EppCarr16sites  = Carrier.Type("Tube Eppendorf 16 Sites", width=1, nSite=16)
Greiner2mLx1    = Labware.Type("Tube Greiner conic 2mL 1 Pos",      1, 1,   maxVol=2000)
Epp2mLx1        = Labware.Type("Tube Eppendorf 2mL 1 Pos",          1, 1,   maxVol=2000)
Eppx1           = Labware.Type("Tube Eppendorf 1 Pos",              1, 1,   maxVol=1500)


TeMag48         = Labware.Type("Tube Eppendorf 48 Pos",             8, 6,   maxVol=1500)
CleanerSWS      = Labware.Type("Washstation 2Grid Cleaner short",   8,      maxVol=100000, conectedWells=True)
WasteWS         = Labware.Type("Washstation 2Grid Waste",           8,      maxVol=100000, conectedWells=True)
CleanerLWS      = Labware.Type("Washstation 2Grid Cleaner long",    8,      maxVol=100000, conectedWells=True)
DiTi_Waste      = Labware.Type("Washstation 2Grid DiTi Waste",      8,      maxVol=100000, conectedWells=True)
DiTi_1000ul     = Labware.DITIrackType("DiTi 1000ul", maxVol=940)
Tip_1000maxVol  = DiTi_1000ul.maxVol
Tip_200maxVol   = 190
def_DiTi        = DiTi_1000ul


MP96well = Labware.Type("MP 96 well 0,2 mL", 8, 12, maxVol=200)
