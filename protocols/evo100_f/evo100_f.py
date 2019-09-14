# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'


from EvoScriPy.protocol_steps import *


class Evo100_FLI(Protocol):
    """
    Using the Evo100_FLI_INNT
    """
    min_s, max_s = 1, 48
    _liquid_classes = None
    _carrier_types = None
    _labware_types = None

    def __init__(self,
                 num_of_samples              = None,
                 GUI                         = None,
                 worktable_template_filename = None,
                 output_filename             = None,
                 firstTip                    = None,
                 run_name                    = None):

        Protocol.__init__(self,
                          GUI                         = GUI,
                          n_tips                      = 4,
                          num_of_samples              = num_of_samples or Evo100_FLI.max_s,
                          worktable_template_filename = worktable_template_filename,
                          output_filename             = output_filename,
                          firstTip                    = firstTip,
                          run_name                    = run_name)

    def set_paths(self):
        Protocol.set_paths(self)
        self.root_directory = Path(__file__).parent
        self.carrier_file = self.root_directory / 'Carrier.cfg'

    def liquid_classes(self):
        if Evo100_FLI._liquid_classes is None:
            Evo100_FLI._liquid_classes = labware.LiquidClasses(self.root_directory)

            # the liquid classes are static members of this robot-specific protocol class
            # (only one copy shared for all objects of this class).
            # But just for convenience of typing we want protocol objects to have
            # a self. object member which reference that liquid class.

        all = Evo100_FLI._liquid_classes.all

        self.Beads_LC_1          = all["MixBeads_1"]
        self.Beads_LC_2          = all["MixBeads_2"]
        self.Te_Mag_LC           = all["Te-Mag"]         # "Water free" but uncentered
        self.Te_Mag_Centre       = all["Te-Mag Centre"]  # To Centre after normal aspiration.
        self.Te_Mag_Rest         = all["Te-Mag Rest"]
        self.Te_Mag_Force_Centre = all["Te-Mag Force Centre"]
        self.Te_Mag_RestPlus     = all["Te-Mag RestPlus"]
        self.Water_free          = all["Water free"]     # General. No detect and no track small volumes < 50 µL

        self.SerumLiqClass      = all["Serum Disp postMix3"]  # or "MN Virus Sample"
        self.TissueHomLiqClass  = all["Serum Asp"]

        self.B_liquidClass      = all["Water free cuvette"]
        self.W_liquidClass      = self.Water_free                           # or "AVR-Water free DITi 1000"
        self.Std_liquidClass    = self.Water_free                           # or "Water free dispense DiTi 1000"
        self.Small_vol_disp     = all["Water wet"]        # or "Water free Low Volume"  ??

        return Evo100_FLI._liquid_classes

    def carrier_types(self):
        if Evo100_FLI._carrier_types is None:
            Evo100_FLI._carrier_types = labware.Carrier.Types(self.carrier_file)

            self.allow_labware("DiTi 3Pos", ['DiTi 1000ul',
                                             '96 Well Microplate',
                                             '96 Well DeepWell square'], widht_in_grids = 6)
            self.allow_labware("MP 3Pos", ['DiTi 1000ul',
                                           '96 Well Microplate',
                                           '96 Well DeepWell square'], widht_in_grids = 6)

            self.allow_labware("Trough 3Pos 25+100ml", 'Trough 100ml', widht_in_grids = 1)
            self.allow_labware("Washstation 2Grid Trough DiTi", ['Washstation 2Grid Cleaner short',
                                                                 'Washstation 2Grid Cleaner long',
                                                                 'Washstation 2Grid Waste',
                                                                 'Washstation 2Grid DiTi Waste',
                                                                 'Trough 100ml'], widht_in_grids = 2)
            self.allow_labware("Tube Eppendorf 16 Sites", ['Tube Greinerconic 2mL 16 Pos',
                                                           'Tube Eppendorf 1 Pos',
                                                           'Tube Eppendorf 2mL 1 Pos',
                                                           'Tube Greiner conic 2mL 1 Pos',
                                                           'Tube Eppendorf 2mL 16 Pos'], widht_in_grids = 1)
            self.allow_labware("Tube Eppendorf 3x16=48 Pos", ['Tube Eppendorf 3x 16 PosR',
                                                              'Tube Eppendorf 3x 16 Pos'], widht_in_grids = 3)
            self.allow_labware("Tube Eppendorf 6x16=96 Pos", ['Tube Eppendorf 6x 16 Pos'], widht_in_grids = 6)
            self.allow_labware("Te-MagS portrait", 'Tube Eppendorf 48 Pos', widht_in_grids = 6)  # ?

        return Evo100_FLI._carrier_types

    def set_defaults(self):

        wt = self.worktable

        wt.def_DiTi_type       = labware.DiTi_1000ul                 # this is a type, the others are labwares

        WashCleanerS    = wt.get_labware("", labware.CleanerSWS)
        WashWaste       = wt.get_labware("", labware.WasteWS)
        WashCleanerL    = wt.get_labware("", labware.CleanerLWS)
        DiTiWaste       = wt.get_labware("", labware.DiTi_Waste)

        wt.def_WashWaste   = WashWaste
        wt.def_WashCleaner = WashCleanerS
        wt.def_DiTiWaste   = DiTiWaste

        Reagent("Liquid waste", wt.def_WashWaste).include_in_check = False

    def waste(self,  from_labware_region : labware.Labware  = None,
                     using_liquid_class  : str              = None,
                     volume              : float            = None,     # todo accept a list ??
                     to_waste_labware    : labware.CuvetteType  = None,
                     optimize            : bool             = True):    # todo: set default as False ??

        """
        Use this function as a final step of a `in-well` pellet wash procedure (magnetically or by centrifuge created).
        Waste a `volume` from each of the selected wells `from_labware_region` (source labware wells)
        `to_waste_labware` using the current LiHa arm with maximum number of tips (of type: `self.worktable.def_DiTi_type`,
        which can be set `with self.tips(tip_type = myTipsRackType)`). # todo: count for 'broken' tips
        If no source wells are selected this function will auto select a `self.num_of_samples` number
        of wells in the source labware.
        If no destination is indicated, `self.worktable.def_WashWaste` will be used.
        The same volume will be wasted from each well (todo: revise this, waste all from EACH well?).
        If no `volume` is indicated then the volume expected to be in the first selected well will be used.
        todo: current hack to be resolved: using an special liquid class that aspirate from a side to avoid a pellet
        expected to be in the opposite side. The user must specify an equivalent class, or we need to introduce a
        kind of `Protocol.def_Waste_liqClass`.
        Aspirate and waste repeatedly with allowed volume until only an small rest are in wells and then change the LC
        to one without liquid detection - liquid level trace. (this rest depends on the well geometry - todo: make it
        a function parameter?). This avoid collision with the button of the well.

        A human readable comment will be automatically added to the script with the details of this operation.

        Warning: modify the selection of wells in both source and target labware

        :param from_labware_region: source labware possibly with selected wells
        :param using_liquid_class:
        :param volume:              is None the volume expected to be in the first selected well will be used
        :param to_waste_labware:    to_waste_labware or self.worktable.def_WashWaste
        :param optimize:            use optimized order of wells - relevant only if re-using tips
        """

        to_waste_labware = to_waste_labware or self.worktable.def_WashWaste
        assert isinstance(from_labware_region, labware.Labware), \
          'A Labware is expected in from_labware_region to waste from, but "' + str(from_labware_region) + '" was used.'

        if not volume or volume < 0.0 :
            volume = 0.0
        assert isinstance(volume, (int, float))

        original_selection = from_labware_region.selected()         # list of the selected well offset
        nt = self.robot.cur_arm().n_tips                  # the number of tips to be used in each cycle of pipetting

        if not original_selection:
            original_selection = range(self.num_of_samples)
        if optimize:                                    # todo: if None reuse self.optimize (to be created !!)
            original_selection = from_labware_region.parallelOrder(nt, original_selection)

        NumSamples = len(original_selection)                        # oriSel used to calculate number of "samples"
        SampleCnt = NumSamples                          # the number of selected wells

        if nt > SampleCnt:                              # very few wells selected (less than tips)
            nt = SampleCnt
        tm = robot.mask_tips[nt]                           # todo: count for 'broken' tips
        nt = to_waste_labware.autoselect(maxTips=nt)
        mV = self.worktable.def_DiTi_type.max_vol

        Rest = 50                    # the volume we cannot further aspirate with liquid detection, to small, collisions
        RestPlus = 50
        CtrVol = 0.5

        # all wells with equal volume. todo: waste all vol from EACH well?. v: just for msg
        v = volume if volume else from_labware_region.Wells[original_selection[0]].vol

        water_free_uncentered = "Te-Mag"  # "Water free" but uncentered  # todo: revert this LC temp hack
        Asp = instructions.aspirate(tm, water_free_uncentered, volume, from_labware_region)
        # Asp = instructions.aspirate(tm, using_liquid_class[0], volume, from_labware_region)

        Dst = instructions.dispense(tm, using_liquid_class, volume, to_waste_labware)
        # Ctr = instructions.moveLiha(instructions.moveLiha.y_move, instructions.moveLiha.z_start, 3.0, 2.0, tm, from_labware_region)

        lf = from_labware_region
        msg = "Waste: {v:.1f} µL from {n:s}".format(v=v, n=lf.label)
        with group(msg):

            msg += " in [grid:{fg:d} site:{fs:d}] in order:".format(fg=lf.location.grid, fs=lf.location.site+1) \
                  + str([i+1 for i in original_selection])
            instructions.comment(msg).exec()

            while SampleCnt:                                # loop wells (samples)
                curSample = NumSamples - SampleCnt
                if nt > SampleCnt:                          # only a few samples left
                    nt = SampleCnt                          # don't use all tips
                    tm = robot.mask_tips[nt]
                    Asp.tipMask = tm
                    Dst.tipMask = tm

                sel = original_selection[curSample:curSample + nt]      # select the next nt (number of used tips) wells
                Asp.labware.selectOnly(sel)

                if volume:                                                  # volume: to be Waste
                    r = volume                                              # r: Waste_available yet
                else:
                    vols = [w.vol for w in Asp.labware.selected_wells()]    # todo priorize this vols !!
                    r_min, r_max = min(vols), max(vols)
                    assert r_min == r_max, "Currently we assumed equal volumen in all wells, but got: " + str(vols)
                    r = r_max

                if not using_liquid_class:
                    if sel:
                        Dst.liquidClass = Asp.labware.selected_wells()[0].reagent.def_liq_class

                with self.tips(tm, drop=True, preserve=False, selected_samples=Asp.labware):

                    # aspirate and waste repeatedly with allowed volume until only Rest uL are in wells
                    while r > Rest:                     # don't aspirate Rest with these Liq Class (Liq Detect)
                        dV = min (r, mV)                # don't aspirate more than the max for that tip type
                        if dV < Rest:
                            break                       # ??  mV < Rest
                        dV -= Rest                      # the last Rest uL have to be aspired with the other Liq Class
                        Asp.volume = dV                 # with Liq Class with Detect: ">> AVR-Serum 1000 <<	365"
                        Dst.volume = dV
                        Asp.liquidClass = water_free_uncentered     # ">> AVR-Serum 1000 <<	365"  # "No Liq Detect"
                        Asp.exec()                      # <---- low level, direct aspirate here !!
                        Asp.volume = CtrVol             # ?? minimal, 'fake' vol ?
                        to_centre = "Te-Mag Centre"     # To Centre after normal aspiration.
                        Asp.liquidClass = to_centre     # just to go to the center

                        with self.tips(allow_air=CtrVol):
                            Asp.exec()
                            if dV + Rest + RestPlus + 2*CtrVol > mV:
                                Dst.exec()              # dispense if there is no capacity for further aspirations
                                r -= dV
                                Dst.volume = 0
                            else:
                                break

                    # now waste the Rest with a LC with no liquid level detection, avoiding collisions
                    Asp.volume = Rest                   # force aspirate Rest, which may be more than rests in well
                    take_rest = "Te-Mag Rest"
                    Asp.liquidClass = take_rest      # ">> AVR-Serum 1000 <<	367" # "No Liq Detect"
                    with self.tips(allow_air = Rest):
                            Asp.exec()
                    Asp.volume = CtrVol
                    force_centre = "Te-Mag Force Centre"
                    Asp.liquidClass = force_centre
                    with self.tips(allow_air = Rest + CtrVol):
                            Asp.exec()
                    Asp.volume = RestPlus
                    take_rest_plus = "Te-Mag RestPlus"
                    Asp.liquidClass = take_rest_plus  # ">> AVR-Serum 1000 <<	369" # "No Liq Detect"
                    with self.tips(allow_air = RestPlus + Rest + CtrVol):
                            Asp.exec()
                    # Ctr.exec()
                    Asp.volume = CtrVol
                    Asp.liquidClass = force_centre
                    Dst.volume += Rest + RestPlus
                    with self.tips(allow_air = CtrVol + RestPlus + Rest + CtrVol):
                            Asp.exec()
                    with self.tips(allow_air = CtrVol + RestPlus + Rest + CtrVol):
                            Dst.exec()

                SampleCnt -= nt
            Asp.labware.selectOnly(original_selection)
        instructions.wash_tips(wasteVol=4).exec()
        return original_selection

