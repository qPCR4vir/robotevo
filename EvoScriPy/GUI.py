from tkinter import *
import Tobias.RobotEvoTob.EvoScriPy.Labware
import Tobias.RobotEvoTob.EvoScriPy.Robot
from Tobias.RobotEvoTob.EvoScriPy.Instructions import Pipette
import Tobias.RobotEvoTob.EvoScriPy.EvoMode
#from Tobias.RobotEvoTob.EvoScriPy.RobotInitRNAextraction import *
#from Tobias.RobotEvoTob.EvoScriPy.RNAextractionMN_Mag_Vet import extractRNA_with_MN_Vet_Kit
import tkinter
from Tobias.RobotEvoTob.EvoScriPy.EvoMode import Script

__author__ = 'tobias.winterfeld'


master = Tk()
logo = PhotoImage(file="../EvoScriPy/logo.gif")
w = Label(master, image=logo)
w.grid(row=0, column=0, rowspan=3, columnspan=3)


def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')


class App(tkinter.Frame):
    """  See: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/minimal-app.html
    """

    def __init__(self, master=None):

        tkinter.Frame.__init__(self, master)
        self.grid()

        #logo = tkinter.PhotoImage(file="../EvoScriPy/logo.png")
        #tkinter.Label(self, image=logo, justify=tkinter.CENTER).grid(row=0, column=0, rowspan=3, columnspan=3)

        tkinter.Label(self, text='Number of Samples (1-48):').grid(row=5, column=0)

        self.NumOfSamples = tkinter.StringVar(master, '12')
        self.sample_num = tkinter.Spinbox(self, from_=1, to=48, increment=1)
        self.sample_num.grid(row=6, column=0)

        self.protocols = {'RNA extraction with the MN_Vet kit': 'extractRNA_with_MN_Vet_Kit',
                          'Others': not_implemented}
        self.protocol = tkinter.StringVar(self, 'RNA extraction with the MN_Vet kit')

        self.protocol_selection = tkinter.Listbox(self, height=len(self.protocols) + 1, width=75,
                                                  selectmode=tkinter.SINGLE)
        self.protocol_selection.grid(row=5, column=1, rowspan=2)

        for name in self.protocols.keys():
            self.protocol_selection.insert(tkinter.END, name)

        self.protocol_selection.activate(1)

        self.sampletypes = {'Serum': not_implemented,
                            'Gewebe': not_implemented}

        self.sampletype = tkinter.Radiobutton(self, text='Serum', value=1)
        self.sampletype.grid(row=5, column=2, )

        self.sampletype = tkinter.Radiobutton(self, text='Gewebe', value=2)
        self.sampletype.grid(row=6, column=2)

        self.run = tkinter.Button(self, text="Synthetize a TECAN script\nfor the selected protocol",
                                  command=self.run_selected)
        self.run.grid(row=8, column=0)

        self.quit = tkinter.Button(self, text="Quit", command=self.quit)
        self.quit.grid(row=9, column=0)

        self.comments = tkinter.Listbox(self, height=25, width=75)
        self.comments.grid(row=8, column=1, rowspan=6)

        self.varoutput = tkinter.Listbox(self, height=25, width=75)
        self.varoutput.grid(row=8, column=2, rowspan=6)

        explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        tkinter.Label(self, justify=tkinter.CENTER, padx=10, text=explanation).grid(row=15, columnspan=3)


    def run_selected(self):
        selected = self.protocol_selection.curselection()
        print(selected)
        if not selected:
            return
        selected = self.protocol_selection.get(selected[0])
        print(selected)
        NumOfSamples = int(self.sample_num.get())

        self.protocols[selected](NumOfSamples)
        Script.done()

        self.comments.delete(0, self.size())
        for line in comments.comments:
            self.comments.insert(tkinter.END, line)

app = App()
master.mainloop()
