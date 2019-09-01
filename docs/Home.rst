
Why RobotEvo? Programming automation of RNA extraction
========================================

(adapted from my `PhD Thesis: RNA virus detection and identification using techniques based on DNA hybridization <https://epub.ub.uni-greifswald.de/frontdoor/index/index/docId/2175>`_)

Usually, prior to proceed to the application of the DNA-hybridization-based technique,
like RT-qPCR, the viral RNA need to be extracted. We used well established methods and
commercially available kits based on columns (RNeasy Mini Kit or QIAamp Viral RNA Mini Kit,
QIAGEN, Hilden, Germany) or magnetized particles
(`NucleoMag® VET kit <http://www.mn-net.com/tabid/12376/default.aspx>`_) from MACHEREY-NAGEL,
Durel, Germany) to achieve the separation, either automatically, using pipetting robots,
or manually.

Especially useful was the combination of magnetized particles with a Freedom EVO universal
pipetting robot from TECAN, Mannerdorf, Switzerland. 

Using the provided software
(`Freedom EVOware <http://lifesciences.tecan.com/products/software/freedom_evoware>`_)
it was comfortable to write simple and specific pipetting protocols in a semi visual way.
Unfortunately, writing more complex or flexible protocols (for example to
accommodate arbitrary number of samples or minor modifications of the protocols)
was very time consuming and error prone. You are compeled to use variables and program-control-flow
structures like IF and LOOP. But you will find that there is a poor or no support of
variables of different types, arrays, structural-programing and objects within
the provided scripting language. 

More important, the powerfull validation and visualization tools
provided by the script editor are full sopprted only in relativelly lineal and simple scripts, considering only the "default" values of the variables, and thus, the default flow-path of the program, not detecting problems in the alternative paths, likely to be found in most runs.


To overcome these limitations and afford automation, a new software was written in
Python, “`RobotEvo <https://github.com/qPCR4vir/robotevo>`_”, which generates the
scripts for the robot.  This new Python library provide new layers of abstraction
to offer a higher level programing model to allow a more direct programing of the
steps needed in a typical biochemical/biological pipetting protocol like RNA
extraction.  The layers of the implementation are: a parser and a generator
(module :file: ˋinstructions.pyˋ of the “low-level” instruction set directly usable by the provided
Freedom EVOware software; a set of “modes” to provide the desired kind of output (human readable
comments, separated instructions, EVOware scripts, etc., in module
:file: ˋevo_mode.pyˋ_; a model of the state of the robot to detect possible errors prior to
the generation of the script by tracking what volume of what mix of
reagents contains at each moment each reservoir or tip (module
[Robot](https://github.com/qPCR4vir/robotevo/blob/master/EvoScriPy/Robot.py) –
this is a **_novel_** functionality impossible to achieve with the original
software); low level pipetting instructions (like aspirate a specific liquid
volume from a given vial into a tip); a higher level command set (like distribute
some reagent into each sample, in module
[protocol steps](https://github.com/qPCR4vir/robotevo/blob/master/EvoScriPy/protocol_steps.py))
to directly program high-level, more realistic protocol scripts including a
base template for a full protocol; and, finally, a set of facilities to declare
the reagents (module Reagent) and the labwares (like reaction tubes, racks of
tubes, racks of tips, cuvettes, etc. in module
[Labware](https://github.com/qPCR4vir/robotevo/blob/master/EvoScriPy/Labware.py)).

For the protocol for RNA extraction (module RNAextractionMN_Mag_Vet) the set
of used labwares and reagents are declared first. Immediately an automatically
generated check-list is presented to the human operator (a graphic user interface –
from module GUI). After a possible adjustment of the predefined parameters (without
any programming) the program go through a few high-level-defined protocol steps of
distributeing buffers, mixing, washing, incubating, etc. generating a very detailed set
of low-level instructions for the physical robot in a script to be imported and
visualized in the TECAN Freedom EVOware software. The obtained script is very long
but structurally very simple and well commented, which facilitates the visual
control of each instruction prior to real pipetting.

![Modules](https://github.com/qPCR4vir/robotevo/blob/master/docs/modules.jpg)
