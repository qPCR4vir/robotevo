# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2016
#
# TODO move to a develop branch

"""
import EvoMode
from Instructions import Pipette
import Reactive as Rtv

iRobot = EvoMode.iRobot(Pipette.LiHa1, nTips=4)
Script = EvoMode.Script(template='RNAext_MNVet.ewt', filename='AWL.esc')
comments = EvoMode.Comments()

EvoMode.current = EvoMode.multiple([iRobot,
                                    Script,
                                    EvoMode.AdvancedWorkList('AWL.gwl'),
                                    EvoMode.ScriptBody('AWL.esc.txt'),
                                    EvoMode.StdOut(),
                                    comments
])

__author__ = 'tobias.winterfeld'

import tkinter as tk
from RNAextractionMN_Mag_Vet import RNAextr_MN_Vet_Kit


def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.createLOGO()
        self.createPROTOKOLLSELECTION()
        self.createSAMPLETYPESELECTION()
        self.createTRACKINGCHCKBOX()
        self.createLiqDetCHCKBOX()
        self.createSAMPLENUM()
        self.createCtrlButtons()
        #self.createREAKTIVEFRAME()
        #self.createPROTOKOLLFRAME()
        self.grid()

    def createLOGO(self):
        self.logo = tk.PhotoImage(file="../EvoScriPy/logo.png")
        self.LOGO = tk.Label(image=self.logo)
        self.LOGO.grid(row=0, column=0, columnspan=4,) # sticky=tk.N+tk.S+tk.W+tk.E
        self.explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        self.LOGObot = tk.Label(text=self.explanation)
        self.LOGObot.grid(row=1,  columnspan=4)

    def createPROTOKOLLSELECTION(self):
        self.protocols = {'RNA extraction with the MN_Vet kit': RNAextr_MN_Vet_Kit,
                          'Others': not_implemented}

        # self.protocol = tk.StringVar(self, 'RNA extraction with the MN_Vet kit')

        self.protocol_selection = tk.Listbox(self, height=5, width=32,
                                             selectmode=tk.SINGLE)
        self.protocol_selection.grid(row=2, rowspan=2, column=0, )

        for name in self.protocols.keys():
            self.protocol_selection.insert(tk.END, name)
        self.protocol_selection.activate(1)

    def createSAMPLETYPESELECTION(self):
        self.sampletype = tk.Radiobutton(self, text='Serum', value=1)
        self.sampletype.grid(row=2, column=1, sticky=tk.W)

        self.sampletype = tk.Radiobutton(self, text='Gewebe', value=2)
        self.sampletype.grid(row=3, column=1, sticky=tk.W)

    def createTRACKINGCHCKBOX(self):
        self.asktraking = tk.Checkbutton(self, text='Traking')
        self.asktraking.grid(row=2, column=2, sticky=tk.W)

    def createLiqDetCHCKBOX(self):
        self.askliqdetec = tk.Checkbutton(self, text='Liquid\ndetection')
        self.askliqdetec.grid(row=3, column=2, sticky=tk.W)

    def createSAMPLENUM(self):
        tk.Label(self, text='Number of Samples (1-48):').grid(row=2, column=3, sticky=tk.S)
        self.NumOfSamples = tk.StringVar(self, '12')
        self.sample_num = tk.Spinbox(self, from_=1, to=48, increment=1)
        self.sample_num.grid(row=3, column=3, sticky=tk.N)

    def createCtrlButtons(self):
        self.run = tk.Button(self, text="Synthetize script",
                             command=self.run_selected)
        self.run.grid(row=2, column=4)

        self.quitButton = tk.Button(self,
                                    text='Quit',
                                    command=self.quit)
        self.quitButton.grid(row=3, column=4, sticky=tk.W+tk.E)

    def createREAKTIVEFRAME(self):

        class ReplicaFrame(tk.Frame):
            def __init__(self, master, reply, num):
                tk.Frame.__init__(self, master)
                self.grid()

                self.reply = reply
                self.num = num
                self.Vol = tk.DoubleVar()
                self.Vol.set(reply.vol)
                self.Well = tk.IntVar()
                self.Well.set(reply.offset + 1)

                self.CheckB = tk.Checkbutton(self, text="Reply" + str(num + 1), justify=tk.LEFT)  # width=15,
                self.CheckB.grid()
                tk.Entry(self, textvariable=self.Well, width=2).grid()
                tk.Spinbox(self,
                           textvariable=self.Vol,
                           increment=1,
                           from_=0.0,
                           to=100000,
                           width=7).grid()

        class ReactiveFrame(tk.Frame):
            def __init__(self, master, react):
                assert isinstance(react, Rtv.Reactive)
                tk.Frame.__init__(self, master)
                self.grid()
                self.columnconfigure(0, minsize=140)
                self.react = react
                self.Vol = tk.DoubleVar()
                self.Vol.set(react.volpersample)
                self.RackName = tk.StringVar()
                self.RackName.set(react.labware.label)
                self.RackGrid = tk.IntVar()
                self.RackGrid.set(react.labware.location.grid)
                self.RackSite = tk.IntVar()
                self.RackSite.set(react.labware.location.site)


                # tk.Label  (self, text='',          ).grid(row=0, column=0)
                tk.Label(self, text=react.name, justify=tk.RIGHT).grid()

                tk.Spinbox(self,
                           textvariable=self.Vol,
                           increment=1, from_=0.0, to=100000, width=5).grid()

                self.RackNameEntry = tk.Entry(self,
                                              textvariable=self.RackName, width=10).grid()
                self.RackGridEntry = tk.Entry(self,
                                              textvariable=self.RackGrid, width=2).grid()
                self.RackSiteEntry = tk.Entry(self,
                                              textvariable=self.RackSite, width=2).grid()

                for rn, reply in enumerate(react.Replicas):
                    # assert isinstance(react,Rtv.Reactive)
                    Application.ReplicaFrame(self, reply, rn)
                    #self.pack()

    def CheckList(self, protocol):
        RL = protocol.Reactives
        self.ReactFrames = []
        Header = tk.Frame(self)
        Header.grid()
        Header.columnconfigure(1, minsize=120)
        tk.Label(Header, text='Reagent', justify=tk.RIGHT).grid()
        tk.Label(Header, text="     µL/sample      ", ).grid()  # sticky=tk.CENTER
        tk.Label(Header, text="Rack   ", ).grid()
        tk.Label(Header, text="Grid", ).grid()
        tk.Label(Header, text="Site        ", ).grid()
        tk.Label(Header, text='          ', ).grid()
        tk.Label(Header, text="Well ", ).grid()
        tk.Label(Header, text="µL/total", ).grid()

        for rn, react in enumerate(protocol.Reactives):
            assert isinstance(react, Rtv.Reactive)
            rf = Application.ReactiveFrame(self, react)
            self.ReactFrames.append(rf)

    def createPROTOKOLLFRAME(self):
        self.yScroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.yScroll.grid()
        self.xScroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.xScroll.grid()

        self.comments = tk.Listbox(self, height=25, width=100,
                                   xscrollcommand=self.xScroll.set,
                                   yscrollcommand=self.yScroll.set)
        self.comments.grid()
        self.xScroll['command'] = self.comments.xview
        self.yScroll['command'] = self.comments.yview

        #self.varoutput = tk.Frame(self)
        #self.varoutput.grid(row=3, column=0, columnspan=8, rowspan=15)


    def run_selected(self):
        selected = self.protocol_selection.curselection()
        print(selected)
        if not selected: return
        selected = self.protocol_selection.get(selected[0])
        print(selected)
        NumOfSamples = int(self.sample_num.get())

        self.protocols[selected](self, NumOfSamples).Run()
        Script.done()

        self.comments.delete(0, self.size())
        for line in comments.comments:
            self.comments.insert(tk.END, line)
            # self.pack()


app = Application()
app.master.title('')
app.mainloop()
"""

def SerumLiqClass():
    print('blubb')
    return

def TissueHomLiqClass():
    return

LiquidClasses = {
    'Aus Tube mit mehr als 300µl Serum': SerumLiqClass,
    'Aus Tube mit weniger als 300µl Serum': SerumLiqClass,
    'Aus 2,0ml Tube mit Stahlkugel und Gewebehomogenat': TissueHomLiqClass
}

for name in LiquidClasses.keys():
    print(name)