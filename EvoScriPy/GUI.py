# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# GUI.py : authors Ariel Vina-Rodriguez (qPCR4vir), Tobias Winterfeld (dondiablo)
# 2014-2018
"""
Implement a GUI that automatically detect available protocols.
"""
import tkinter
from tkinter.filedialog import askopenfilename

from protocols import available

__author__ = 'qPCR4vir'

GUI4parameters = {}


class App(tkinter.Frame):
    """  See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
    """

    class GUI4Protocols:

        def __init__(self):
            self.protocols = {}
            for av in available:
                if isinstance(av, tuple):
                    class_name, parameters = av
                    self.protocols[class_name.name + ': ' + parameters.run_name] = av
                else:
                    self.protocols[av.name] = av
            self.GUI4parameters = GUI4parameters

        def versions(self, prot_name):
            class_name = self.protocols[prot_name]
            if isinstance(class_name, tuple):
                class_name, parameters = class_name
            return class_name.versions

        def new_parameters(self, prot_name, GUI):

            protocol_class = self.protocols[prot_name]
            if isinstance(protocol_class, tuple):
                protocol_class, parameters = protocol_class
                parameters.GUI = GUI
            else:
                parameters = protocol_class.Parameter(GUI)
            # run the corresponding GUI
            print ('run GUI_init for ' + prot_name)
            return protocol_class, parameters, self.GUI4parameters[protocol_class.name](parameters)

        def isPipeline(self, prot_name):
            protocol_class = self.protocols[prot_name]
            if isinstance(protocol_class, tuple):
                protocol_class, parameters = protocol_class
            return protocol_class.isPipeline

    class GUI_init_pipeline:
        """  Show the parameters of the pipeline for review: a list of the protocols to run with run names

        """

        class ProtocolFrame(tkinter.Frame):

            def __init__(self, GUI, prot):
                self.GUI = GUI
                self.protocol = prot
                print ('protocol: ' + prot[0])
                tkinter.Frame.__init__(self, GUI.varoutput)
                self.grid(sticky=tkinter.N + tkinter.S and tkinter.E)
                self.selected_protocol = tkinter.StringVar(self)  # variable

                self.protocol_selection = tkinter.OptionMenu(self, self.selected_protocol, *GUI.GUIprot.protocols)
                #self.protocol_selection.grid(row=0, column=0, rowspan=1, columnspan=4, sticky=tkinter.W + tkinter.E)
                self.protocol_selection.grid(row=0, column=0, sticky=tkinter.W + tkinter.E)

                self.selected_protocol.set(prot[0])  # variable def value
                self.selected_protocol.trace("w", self.prot_changed)

                self.ProtName = tkinter.StringVar(self)
                self.ProtName.set(prot[1])
                self.RackNameEntry = tkinter.Entry(self, textvariable=self.ProtName)
                self.RackNameEntry.grid(row=0, column=1, sticky=tkinter.W)
                #self.RackNameEntry.trace("w", self.name_changed)


            def Run(self):
                self.runb = tkinter.Button(self, #state=tkinter.DISABLED,
                                           text='Run', command=self.run_prot)
                self.runb.grid( row=0, column=2)
                #self.runb.configure(state='normal')
                self.runb.mainloop()



            def run_prot(self):
                self.runb.configure(state='disable')
                self.protocol[1] = self.ProtName.get()
                self.update_protocol()
                print('Fro pipeline Run GUI for protocol: '  + self.protocol[0] +' run-named '+ self.protocol[1])
                App.GUI_protocol(self.protocol[0], tkinter.Tk())



            def prot_changed(self, *args):
                print('Changing: ' + self.protocol[0])
                self.protocol[0]= self.selected_protocol.get()
                print('to: ' + self.protocol[0])

            def name_changed(self, *args):
                print('Changing: ' + self.protocol[1])
                self.protocol[1]= self.selected_protocol.get()
                print('to: ' + self.protocol[1])

            def update_protocol(self):
                self.prot_changed()
                self.name_changed()

        def __init__(self, parameters):
            self.parameters = parameters
            print('run GUI_init_pipeline for: ')

            tkinter.Button(parameters.GUI.varoutput, text='add', command=self.add_prot).grid( row=0, column=2)
            self.ProtcolFrames = [App.GUI_init_pipeline.ProtocolFrame(parameters.GUI, prot) for prot in parameters.Protocol_classes]


        def add_prot(self):
            self.parameters.Protocol_classes.append(['Add protocol or pipeline', 'run name'])
            self.ProtcolFrames.append(
                App.GUI_init_pipeline.ProtocolFrame(self.parameters.GUI, self.parameters.Protocol_classes[-1]))

        def update_parameters(self):
            pass    # ??



    from EvoScriPy.protocol_steps import Pipeline
    GUI4parameters[Pipeline.name]=GUI_init_pipeline
    #from protocols import PipelineTest
    #GUI4parameters[PipelineTest.name]=GUI_init_pipeline

    class GUI_init_parameters: # (tkinter.Frame)

        def __init__(self, parameters):
            self.parameters = parameters

            # worktable_template_filename
            tkinter.Label(self.parameters.GUI.GUI_parameters_frame, text='WorkTable:').grid(row=0, column=0, columnspan=1,
                                                        sticky=tkinter.N + tkinter.W)
            self.worktable_filename_v = tkinter.StringVar( self.parameters.GUI.GUI_parameters_frame)
            self.worktable_filename_v.set(parameters.worktable_template_filename)
            tkinter.Entry(self.parameters.GUI.GUI_parameters_frame, textvariable=self.worktable_filename_v).grid(row=0, column=1, columnspan=9,
                                                                             sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.parameters.GUI.GUI_parameters_frame, text='...', command=self.selet_WT_FN).grid(row=0, column=10)
            self.worktable_filename_v.trace("w", self.set_WT_FN)

            # output_filename
            tkinter.Label(self.parameters.GUI.GUI_parameters_frame, text='Output filename:').grid(row=1, column=0, columnspan=1,
                                                                                      sticky=tkinter.N + tkinter.W)
            self.output_filename_v = tkinter.StringVar(self.parameters.GUI.GUI_parameters_frame)
            self.output_filename_v.set(parameters.output_filename)
            tkinter.Entry(self.parameters.GUI.GUI_parameters_frame, textvariable=self.output_filename_v).grid(row=1,
                                                                                                           column=1,
                                                                                                           columnspan=9,
                                                                                                           sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.parameters.GUI.GUI_parameters_frame, text='...', command=self.selet_O_FN).grid(row=1,
                                                                                                          column=10)
            self.output_filename_v.trace("w", self.set_O_FN)

            # First tip (in the first tip rack)
            tkinter.Label(self.parameters.GUI.GUI_parameters_frame, text='First tip:').grid(row=2, column=0, columnspan=1,
                                                        sticky=tkinter.N + tkinter.W)
            self.firstTip_v = tkinter.StringVar(self.parameters.GUI.GUI_parameters_frame )
            self.firstTip_v.set(parameters.firstTip)
            tkinter.Entry(self.parameters.GUI.GUI_parameters_frame, textvariable=self.firstTip_v).grid(row=2, column=1, columnspan=1,
                                                                             sticky=tkinter.N + tkinter.E + tkinter.W)
            self.firstTip_v.trace("w", self.set_firstTip)

        def set_firstTip(self, *args):
            self.parameters.firstTip = self.firstTip_v.get()

        def set_WT_FN(self, *args):
            self.parameters.worktable_template_filename = self.worktable_filename_v.get()

        def selet_WT_FN(self):
            self.worktable_filename_v.set( tkinter.filedialog.askopenfilename(title='Select the WorkTable template') )

        def set_O_FN(self, *args):
            self.parameters.output_filename = self.output_filename_v.get()

        def selet_O_FN(self):
            self.output_filename_v.set( tkinter.filedialog.asksaveasfilename(title='Select the output filename') )

        def update_parameters(self):
            self.set_firstTip()
            self.set_WT_FN()
            self.set_O_FN()


    from EvoScriPy.protocol_steps import Protocol
    GUI4parameters[Protocol.name]=GUI_init_parameters

    class GUI_init_RNA_ext_MN(GUI_init_parameters):


        def __init__(self, parameters):
            App.GUI_init_parameters.__init__(self, parameters)

            # Number of Samples
            min_s, max_s = self.min_max_Number_of_Samples()
            label = "Number of Samples: ({}-{}) ".format(min_s, max_s)
            tkinter.Label(self.parameters.GUI.GUI_parameters_frame, text=label).grid(row=2, column=3, columnspan=2,
                                                                       sticky=tkinter.N + tkinter.W)

            self.NumOfSamples = tkinter.IntVar(self.parameters.GUI.GUI_parameters_frame)
            self.NumOfSamples.set(self.parameters.NumOfSamples)
            self.sample_num = tkinter.Spinbox(self.parameters.GUI.GUI_parameters_frame, textvariable=self.NumOfSamples,
                                              from_=min_s, to=max_s, increment=1,
                                              command=self.read_NumOfSamples)
            self.sample_num.grid(row=2, column=5, columnspan=1)


        def min_max_Number_of_Samples(self):
            return 1 , 48

        def read_NumOfSamples(self, *args):
            self.parameters.NumOfSamples = self.NumOfSamples.get()
            print(" --- NumOfSamples set to: %d" % (self.parameters.NumOfSamples))

        def update_parameters(self):
            App.GUI_init_parameters.update_parameters(self)
            self.read_NumOfSamples()


    from protocols.RNAextractionMN_Mag import RNAextr_MN_Vet_Kit
    GUI4parameters[RNAextr_MN_Vet_Kit.name]=GUI_init_RNA_ext_MN

    class GUI_init_RNA_ext_Fisher(GUI_init_RNA_ext_MN):

        def __init__(self, parameters):
            App.GUI_init_RNA_ext_MN.__init__(self, parameters)

        def min_max_Number_of_Samples(self):
            return 1 , 96
    from protocols.KingFisher_RNAextNucleoMag_EtOH80p         import KingFisher_RNAextNucleoMag_EtOH80p
    GUI4parameters[KingFisher_RNAextNucleoMag_EtOH80p.name   ]=GUI_init_RNA_ext_Fisher
    from protocols.PreKingFisher_RNAextNucleoMag              import PreKingFisher_RNAextNucleoMag
    GUI4parameters[PreKingFisher_RNAextNucleoMag.name        ]=GUI_init_RNA_ext_Fisher
    from protocols.PreKingFisher_RNAextNucleoMag_EtOH80p      import PreKingFisher_RNAextNucleoMag_EtOH80p
    GUI4parameters[PreKingFisher_RNAextNucleoMag_EtOH80p.name]=GUI_init_RNA_ext_Fisher


    class GUI_init_Prefill_plates_VEW1_ElutionBuffer_VEW2(GUI_init_RNA_ext_MN):

        def __init__(self, parameters):
            App.GUI_init_RNA_ext_MN.__init__(self, parameters)

        def min_max_Number_of_Samples(self):
            return 1 , 96
    from protocols.Prefill_plates_VEW1_ElutionBuffer_VEW2 import Prefill_plates_VEW1_ElutionBuffer_VEW2
    GUI4parameters[Prefill_plates_VEW1_ElutionBuffer_VEW2.name]=GUI_init_Prefill_plates_VEW1_ElutionBuffer_VEW2

    class GUI_protocol(tkinter.Frame):
        def __init__(self, protocol_name, master=None):
            tkinter.Frame.__init__(self, master)
            self.master.title(protocol_name)
            self.grid()

            self.protocol_name = protocol_name
            self.GUIprot = App.GUI4Protocols()  # values
            g = self.GUIprot

            self.protocol_versions = g.versions(protocol_name)
            self.selected_version = tkinter.StringVar(self)  # variable

            self.version_selection = tkinter.OptionMenu(self, self.selected_version, *self.protocol_versions)
            self.version_selection.grid(row=1, column=0, rowspan=1, columnspan=4, sticky=tkinter.W + tkinter.E)
            self.selected_version.set(next(iter(self.protocol_versions)))  # variable def value
            #self.setVariantsMenu(protocol_name)

            # initialize parameters
            self.GUI_parameters_frame = tkinter.Frame(self)
            self.GUI_parameters_frame.grid(row=0, column=4, columnspan=11, rowspan=3)

            # run / quit_bt     ---------------------
            self.run = tkinter.Button(self, text="Initialize the selected protocol",
                                      command=self.run_selected)
            self.run.grid(row=0, column=15, columnspan=2)

            self.quit_bt = tkinter.Button(self, text="Synthetize the TECAN script", command=self.quit,
                                          state=tkinter.DISABLED)
            self.quit_bt.grid(row=1, column=15, columnspan=2)

            if g.isPipeline(protocol_name):
                pass
            else:
                # comments: visualize the synthesized script -----------------------
                self.yScroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
                self.yScroll.grid(row=3, column=16,  rowspan=20, sticky=tkinter.N + tkinter.S)
                self.xScroll = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
                self.xScroll.grid(row=23, column=8, columnspan=8, sticky=tkinter.E + tkinter.W)

                self.comments = tkinter.Listbox(self, height=25, width=100,
                                                xscrollcommand=self.xScroll.set,
                                                yscrollcommand=self.yScroll.set)
                self.comments.grid(row=3, column=8, rowspan=20, columnspan=8,
                                   sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)
                self.xScroll['command'] = self.comments.xview
                self.yScroll['command'] = self.comments.yview

            self.varoutput = tkinter.Frame(self)
            self.varoutput.grid(row=3, column=0, columnspan=8, rowspan=15)
            # create and initialize the Parameters
            self.protocol_class, self.parameters, self.GUI_init = self.GUIprot.new_parameters(protocol_name, self)
            self.mainloop()

        def setVariantsMenu(self, value):
            selected = self.protocol_name
            self.protocol_versions = self.GUIprot.versions(selected)
            m = self.version_selection.children['menu']
            m.delete(0, 'end')
            for val in self.protocol_versions:
                m.add_command(label=val, command=lambda v=self.selected_version, l=val: v.set(l))
            self.selected_version.set(next(iter(self.protocol_versions)))  # variable def value

        def update_parameters(self):
            self.GUI_init.update_parameters()

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

        class ReactiveFrame(tkinter.Frame):

            def __init__(self, check_list, react):
                tkinter.Frame.__init__(self, check_list.varoutput)
                self.grid(sticky=tkinter.N + tkinter.S and tkinter.E)
                self.columnconfigure(0, minsize=140)
                self.react = react
                self.RackName = tkinter.StringVar(self)
                self.RackName.set(react.labware.label)
                self.RackGrid = tkinter.IntVar(self)
                self.RackGrid.set(react.labware.location.grid)
                self.RackSite = tkinter.IntVar(self)
                self.RackSite.set(react.labware.location.site)
                self.check_list = check_list

                tkinter.Label(self, text=react.name, justify=tkinter.RIGHT).grid(row=0, column=0, sticky=tkinter.E)

                dis = tkinter.DISABLED if react.components else tkinter.NORMAL

                self.Vol = tkinter.DoubleVar(self)
                self.Vol.set(react.volpersample)
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

                self.ReplicaFrames = [App.GUI_protocol.ReplicaFrame(self, reply, rn) for rn, reply in enumerate(react.Replicas)]

            def setVol(self, *args):

                print("changing volumen of '{0}' from {1} to {2}".format(
                    self.react.name, self.react.volpersample, self.Vol.get()))

                self.react.volpersample = self.Vol.get()

                for rf in self.check_list.ReactFrames:  # change possibles mix.
                    for c in rf.react.components:
                        if self.react is c:
                            rf.react.init_vol()
                            rf.Vol.set(rf.react.volpersample)

                self.react.init_vol()
                for rf in self.ReplicaFrames:  # change replicas
                    rf.Vol.set(rf.reply.vol)

        def CheckList(self, protocol):

            self.GUI_init.update_parameters()

            Header=tkinter.Frame(self.varoutput)
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

            self.ReactFrames = [App.GUI_protocol.ReactiveFrame(self, react) for react in protocol.worktable.Reactives]

            # self.GUI_parameters_frame.destroy() #    ['state'] = 'disabled'
            for child in self.GUI_parameters_frame.winfo_children():
                child.configure(state='disable')
            self.quit_bt['state'] = 'normal'
            self.run['state'] = 'disabled'
            self.master.mainloop()
            self.quit_bt['text'] = 'Quit'

        def CheckPipeline(self, pipeline):
           #for prot, run_name in pipeline.
           print ('checking pipeline ' + self.protocol_class.name)
           for GUI_init_prot in self.GUI_init.ProtcolFrames:
               GUI_init_prot.Run()



        def run_selected(self):
            # create and run the protocol
            self.GUI_init.update_parameters()

            protocol = self.protocol_class(self.parameters)
            protocol.Run()
            if protocol.isPipeline:
                pass
            else:
                for line in protocol.comments():
                    self.comments.insert(tkinter.END, line)

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.master.title('RobotEvo')

        self.logo = tkinter.PhotoImage(file="../EvoScriPy/logo.png")
        self.w = tkinter.Label(self, image=self.logo)
        self.w.grid(row=0, column=0, columnspan=4, sticky=tkinter.W + tkinter.E)
        tkinter.Label(self,  padx=10, text='Please, select the protocol for which you want to generate an Evoware script:').grid(row=1, columnspan=3)

        # Protocol selection ------------------
        self.GUIprot = App.GUI4Protocols()        # values
        g=self.GUIprot
        self.selected_protocol = tkinter.StringVar(master)      # variable

        self.protocol_selection = tkinter.OptionMenu(self, self.selected_protocol, *g.protocols, command=self.protocol_selected)
        self.protocol_selection.grid(row=2, column=1, rowspan=1, columnspan=3, sticky=tkinter.W + tkinter.E)
        self.selected_protocol.set(available[0].name)           # variable def value

        explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        tkinter.Label(self, justify=tkinter.CENTER, padx=10, text=explanation).grid(row=3, columnspan=4)
        self.grid()

        #self.protocol_selected(None)

    def protocol_selected(self, value):
        selected = self.selected_protocol.get()
        print('Selected protocol: ' + selected)
        App.GUI_protocol(selected, tkinter.Tk())


if __name__ == "__main__":
    app = App(tkinter.Tk())
    app.master.mainloop()
