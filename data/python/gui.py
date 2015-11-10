__author__ = 'Ariel'

import tkinter
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from tkinter import filedialog

class App(tkinter.Frame):

    def __init__(self):

        tkinter.Frame.__init__(self, tkinter.Tk())
        self.grid()

        self.original_file_name= None
        self.original_file = None

        tkinter.Label(self, text='Original list of seq').grid(row=1, column=1, columnspan=1)
        tkinter.Button(self, text="Load",
                             command=self.load_original).grid(row=1, column=2, columnspan=1)
        self.txt_original = tkinter.Text(self)
        self.txt_original.grid(row=2, column=1, columnspan=2)

        tkinter.Button(self, text="Load ID to BLAST",
                             command=self.load_to_blast).grid(row=1, column=3, columnspan=1)
        self.txt_blast = tkinter.Text(self)
        self.txt_blast.grid(row=2, column=3, columnspan=1)
        tkinter.Button(self, text="BLAST",
                                  command=self.print_blast).grid(row=3, column=3, columnspan=1)

        tkinter.Label(self, text='To insert').grid(row=1, column=4, columnspan=1)
        self.txt_blast_unique = tkinter.Text(self)
        self.txt_blast_unique.grid(row=2, column=4, columnspan=1)
        tkinter.Button(self, text="Load BLAST",
                                  command=self.load_blast).grid(row=3, column=4, columnspan=1)

    def load_original(self):
        self.original_file = filedialog.askopenfile(filetypes=( ("TXT", "*.txt"), ("All files", "*.*") ))
        if self.original_file:
            # self.txt_original.edit_reset()
            self.txt_original.delete(1.0, tkinter.END)
            for line in self.original_file:
                self.txt_original.insert(tkinter.END,line)
            self.original_file.close()

    def load_to_blast(self):
        self.to_blast_file = filedialog.askopenfile(filetypes=(("TXT", "*.txt"), ("All files", "*.*") ))
        if self.to_blast_file:
            # self.txt_original.edit_reset()
            self.txt_blast.delete(1.0, tkinter.END)
            for line in self.to_blast_file:
                self.txt_blast.insert(tkinter.END,line)
            self.to_blast_file.close()

    def load_blast(self):
        self.blast_file = filedialog.askopenfile(filetypes=(("BLAST (xml)", "*.xml"), ("All files", "*.*") ))
        if self.blast_file:
            to_add = set()
            blast_records = NCBIXML.parse(self.blast_file)
            for blast_record in blast_records:
                for alignment in blast_record.alignments:
                    to_add.add(alignment.accession) #alignment.title.split('|')[3].split('.')[0])
            self.txt_blast_unique.delete(1.0, tkinter.END)
            for line in to_add:
                self.txt_blast_unique.insert(tkinter.END,line)
            self.blast_file.close()

    def print_blast(self):

        for ID in self.txt_blast.get('1.0',tkinter.END).splitlines() :
            print (ID)
            # result_handle = NCBIWWW.qblast("blastn", "nt", ID)
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


if __name__=='__main__':
    App().mainloop()
