__author__ = 'tobias.winterfeld'

from tkinter import *

master = Tk()
'''frame = Frame(master)
'''
logo = PhotoImage(file="C:\Prog\EvoScriPy\FLI-Logo_mit_Farbverlauf.png")
w1 = Label(master, image=logo).grid(row=0, column=1)

class App:


    def __init__(self, frame, buttons = ['START', 'STOPP', 'PAUSE', 'Get Variable', 'Get Volumina', 'Quit']):
        frame2 = Frame(frame)
        r = 0
        frame2.grid(row=r, column=1)
        for b in buttons:
            self.button = Button(frame, text=buttons[r], command=frame.quit)
            self.button.grid(row=r+1, column=0)
            r += 1

app = App(master)
mainloop()
