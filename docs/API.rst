The final goal of RobotEvo is to help you to translate your normal laboratory protocol into an script executable by a robot. Thus, the `class Protocol` offers the base to all the custom protocol classes you will write. You will probably derived from `Protocol` one more intermediary protocol class that will define a few characteristic specific to the concrete robot you are using, probably setting some "sensible defaults" in the constructor of that "robot-specific protocol class". 

Now, in a concrete protocol derived from that intermediary class, you will define concrete arguments in the constructor, and re-implement the `Run()` function. Particularly, you may pass to the constructor the path to the description of the worktable you want to use (this may be an evoware worktable template file or just a working script file). 

Normally, by running `Run()` the worktable file is parsed and numerous `Labware` objects are created in association with that ´Worktable´. In this function you will then create the `Reagent`s you want to manipulate, and also may  `get_labware(label)` - where `label` is the unique name given to some object (tip rack, microplate, etc.) in the worktable defined in evoware. `Reagent`s and `Labware` objects give you access to individual `Wells`, which are the basic containers of liquid (or `Reagent`s) and which, in some circumstances, can be manipulated too. (todo: edit laware's names directly from RobotEvo). After some of those objects are created you can begin to perform the actions that the  API `protocol steps` offers.

How exactly the robot arms pipette (speed, liquid level detection, wet-free, etc.) is defined by liquid classes. The liquid classes are managed internally in an evoware data bank associate with each concrete/physical robot and exposed to the script only by name. One name in one robot may mean something different in another robot or may not be defined at all.
Consequently, In  RobotEvo the Liquid classes are set by name. The name have to be exactly copied from evoware. Use or create a named liquid class in evoware with all the characteristic you need. Them transfer the name to RobotEvo. Create and transfer to RobotEvo as many Liquid classes as you need. 

:doc: ˋReagents <reagents>ˋ
============================
A `Reagent` is a fundamental concept in RobotEvo programming. It makes possible to define a protocol in a natural way, matching what a normal laboratory's protocol indicates.
Defines a named homogeneous liquid solution, the wells it occupy, the initial amount needed to run the protocol (auto calculated), and how much is needed per sample, if applicable. It is also used to define samples, intermediate reactions and products. It makes possible a robust tracking of all actions and a logical error detection, while significantly simplifying the  programming of non trivial protocols.
 - Reagent
 - preMix


[Worktable and labwares]
============================================
 - Worktable
 - Worktable.Location
 - Labware.Type
   + Specialized types:
     + DiTiRackType
     + CuvetteType 
 - Labware.Type.Series
 - Labware
   + Specialized labwares:
     + DitiRack
     + Cuvette

[Principal API: Protocol steps]
==============================================
All these functions are member of the base `class Protocol`, from which all user protocols are derived.


[High level functions]
^^^^^^^^^^^^^^^^^^^^^^
These are the functions you will use in "every day" protocol programming. They allow you to specify the kind of tips to use and them command the operations you need on your reagents, samples, reactions, etc., almost directly as it states in the steps of your "hand written" original laboratory protocol.

[Low level functions:]
^^^^^^^^^^^^^^^^^^^^^^

Advanced functions.
---------------------

Are you doing some advanced protocol development that cannot be efficiently or clearly expressed using the previous [High level functions](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#high-level-functions)? Then, you may use the following functions. Keep in mind that it is now your responsibility to know what robot/protocol "state" are ignored by these new functions. For example, before `aspirate` you will need to mount "by yourself" the tips in the correct position of the used arm, because `aspirate` ignores the higher level [`with tips`](https://github.com/qPCR4vir/robotevo/wiki/Protocol-steps-(principal-API)#with-protocoltipstip_type). But don't worry, **`RobotEvo`** still keeps track of the ("internal") robot state and will throw errors informing you about most logical mistakes (like in the previous example forgetting to mount the tips). In some cases these functions may be used to construct new high lever functions.


[Atomic functions]
____________________________
These are functions aimed to isolate what a physical robot would make at once: pick some tips, aspirate some liquid, etc. They are simple to understand, but are harder to use in "every day" protocol programming. They may be a great tool to set up your robot and to get an initial familiarization with all the system. 

[Other low level functions:]
----------------------------
