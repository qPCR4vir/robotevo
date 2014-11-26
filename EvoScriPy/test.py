__author__ = 'tobias.winterfeld'

import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.grid()
        self.createWidgets()

    def createWidgets(self):
        rtv = {'VEW1': 600, 'VEW2': 600, 'BindBuff': 800}
        r = 0
        for w in rtv:
            self.CheckList = tk.Checkbutton(text=w)
            self.CheckList.grid(row=r, sticky=tk.W)
            line = rtv[w], ' µl'
            self.stdVol = tk.Label(text=line)
            self.stdVol.grid(row=r, column=1)
            self.enterVol = tk.Entry(text=rtv[w])
            self.enterVol.grid(row=r, column=2, sticky=tk.W)
            r += 1


app = Application()
app.master.title('testing Checklist')
app.mainloop()