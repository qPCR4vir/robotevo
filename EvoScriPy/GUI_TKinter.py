__author__ = 'tobias.winterfeld'


from tkinter import *

import EvoMode
from Instructions import *
from Instructions_Te_MagS import *
from Labware import *
import Robot
import Reactive as React
from RNAextractionMN_Mag_Vet import extractRNA_with_MN_Vet_Kit

EvoMode.CurEvo = EvoMode.multiEvo([EvoMode.AdvancedWorkList('AWL.gwl'),
                                   EvoMode.ScriptBody('AWL.esc.txt'),
                                   EvoMode.EvoScript(template='RNAext_MNVet.ewt',
                                                     filename='AWL.esc',
                                                     arms=Robot.Robot.Arm(4) ),
                                   EvoMode.EvoStdOut()
                                    ])



from RNAextractionMN_Mag_Vet import extractRNA_with_MN_Vet_Kit
root = Tk()

whatever_you_do = "Whatever you do will be insignificant, but it is very important that you do it.\n(Mahatma Gandhi)"
explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"

logo = PhotoImage(file='..\EvoScriPy\FLI-Logo_mit_Farbverlauf.png')

w1 = Label(root, image=logo).pack(side="top")

w2 = Label(root,
           justify=CENTER,
           padx = 10,
           text=explanation).pack(side="bottom")

msg = Message(root, text = whatever_you_do)
msg.config(bg='lightgreen', font=('times', 24, 'italic'))

def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')

class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack(side="left")

        self.button = Button(frame,
                             text="START", fg="green", bg="black",
                             command=self.write_slogan)
        self.button.pack()

        self.button1 = Button(frame,
                             text="STOPP", fg="red", bg="black",
                             command=self.write_slogan)
        self.button1.pack()

        self.button2 = Button(frame,
                             text="Pause", fg="yellow", bg="black",
                             command=self.write_slogan)
        self.button2.pack()

        self.button3 = Button(frame,
                             text="Hallo", fg="red", bg="black",
                             command=self.write_slogan)
        self.button3.pack()

        self.slogan = Button(frame,
                             text="QUIT",
                             command=frame.quit)
        self.slogan.pack()

        self.protocols={'RNA extraction with the MN_Vet kit': extractRNA_with_MN_Vet_Kit,
                        'Others': not_implemented}
        self.protocol=StringVar(master,'RNA extraction with the MN_Vet kit')

        self.protocol_selection=Listbox(master )
        self.protocol_selection.pack(side='top')

        for name in self.protocols.keys():
            self.protocol_selection.insert(END,name )

        self.NumOfSamples=StringVar(master,'12')

        self.sample_num=Spinbox(master,from_=1,to=48,increment=1 )
        self.sample_num.pack(side='right')


        self.run = Button(frame,
                             text="Run the selected protocol",
                             command=self.run_selected)
        self.run.pack()



    def run_selected(self):
        selected=self.protocol_selection.curselection()
        print (selected)
        selected=self.protocol_selection.get(selected[0])
        print (selected)
        NumOfSamples=int(self.sample_num.get())

        self.protocols[selected](NumOfSamples)

    def write_slogan(self):
        msg.pack(),








app = App(root)
root.mainloop()
