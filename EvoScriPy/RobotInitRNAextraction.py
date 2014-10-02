__author__ = 'Ariel'

from Labware import *

ElutBuf       = Labware(Trough_100ml, Labware.Location(6, 0), "1-VEL-ElutionBuffer" )
LysBuf        = Labware(Trough_100ml, Labware.Location(6, 1), "2-Vl Lysis Buffer"   )
BindBuf       = Labware(Trough_100ml, Labware.Location(6, 2), "3-VEB Binding Buffer")

BioWaste      = Labware(Trough_100ml, Labware.Location(22,2), "6-Waste"             )
Unused8      = Labware(Trough_100ml, Labware.Location(24,1), "8-Unused"           )
Unused9      = Labware(Trough_100ml, Labware.Location(24,2), "9-Unused"           )


DiTi1000_1    = DiTi_Rack(DiTi_1000ul, Labware.Location(25,0),"1000-1")
DiTi1000_2    = DiTi_Rack(DiTi_1000ul, Labware.Location(25,1),"1000-2")
DiTi1000_3    = DiTi_Rack(DiTi_1000ul, Labware.Location(25,2),"1000-3")

# set_DITI_Counter2( DiTi1000_2,  DiTi1000_2.offsetFromName('E7')  ).exec()

B_liquidClass = "Buffer free DITi 1000-AVR"
W_liquidClass = "AVR-Water free DITi 1000"
Std_liquidClass = "Water free dispense DiTi 1000"
