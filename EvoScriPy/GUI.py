# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# GUI.py : authors Ariel Vina-Rodriguez (qPCR4vir), Tobias Winterfeld (dondiablo)
# 2014-2016
"""
Implement a GUI that automatically detect available protocols.
"""
import tkinter
from protocols import available

__author__ = 'qPCR4vir'


class App(tkinter.Frame):
    """  See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
    """

    def __init__(self, master=None):
        self.logo = tkinter.PhotoImage(file="../EvoScriPy/logo.png")
        self.w = tkinter.Label(master, image=self.logo)
        self.w.grid(row=0, column=0, columnspan=15, sticky=tkinter.W + tkinter.E)

        tkinter.Frame.__init__(self, master)
        self.grid()

        tkinter.Label(self, text='Number of Samples (1-48):').grid(row=1, column=8, columnspan=4)

        self.NumOfSamples = tkinter.StringVar(master, '12')
        self.sample_num = tkinter.Spinbox(self, from_=1, to=48, increment=1)
        self.sample_num.grid(row=2, column=8, columnspan=4)

        self.protocols = {p.name: p for p in available}
        self.protocol_selection = tkinter.Listbox(self, height=5, width=25,  selectmode=tkinter.SINGLE)
        self.protocol_selection.grid(row=1, column=0, rowspan=2, columnspan=4, sticky=tkinter.W + tkinter.E)
        for name in self.protocols.keys():
            self.protocol_selection.insert(tkinter.END, name)
        self.protocol_selection.activate(0)

        self.used_protocols = {}

        self.protocol_versions = self.protocols[self.protocol_selection.get(0)].versions
        self.version_selection = tkinter.Listbox(self, height=5, width=25, selectmode=tkinter.SINGLE)
        self.version_selection.grid(row=1, column=4, rowspan=2, columnspan=4, sticky=tkinter.W + tkinter.E)
        for name in self.protocol_versions.keys():
            self.version_selection.insert(tkinter.END, name)
        self.version_selection.activate(1)

        self.run = tkinter.Button(self, text="Synthetize a TECAN script\nfor the selected protocol",
                                  command=self.run_selected)
        self.run.grid(row=1, column=12, columnspan=4)

        self.quit = tkinter.Button(self, text="Quit", command=self.quit)
        self.quit.grid(row=2, column=12, columnspan=4)

        self.yScroll = tkinter.Scrollbar(self, orient=tkinter.VERTICAL)
        self.yScroll.grid(row=3, column=15, columnspan=14, sticky=tkinter.N + tkinter.S)
        self.xScroll = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL)
        self.xScroll.grid(row=17, column=8, columnspan=7, sticky=tkinter.E + tkinter.W)

        self.comments = tkinter.Listbox(self, height=25, width=100,
                                        xscrollcommand=self.xScroll.set,
                                        yscrollcommand=self.yScroll.set)
        self.comments.grid(row=3, column=8, columnspan=7)
        self.xScroll['command'] = self.comments.xview
        self.yScroll['command'] = self.comments.yview

        self.varoutput = tkinter.Frame(self)
        self.varoutput.grid(row=3, column=0, columnspan=8, rowspan=15)

        explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        tkinter.Label(self, justify=tkinter.CENTER, padx=10, text=explanation).grid(row=18, columnspan=16)

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

            self.CheckB = tkinter.Checkbutton(self, text="Reply" + str(num + 1), justify=tkinter.LEFT)  # width=15,
            self.CheckB.grid(column=0, row=0, )
            tkinter.Entry(self, textvariable=self.Well, width=2).grid(row=0, column=1, )
            tkinter.Spinbox(self,
                            textvariable=self.Vol,
                            increment=1,
                            from_=0.0,
                            to=100000,
                            width=7).grid(column=2, row=0)

    class ReactiveFrame(tkinter.Frame):
        def __init__(self, master, react):
            tkinter.Frame.__init__(self, master)
            self.grid(sticky=tkinter.N + tkinter.S and tkinter.E)
            self.columnconfigure(0, minsize=140)
            self.react = react
            self.Vol = tkinter.DoubleVar()
            self.Vol.set(react.volpersample)
            self.RackName = tkinter.StringVar()
            self.RackName.set(react.labware.label)
            self.RackGrid = tkinter.IntVar()
            self.RackGrid.set(react.labware.location.grid)
            self.RackSite = tkinter.IntVar()
            self.RackSite.set(react.labware.location.site)

            tkinter.Label(self, text=react.name, justify=tkinter.RIGHT).grid(row=0, column=0, sticky=tkinter.E)

            tkinter.Spinbox(self,
                            textvariable=self.Vol,
                            increment=1, from_=0.0, to=100000, width=5).grid(row=0, column=1, sticky=tkinter.W)

            self.RackNameEntry = tkinter.Entry(self,
                                               textvariable=self.RackName, width=10).grid(row=0, column=2, padx=5,
                                                                                         sticky=tkinter.W)
            self.RackGridEntry = tkinter.Entry(self,
                                               textvariable=self.RackGrid, width=2).grid(row=0, column=3, padx=5,
                                                                                         sticky=tkinter.W)
            self.RackSiteEntry = tkinter.Entry(self,
                                               textvariable=self.RackSite, width=2).grid(row=0, column=4, padx=5,
                                                                                         sticky=tkinter.W)

            for rn, reply in enumerate(react.Replicas):
                # assert isinstance(react,Rtv.Reactive)
                App.ReplicaFrame(self, reply, rn)
                # self.pack()

    def CheckList(self, protocol):
        RL=protocol.Reactives
        self.ReactFrames=[]
        Header=tkinter.Frame(self.varoutput)
        Header.grid( sticky=tkinter.E)
        Header.columnconfigure(1, minsize=120)
        tkinter.Label (Header, text='Reagent', justify=tkinter.RIGHT).grid(row=0, column=0,sticky=tkinter.E)
        tkinter.Label (Header, text="     µL/sample      ", ).grid(row=0, column=1, ) # sticky=tkinter.CENTER
        tkinter.Label (Header, text="Rack   ",     ).grid(row=0, column=2,sticky=tkinter.E)
        tkinter.Label (Header, text="Grid",          ).grid(row=0, column=3,sticky=tkinter.E)
        tkinter.Label (Header, text="Site        ",          ).grid(row=0, column=4,sticky=tkinter.E)
        tkinter.Label (Header, text='          ',      ).grid(row=0, column=5, sticky=tkinter.E)
        tkinter.Label (Header, text="Well ",          ).grid(row=0, column=6, sticky=tkinter.E)
        tkinter.Label (Header, text="µL/total",          ).grid(row=0, column=7, sticky=tkinter.E)

        for rn, react in enumerate(protocol.Reactives):
            # assert isinstance(react,Rtv.Reactive)
            rf=App.ReactiveFrame(self.varoutput,react)
            self.ReactFrames.append(rf)

    def run_selected(self):
        selected = self.protocol_selection.curselection() # list of selected index
        print(selected)
        if not selected: return
        selected = self.protocol_selection.get(selected[0]) # text of first selected protocol
        print(selected)
        NumOfSamples = int(self.sample_num.get())

        if selected in self.used_protocols:
            protocol = self.used_protocols[selected]    # how to set the Num of Samples?
        else:
            # here we could inspect what protocol is about to run and select an specific GUI
            protocol = self.protocols[selected](self, NumOfSamples)
            self.used_protocols[selected] = protocol

        protocol.Run()  # create and run the protocol

        self.comments.delete(0, self.size())
        for line in protocol.comments():
            self.comments.insert(tkinter.END, line)
            # self.pack()


if __name__ == "__main__":
    app = App(tkinter.Tk())
    app.master.mainloop()
