__author__ = 'Ariel'

import tkinter
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from tkinter import filedialog
from tkinter import scrolledtext

class App(tkinter.Frame):

    def __init__(self, mainw):

        tkinter.Frame.__init__(self, mainw,  width=600, height=600)
        mainw.title('Adding new sequences')
        self.grid()
        # self.pack(fill="both", expand=True)
        # ensure a consistent GUI size
        # self.grid_propagate(False)
        # implement stretchability
        # self.grid_rowconfigure(3, weight=3)
        # self.grid_columnconfigure(4, weight=4)

        self.original_file_name= None
        self.original_file = None
        self.IDs =set()
        w = 15
        h = 40

        tkinter.Button(self, text="Load original list of seq",
                             command=self.load_original)             .grid(row=0, column=0)
        self.txt_original = scrolledtext.ScrolledText(self, height=h, width=w)
        self.txt_original                                            .grid(row=1, column=0, sticky="nsew", padx=2, pady=2, columnspan=2)


        tkinter.Button(self, text="Load ID to add",
                             command=self.load_to_add)             .grid(row=0, column=2, columnspan=2)
        self.txt_blast = scrolledtext.ScrolledText(self, height=h, width=w)
        self.txt_blast                                               .grid(row=1, column=2, sticky="nsew", padx=2, pady=2, columnspan=2)
        tkinter.Button(self, text="clear",
                             command=self.clear_blast)               .grid(row=2, column=2)
        tkinter.Button(self, text="BLAST",
                             command=self.blast)                     .grid(row=2, column=3)


        tkinter.Button(self, text="Filter",
                             command=self.filter)                    .grid(row=0, column=4, columnspan=2)
        self.txt_unique = scrolledtext.ScrolledText(self, height=h, width=w)
        self.txt_unique                                              .grid(row=1, column=4, sticky="nsew", padx=2, pady=2, columnspan=2)
        tkinter.Button(self, text="clear",
                             command=self.clear_unique)              .grid(row=2, column=4)
        tkinter.Button(self, text="Load BLAST",
                             command=self.load_blast)                .grid(row=2, column=5)

    def clear_blast(self):
        self.txt_blast.delete(1.0, tkinter.END)

    def clear_unique(self):
        self.txt_unique.delete(1.0, tkinter.END)

    def load_original(self):
        with filedialog.askopenfile(filetypes=( ("TXT", "*.txt"), ("All files", "*.*") )) as original:
            self.txt_original.delete(1.0, tkinter.END)
            for line in original:
                self.txt_original.insert(tkinter.END,line)


    def load_to_add(self):
        with filedialog.askopenfile(filetypes=(("TXT", "*.txt"), ("All files", "*.*") )) as to_add_file:
            for line in to_add_file:
                self.txt_blast.insert(tkinter.END,line)

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
        for ID in self.txt_blast.get('1.0',tkinter.END).splitlines() :
            print (ID)
            result_handle = NCBIWWW.qblast("blastn", "nt", ID)
            print (ID)
            blast_records = NCBIXML.parse(result_handle)
            for blast_record in blast_records:
                for alignment in blast_record.alignments:
                    print (alignment.title.split('|')[3].split('.')[0])
                    """
                    for hsp in alignment.hsps:
                        if hsp.expect < 0.01 :
                            print('****Alignment****')
                            print('sequence:', alignment.title)
                            print('length:', alignment.length)
                            print('e value:', hsp.expect)
                            print(hsp.query[0:75] + '...')
                            print(hsp.match[0:75] + '...')
                            print(hsp.sbjct[0:75] + '...')
                    """

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
