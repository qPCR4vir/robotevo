__author__ = 'Ariel'

import Labware as Lab


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

# set_DITI_Counter2( DiTi1000_2,  DiTi1000_2.offsetFromName('E7')  ).exec()

Water_free = "Water free"  # General. No detect and no track small volumes < 50 µL

B_liquidClass   = Water_free #    or "Buffer free DITi 1000-AVR" ?
W_liquidClass   = Water_free #    or "AVR-Water free DITi 1000"
Std_liquidClass = Water_free #    or "Water free dispense DiTi 1000"
Te_Mag = "Te-Mag" # "Water free" but uncentred
