__author__ = 'tobias.winterfeld'


from tkinter import *
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

class App:
  def __init__(self, master):
    frame = Frame(master)
    frame.pack(side="left")

    self.button = Button(frame,
                         text="START", fg="green", bg="black",
                         command=self.write_slogan)
    self.button.pack(side="center")

    self.button1 = Button(frame,
                         text="STOPP", fg="red", bg="black",
                         command=self.write_slogan)
    self.button1.pack(side="center")

    self.button2 = Button(frame,
                         text="Pause", fg="yellow", bg="black",
                         command=self.write_slogan)
    self.button2.pack(side="center")

    self.button3 = Button(frame,
                         text="Hallo", fg="red", bg="black",
                         command=self.write_slogan)
    self.button3.pack(side="center")

    self.slogan = Button(frame,
                         text="QUIT",
                         command=frame.quit)
    self.slogan.pack(side="center")
  def write_slogan(self):
      msg.pack(),








app = App(root)
root.mainloop()
