__author__ = 'Ariel'

import Labware as Lab


TeMg_Heat       = Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 0), "48 Pos Heat")
TeMag           = Lab.Labware(Lab.TeMag48,      Lab.Labware.Location(14, 1), "48PosMagnet")
WashCleanerS    = Lab.Labware(Lab.CleanerSWS,   Lab.Labware.Location(22, 0))
WashWaste       = Lab.Labware(Lab.WasteWS,      Lab.Labware.Location(22, 1))
WashCleanerL    = Lab.Labware(Lab.CleanerLWS,   Lab.Labware.Location(22, 2))
DiTiWaste       = Lab.Labware(Lab.DiTi_Waste,   Lab.Labware.Location(22, 6))

Lab.def_LabW        = Lab.Labware(type=Lab.MP96well,location=Lab.Labware.Location(1,1))
Lab.def_WashWaste   = WashWaste
Lab.def_WashCleaner = WashCleanerS
Lab.def_DiTiWaste   = DiTiWaste
Lab.def_DiTi        = Lab.DiTi_1000ul   # todo revise



ElutBuf       = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(6, 0), "1-VEL-ElutionBuffer" )
LysBuf        = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(6, 1), "2-Vl Lysis Buffer"   )
BindBuf       = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(6, 2), "3-VEB Binding Buffer")

BioWaste      = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(22,2), "6-Waste"             )
Unused8       = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(24,1), "8-Unused"           )
Unused9       = Lab.Labware(Lab.Trough_100ml, Lab.Labware.Location(24,2), "9-Unused"           )


DiTi1000_1    = Lab.DiTi_Rack(Lab.DiTi_1000ul, Lab.Labware.Location(25,0),"1000-1")
DiTi1000_2    = Lab.DiTi_Rack(Lab.DiTi_1000ul, Lab.Labware.Location(25,1),"1000-2")
DiTi1000_3    = Lab.DiTi_Rack(Lab.DiTi_1000ul, Lab.Labware.Location(25,2),"1000-3")

# set_DITI_Counter2( DiTi1000_2,  DiTi1000_2.offsetFromName('E7')  ).exec()

B_liquidClass = "Buffer free DITi 1000-AVR"
W_liquidClass = "AVR-Water free DITi 1000"
Std_liquidClass = "Water free dispense DiTi 1000"
