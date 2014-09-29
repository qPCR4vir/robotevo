__author__ = 'tobias.winterfeld'

from tkinter import *

"""
'''
colours = ['red','green','orange','white','yellow','blue']

for r,c in enumerate( colours):
    Label(text=c, relief=RIDGE,width=15).grid(row=r,column=0)
    Entry(bg=c, relief=SUNKEN,width=10).grid(row=r,column=1)

mainloop()


import tkinter as tk
import random

root = tk.Tk()
# width x height + x_offset + y_offset:
root.geometry("170x200+30+30")

languages = ['Python','Perl','C++','Java','Tcl/Tk']
labels = range(5)
for i in range(5):
   ct = [random.randrange(256) for x in range(3)]
   brightness = int(round(0.299*ct[0] + 0.587*ct[1] + 0.114*ct[2]))
   ct_hex = "%02x%02x%02x" % tuple(ct)
   bg_colour = '#' + "".join(ct_hex)
   l = tk.Label(root,
                text=languages[i],
                fg='White' if brightness < 120 else 'Black',
                bg=bg_colour)
   l.place(x = 20, y = 30 + i*30, width=120, height=25)
'''

master = Tk()
SampFrame = Frame(master)
ButtonFrame = Frame(master)
KitFrame = Frame(master)
VarFrame = Frame(master)

logo = PhotoImage(file="C:\Prog\EvoScriPy\FLI-Logo_mit_Farbverlauf.png")
w1 = Label(master, image=logo).grid(row=0, column=1)

class App:


    def __init__(self, ButtonFrame, buttons = ['START', 'STOPP', 'PAUSE', 'Get Variable', 'Get Volumina', 'Quit']):
        frame = Frame(ButtonFrame)
        r = 0
        frame.grid(row=r, column=1)
        for b in buttons:
            self.button = Button(frame, text=buttons[r], command=frame.quit)
            self.button.grid(row=r+1, column=0)
            r += 1



app = App(master)
root.mainloop()
"""

from tkinter import ttk
import tkinter

root = tkinter.Tk()

style = ttk.Style()
style.layout("TMenubutton", [
   ("Menubutton.background", None),
   ("Menubutton.button", {"children":
       [("Menubutton.focus", {"children":
           [("Menubutton.padding", {"children":
               [("Menubutton.label", {"side": "left", "expand": 1})]
           })]
       })]
   }),
])

mbtn = ttk.Menubutton(text='Text')
mbtn.pack()
root.mainloop()
