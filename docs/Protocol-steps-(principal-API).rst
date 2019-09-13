Principal API: Protocol steps
=======================================

All these functions are member of the base :py:class:`~protocol_steps.Protocol`, from which all user protocols are derived.

High level functions:
^^^^^^^^^^^^^^^^^^^^

These are the functions you will use in "every day" protocol programming. They allow you to specify the kind of tips to use and them command the operations you need on your reagents, samples, reactions, etc., almost directly as it states in the steps of your "hand written" original laboratory protocol.
 - :py:method:`protocol_steps.Protocol.with tips(tip_type)`_
 - `protocol_steps.Protocol.distribute(reagent, to_labware_region)`_
 - `~protocol_steps.transfer(from_labware_region, to_labware_region)`
 - `mix(in_labware_region, using_liquid_class, volume)`_
 - `mix_reagent(reagent, cycles, vol_perc)`_
 - `waste(from_labware_region)`_
 - `makePreMix(preMix)`_
 - `getTips(TIP_MASK, tip_type, selected_samples)`_
 - `dropTips(TIP_MASK)`_
 - `go_first_pos(first_tip)`_
 - `check_reagents_levels()`_
 - `check_reagent_level(reagent, LiqClass)`_

Advanced functions.
^^^^^^^^^^^^^^^^^^

Are you doing some advanced protocol development that cannot be efficiently or clearly expressed using the previous [High level functions](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#high-level-functions)? Then, you may use the following functions. Keep in mind that it is now your responsibility to know what robot/protocol "state" are ignored by these new functions. For example, before `aspirate` you will need to mount "by yourself" the tips in the correct position of the used arm, because `aspirate` ignores the higher level [`with tips`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#with-protocoltipstip_type). But don't worry, **`RobotEvo`** still keeps track of the ("internal") robot state and will throw errors informing you about most logical mistakes (like in the previous example forgetting to mount the tips). In some cases these functions may be used to construct new high lever functions.

Atomic functions
-----------------------------------------------------------
These are functions aimed to isolate what a physical robot would make at once: pick some tips, aspirate some liquid, etc. They are simple to understand, but are harder to use in "every day" protocol programming. They may be a great tool to set up your robot and to get an initial familiarization with all the system. 
- `pick_up_tip(tips, tip_type, arm)`
- `drop_tip(tips, arm)`
- `aspirate(arm, tips, volume, from_wells)`
- `dispense(arm, tips, volume, to_wells)`

Other low level functions:
--------------------------
- `_dispensemultiwells(tips, labware)`
- `_aspirate_multi_tips(reagent, tips, vol)`
- `_multidispense_in_replicas(reagent, [vol])`

------------------------
Protocol steps
==============


.. automodule:: protocol_steps
   :members:
   :show-inheritance:

