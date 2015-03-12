from tkinter import *

# Ereignisbehandlung
def buttonWeiterClick():
    stand = int(labelZahl.cget('text'))
    stand = stand + 1
    labelZahl.config(text=str(stand))

def buttonZurueckClick():
    stand = int(labelZahl.cget('text'))
    stand = stand - 1
    labelZahl.config(text=str(stand))

def buttonNullClick():
    stand = int(labelZahl.cget('text'))
    stand = stand - stand
    labelZahl.config(text=str(stand))

# GUI-Objekte

# Fenster
tkFenster = Tk()
tkFenster.title('Zähler')
tkFenster.geometry('170x125')

# Label
labelZahl = Label(master=tkFenster, text='0', bg='gray', font=('Arial', 36))
labelZahl.place(x=5, y=5, width=160, height=80)

# Button
buttonWeiter = Button(master=tkFenster, text='weiter', bg='#D5E88F', command=buttonWeiterClick)
buttonWeiter.place(x=115, y=90, width=50, height=30)
buttonZurueck = Button(master=tkFenster, text='zurück', bg='#FFCFC9', command=buttonZurueckClick)
buttonZurueck.place(x=5, y=90, width=50, height=30)
buttonNull = Button(master=tkFenster, text='Null', bg='#FBD975', command=buttonNullClick)
buttonNull.place(x=60, y=90, width=50, height=30)

# Aktivierung des Fensters
tkFenster.mainloop()


"""
from tkinter import *

# Erzeugung des Fensters

tkFenster = Tk()
tkFenster.title('Kalender')
tkFenster.geometry('130x85')

# Label für die Anzeige der Daten

labelWochentag = Label(master=tkFenster, text='Montag', fg='white', bg='gray', font=('Arial', 16))
labelWochentag.place(x=5, y=5, width=120, height=20)

labelTag = Label(master=tkFenster, text='21', fg='red', bg='#FFCFC9', font=('Arial', 24))
labelTag.place(x=5, y=30, width=55, height=50)

schriftfarbe = labelTag.cget('fg')              # lesender Zugriff auf Attribute von labelTag
hintergrundfarbe = labelTag.cget('bg')          # lesender Zugriff auf Attribute von labelTag
schriftformat = labelTag.cget('font')           # lesender Zugriff auf Attribute von labelTag

labelMonat = Label(master=tkFenster, text='01')
labelMonat.config(fg=schriftfarbe)              # schreibender Zugriff auf Attribute von labelMonat
labelMonat.config(bg=hintergrundfarbe)          # schreibender Zugriff auf Attribute von labelMonat
labelMonat.config(font=schriftformat)           # schreibender Zugriff auf Attribute von labelMonat
labelMonat.place(x=70, y=30, width=55, height=50)

# Aktivierung des Fensters

tkFenster.mainloop()



from tkinter import *

# Erzeugung des Fensters

tkFenster = Tk()
tkFenster.title('Kalender')
tkFenster.geometry('130x145')

# Label für die Anzeige der Daten

labelMonat = Label(master=tkFenster, text='Januar', fg='white', bg='gray', font=('Arial', 16))
labelMonat.place(x=5, y=5, width=120, height=20)

labelTag = Label(master=tkFenster, text='21', fg='red', bg='#FFCFC9', font=('Arial', 72))
labelTag.place(x=5, y=30, width=120, height=80)

labelWochentag = Label(master=tkFenster, text='Montag', bg='gray')
labelWochentag.place(x=35, y=115, width=60, height=30)

# Aktivierung des Fensters

tkFenster.mainloop()
"""