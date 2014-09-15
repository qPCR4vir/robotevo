__author__ = 'tobias.winterfeld'

from tkinter import *

master = Tk()

logo = PhotoImage(file="C:\Prog\EvoScriPy\FLI-Logo_mit_Farbverlauf.png")
w1 = Label(master, image=logo).grid(row=0, column=0)

r = 0
buttons = ['START', 'STOPP', 'PAUSE', 'Get Variable', 'Get Volumina', 'Quit']
class App:


    for b in buttons:
        def __init__(self, master, buttons = ['START', 'STOPP', 'PAUSE', 'Get Variable', 'Get Volumina', 'Quit']):
            frame = Frame(master)
            frame.grid(row=r, column=0)
            self.button = Button(frame, text=buttons, command=frame.quit)
            self.button.grid(row=r, column=0)
    r += 1

app = App(master)
mainloop()
