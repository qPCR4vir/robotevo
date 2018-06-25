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


class App(tkinter.Frame):
    """  See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
    """

    class GUI_init_parameters: # (tkinter.Frame)

        def __init__(self, parameters):
            self.parameters = parameters

            # worktable_template_filename
            tkinter.Label(self.parameters.GUI.GUI_parameters, text='WorkTable:').grid(row=0, column=0, columnspan=1,
                                                        sticky=tkinter.N + tkinter.W)
            self.worktable_filename_v = tkinter.StringVar( )
            self.worktable_filename_v.set(parameters.worktable_template_filename)
            tkinter.Entry(self.parameters.GUI.GUI_parameters, textvariable=self.worktable_filename_v).grid(row=0, column=1, columnspan=9,
                                                                             sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.parameters.GUI.GUI_parameters, text='...', command=self.selet_WT_FN).grid(row=0, column=10)
            self.worktable_filename_v.trace("w", self.set_WT_FN)

            # output_filename
            tkinter.Label(self.parameters.GUI.GUI_parameters, text='Output filename:').grid(row=1, column=0, columnspan=1,
                                                                                      sticky=tkinter.N + tkinter.W)
            self.output_filename_v = tkinter.StringVar()
            self.output_filename_v.set(parameters.output_filename)
            tkinter.Entry(self.parameters.GUI.GUI_parameters, textvariable=self.output_filename_v).grid(row=1,
                                                                                                           column=1,
                                                                                                           columnspan=9,
                                                                                                           sticky=tkinter.N + tkinter.E + tkinter.W)

            tkinter.Button(self.parameters.GUI.GUI_parameters, text='...', command=self.selet_O_FN).grid(row=1,
                                                                                                          column=10)
            self.output_filename_v.trace("w", self.set_O_FN)

            # First tip (in the first tip rack)
            tkinter.Label(self.parameters.GUI.GUI_parameters, text='First tip:').grid(row=2, column=0, columnspan=1,
                                                        sticky=tkinter.N + tkinter.W)
            self.firstTip_v = tkinter.StringVar( )
            self.firstTip_v.set(parameters.firstTip)
            tkinter.Entry(self.parameters.GUI.GUI_parameters, textvariable=self.firstTip_v).grid(row=2, column=1, columnspan=1,
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



    class GUI_init_RNA_ext_MN(GUI_init_parameters):

        def __init__(self, parameters):
            App.GUI_init_parameters.__init__(self, parameters)

            # Number of Samples
            min_s, max_s = self.min_max_Number_of_Samples()
            label = "Number of Samples: ({}-{}) ".format(min_s, max_s)
            tkinter.Label(self.parameters.GUI.GUI_parameters, text=label).grid(row=2, column=3, columnspan=2,
                                                                       sticky=tkinter.N + tkinter.W)

            self.NumOfSamples = tkinter.IntVar()
            self.NumOfSamples.set(self.parameters.NumOfSamples)
            self.sample_num = tkinter.Spinbox(self.parameters.GUI.GUI_parameters, textvariable=self.NumOfSamples,
                                              from_=min_s, to=max_s, increment=1,
                                              command=self.read_NumOfSamples)
            self.sample_num.grid(row=2, column=5, columnspan=1)


        def min_max_Number_of_Samples(self):
            return 1 , 48

        def read_NumOfSamples(self):
            self.parameters.NumOfSamples = self.NumOfSamples
            print(" --- NumOfSamples set to: ", str(self.parameters.NumOfSamples))


    class GUI_init_RNA_ext_Fisher(GUI_init_RNA_ext_MN):

        def __init__(self, parameters):
            App.GUI_init_RNA_ext_MN.__init__(self, parameters)

        def min_max_Number_of_Samples(self):
            return 1 , 96


    class GUI_init_Prefill_plates_VEW1_ElutionBuffer_VEW2(GUI_init_RNA_ext_MN):

        def __init__(self, parameters):
            App.GUI_init_RNA_ext_MN.__init__(self, parameters)

        def min_max_Number_of_Samples(self):
            return 1 , 96




    def __init__(self, master=None):

        tkinter.Frame.__init__(self, master)
        self.grid()

        # Protocol selection ------------------
        self.protocols = {p.name: p for p in available}         # values
        self.selected_protocol = tkinter.StringVar(master)      # variable

        self.protocol_selection = tkinter.OptionMenu(self, self.selected_protocol, *self.protocols, command=self.protocol_selected)
        self.protocol_selection.grid(row=0, column=0, rowspan=1, columnspan=4, sticky=tkinter.W + tkinter.E)
        self.selected_protocol.set(available[0].name)           # variable def value


        self.protocol_versions = self.protocols[self.selected_protocol.get()].versions   # values
        self.selected_version = tkinter.StringVar(master)                                # variable

        self.version_selection = tkinter.OptionMenu(self, self.selected_version, *self.protocol_versions)
        self.version_selection.grid(row=1, column=0, rowspan=1, columnspan=4, sticky=tkinter.W + tkinter.E)
        self.selected_version.set(next(iter(self.protocol_versions)))  # variable def value

        self.used_protocols = {}                  # ???

        # initialize parameters
        self.GUI_parameters = tkinter.Frame(self)
        self.GUI_parameters.grid(row=0, column=4, columnspan=11, rowspan=3)
        self.protocol_selected(None)

        # run / quit     ---------------------
        self.run = tkinter.Button(self, text="Initialize the selected protocol",
                                  command=self.run_selected)
        self.run.grid(row=0, column=15, columnspan=2)

        self.quit = tkinter.Button(self, text="Synthetize the TECAN script", command=self.quit, state=tkinter.DISABLED)
        self.quit.grid(row=1, column=15, columnspan=2)

        # comments: visualize the synthesized script -----------------------
        self.yScroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        self.yScroll.grid(row=3, column=16,  rowspan=20, sticky=tkinter.N + tkinter.S)
        self.xScroll = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        self.xScroll.grid(row=23, column=8, columnspan=8, sticky=tkinter.E + tkinter.W)

        self.comments = tkinter.Listbox(self, height=25, width=100,
                                        xscrollcommand=self.xScroll.set,
                                        yscrollcommand=self.yScroll.set)
        self.comments.grid(row=3, column=8, rowspan=20, columnspan=8, sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W)
        self.xScroll['command'] = self.comments.xview
        self.yScroll['command'] = self.comments.yview

        self.varoutput = tkinter.Frame(self)
        self.varoutput.grid(row=3, column=0, columnspan=8, rowspan=15)

    def protocol_selected(self, value):
        selected = self.selected_protocol.get()
        print('Selected protocol: ' + selected)

        # create and initialize the Parameters
        self.parameters = self.protocols[self.selected_protocol.get()].Parameter(self)
        self.setVariantsMenu(None)
        for child in self.GUI_parameters.winfo_children():
            child.destroy() # .configure(state='disable')

        if selected == "RNA extraction with the MN_Vet kit":
            App.GUI_init_RNA_ext_MN(self.parameters)

        elif   selected == "PreKingFisher for RNA extraction with the NucleoMag MN_Vet kit"\
            or selected == "PreKingFisher for RNA extraction with the NucleoMag MN_Vet kit and EtOH80p Plate preFill":
            App.GUI_init_Prefill_plates_VEW1_ElutionBuffer_VEW2(self.parameters)

        elif selected == "Prefill plates with VEW1, Elution buffer and VEW2":
            App.GUI_init_RNA_ext_Fisher(self.parameters)

        else:
            App.GUI_init_parameters(self.parameters)

    def setVariantsMenu(self, value):
        selected = self.selected_protocol.get()
        self.protocol_versions = self.protocols[selected].versions   # values
        m=self.version_selection.children['menu']
        m.delete(0,'end')
        for val in self.protocol_versions:
            m.add_command(label=val, command=lambda v=self.selected_version, l=val: v.set(l))
        self.selected_version.set(next(iter(self.protocol_versions)))  # variable def value

    class ReplicaFrame(tkinter.Frame):
        def __init__(self, master, reply, num):
            tkinter.Frame.__init__(self, master)
            self.grid(sticky=tkinter.N + tkinter.S, row=num, column=6, columnspan=3)

            self.reply = reply
            self.num = num
            self.Vol = tkinter.DoubleVar()
            self.Vol.set(reply.vol)
            self.Well = tkinter.IntVar()
            self.Well.set(reply.offset + 1)

            self.CheckB = tkinter.Checkbutton(self, text="Reply" + str(num + 1), justify=tkinter.LEFT, state=tkinter.DISABLED)  # width=15,
            self.CheckB.grid(column=0, row=0, )
            tkinter.Entry(self, textvariable=self.Well, width=2).grid(row=0, column=1) #, state=tkinter.DISABLED
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
            self.RackName = tkinter.StringVar()
            self.RackName.set(react.labware.label)
            self.RackGrid = tkinter.IntVar()
            self.RackGrid.set(react.labware.location.grid)
            self.RackSite = tkinter.IntVar()
            self.RackSite.set(react.labware.location.site)
            self.check_list = check_list

            tkinter.Label(self, text=react.name, justify=tkinter.RIGHT).grid(row=0, column=0, sticky=tkinter.E)

            dis = tkinter.DISABLED if react.components else tkinter.NORMAL

            self.Vol = tkinter.DoubleVar()
            self.Vol.set(react.volpersample)
            tkinter.Spinbox(self,
                            textvariable=self.Vol,  state=dis,     command= self.setVol,
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

            self.ReplicaFrames= [App.ReplicaFrame(self, reply, rn) for rn, reply in enumerate(react.Replicas)]

        def setVol(self, *args):

            print("changing volumen of '{0}' from {1} to {2}".format(
                           self.react.name, self.react.volpersample, self.Vol.get()) )

            self.react.volpersample = self.Vol.get()

            for rf in self.check_list.ReactFrames:             # change possibles mix.
                for c in rf.react.components:
                    if self.react is c:
                        rf.react.init_vol()
                        rf.Vol.set(rf.react.volpersample)

            self.react.init_vol()
            for rf in self.ReplicaFrames:   # change replicas
                rf.Vol.set(rf.reply.vol)


    def CheckList(self, protocol):

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

        self.ReactFrames = [App.ReactiveFrame(self,react) for react in protocol.Reactives]

        #self.GUI_parameters.destroy() #    ['state'] = 'disabled'
        for child in self.GUI_parameters.winfo_children():
            child.configure(state='disable')
        self.quit              ['state'] = 'normal'
        self.run               ['state'] = 'disabled'
        #self.sample_num        ['state'] = 'disabled'
        self.protocol_selection['state'] = 'disabled'

        self.master.mainloop()
        self.quit['text'] = 'Quit'

    def run_selected(self):
        selected = self.selected_protocol.get()
        print(selected)
        if not selected: return

        # create and run the protocol
        protocol = self.protocols[selected](self.parameters)
        protocol.Run()

        for line in protocol.comments():
            self.comments.insert(tkinter.END, line)


if __name__ == "__main__":
    app = App(tkinter.Tk())
    app.master.mainloop()
