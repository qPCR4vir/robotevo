__author__ = 'tobias.winterfeld'


from tkinter import *

root = Tk()
logo = PhotoImage(file='..\EvoScriPy\FLI-Logo_mit_Farbverlauf.png')
w1 = Label(root, image=logo).pack(side="top")
explanation = """Hier entsteht die neue Grafische Benutzeroberfläche
für die einfache Anwendung der automatisierten RNA-Extraktion"""
w2 = Label(root,
           justify=CENTER,
           padx = 10,
           text=explanation).pack(side="bottom")
root.mainloop()
