# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019

__author__ = 'qPCR4vir'

"""
Implement a GUI that automatically detect available protocols.
"""

import tkinter
from tkinter.filedialog import askopenfilename

from protocols import available



GUI4parameters = {}  # map { 'protocol class name' : GUI_init_parameters class to use }
av_prot_names = []   # list of "protocol names+: + run names" with the same index as available executables


class App(tkinter.Frame):
    """ GUI orgaization:

     app = App(master = tkinter.Tk()), - tkinter.Frame.__init__(self, master). :  new window
         - Logo,
         - DropBox (OptionMenu) protocol_selection -> protocol_selected(self, value): for the selected create:

     GUI_protocol(protocol), - tkinter.Frame.__init__(self, tkinter.Tk()) :  new window
         - protocol.GUI = self: this is the GUI protocols refer.
         - OptionMenu Versions ->
         - Buttons: run: "Initialize protocol" -> command=self.run_selected,
                    quit:"Synthetize script"   -> command=self.quit
         - Listbox Comments
         - self.GUI_init       = GUI4parameters[protocol.name](protocol):
                                 populate and update GUI_parameters to check protocol initialization parameters
         - self.GUI_parameters = tkinter.Frame(self): (between Versions and buttons), for file IO, #samples, first tip, ect.
         - self.GUI_CheckList  = tkinter.Frame(self): Headers, reagent_frames, ReplicaFrame   . self.master.mainloop()
         - self.mainloop()

     GUI_init (and derived GUI_init_parameters, GUI_init_pipeline):
         populate and update GUI_parameters to check protocol initialization parameters

         GUI_init_parameters:
         - WorkTable and Output file, First tip
         GUI_init_RNAext_parameters: add NumOfSamples

         GUI_init_pipeline:
         - self.ProtcolFrames = list of ProtocolFrame(prot)
         - ProtocolFrame(tkinter.Frame) - tkinter.Frame.__init__(self, prot.pipeline.GUI.GUI_CheckList)
         - Label protocol.name: entry run_name
         - Button run:  run.mainloop() ->  run_prot: App.GUI_protocol(self.protocol) in a new window

    """
    # See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html


    # GUI classes to handle initialization parameters of protocol objects
    class GUI_init_pipeline:
        """  Show the parameters of the pipeline for review: a list of the protocols to run with run names

        """

        class ProtocolFrame(tkinter.Frame):

            def __init__(self, prot):
                self.protocol = prot
                if prot.run_name is None: prot.run_name = ""
                print ('protocol: ' + prot.name)
                tkinter.Frame.__init__(self, prot.pipeline.GUI.GUI_CheckList)
                self.grid(sticky=tkinter.N + tkinter.S and tkinter.E)

                self.protocol_label = tkinter.Label(self, text=self.protocol.name)
                self.protocol_label.grid(row=0, column=0, sticky=tkinter.W + tkinter.E)

                self.ProtName = tkinter.StringVar(self)
                self.ProtName.set(prot.run_name)
                self.RackNameEntry = tkinter.Entry(self, textvariable=self.ProtName)
                self.RackNameEntry.grid(row=0, column=1, sticky=tkinter.W)

            def Run(self):
                self.runb = tkinter.Button(self,  # state=tkinter.DISABLED,
                                           text='Run', command=self.run_prot)
                self.runb.grid( row=0, column=2)
                # self.runb.configure(state='normal')
                self.runb.mainloop()

            def run_prot(self):
                self.runb.configure(state='disable')
                self.protocol.run_name = self.ProtName.get()
                print('For pipeline Run GUI for protocol: '  + self.protocol.name +' run-named '+ self.protocol.run_name)
                App.GUI_protocol(self.protocol)

        def __init__(self, pipeline):
            self.pipeline = pipeline   # todo ??
            print('run GUI_init_pipeline for: ')
            self.ProtcolFrames = [App.GUI_init_pipeline.ProtocolFrame(prot) for prot in pipeline.protocols]

        def update_parameters(self):
            pass    # ??

    from EvoScriPy.protocol_steps import Pipeline
    GUI4parameters[Pipeline.name]=GUI_init_pipeline


    class GUI_init_parameters: # (uses the tkinter.Frame protocol.GUI.GUI_parameters)

        def __init__(self, protocol):
            self.protocol = protocol

            # worktable_template_filename
            tkinter.Label(self.protocol.GUI.GUI_parameters, text='WorkTable:').grid(row=0, column=0, columnspan=1,
                                                                                          sticky=tkinter.N + tkinter.W)
            self.worktable_filename_v = tkinter.StringVar(self.protocol.GUI.GUI_parameters)
            self.worktable_filename_v.set(protocol.worktable_template_filename)
            tkinter.Entry(self.protocol.GUI.GUI_parameters, textvariable=self.worktable_filename_v).grid(row=0, column=1, columnspan=9,
                                                                                                               sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.protocol.GUI.GUI_parameters, text='...', command=self.selet_WT_FN).grid(row=0, column=10)
            self.worktable_filename_v.trace("w", self.set_WT_FN)

            # output_filename
            tkinter.Label(self.protocol.GUI.GUI_parameters, text='Output filename:').grid(row=1, column=0, columnspan=1,
                                                                                                sticky=tkinter.N + tkinter.W)
            self.output_filename_v = tkinter.StringVar(self.protocol.GUI.GUI_parameters)
            self.output_filename_v.set(protocol.output_filename)
            self.output_filename_Entry = tkinter.Entry(self.protocol.GUI.GUI_parameters, textvariable=self.output_filename_v).grid(row=1,
                                                                                                            column=1,
                                                                                                            columnspan=9,
                                                                                                            sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.protocol.GUI.GUI_parameters, text='...', command=self.selet_O_FN).grid(row=1,
                                                                                                             column=10)
            self.output_filename_v.trace("w", self.set_O_FN)

            # First tip (in the first tip rack)
            tkinter.Label(self.protocol.GUI.GUI_parameters, text='First tip:').grid(row=2, column=0, columnspan=1,
                                                                                          sticky=tkinter.N + tkinter.W)
            self.firstTip_v = tkinter.StringVar(self.protocol.GUI.GUI_parameters)
            self.firstTip_v.set(protocol.firstTip)
            tkinter.Entry(self.protocol.GUI.GUI_parameters, textvariable=self.firstTip_v).grid(row=2, column=1, columnspan=1,
                                                                                                     sticky=tkinter.N + tkinter.E + tkinter.W)
            self.firstTip_v.trace("w", self.set_firstTip)

        def set_firstTip(self, *args):
            self.protocol.firstTip = self.firstTip_v.get()

        def set_WT_FN(self, *args):
            self.protocol.worktable_template_filename = self.worktable_filename_v.get()

        def selet_WT_FN(self):
            self.worktable_filename_v.set( tkinter.filedialog.askopenfilename(title='Select the WorkTable template') )

        def set_O_FN(self, *args):
            self.protocol.output_filename = self.output_filename_v.get()

        def change_O_FN(self, new_O_FN):
            print("\nChanging prot name from: " + self.output_filename_v.get())
            self.output_filename_v.set(new_O_FN)
            print("\nto                     : " + self.output_filename_v.get())

        def selet_O_FN(self):
            self.output_filename_v.set( tkinter.filedialog.asksaveasfilename(title='Select the output filename') )

        def update_parameters(self):
            self.set_firstTip()
            self.set_WT_FN()
            self.set_O_FN()

    from EvoScriPy.protocol_steps import Protocol
    GUI4parameters[Protocol.name]=GUI_init_parameters


    class GUI_init_RNAext_parameters(GUI_init_parameters):


        def __init__(self, protocol):
            App.GUI_init_parameters.__init__(self, protocol)

            # Number of Samples
            label = "Number of Samples: ({}-{}) ".format(protocol.min_s, protocol.max_s)
            tkinter.Label(self.protocol.GUI.GUI_parameters, text=label).grid(row=2, column=3, columnspan=2,
                                                                                   sticky=tkinter.N + tkinter.W)

            self.NumOfSamples = tkinter.IntVar(self.protocol.GUI.GUI_parameters)
            self.NumOfSamples.set(self.protocol.NumOfSamples)
            self.sample_num = tkinter.Spinbox(self.protocol.GUI.GUI_parameters, textvariable=self.NumOfSamples,
                                              from_=protocol.min_s, to=protocol.max_s, increment=1,
                                              command=self.read_NumOfSamples)
            self.sample_num.grid(row=2, column=5, columnspan=1)


        def read_NumOfSamples(self, *args):
            self.protocol.NumOfSamples = self.NumOfSamples.get()
            print(" --- NumOfSamples set to: %d" % (self.protocol.NumOfSamples))

        def update_parameters(self):
            App.GUI_init_parameters.update_parameters(self)
            self.read_NumOfSamples()

    from protocols.Prefill_plate_in_Evo200 import Prefill_plate_in_Evo200
    GUI4parameters[Prefill_plate_in_Evo200.name] = GUI_init_RNAext_parameters

    from protocols.RNAextractionMN_Mag_Vet import RNAextr_MN_Vet_Kit
    GUI4parameters[RNAextr_MN_Vet_Kit.name]=GUI_init_RNAext_parameters

    from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p      import PreKingFisher_RNAextNucleoMag_EtOH80p
    GUI4parameters[PreKingFisher_RNAextNucleoMag_EtOH80p.name]=GUI_init_RNAext_parameters

    from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
    GUI4parameters[Prefill_plates_VEW1_ElutionBuffer_VEW2.name]=GUI_init_RNAext_parameters

    from protocols.Prefill_plates_LysisBuffer import Prefill_plates_LysisBuffer
    GUI4parameters[Prefill_plates_LysisBuffer.name]=GUI_init_RNAext_parameters

    from protocols.Prefill_plates_LysisBuffer_and_ProtKpreMix import Prefill_plates_LysisBuffer_and_ProtKpreMix
    GUI4parameters[Prefill_plates_LysisBuffer_and_ProtKpreMix.name]=GUI_init_RNAext_parameters


    class GUI_protocol(tkinter.Frame):
        """ Implements a GUI for the selected protocol. Each protocol receive a reference to it in .GUI
            Opens in a new window. Has:
            - GUI_init, to review creation parameters,
            - GUI_parameters for CheckList prior to actually running the protocol,
            - Comments that shows the run.

            Alternatively, for Pipelines shows the list of protocols for sequential running
            """

        def __init__(self, protocol):
            self.protocol = protocol
            self.output_filename = protocol.output_filename
            protocol.GUI = self

            tkinter.Frame.__init__(self, tkinter.Tk())
            self.master.title(protocol.name)
            self.grid()

            self.selected_version_StrVar = tkinter.StringVar(self )                # variable  ? command=lambda v=self: v.setVariant(l)
            self.selected_version_StrVar.set(next(iter(self.protocol.versions)))  # variable def value

            self.version_selection_Menu = tkinter.OptionMenu(self, self.selected_version_StrVar, *self.protocol.versions)
            self.version_selection_Menu.grid(row=1, column=0, rowspan=1, columnspan=4, sticky=tkinter.W + tkinter.E)

            # initialize parameters
            self.GUI_parameters = tkinter.Frame(self)
            self.GUI_parameters.grid(row=0, column=4, columnspan=11, rowspan=3)

            # run / quit_bt     ---------------------
            self.run = tkinter.Button(self, text="Initialize the selected protocol",
                                      command=self.run_selected)
            self.run.grid(row=0, column=15, columnspan=2)

            self.quit_bt = tkinter.Button(self, text="Synthetize the TECAN script", command=self.quit,
                                          state=tkinter.DISABLED)
            self.quit_bt.grid(row=1, column=15, columnspan=2)

            if isinstance(protocol, App.Pipeline):
                pass
            else:
                # comments: visualize the synthesized script -----------------------
                self.yScroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
                self.yScroll.grid(row=3, column=16,  rowspan=20, sticky=tkinter.N + tkinter.S)
                self.xScroll = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
                self.xScroll.grid(row=23, column=8, columnspan=8, sticky=tkinter.E + tkinter.W)

                self.comments = tkinter.Listbox(self, height=30, width=150,
                                                xscrollcommand=self.xScroll.set,
                                                yscrollcommand=self.yScroll.set)
                self.comments.grid(row=3, column=8, rowspan=20, columnspan=8,
                                   sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)
                self.xScroll['command'] = self.comments.xview
                self.yScroll['command'] = self.comments.yview

            self.GUI_CheckList = tkinter.Frame(self)
            self.GUI_CheckList.grid(row=3, column=0, columnspan=8, rowspan=15)

            # show the Parameters with the corresponding GUI_init_parameter
            self.GUI_init = GUI4parameters[protocol.name](protocol)
            self.mainloop()

        def setVariant(self, variant):
            self.selected_version_StrVar.set(variant)
            self.protocol.output_filename = self.output_filename + "_" + variant
            self.GUI_init.change_O_FN(self.protocol.output_filename)

        def setVariantsMenu(self, value):
            m = self.version_selection_Menu.children['menu']
            m.delete(0, 'end')
            for val in self.protocol.versions:
                m.add_command(label=val, command=lambda v=self, l=val: v.setVariant(l))
            self.setVariant(next(iter(self.protocol.versions)))  # variable def value

        def update_parameters(self):
            self.protocol.version = self.selected_version_StrVar.get()
            self.protocol.versions[self.protocol.version]()
            self.GUI_init.update_parameters()  # ??

        class ReplicaFrame(tkinter.Frame):
            def __init__(self, master, reply, num):
                tkinter.Frame.__init__(self, master)
                self.grid(sticky=tkinter.N + tkinter.S, row=num, column=6, columnspan=3)

                self.reply = reply
                self.num = num
                self.Vol = tkinter.DoubleVar(self)
                self.Vol.set(reply.vol)
                self.Well = tkinter.IntVar(self)
                self.Well.set(reply.offset + 1)

                self.CheckB = tkinter.Checkbutton(self, text="Reply" + str(num + 1), justify=tkinter.LEFT,
                                                  state=tkinter.DISABLED)  # width=15,
                self.CheckB.grid(column=0, row=0, )
                tkinter.Entry(self, textvariable=self.Well, width=2).grid(row=0, column=1)  # , state=tkinter.DISABLED
                tkinter.Spinbox(self,
                                textvariable=self.Vol, state=tkinter.DISABLED,
                                increment=1,
                                from_=0.0,
                                to=100000,
                                width=7).grid(column=2, row=0)

        class ReagentFrame(tkinter.Frame):

            def __init__(self, check_list, reagent):
                tkinter.Frame.__init__(self, check_list.GUI_CheckList)
                self.grid(sticky=tkinter.N + tkinter.S and tkinter.E)
                self.columnconfigure(0, minsize=140)
                self.reagent = reagent
                self.RackName = tkinter.StringVar(self)
                self.RackName.set(reagent.labware.label)
                self.RackGrid = tkinter.IntVar(self)
                self.RackGrid.set(reagent.labware.location.grid)
                self.RackSite = tkinter.IntVar(self)
                self.RackSite.set(reagent.labware.location.site + 1)
                self.check_list = check_list

                tkinter.Label(self, text=reagent.name, justify=tkinter.RIGHT).grid(row=0, column=0, sticky=tkinter.E)

                dis = tkinter.DISABLED if reagent.components else tkinter.NORMAL

                self.Vol = tkinter.DoubleVar(self)
                self.Vol.set(reagent.volpersample)
                tkinter.Spinbox(self,
                                textvariable=self.Vol,  state=dis,     command=self.setVol,
                                increment=1, from_=0.0, to=100000, width=5).grid(row=0, column=1, sticky=tkinter.W)

                self.RackNameEntry = tkinter.Entry(self, state=tkinter.DISABLED,
                                                   textvariable=self.RackName, width=10).grid(row=0, column=2, padx=5,
                                                                                              sticky=tkinter.W)
                self.RackGridEntry = tkinter.Entry(self, state=tkinter.DISABLED,
                                                   textvariable=self.RackGrid, width=2).grid(row=0, column=3, padx=5,
                                                                                             sticky=tkinter.W)
                self.RackSiteEntry = tkinter.Entry(self, state=tkinter.DISABLED,
                                                   textvariable=self.RackSite, width=2).grid(row=0, column=4, padx=5,
                                                                                             sticky=tkinter.W)

                self.ReplicaFrames = [App.GUI_protocol.ReplicaFrame(self, reply, rn) for rn, reply in enumerate(reagent.Replicas)]

            def setVol(self, *args):

                print("changing volumen of '{0}' from {1} to {2}".format(
                    self.reagent.name, self.reagent.volpersample, self.Vol.get()))

                self.reagent.volpersample = self.Vol.get()

                for rf in self.check_list.ReactFrames:  # change possibles mix.
                    for c in rf.react.components:
                        if self.reagent is c:
                            rf.react.init_vol()
                            rf.Vol.set(rf.react.volpersample)

                self.reagent.init_vol()
                for rf in self.ReplicaFrames:  # change replicas
                    rf.Vol.set(rf.reply.vol)

        def CheckList(self):

            self.GUI_init.update_parameters()

            Header=tkinter.Frame(self.GUI_CheckList)
            Header.grid( sticky=tkinter.E)
            Header.columnconfigure(1, minsize=120)
            tkinter.Label (Header, text='Reagent', justify=tkinter.RIGHT).grid(row=0, column=0, sticky=tkinter.E)
            tkinter.Label (Header, text="     µL/sample      ",         ).grid(row=0, column=1 ) # , sticky=tkinter.CENTER
            tkinter.Label (Header, text="Rack   ",                      ).grid(row=0, column=2, sticky=tkinter.E)
            tkinter.Label (Header, text="Grid",                         ).grid(row=0, column=3, sticky=tkinter.E)
            tkinter.Label (Header, text="Site        ",                 ).grid(row=0, column=4, sticky=tkinter.E)
            tkinter.Label (Header, text='          ',                   ).grid(row=0, column=5, sticky=tkinter.E)
            tkinter.Label (Header, text="Well ",                        ).grid(row=0, column=6, sticky=tkinter.E)
            tkinter.Label (Header, text="µL/total",                     ).grid(row=0, column=7, sticky=tkinter.E)
            # todo: add "global protocol variables" like number of samples, worktable template and output files

            self.reagent_frames = [App.GUI_protocol.ReagentFrame(self, reagent)
                                   for reagent in self.protocol.worktable.reagents]

            # self.GUI_parameters.destroy() #    ['state'] = 'disabled'
            for child in self.GUI_parameters.winfo_children():
                child.configure(state='disable')
            self.quit_bt['state'] = 'normal'
            self.run['state'] = 'disabled'
            self.master.mainloop()
            self.quit_bt['text'] = 'Quit'

        def CheckPipeline(self, pipeline):
           #for prot, run_name in pipeline.
           print ('checking pipeline ' + self.protocol.name)
           for GUI_init_prot in self.GUI_init.ProtcolFrames:
               GUI_init_prot.Run()

        def run_selected(self):
            # create and run the protocol
            self.GUI_init.update_parameters()

            self.protocol.Run()
            if isinstance(self.protocol, App.Pipeline):
                pass
            else:
                for line in self.protocol.comments():
                    self.comments.insert(tkinter.END, line)

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.master.title('RobotEvo')

        tkinter.Label(self,  padx=10, text='Please, select the protocol for which you want to generate an Evoware script:').grid(row=1, columnspan=3)

        # Protocol selection ------------------
        global av_prot_names
        av_prot_names = [prot.name + (': ' + prot.run_name if prot.run_name else '') for prot in available]
        self.selected_protocol = tkinter.StringVar(master)      # variable
        self.selected_protocol.set(av_prot_names[0])                # variable initial value

        self.protocol_selection = tkinter.OptionMenu(self, self.selected_protocol, *av_prot_names, command=self.protocol_selected)
        self.protocol_selection.grid(row=2, column=1, rowspan=1, columnspan=3, sticky=tkinter.W + tkinter.E)

        self.grid()

        #self.protocol_selected(None)

    def protocol_selected(self, value):
        selected = self.selected_protocol.get()
        print('Selected protocol: ' + value)
        App.GUI_protocol(available[ av_prot_names.index(value)])


if __name__ == "__main__":
    app = App(tkinter.Tk())
    app.master.mainloop()



