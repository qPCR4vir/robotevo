# Copyright (C) 2014-2016, Ariel Vina Rodriguez ( ariel.rodriguez@fli.bund.de , arielvina@yahoo.es )
#  https://www.fli.de/en/institutes/institut-fuer-neue-und-neuartige-tierseuchenerreger/wissenschaftlerinnen/prof-dr-m-h-groschup/
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
#        Tobias Winterfeld (dondiablo)
# 2014-2016
#
# TODO move to a develop branch


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

from tkinter import *
from RNAextractionMN_Mag_Vet import *

def not_implemented(NumOfSamples):
    print('This protocols have yet to be implemented.')


__author__ = 'tobias.winterfeld'


## GUI-Objekte

# Fenster
tkFenster = Tk()
tkFenster.title('FLI - EvoScriPy')
#tkFenster.geometry('1080x500')



# FLI - Logo - Lable
logo = PhotoImage(file="../EvoScriPy/logo.png")
logoFLI = Label(master=tkFenster, image=logo)
#logoFLI.place(x=5, y=5, width=1070)
logoFLI.pack()


def step1():
    stepFrame = Frame(tkFenster)
    stepFrame.pack()

    # Probenart bzw LiquidClass

    lableLC = Label(master=stepFrame, text='Welche LiquidClass soll verwendet werden?\n(Abhängig vom Ausgangsmaterial)')
    lableLC.pack()
    LiquidClasses = {
            'Aus Tube mit mehr als 300µl Serum'                 : SerumLiqClass,
            'Aus Tube mit weniger als 300µl Serum'              : SerumLiqClass,
            'Aus 2,0ml Tube mit Stahlkugel und Gewebehomogenat' : TissueHomLiqClass
    }

    for name in LiquidClasses.keys():

        name = Radiobutton(master=stepFrame, text=name, indicatoron=0, value=name, variable=None, width=50)
        name.pack()


    # Probenzahl - Lable+Spinbox
    lableProbenzahl = Label(master=stepFrame, text='Wie viele Proben? (1-48)')
    #lableProbenzahl.place(x=5, y=113)
    lableProbenzahl.pack()

    spinProben = Spinbox(master=stepFrame, from_=1, to=48, increment=1, justify=CENTER)
    #spinProben.place(x=5, y=133)
    spinProben.pack()

    # Protokoll - Listbox
    protocols = {'RNA extraction with the MN_Vet kit': RNAextr_MN_Vet_Kit,
                                             'Others': not_implemented
                }
    lableProtocols = Label(master=stepFrame, text='Welches Protokoll?')
    lableProtocols.pack()
    listProtocols = Listbox(master=stepFrame, height=5, width=35, selectmode=SINGLE)
    #listProtocols.place(x=150, y=113)
    listProtocols.pack()
    for name in protocols.keys():
        listProtocols.insert(END, name)

    listProtocols.activate(1)

    # Buttons - Quit, Weiter

    buttonZurück=Button(master=stepFrame, text='Zurück', command=None)
    buttonZurück.pack()
    buttonBeenden=Button(master=stepFrame, text='Beenden', command=quit)
    buttonBeenden.pack()
    buttonWeiter=Button(master=stepFrame, text='Weiter', command=step2())
    buttonWeiter.pack()


def step2():
    #stepFrame.destroy()

    stepFrame2 = Frame(tkFenster)
    stepFrame2.pack()
    # zeige Puffer und Volumina als Checkliste zum editieren
    # Buttons - Quit, Weiter, Zurück

    buttonZurück=Button(master=stepFrame2, text='Zurück', command=step1)
    buttonZurück.pack()
    buttonBeenden=Button(master=stepFrame2, text='Beenden', command=quit)
    buttonBeenden.pack()
    buttonWeiter=Button(master=stepFrame2, text='Weiter', command=None)
    buttonWeiter.pack()

## Aktivierung des Fensters
step1()
tkFenster.mainloop()