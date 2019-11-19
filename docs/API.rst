API
=====

The final goal of RobotEvo is to help you to translate your normal laboratory protocol into an script executable
by a robot. Thus, the `class Protocol` offers the base to all the custom protocol classes you will write.
You will probably derived from `Protocol` one more intermediary protocol class that will define a few characteristic
specific to the concrete robot you are using, probably setting some "sensible defaults" in the constructor of that
"robot-specific protocol class".

Now, in a concrete protocol derived from that intermediary class, you will define concrete arguments in the constructor,
and re-implement the `run()` function. Particularly, you may pass to the constructor the path to the description
of the worktable you want to use (this may be an evoware worktable template file or just a working script file).

Normally, by running `run()` the worktable file is parsed and numerous `Labware` objects are created in association
with that ´Worktable´. In this function you will then create the `Reagent`s you want to manipulate, and also may
`get_labware(label)` - where `label` is the unique name given to some object (tip rack, microplate, etc.)
in the worktable defined in evoware. `Reagent`s and `Labware` objects give you access to individual `Wells`,
which are the basic containers of liquid (or `Reagent`s) and which, in some circumstances, can be manipulated too.
(todo: edit laware's names directly from RobotEvo). After some of those objects are created you can begin
to perform the actions that the  API `protocol steps` offers.

How exactly the robot arms pipette (speed, liquid level detection, wet-free, etc.) is defined by liquid classes.
The liquid classes are managed internally in an evoware data bank associate with each concrete/physical robot
and exposed to the script only by name. One name in one robot may mean something different in another robot
or may not be defined at all. Consequently, in  RobotEvo the Liquid classes are set by name. The name have to be exactly
copied from evoware.
Use or create a named liquid class in evoware with all the characteristic you need. Them transfer the name to RobotEvo.
Create and transfer to RobotEvo as many Liquid classes as you need.

.. automodule:: protocol_steps
   :members:
   :show-inheritance:


.. automodule:: reagent
   :members:
   :show-inheritance:


.. automodule:: labware
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: evo_mode
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: robot
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: GUI
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: instructions
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: instructions_Te_MagS
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: instructions_Base
   :members:
   :undoc-members:
   :show-inheritance:

Examples:
=========

.. automodule:: ../protocols/demos/hello_world/hello_world.py
   :members:
   :undoc-members:
   :show-inheritance:


.. automodule:: ../protocols/demos/demo_two_mixes/demo_two_mixes
   :members:
   :undoc-members:
   :show-inheritance:
