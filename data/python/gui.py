__author__ = 'Ariel'

import tkinter
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from tkinter import filedialog
from tkinter import scrolledtext

class App(tkinter.Frame):

    def __init__(self):

        tkinter.Frame.__init__(self, tkinter.Tk(),  width=600, height=600)
        self.master.title('Adding new sequences')
        self.grid(sticky=tkinter.NS)

        self.winfo_toplevel().rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        w = 15
        h = 40

        self.ID_original = ID_list(self, "Load original list of ID", w, h)
        self.ID_original.grid(row=0, column=0, sticky=tkinter.NSEW)

        self.ID_add = ID_list(self, "Load ID to add", w, h)
        self.ID_add.grid(row=0, column=1, sticky=tkinter.NSEW)
        tkinter.Button(self, text="BLAST",
                             command=self.blast)                     .grid(row=2, column=1)

        self.ID_unique = ID_list(self, "Load", w, h)
        self.ID_unique.grid(row=0, column=2, sticky=tkinter.NSEW)
        tkinter.Button(self, text="Load BLAST",
                             command=self.load_blast)                .grid(row=2, column=2)
        tkinter.Button(self, text="Filter",
                             command=self.filter)                    .grid(row=3, column=2)

    def filter_add(self, add):
        ori  ={ID for ID in self.ID_original.lines()}
        uniq ={ID for ID in self.ID_unique.lines()}
        uniq ={ID for ID in add|uniq if ID not in ori}
        self.ID_add.clear()
        self.ID_unique.clear()
        for ID in uniq:
            self.ID_unique.txt_list.insert(tkinter.END, ID+'\n')

    def filter(self):
        add  ={ID for ID in self.ID_add.lines()}
        self.filter_add(add)

    def blast(self):
        IDs=[ID for ID in self.ID_add.lines()]
        print (' '.join(IDs))
        self.master.title('Toking to NCBI. Be VERY patient ...')
        result_handle = NCBIWWW.qblast("blastn", "nt", '\n'.join(IDs) )
        self.master.title('Adding new sequences')
        print('returned')
        blast_file_name = filedialog.asksaveasfilename(filetypes=(("BLAST (xml)", "*.xml"), ("All files", "*.*") ))
        with open(blast_file_name, mode='w') as blast_file:
            blast_file.write(result_handle.read())
        result_handle.close()
        # self.load_blast_data(result_handle)
        with open(blast_file_name, mode='r') as blast_file:
            self.load_blast_data(blast_file)

    def load_blast(self):
        with filedialog.askopenfile(filetypes=(("BLAST (xml)", "*.xml"), ("All files", "*.*") )) as blast_file:
            self.load_blast_data(blast_file)

    def load_blast_data(srefacelf,blast_data):
        add = set()
        blast_records = NCBIXML.parse(blast_data)
        for blast_record in blast_records:
            for alignment in blast_record.alignments:
                add.add(alignment.accession)           #alignment.title.split('|')[3].split('.')[0])
        self.filter_add(add)

class ID_list(tkinter.Frame):
    def __init__(self, root, load_titel, width=15, height=40):
        tkinter.Frame.__init__(self, root)
        self.grid(sticky=tkinter.NS)
        self.rowconfigure(1, weight=1)

        tkinter.Button(self, text=load_titel,
                             command=self.load)                      .grid(row=0, column=0, columnspan=2)
        self.txt_list = scrolledtext.ScrolledText(self,  width=width, height=height)
        self.txt_list                                                .grid(row=1, column=0, sticky=tkinter.NSEW, padx=2, pady=2, columnspan=2)
        tkinter.Button(self, text="clear",
                             command=self.clear)                     .grid(row=2, column=0)
        tkinter.Button(self, text="Save",
                             command=self.save)                      .grid(row=2, column=1)

    def clear(self):
        self.txt_list.delete(1.0, tkinter.END)

    def load(self):
        with filedialog.askopenfile(filetypes=(("TXT", "*.txt"), ("All files", "*.*") )) as ID_file:
            for line in ID_file:
                self.txt_list.insert(tkinter.END,line)

    def save(self):
        with filedialog.asksaveasfile(mode='w', filetypes=(("TXT", "*.txt"), ("All files", "*.*") )) as ID_file:
            ID_file.write('\n'.join(self.txt_list.get('1.0',tkinter.END).splitlines()))

    def lines(self):
        return self.txt_list.get('1.0',tkinter.END).splitlines()


if __name__=='__main__':
    App().mainloop()
