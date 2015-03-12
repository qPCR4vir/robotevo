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

import tkinter as tk
from RNAextractionMN_Mag_Vet import *
def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.logo = tk.PhotoImage(file="../EvoScriPy/logo.png")
        self.logoFLI = tk.Label(self, image=self.logo)
        self.logoFLI.pack()
        self.step1()

    def step1(self):

        # Probenart bzw LiquidClass

        self.lableLC = tk.Label(self, text='Welche LiquidClass soll verwendet werden?\n(Abhängig vom Ausgangsmaterial)')
        self.lableLC.pack()
        self.LiquidClasses = {
                'Aus Tube mit mehr als 300µl Serum'                 : SerumLiqClass,
                'Aus Tube mit weniger als 300µl Serum'              : SerumLiqClass,
                'Aus 2,0ml Tube mit Stahlkugel und Gewebehomogenat' : TissueHomLiqClass
        }

        for name in self.LiquidClasses.keys():

            self.name = tk.Radiobutton(self, text=name, indicatoron=0, value=name, variable=None, width=50)
            self.name.pack()


        # Probenzahl - Lable+Spinbox
        self.lableProbenzahl = tk.Label(self, text='Wie viele Proben? (1-48)')
        #lableProbenzahl.place(x=5, y=113)
        self.lableProbenzahl.pack()

        self.spinProben = tk.Spinbox(self, from_=1, to=48, increment=1, justify=tk.CENTER)
        #spinProben.place(x=5, y=133)
        self.spinProben.pack()

        # Protokoll - Listbox
        self.protocols = {'RNA extraction with the MN_Vet kit': RNAextr_MN_Vet_Kit,
                                                 'Others': not_implemented
                    }
        self.lableProtocols = tk.Label(self, text='Welches Protokoll?')
        self.lableProtocols.pack()
        self.listProtocols = tk.Listbox(self, height=5, width=35, selectmode=tk.SINGLE)
        #listProtocols.place(x=150, y=113)
        self.listProtocols.pack()
        for name in self.protocols.keys():
            self.listProtocols.insert(tk.END, name)

        self.listProtocols.activate(1)

        # Buttons - Quit, Weiter

        self.buttonZurück=tk.Button(self, text='Zurück', command=None)
        self.buttonZurück.pack()
        self.buttonBeenden=tk.Button(self, text='Beenden', command=quit)
        self.buttonBeenden.pack()
        self.buttonWeiter=tk.Button(self, text='Weiter', command=self.step2)
        self.buttonWeiter.pack()

    def step2(self):

        self.lableLC.destroy()
        for name in self.LiquidClasses.keys():
            self.name.destroy()
        #self.name.destroy()

        self.lableProbenzahl.destroy()
        self.spinProben.destroy()
        self.lableProtocols.destroy()
        self.listProtocols.destroy()
        self.buttonZurück.destroy()
        self.buttonBeenden.destroy()
        self.buttonWeiter.destroy()


        self.quitButton = tk.Button(self, text='Quit2',
                                    command=self.quit)
        self.quitButton.pack()
        self.lable = tk.Label(self, text="EDNLICH!!!!")
        self.lable.pack()

app = Application()
app.master.title('Sample application')
app.mainloop()
