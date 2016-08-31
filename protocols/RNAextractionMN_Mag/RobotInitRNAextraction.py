# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016

__author__ = 'Ariel'


TeMg_Heat       = None # Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 1), "48 Pos Heat")
TeMag           = None # Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 2), "48PosMagnet")
WashCleanerS    = None # Lab.Cuvette(Lab.CleanerSWS,   Lab.Labware.Location(22, 1), "Washstation 2Grid Cleaner short")
WashWaste       = None # Lab.Cuvette(Lab.WasteWS,      Lab.Labware.Location(22, 2), "Washstation 2Grid Waste")
WashCleanerL    = None # Lab.Cuvette(Lab.CleanerLWS,   Lab.Labware.Location(22, 3), "Washstation 2Grid Cleaner long")
DiTiWaste       = None # Lab.DITIwaste(Lab.DiTi_Waste,   Lab.Labware.Location(22, 7), "Washstation 2Grid DiTi Waste")

# Lab.def_LabW        = None # Lab.Labware(type=Lab.MP96well,location=Lab.Labware.Location(1,2))
# Lab.def_WashWaste   = None # WashWaste
# Lab.def_WashCleaner = None # WashCleanerS
# Lab.def_DiTiWaste   = None # DiTiWaste
# Lab.def_DiTi        = None # Lab.DiTi_1000ul   # todo revise


ElutBuf       = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 1), "1-VEL-ElutionBuffer" )
LysBuf        = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 2), "2-Vl Lysis Buffer"   )
BindBuf       = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 3), "3-VEB Binding Buffer")

BioWaste      = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22,6), "6-Waste"             )
Unused8       = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24,2), "8-Unused"           )
Unused9       = None # Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24,3), "9-Unused"           )


DiTi1000_1    = None # Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,1),"1000-1")
DiTi1000_2    = None # Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,2),"1000-2")
DiTi1000_3    = None # Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,3),"1000-3")


Reactives  = None # Lab.Labware(Lab.GreinRack16_2mL, Lab.Labware.Location(7, 1 ), "Reactives")
Eluat      = None # Lab.Labware(Lab.EppRack3x16R,    Lab.Labware.Location(8, 1 ), "Eluat" )
Samples    = None # Lab.Labware(Lab.EppRack3x16,     Lab.Labware.Location(11, 1), "Proben")


def init_RNAextraction():
    import EvoScriPy.Labware as Lab

    print('Init init_RNAextraction()')

    # https://docs.python.org/3.5/reference/simple_stmts.html#global
    # https://www.python.org/dev/peps/pep-3104/   for nonlocal
    # https://docs.python.org/3/faq/programming.html#id8
    global TeMg_Heat, TeMag, WashCleanerS, WashWaste, WashCleanerL, DiTiWaste, ElutBuf, LysBuf, BindBuf
    global BioWaste, Unused8, Unused9, DiTi1000_1, DiTi1000_2, DiTi1000_3, Reactives, Reactives, Eluat, Samples

    TeMg_Heat       = Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 1), "48 Pos Heat")
    TeMag           = Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 2), "48PosMagnet")
    WashCleanerS    = Lab.Cuvette(Lab.CleanerSWS,   Lab.Labware.Location(22, 1), "Washstation 2Grid Cleaner short")
    WashWaste       = Lab.Cuvette(Lab.WasteWS,      Lab.Labware.Location(22, 2), "Washstation 2Grid Waste")
    WashCleanerL    = Lab.Cuvette(Lab.CleanerLWS,   Lab.Labware.Location(22, 3), "Washstation 2Grid Cleaner long")
    DiTiWaste       = Lab.DITIwaste(Lab.DiTi_Waste,   Lab.Labware.Location(22, 7), "Washstation 2Grid DiTi Waste")

    Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.Labware.Location(1,2))
    Lab.def_WashWaste   = WashWaste
    Lab.def_WashCleaner = WashCleanerS
    Lab.def_DiTiWaste   = DiTiWaste
    Lab.def_DiTi        = Lab.DiTi_1000ul   # todo revise

    ElutBuf       = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 1), "1-VEL-ElutionBuffer" )
    LysBuf        = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 2), "2-Vl Lysis Buffer"   )
    BindBuf       = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(6, 3), "3-VEB Binding Buffer")

    BioWaste      = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(22,6), "6-Waste"             )
    Unused8       = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24,2), "8-Unused"           )
    Unused9       = Lab.Cuvette(Lab.Trough_100ml, Lab.Labware.Location(24,3), "9-Unused"           )

    DiTi1000_1    = Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,1),"1000-1")
    DiTi1000_2    = Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,2),"1000-2")
    DiTi1000_3    = Lab.DITIrack(Lab.DiTi_1000ul, Lab.Labware.Location(25,3),"1000-3")

    Reactives = Lab.Labware(Lab.GreinRack16_2mL, Lab.Labware.Location(7, 1), "Reactives")
    Eluat = Lab.Labware(Lab.EppRack3x16R, Lab.Labware.Location(8, 1), "Eluat")
    Samples = Lab.Labware(Lab.EppRack3x16, Lab.Labware.Location(11, 1), "Proben")

    # set_DITI_Counter2( DiTi1000_2,  DiTi1000_2.offsetFromName('E7')  ).exec()


