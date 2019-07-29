RobotEvo generates human readable protocols and  Freedom EVOware scripts for the Freedom EVO universal pipetting robot from TECAN. It provides new layers of abstraction to offer a higher level programing model that allows a more direct programing of the steps needed in a typical biochemical/biological pipetting protocol like RNA extraction. More in the [Wiki](https://github.com/qPCR4vir/robotevo/wiki)

RobotEvo simplify the programming of a liquid-handling robot for laboratory automation, for example an RNA extraction protocol.

Code organization - here are some directories / files you will encounter in this repository:


 - `RobotEvo` is this whole Python library to model a Tecan Evo Robot (The Freedom EVO 75 or 100 for example)

 - `EvoScriPy` is the python "API" that users can use to program the protocols.

 - `protocols` are already programed protocols (python scripts writen by RobotEvo 'users', using the EvoScriPy API).

 - `RNAextractionMN_Mag_Vet` is a protocol for RNA extraction using the [NucleoMag® VET kit](http://www.mn-net.com/tabid/12376/default.aspx) from MACHEREY-NAGEL.

 - `EvoScripts` TECAN Evoware templates and scripts. Includes our old, "manually" generated TECAN Evoware scripts for RNA extraction.

 - `current` are the final evoware protocols scripts and englisch-commented protocols sintetized by running the RobotEvo python scripts user protocols.

---------------------------------------------------------------------------------------------
How to use:
- RobotEvo is a simple and standard Python sofware. Donwload or clone: https://github.com/qPCR4vir/robotevo. 
  Make sure you have a working python3 installed.
- Just run the protocol scrpit you need (make sure the correct arguments are used). 
  Alternatively run `RobotEvo\EvoScriPy\GUI.py` to run a GUI (which uses `tkinter`) 
  that will allow you to chosee from existing and registered in your copy of RobotEvo protocols. 
  Modify the protocols parameters as needed and synthesize the robot scripts. 
  Import this script into the original robot-software to first review and then run it.
- Write new protocols by deriving from `class Protocol` and implementing the function `Run` mostly using the higher-level functions from `protocol_steps.py`, but also low level functions from `instructions.py`.


------------

Please cite:
Viña Rodríguez, A. (2018). "_RNA virus detection and identification using techniques based on DNA hybridization_".[Doctoral Thesis](https://epub.ub.uni-greifswald.de/frontdoor/index/index/docId/2175). Ernst-Moritz-Arndt-Universität, Mathematisch-Naturwissenschaftliche Fakultät

**Copyright (C)** 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
Distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
Author Ariel Vina-Rodriguez (qPCR4vir)
 The scripts writen by users of RobotEvo to implement especific protocols (derived from `class Protocol`, and specially, overwriting the function `Run`), and the generated files produced by runing those "user-protocols" may containg confidential information, are considered "user data", are not subjected to the RobootEvo copy-right and licensing and are expected to be keep privately.
 Users that decide to public here user-protocols (for example if they are planing to publish it in a scientific journal) agree to accept distribution under the RobotEvo licensing.
 
---------
**Code style**: the main goal is to make the code as readable as possible **to humans** (not to tools). 

Good names are the first priority. 
You may help to choose better names in many cases (English is not our first language). 

Python is well known for the fact that it is probably the only popular general programming 
language that enforce by "law" readability through vertical formatting. We continue that idea, 
and use vertical formatting wherever it improve readability, 
particularly in definitions and calls of functions with many arguments, `if` with many conditions and 
series of assignments. 

We will adhere to the PEP8 rules of code style when it does not significantly dismantle 
readability by preventing vertical formatting. The lines are 130 character length, 
which is optimal for reading two scripts in parallel in a HD monitor (landscape) or one long portrait.