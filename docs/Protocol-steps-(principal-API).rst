[Principal API: Protocol steps](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-%28principal-API%29/)
=======================================

All these functions are member of the base `class Protocol`, from which all user protocols are derived.

High level functions:
^^^^^^^^^^^^^^^^^^^^

These are the functions you will use in "every day" protocol programming. They allow you to specify the kind of tips to use and them command the operations you need on your reagents, samples, reactions, etc., almost directly as it states in the steps of your "hand written" original laboratory protocol.
 - [`with tips(tip_type)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#with-protocoltipstip_type)
 - [`distribute(reagent, to_labware_region)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocoldistributereagent-to_labware_region)
 - [`transfer(from_labware_region, to_labware_region)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocoltransferfrom_labware_region-to_labware_region)
 - [`mix(in_labware_region, using_liquid_class, volume)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolmixin_labware_region-using_liquid_class-volume)
 - [`mix_reagent(reagent, cycles, vol_perc)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolmix_reagentreagent-cycles-vol_perc)
 - [`waste(from_labware_region)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolwastefrom_labware_region)
 - [`makePreMix(preMix)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolmakepremixpremix)
 - [`getTips(TIP_MASK, tip_type, selected_samples)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolgettipstip_mask-tip_type-selected_samples) 
 - [`dropTips(TIP_MASK)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocoldroptipstip_mask)
 - [`go_first_pos(first_tip)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolgo_first_posfirst_tip)
 - [`check_reagents_levels()`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolcheck_reagents_levels)
 - [`check_reagent_level(reagent, LiqClass)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolcheck_reagent_levelreagent-liqclass)

Advanced functions.
^^^^^^^^^^^^^^^^^^

Are you doing some advanced protocol development that cannot be efficiently or clearly expressed using the previous [High level functions](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#high-level-functions)? Then, you may use the following functions. Keep in mind that it is now your responsibility to know what robot/protocol "state" are ignored by these new functions. For example, before `aspirate` you will need to mount "by yourself" the tips in the correct position of the used arm, because `aspirate` ignores the higher level [`with tips`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#with-protocoltipstip_type). But don't worry, **`RobotEvo`** still keeps track of the ("internal") robot state and will throw errors informing you about most logical mistakes (like in the previous example forgetting to mount the tips). In some cases these functions may be used to construct new high lever functions.
#### [Atomic functions](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#--atomic-functions):
These are functions aimed to isolate what a physical robot would make at once: pick some tips, aspirate some liquid, etc. They are simple to understand, but are harder to use in "every day" protocol programming. They may be a great tool to set up your robot and to get an initial familiarization with all the system. 
- [`pick_up_tip(tips, tip_type, arm)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolpick_up_tiptips-tip_type-arm)
- [`drop_tip(tips, arm)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocoldrop_tiptips-arm)
- [`aspirate(arm, tips, volume, from_wells)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocolaspiratearm-tips-volume-from_wells)
- [`dispense(arm, tips, volume, to_wells)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocoldispensearm-tips-volume-to_wells)
#### [Other low level functions:](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#--other-low-level-functions)
- [`_dispensemultiwells(tips, labware)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocol_dispensemultiwellstips-labware)
- [`_aspirate_multi_tips(reagent, tips, vol)`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocol_aspirate_multi_tipsreagent-tips-vol)
- [`_multidispense_in_replicas(reagent, [vol])`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#protocol_dispensemultiwellstips-labware)

------------------------
Protocol steps
==============


.. automodule:: protocol_steps
   :members:
   :undoc-members:
   :show-inheritance:


### with Protocol.tips(tip_type)

    @contextmanager
    def tips(self,  tipsMask    = None, tip_type     = None,
                    reuse       = None, drop         = None,
                    preserve    = None, usePreserved = None,  selected_samples   = None,
                    allow_air   = None, drop_first   = False, drop_last          = False   ):
        '''

        :param tipsMask     :
        :param reuse        : Reuse the tips or drop it and take new BEFORE each individual action
        :param drop         : Drops the tips AFTER each individual action,
                              like after one aspiration and distribute of the reagent into various target
        :param preserve     : puts the tip back into a free place in some rackt of the same type
        :param usePreserved : pick the tips from the preserved
        :param selected_samples:
        :param allow_air    :
        :param drop_first   : Reuse the tips or drop it and take new once BEFORE the whole action
        :param drop_last    : Drops the tips at THE END of the whole action
        :return:
        '''


### Protocol.distribute(reagent, to_labware_region)

    def distribute(self,
               volume            : float        = None,
               reagent           : Rtv.Reagent  = None,
               to_labware_region : Lab.Labware  = None,
               optimize          : bool         = True,
               NumSamples        : int          = None,
               using_liquid_class: (str, tuple) = None,
               TIP_MASK          : int          = None,
               num_tips          : int          = None):
  
To distribute a reagent into some wells.
        This is a high level function with works with the concept of "reagent". This a a concept introduced by
        RobotEvo that don't exist in EVOware and other similar software. It encapsulated the name, wells occupied by
        each of the aliquots of the reagent, the volume corresponding to one sample (if any) and the current volume
        in each aliquot. This function can use multiple of those aliquots to distribute the reagent to the target
        wells using multiple tips (the maximum will be used if `num_tips` is not set).
        
By default a number of wells equal to the number of samples set in the protocol will be auto selected in the
        target labware `to_labware_region`, but this selection can be set explicitly (setting `well.selFlag=True`, 
        for example by calling `to_labware_region.selectOnly(self, sel_idx_list)`). If `NumSamples` is set
        it will rewrite (reset) the selected wells in the target `to_labware_region`.
        
 Please, carefully indicate whether to use "parallel optimization" in the pipetting order 
        by setting `optimize`. (very important unless you are using a full column
        pipetting arm). Check that the created script don't have conflicts in
        the order of the samples and the "geometry" of the labware areas (selection of wells)
        during each pipetting step. This is ease to "see" in the EVOware visual script editor. The generated
        .protocol.txt can also be used to check this. RobotEvo will detect
        some errors, but currently not all, assuming the areas are relatively "regular".

The same volume will be transfer to each well. It will be dispensed in only one pass: muss fit
        into the current tips
        If the liquid classes (LC) to be used are not explicitly passed the default LC of the reagent
        will be used. The generated .esc and .gwl can also be used to check this.
        
A human readable comment will be automatically added to the script with the details of this operation.

        :param NumSamples       : Priorized   !!!! If true reset the selection
        :param reagent          : Reagent to distribute
        :param to_labware_region: Labware in which the destine well are selected
        :param volume           : if not, volume is set from the default of the source reagent
        :param optimize         : minimize zigzag of multi pipetting
        :param num_tips         : the number of tips to be used in each cycle of pipetting = all

### Protocol.makePreMix(preMix)
 
    def makePreMix(self,  preMix        : Rtv.preMix,
                          NumSamples    : int       = None,
                          force_replies : bool      = False):
 
 A preMix is just that: a premix of reagents (aka - components)
        which have been already defined to add some vol per sample.
 Uses one new tip per component.
 It calculates and checks self the minimum and maximum number of replica of the resulting preMix

        :param preMix    : what to make, a predefined preMix
        :param NumSamples:
        :param force_replies: use all the preMix predefined replicas
        :return:
 
### Protocol.transfer(from_labware_region, to_labware_region)
   
    def transfer(self,
                 from_labware_region: Lab.Labware,
                 to_labware_region  : Lab.Labware,
                 volume             : (int, float),
                 using_liquid_class : (str,tuple)   = None,
                 optimizeFrom       : bool          = True,
                 optimizeTo         : bool          = True,
                 NumSamples         : int           = None) -> object:


To transfer reagents (typically samples or intermediary reactions) from some wells in the source labware to
the same number of wells in the target labware using the current LiHa arm with maximum number of tips
(of type: `self.worktable.def_DiTi`, which can be set `with self.tips(tip_type = myTipsRackType)`).

The number of "samples" may be explicitly indicated in which case will be assumed to begin from the
first well of the labware. Alternatively the wells in the source or target or in both may be
previously directly "selected" (setting `well.selFlag=True`, for example by calling
`from_labware_region.selectOnly(self, sel_idx_list)`), in which case transfer the minimum length selected.
If no source wells are selected this function will auto select the protocol's `self.NumOfSamples` number
        of wells in the source and target labwares.
        Please, carefully indicate whether to use "parallel optimization" in the pipetting order for both source and
        target by setting `optimizeFrom` and `optimizeTo`. (very important unless you are using a full column
        pipetting arm). Check that the created script don't have conflicts in
        the order of the samples and the "geometry" of the labware areas (selection of wells)
        during each pipetting step. This is ease to "see" in the EVOware visual script editor. The generated
        .protocol.txt can also be used to check this. RobotEvo will detect
        some errors, but currently not all, assuming the areas are relatively "regular".

The same volume will be transfer from each well. It will be aspirated/dispensed in only one pass: muss fit
        into the current tips
        todo ?! If no `volume` is indicated then the volume expected to be in the first selected well will be used.

If the liquid classes (LC) to be used are not explicitly passed the default LC in the first well of the current
        pipetting step will be used. The generated .esc and .gwl can also be used to check this.

A human readable comment will be automatically added to the script with the details of this operation.

Warning: modify the selection of wells in both source and target labware to reflect the wells actually used


        :param from_labware_region  : Labware in which the source wells are located and possibly selected
        :param to_labware_region    : Labware in which the target wells are located and possibly selected
        :param volume               : if not, volume is set from the default of the source reagent
        :param using_liquid_class   : LC or tuple (LC to aspirate, LC to dispense)
        :param optimizeFrom         : bool - use from_labware_region.parallelOrder(...) to aspirate
        :param optimizeTo           : bool - use to_labware_region.parallelOrder(...) to aspirate
        :param NumSamples           : Prioritized. If used reset the well selection
        :return:

### Protocol.mix(in_labware_region, using_liquid_class, volume)
    def mix(self,  in_labware_region  : Lab.Labware, 
                   using_liquid_class : str        = None, 
                   volume             : float      = None, 
                   optimize           : bool       = True):

Mix the reagents in each of the wells selected `in_labware_region`, `using_liquid_class` and `volume`

        :param in_labware_region:
        :param using_liquid_class:
        :param volume:
        :param optimize:

### Protocol.mix_reagent(reagent, cycles, vol_perc)  
    def mix_reagent(self,   reagent   : Rtv.Reagent,
                            LiqClass  : str  = None,
                            cycles    : int  = 3,
                            maxTips   : int  = 1,
                            vol_perc  : int  = 90   ):
Select all possible replica of the given reagent and mix using the given % of the current volume in EACH well or the maximum volume for the tip. Use the given "liquid class" or the reagent default.
        :param reagent:
        :param LiqClass:
        :param cycles:
        :param maxTips:
        :param vol_perc:  % of the current vol in EACH well to mix

### Protocol.waste(from_labware_region)

    Protocol.waste(from_labware_region : Lab.Labware              = None,
                   using_liquid_class  : str                      = None,
                   volume              : float                    = None,   
                   to_waste_labware    : Lab.Labware.CuvetteType  = None,
                   optimize            : bool                     = True):

Use this function as a final step of a `in-well` pellet wash procedure (magnetic or centrifuge created).

Waste a `volume` from each of the selected wells `from_labware_region` (source labware wells)
`to_waste_labware` using the current LiHa arm with maximum number of tips (of type: `self.worktable.def_DiTi`,
which can be set `with self.tips(tip_type = myTipsRackType)`).  
If no source wells are selected this function will auto select a `self.NumOfSamples` number
of wells in the source labware.

If no destination is indicated, `self.worktable.def_WashWaste` will be used.

The same volume will be wasted from each well. If no `volume` is indicated then the volume expected to be in the first selected well will be used. 

It uses an special liquid class that aspirate from a side to avoid a pellet
expected to be in the opposite side. 
The user must specify an equivalent class (or we need to introduce a
kind of `Protocol.def_Waste_liqClass`?). Aspirate and waste repeatedly with allowed volume until only an small rest are in wells and then change the LC to one without liquid detection - liquid level trace (this rest depends on the well geometry).  This avoid collision with the button of the well.

A human readable comment will be automatically added to the script with the details of this operation.

Warning: modify the selection of wells in both source and target labware

### Protocol.getTips(TIP_MASK, tip_type, selected_samples) 
    def getTips(self, TIP_MASK         = -1, 
                      tip_type         = None, 
                      selected_samples = None ):  # todo TIP_MASK=None
It will decide to get new tips or to pick back the preserved tips for the selected samples

        :param TIP_MASK: 
        :param tip_type: 
        :param selected_samples: 

### Protocol.dropTips(TIP_MASK)
    def dropTips(self, TIP_MASK=-1):

It will decide to really drop the tips or to put it back in some DiTi rack

        :param TIP_MASK:

### Protocol.go_first_pos(first_tip)

    def go_first_pos(self, first_tip: (int, str) = None):
 
 Optionally set the `Protocol.firstTip`, a position in rack, like 42 or 'B06' (optionally including the rack self referenced with a number, like '2-B06', were 2 will be the second rack in the wortable series of default tip type). Currently, for a more precise set, use directly:

        Itr.set_DITI_Counter2(labware=rack, posInRack=firstTip).exec()

### Protocol.check_reagents_levels()

    def check_reagents_levels(self):

Will emit a liquid level detection on every well occupied by all the reagents defined so fort. Will be executed at the end of `self.CheckList()` but only if `self.check_initial_liquid_level` is `True`

### Protocol.check_reagent_level(reagent, LiqClass):

    def check_reagent_level(self, reagent, LiqClass=None):

Select all possible replica of the given reagent and detect the liquid level,
        contrasting it with the current (expected) volumen in EACH well.
Use the given liquid class or the reagent default.

        :param reagent:
        :param LiqClass:

### Advanced functions.

#### - Atomic functions:

#### Protocol.pick_up_tip(tips, tip_type, arm)

    def pick_up_tip(self, TIP_MASK    : int        = None,
                          tip_type    :(str, lab.DITIrackType, lab.DITIrack, lab.DITIrackTypeSeries)= None,
                          arm         : robot.Arm    = None,
                          AirgapVolume: float      = 0,
                          AirgapSpeed : int        = None):

Atomic operation. Get new tips. It take a labware type or name instead of the labware itself (DiTi rack)
        because the real robot take track of the next position to pick, including the rack and the site (the labware).
        It only need a labware type (tip type) and it know where to pick the next tip. Example:

            self.pick_up_tip('DiTi 200 ul')  # will pick a 200 ul tip with every tip arm.

        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.tipMask[index] and Robot.tipsMask[index])
        :param tip_type: if None the worktable default DiTi will be used.
        :param arm:      Uses the default Arm (pipette) if None
        :param AirgapSpeed:  int 1-1000. Speed for the airgap in μl/s
        :param AirgapVolume: 0 - 100.  Airgap in μl which is aspirated after dropping the DITIs
        :return:

#### Protocol.drop_tip(tips, arm)

    def drop_tip(self,  TIP_MASK    : int         = None,
                        DITI_waste  : lab.Labware = None,
                        arm         : robot.Arm   = None,
                        AirgapVolume: float       = 0,
                        AirgapSpeed : int         = None):

        :param TIP_MASK:     Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                             If None all tips are used. (see Robot.tipMask[index] and Robot.tipsMask[index])
        :param DITI_waste:   Specify the worktable position for the DITI waste you want to use.
                             You must first put a DITI waste in the Worktable at the required position.
        :param arm:          Uses the default Arm (pipette) if None
        :param AirgapSpeed:  int 1-1000. Speed for the airgap in μl/s
        :param AirgapVolume: 0 - 100.  Airgap in μl which is aspirated after dropping the DITIs

#### Protocol.aspirate(arm, tips, volume, from_wells)
    def aspirate(self,   arm        : robot.Arm         = None,
                         TIP_MASK   : int               = None,
                         volume     : (float, list)     = None,
                         from_wells : [lab.Well]        = None,
                         liq_class  : str               = None):
Atomic operation. Use arm (pipette) with masked (selected) tips to aspirate volume from wells.

        :param arm:      Uses the default Arm (pipette) if None
        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.tipMask[index] and Robot.tipsMask[index])
        :param volume:   One (the same) for each tip or a list specifying the volume for each tip.
        :param from_wells: list of wells to aspirate from.
        :param liq_class: the name of the Liquid class, as it appears in your own EVOware database.
                          instr.def_liquidClass if None

#### Protocol.dispense(arm, tips, volume, to_wells)

    def dispense(self, 
                 arm        : robot.Arm         = None,
                 TIP_MASK   : int               = None,
                 volume     : (float, list)     = None,
                 to_wells   : [lab.Well]        = None,
                 liq_class  : str               = None):

Atomic operation. Use arm (pipette) with masked (selected) tips to dispense volume to wells.

        :param arm:      Uses the default Arm (pipette) if None
        :param TIP_MASK: Binary flag bit-coded (tip1=1, tip8=128) selects tips to use in a multichannel pipette arm.
                         If None all tips are used. (see Robot.tipMask[index] and Robot.tipsMask[index])
        :param volume:   One (the same) for each tip or a list specifying the volume for each tip.
        :param to_wells: list of wells to aspirate from.
        :param liq_class: the name of the Liquid class, as it appears in your own EVOware database.
                          instr.def_liquidClass if None

#### todo:
    def atomic_mix(self):       # todo
        pass

    def delay(self):            # todo
        pass


#### - Other low level functions:
#### Protocol._aspirate_multi_tips(reagent, tips, vol)
 
    def _aspirate_multi_tips(self, reagent  : Rtv.Reagent,
                                   tips     : int           = None,
                                   vol      : (float, list) = None,
                                   LiqClass : str           = None):

Intermediate-level function. Aspirate with multiple tips from multiple wells with different volume.
        Example: you want to aspirate 8 different volume of a reagent into 8 tips, but the reagent
        have only 3 replicas (only 3 wells contain the reagent). This call will generate the instructions to
        fill the tips 3 by 3 with the correct volume. Assumes the tips are mounted in the current arm.

        :param tips     : number of tips beginning from #1 to use
        :param reagent  : reagent to aspirate, with some number of wells in use
        :param vol:
        :param LiqClass:

#### Protocol._dispensemultiwells(tips, labware)

     def _dispensemultiwells(self, tips : int, liq_class, labware : Lab.Labware, vol : (float, list)):

Intermediate-level function. One dispense from multiple tips in multiple wells with different volume

        :param tips: number of tips to use                   
        :param liq_class:
        :param labware:
        :param vol:

#### Protocol._multidispense_in_replicas(reagent, [vol])
    def _multidispense_in_replicas(self, tip     : int, 
                                        reagent : Rtv.Reagent, 
                                        vol     : list         ) :
Multi-dispense of the content of ONE tip into the reagent replicas