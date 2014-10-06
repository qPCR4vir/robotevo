__author__ = 'Ariel'
# from Labware import *
# import Robot
import EvoMode
from Instructions import Pipette
iRobot = EvoMode.iRobot( Pipette.LiHa1, nTips=4)
Script = EvoMode.Script(template = 'RNAext_MNVet.ewt',    filename = 'AWL.esc' )
comments=EvoMode.Comments()

EvoMode.current = EvoMode.multiple([iRobot,
                                    Script,
                                    EvoMode.AdvancedWorkList('AWL.gwl'),
                                    EvoMode.ScriptBody('AWL.esc.txt'),
                                    EvoMode.StdOut(), comments
                                    ])



from RNAextractionMN_Mag_Vet import extractRNA_with_MN_Vet_Kit

import tkinter as tk


def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')


class App(tk.Frame):
    """  See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
    """

    def __init__(self, master=None):

        tk.Frame.__init__(self, master)
        self.grid()

        logo = tk.PhotoImage(file='..\EvoScriPy\FLI-Logo_mit_Farbverlauf.png')
        tk.Label(self, image=logo).grid(row=0, rowspan=2, columnspan=3)

        tk.Label(self, text='Number of Samples (1-48):').grid(row=1, column=0)

        self.NumOfSamples = tk.StringVar(master, '12')

        self.sample_num = tk.Spinbox(self, from_=1, to=48, increment=1)
        self.sample_num.grid(row=2, column=0)

        self.protocols = {'RNA extraction with the MN_Vet kit': extractRNA_with_MN_Vet_Kit,
                          'Others': not_implemented}
        self.protocol = tk.StringVar(self, 'RNA extraction with the MN_Vet kit')

        self.protocol_selection = tk.Listbox(self, height=len(self.protocols) + 1, width=80, selectmode=tk.SINGLE)
        self.protocol_selection.grid(row=1, column=1)

        for name in self.protocols.keys():
            self.protocol_selection.insert(tk.END, name)

        self.protocol_selection.activate(1)

        self.run = tk.Button(self, text="Synthetize a TECAN script\nfor the selected protocol",
                             command=self.run_selected)
        self.run.grid(row=3, column=0)

        self.quit = tk.Button(self, text="Quit", command=self.quit)
        self.quit.grid(row=4, column=0)

        self.comments = tk.Listbox(self, height=25, width=150)
        self.comments.grid(row=3, column=1, rowspan=6)

        explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        tk.Label(self, justify=tk.CENTER, padx=10, text=explanation).grid(row=9, columnspan=3)


    def run_selected(self):
        selected = self.protocol_selection.curselection()
        print(selected)
        if not selected: return
        selected = self.protocol_selection.get(selected[0])
        print(selected)
        NumOfSamples = int(self.sample_num.get())

        self.protocols[selected](NumOfSamples)
        Script.done()

        self.comments.delete(0, self.size())
        for line in comments.comments:
            self.comments.insert(tk.END, line)


app = App(tk.Tk())
app.master.title('INNT - Automatisiert RNA-Extraktion')
app.mainloop()
