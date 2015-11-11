__author__ = 'Ariel'

import tkinter
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from tkinter import filedialog
from tkinter import scrolledtext

class App(tkinter.Frame):

    def __init__(self, mainw):

        tkinter.Frame.__init__(self, mainw,  width=600, height=600)
        self.mainwin=mainw
        self.mainwin.title('Adding new sequences')
        self.grid()

        w = 15
        h = 40

        tkinter.Button(self, text="Load original list of seq",
                             command=self.load_original)             .grid(row=0, column=0)
        self.txt_original = scrolledtext.ScrolledText(self,  width=w, height=h)#
        self.txt_original                                            .grid(row=1, column=0, sticky=tkinter.NSEW, padx=2, pady=2)
        tkinter.Button(self, text="clear",
                             command=self.clear_original)            .grid(row=2, column=0)
        tkinter.Button(self, text="Save",
                             command=self.save_original)             .grid(row=3, column=0)



        tkinter.Button(self, text="Load ID to add",
                             command=self.load_to_add)               .grid(row=0, column=1)
        self.txt_blast = scrolledtext.ScrolledText(self,  width=w)#, height=h+5
        self.txt_blast                                               .grid(row=1, column=1, sticky=tkinter.NSEW, padx=2, pady=2)
        tkinter.Button(self, text="clear",
                             command=self.clear_blast)               .grid(row=2, column=1)
        tkinter.Button(self, text="Save",
                             command=self.save_blast)                .grid(row=3, column=1)
        tkinter.Button(self, text="BLAST",
                             command=self.blast)                     .grid(row=4, column=1)


        tkinter.Button(self, text="Load",
                             command=self.load_unique)               .grid(row=0, column=2)
        self.txt_unique = scrolledtext.ScrolledText(self,  width=w)#, height=0
        self.txt_unique                                              .grid(row=1, column=2, sticky=tkinter.NSEW, padx=2, pady=2)
        tkinter.Button(self, text="clear",
                             command=self.clear_unique)              .grid(row=2, column=2)
        tkinter.Button(self, text="Save",
                             command=self.save_unique)               .grid(row=3, column=2)
        tkinter.Button(self, text="Load BLAST",
                             command=self.load_blast)                .grid(row=5, column=2)
        tkinter.Button(self, text="Filter",
                             command=self.filter)                    .grid(row=4, column=2)


    def clear_txt(self, txt_list):
        txt_list.delete(1.0, tkinter.END)

    def clear_original(self):
        self.clear_txt(self.txt_original)

    def clear_blast(self):
        self.clear_txt(self.txt_blast)

    def clear_unique(self):
        self.clear_txt(self.txt_unique)

    def load_IDs(self, txt_list):
        with filedialog.askopenfile(filetypes=(("TXT", "*.txt"), ("All files", "*.*") )) as ID_file:
            for line in ID_file:
                txt_list.insert(tkinter.END,line)

    def load_original(self):
        self.load_IDs(self.txt_original)

    def load_to_add(self):
        self.load_IDs(self.txt_blast)

    def load_unique(self):
        self.load_IDs(self.txt_unique)

    def save_IDs(self, txt_list):
        with filedialog.asksaveasfile(mode='w', filetypes=(("TXT", "*.txt"), ("All files", "*.*") )) as ID_file:
            ID_file.write('\n'.join(txt_list.get('1.0',tkinter.END).splitlines()))

    def save_original(self):
        self.save_IDs(self.txt_original)

    def save_blast(self):
        self.save_IDs(self.txt_blast)

    def save_unique(self):
        self.save_IDs(self.txt_unique)

    def filter_add(self, add):
        ori  ={ID for ID in self.txt_original.get('1.0',tkinter.END).splitlines()}
        uniq ={ID for ID in self.txt_unique.get('1.0',tkinter.END).splitlines()}
        uniq ={ID for ID in add|uniq if ID not in ori}
        self.clear_blast()
        self.clear_unique()
        for ID in uniq:
            self.txt_unique.insert(tkinter.END,ID+'\n')

    def filter(self):
        add  ={ID for ID in self.txt_blast.get('1.0',tkinter.END).splitlines()}
        self.filter_add(add)

    def blast(self):
        IDs=[ID for ID in self.txt_blast.get('1.0',tkinter.END).splitlines()]
        print (' '.join(IDs))
        self.mainwin.title('Toking to NCBI. Be VERY patient ...')
        result_handle = NCBIWWW.qblast("blastn", "nt", '\n'.join(IDs) )
        self.mainwin.title('Adding new sequences')
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

    def load_blast_data(self,blast_data):
        add = set()
        blast_records = NCBIXML.parse(blast_data)
        for blast_record in blast_records:
            for alignment in blast_record.alignments:
                add.add(alignment.accession)           #alignment.title.split('|')[3].split('.')[0])
        self.filter_add(add)


if __name__=='__main__':
    App(tkinter.Tk()).mainloop()
