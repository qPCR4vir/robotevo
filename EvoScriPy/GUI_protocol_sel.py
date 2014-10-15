__author__ = 'Ariel'

# from Labware import *
# import Robot
import EvoMode
from Instructions import Pipette

comments=EvoMode.Comments()

EvoMode.current = EvoMode.multiple([EvoMode.iRobot( Pipette.LiHa1, nTips=4),
                                    EvoMode.Script(template = 'RNAext_MNVet.ewt',
                                                   filename = 'AWL.esc' ),
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
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack(side="left")

        logo = tk.PhotoImage(file='..\EvoScriPy\FLI-Logo_mit_Farbverlauf.png')
        tk.Label(self, image=logo).pack(side="top")

        tk.Label(self,text='Number of Samples (1-48):').pack(side='top')

        self.NumOfSamples=tk.StringVar(master,'12')

        self.sample_num=tk.Spinbox(self,from_=1,to=48,increment=1  )
        self.sample_num.pack(side='top' )


        self.protocols={'RNA extraction with the MN_Vet kit': extractRNA_with_MN_Vet_Kit,
                        'Others': not_implemented}
        self.protocol=tk.StringVar(self,'RNA extraction with the MN_Vet kit')

        self.protocol_selection=tk.Listbox(self, height=len(self.protocols)+1, width=80, selectmode=tk.SINGLE )
        self.protocol_selection.pack(side='top')

        for name in self.protocols.keys():
            self.protocol_selection.insert(tk.END,name )

        self.protocol_selection.activate(1)


        self.run = tk.Button(self, text="Synthetize a TECAN script for the selected protocol",  command=self.run_selected)
        self.run.pack(side='top')

        self.quit = tk.Button(self,   text="Quit",   command=self.quit)
        self.quit.pack(side='top')

        self.comments=tk.Listbox(self,height=25, width=150)
        self.comments.pack(side="bottom")

        explanation = "Hier entsteht die neue Grafische Benutzeroberfläche für die einfache Anwendung der automatisierten RNA-Extraktion"
        tk.Label(self,width=100,   justify=tk.CENTER,   padx = 10,  text=explanation).pack(side="bottom")



    def run_selected(self):
        selected=self.protocol_selection.curselection()
        print (selected)
        if not selected: return
        selected=self.protocol_selection.get(selected[0])
        print (selected)
        NumOfSamples=int(self.sample_num.get())

        self.protocols[selected](NumOfSamples)

        self.comments.delete(0,self.size())
        for line in comments.comments:
            self.comments.insert(tk.END,line)




app = App(tk.Tk() )
app.master.title('INNT - Automatisiert RNA-Extraktion')
app.mainloop()
