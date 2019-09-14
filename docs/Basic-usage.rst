- How to run an existing protocol?
- How does it works?
- A Hello World! example.
- How to modify an existing protocol?
- Now to write a new protocol?


How to run an existing protocol?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure you have a working python3 interprete in your device (PC, tablet, smartphone, etc.) and a copy of RobotEvo (downloaded or cloned from GitHub).

Now, the simplest way is to run the python script containing the protocol, providing it have a "main" function.

For better control, in a your onw python script, import the desired protocol and just create an instance (python object) of the protocol, 
possibly setting some of the constructor parameters, and call the `.run()` method of that object.
You can see many examples of this usage in the script robotevo/protocols/test.py 
This will create a set of files with the generated evoware scripts, a human readable protocol, and comments, possibly including warnings. 
It may abort with more or less detailed messages about the errors.

Alternatively run `GUI.py` (only in devices with a functioning standard python module "tkinter") to select the protocol, 
the desired protocol "variant" and change some other minor parameters like number of samples or required reagents volume.

To make the actual pippeting in the real robot, open the generated `.esc` script in the EVOware editor. 
It will alert you that the check sum have not been set, which in this case just flags the fact that this is a newly generated script you have not run yet. 
Accept to load it in the EVOware script editor. Here you will have very good assistance to visualize 
the details of each step and to do a normal, full TECAN validation of the correctness of the script. 

Use the visual worktable map to correctly setup the labware. Use the detailed comments automatically 
inserted by RobotEvo in the script or the associated `.protocol.txt` file to fill the expected initial volume of each reagent.

Use EVOware to run the script as usually.

## How does it works?
Already the creation of the protocol object will run some "boilerplate" code to setup things we need to run the useful part of our protocol. 

For example it will parse the provided worktable template file (a `.ewt` or just a compatible `.esc` evoware file) 
and will remember (in a sort of `map`) all the labware present in the worktable, including its unique name, type and location.

It will also initialize some other characteristics of the used robot (not present in the worktable file) like number of tips in the LiHa, etc. 

Additionally it will set the desired EvoMode: what kind of output we want to produce - normally an evoware script (his generated script will include again all the information for the worktable), 
but also a human readable protocol, etc.

By running `.run()` we "create" or "get", from the parsed worktable file, labwares, like multiplates,
tube racks, etc, and "create" the reagents defined there in the script, including location in the worktable, volume, etc. 
This make possible for the "internal iRobot" to model or track the content of each well, 
and to detect (and report) potential logical errors in the protocol.

If at this point the protocol include a call to `.cehcklist()` instructions will be generated to inform to the human robot-operator **at run time**, the positions and initial quantity of all reagents he need to make sure are in place. If a GUI is in use and was previosly created 
a new sub-GUI will be automatically generated to show all the details of the defined reagents 
making possible to change some properties without modifying programmatically the protocol. 

A typical protocol will use the high level instructions inherited from `protocol_steps`, 
like `transfer`, `distribute`, `with tips`, etc., to express the "physical" protocol. 
This instructions are in turn internally implemented using lower level instructions like `aspirate`, 
`get tips`. etc. 
Each of this low level intructions will interact with the selected EvoMode to generate the corresponding instructions 
in the EVOware script and to check errors and change the state of the internally modeled `iRobot`, 
including the liquid volume in each well and tip and many other details.

## A Hello World! example.
Let create the classical, in the the world of programming, Hello World! example. 
It will just shows that message in the screen of the PC controlling the robot and will wait for user confirmation producing a typical sound.

By running the script:

    from EvoScriPy.protocol_steps import Protocol
    import EvoScriPy.Instructions as Itr

    class HelloWorld(Protocol):

        name = "Hello World"

        def __init__(self, GUI = None):
            Protocol.__init__(self,
                              GUI                           = GUI,
                              output_filename               = '../current/tests/hello_world',
                              worktable_template_filename   = '../EvoScripts/wt_templates/Prefill_VEW1_ElutB_and_VEW2.ewt')  # set here a valid template

        def run(self):
            self.check_list()
            Itr.userPrompt("Hello World!").exec()     # the actual work.
            self.done()


    if __name__ == "__main__":
        HelloWorld().run()

[IMPORTANT: replace the `worktable_template_filename` argument with a valid -for your very onw robot- worktable template (`.ewt`) or script (`.esc`).]

we will have some files (currently 4) generated with names following the pattern of the `output_filename` constructor argument: in particular '../current/tests/hello_world.esc' will contain a new evoware script you can load into the Freedom evoware editor. After you agree to use the script with an still unvalidated check-summe you will see it just contain an instruction for a simple user promt. By using evoware to run this script you will get:
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/HelloW.png)

How to modify an existing protocol?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now to write a new protocol?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 
    from   EvoScriPy.protocol_steps import *
    import EvoScriPy.Instructions   as     Itr
    import EvoScriPy.Labware        as     Lab
    import EvoScriPy.Reagent        as     Rtv
    
    from protocols.Evo200 import Evo200
    
    
    class Prefill_plate_in_Evo200(Evo200):
        """
        Prefill one plate with Buffer.
        """
    
        name = "Prefill one plate with Buffer."
        min_s, max_s = 1, 96/6
    
        # for now just ignore the variants
        def def_versions(self):
            self.versions = {'No version': self.V_def               }
    
        def V_def(self):
            pass
    
        def __init__(self,
                     GUI                         = None,
                     NumOfSamples: int           = None,
                     worktable_template_filename = None,
                     output_filename             = None,
                     firstTip                    = None,
                     run_name: str               = ""):
    
            Evo200.__init__(self,
                            GUI                         = GUI,
                            NumOfSamples                = NumOfSamples or Prefill_plate_in_Evo200.max_s,
                            worktable_template_filename = worktable_template_filename or
                                                          '../EvoScripts/wt_templates/demo-two.mixes.Evo200example.ewt',
                            output_filename             = output_filename or '../current/two.mixes',
                            firstTip                    = firstTip,
                            run_name                    = run_name)
    
        def run(self):
            self.initialize()    # if needed calls Executable.initialize() and set_EvoMode
                                 # which calls GUI.update_parameters() and set_defaults() from Evo200
    
            self.check_initial_liquid_level = True
            self.show_runtime_check_list    = True
    
            NumOfSamples = self.NumOfSamples
            assert 1 <= NumOfSamples <= 96/6 , "In this demo we want to set 6x NumOfSamples in a 96 well plate."
            wt           = self.worktable
    
            Itr.comment('Prefill a plate with some dilutions of two master mix and Buffer Reagent for {:d} samples.'\
                           .format(NumOfSamples     )).exec()
    
                                                                # Get Labwares (Cuvette, eppys, etc.) from the work table
            BufCuvette   = wt.getLabware(Lab.Trough_100ml, "BufferCub")
            master_mixes_= wt.getLabware(Lab.Eppendorfrack,    "mixes")
    
    
            self.go_first_pos()                                                     #  Set the initial position of the tips
    
                                                                                      # Set volumen / sample
            all_samples = range(NumOfSamples)
            maxTips     = min  (self.n_tips, NumOfSamples)
            maxMask     = Rbt.tipsMask[maxTips]
    
            buf_per_sample =0
            well_v = 100
    
            dil_mix1_10 = well_v /10                # to be distribute from original mix1 to mix1_10
            buf_mix1_10 = well_v - dil_mix1_10
            buf_per_sample += buf_mix1_10
    
            dil_mix2_10 = well_v / 10               # to be distribute from original mix2 to mix2_10
            buf_mix2_10 = well_v - dil_mix2_10
            buf_per_sample += buf_mix2_10
    
            dil_mix1_100 = well_v / 10              # to be transfered from mix1_10 to mix1_100
            buf_mix1_100 = well_v - dil_mix1_100
            buf_per_sample += buf_mix1_100
    
            dil_mix2_100 = well_v / 10              # to be transfered from mix2_10 to mix2_100
            buf_mix2_100 = well_v - dil_mix2_100
            buf_per_sample += buf_mix2_100
    
    
            # Define the reagents in each labware (Cuvette, eppys, etc.)
    
            buffer_reag = Rtv.Reagent("Buffer ",
                                      BufCuvette,
                                      volpersample = buf_per_sample,
                                      # def_liq_class  = 'MN VL',
                                      # num_of_samples= NumOfSamples
                                      )
    
            mix1 =Rtv.Reagent("mix1",
                              master_mixes_,
                              volpersample = dil_mix1_10,
                              # def_liq_class  = 'MN VL'
                              )
    
            mix2 = Rtv.Reagent("mix2",
                               master_mixes_,
                               volpersample  = dil_mix2_10,
                               # def_liq_class  = 'MN VL'
                               )
    
            # Show the check_list GUI to the user for possible small changes
    
            self.check_list()
    
            Itr.wash_tips(wasteVol=5, FastWash=True).exec()
    
            Plat1 = wt.getLabware(Lab.MP96MachereyNagel, "plate1")
            Plat2 = wt.getLabware(Lab.MP96well,          "plate2")
    
            # Define place for temporal reactions
            mix1_10 = Rtv.Reagent(f"mix1, diluted 1:10",
                            Plat1,
                            initial_vol = 0.0,
                            replicas    = NumOfSamples,
                            excess      = 0)
    
            mix2_10 = Rtv.Reagent(f"mix2, diluted 1:10",
                            Plat1,
                            initial_vol = 0.0,
                            replicas    = NumOfSamples,
                            excess      = 0)
    
            mix1_100 = Rtv.Reagent(f"mix1, diluted 1:100",
                                  Plat2,
                                  initial_vol=0.0,
                                  replicas=NumOfSamples,
                                  excess=0)
    
            mix2_100 = Rtv.Reagent(f"mix2, diluted 1:100",
                                  Plat2,
                                  initial_vol=0.0,
                                  replicas=NumOfSamples,
                                  excess=0)
    
            loc = Plat2.location               # just showing how to move the plate from one site to the next in the carrier
            loc.site -= 1
            car = Lab.Carrier(Lab.Carrier.Type("MP 3Pos", nSite=3), loc.grid, label = "MP 3Pos")
            loc.rack = car
            Itr.transfer_rack(Plat2, loc ).exec()                                              # just showing how RoMa works.
    
            with group("Fill plate with mixes "):
    
                Itr.userPrompt("Put the plates for Buffer ").exec()
    
                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent           = mix1,
                                to_labware_region = mix1_10.select_all())
    
                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent           = mix2,
                                to_labware_region = mix2_10.select_all())
    
                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=buffer_reag, to_labware_region=mix1_10.select_all(), volume=buf_mix1_10)
                    self.distribute(reagent=buffer_reag, to_labware_region=mix2_10.select_all(), volume=buf_mix2_10)
    
                with self.tips(reuse=True, drop=False):
                    self.transfer(from_labware_region = mix1_10.select_all(),
                                  to_labware_region   = mix1_100.select_all(),
                                  volume              = dil_mix1_100)
    
                with self.tips(reuse=True, drop=False):
                    self.transfer(from_labware_region = mix2_10.select_all(),
                                  to_labware_region   = mix2_100.select_all(),
                                  volume              = dil_mix2_100)
    
                with self.tips(reuse=True, drop=False):
                    self.distribute(reagent=buffer_reag, to_labware_region=mix1_100.select_all(), volume=buf_mix1_100)
                    self.distribute(reagent=buffer_reag, to_labware_region=mix2_100.select_all(), volume=buf_mix2_100)
    
                self.dropTips()
    
            self.done()
    
    
    if __name__ == "__main__":
        p = Prefill_plate_in_Evo200(NumOfSamples    = 4,
                                    run_name        = "_4s_mix_1_2")
        p.use_version('No version')
        p.run()

we will have:
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-1.png)
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-2.png)
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-3.png)
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-4.png)
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-5.png)
![](https://github.com/qPCR4vir/robotevo/blob/master/docs/demo2mix-list-6.png)