__author__ = 'Ariel'

import tkinter
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio import Entrez
Entrez.email = "ArielVina.Rodriguez@fli.bund.de"
from Bio import SeqIO
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
        ori  = set(self.ID_original.lines())
        uniq = set(self.ID_unique.lines())
        uniq.update(add)
        uniq -= ori
        self.ID_add.clear()
        self.ID_unique.clear()
        for ID in uniq:
            self.ID_unique.add(ID)

    def filter(self):
        self.filter_add(self.ID_add.lines())

    def blast(self):
        IDs = self.ID_add.lines()
        print (' '.join(IDs))
        self.master.title('Toking to NCBI. Running BLAST. Be VERY patient ...')
        result_handle = NCBIWWW.qblast("blastn", "nt", '\n'.join(IDs))#, hitlist_size=50, perc_ident=90, threshold=1, alignments=50, filter="HEV", format_type='XML', results_file=blast_file_name )
        self.master.title('Adding new sequences')
        print('returned')
        blast_file_name = filedialog.asksaveasfilename(filetypes=(("BLAST", "*.xml"), ("All files", "*.*") ), defaultextension='xml', title='Save the BLAST result in XML format')
        with open(blast_file_name, mode='w') as blast_file:
            blast_file.write(result_handle.read())
        result_handle.close()
        # self.load_blast_data(result_handle)
        with open(blast_file_name, mode='r') as blast_file:
            self.load_blast_data(blast_file)

    def load_blast(self):
        with filedialog.askopenfile(filetypes=(("BLAST (xml)", "*.xml"), ("All files", "*.*") ), title='Load a BLAST result in XML format') as blast_file:
            self.load_blast_data(blast_file)

    def load_blast_data(srefacelf,blast_data):
        IDs = set()
        blast_records = NCBIXML.parse(blast_data)
        for blast_record in blast_records:
            for alignment in blast_record.alignments:
                IDs.add(alignment.accession)           # alignment.title.split('|')[3].split('.')[0])
        self.filter_add(IDs)

class ID_list(tkinter.Frame):
    def __init__(self, root, load_titel, width=15, height=40):
        tkinter.Frame.__init__(self, root)
        self.grid(sticky=tkinter.NS)
        self.rowconfigure(1, weight=1)

        tkinter.Button(self, text=load_titel,
                             command=self.load)                      .grid(row=0, column=0, columnspan=3)
        self.txt_list = scrolledtext.ScrolledText(self,  width=width, height=height)
        self.txt_list                                                .grid(row=1, column=0, sticky=tkinter.NSEW, padx=2, pady=2, columnspan=3)
        tkinter.Button(self, text="clear",
                             command=self.clear)                     .grid(row=2, column=0)
        tkinter.Button(self, text="Save",
                             command=self.save)                      .grid(row=2, column=1)
        tkinter.Button(self, text="Get",
                             command=self.get)                       .grid(row=2, column=2 )

    def add(self, ID):
        self.txt_list.insert(tkinter.END, ID+'\n')

    def clear(self):
        self.txt_list.delete(1.0, tkinter.END)

    def load(self):
        with filedialog.askopenfile(filetypes=(("TXT", "*.txt"), ("All files", "*.*") ), title='Load a ID list in txt format') as ID_file:
            self.add(ID_file.read())
            #for ID in ID_file:
            #    self.add(ID)

    def save(self):
        with filedialog.asksaveasfile(mode='w', filetypes=(("TXT", "*.txt"), ("All files", "*.*") ), defaultextension='txt', title='Save the ID list in txt format') as ID_file:
            ID_file.write('\n'.join(self.lines()))

    def lines(self):
        return self.txt_list.get('1.0',tkinter.END).splitlines()

    def get(self):
        IDs = ', '.join(self.lines())
        print (IDs)
        self.master.master.title('Toking to NCBI. Getting sequences. Be VERY patient ...')
        seq_handle = Entrez.efetch(db="nuccore", id=IDs, rettype="gb", retmode="XML" )# Entrez.efetch(db="nucleotide", id="57240072", rettype="gb", retmode="text")
        self.master.master.title('Adding new sequences')
        print('returned')
        xml_file_name = filedialog.asksaveasfilename(filetypes=(("Seq (xml)", "*.xml"), ("All files", "*.*") ), defaultextension='xml', title='Save the GenBank sequences in XML format')
        fasta_file_name = xml_file_name.replace('.xml', '.fasta')
        csv_file_name = xml_file_name.replace('.xml', '.csv')
        with open(xml_file_name, mode='w') as seq_file:
            for line in seq_handle:
                seq_file.write(line)
        seq_handle.close()
        for seq_record in SeqIO.parse("ls_orchid.gbk", "genbank"):
            print(seq_record.id)
            print(repr(seq_record.seq))
            print(len(seq_record))

        # self.load_blast_data(result_handle)
        #with open(blast_file_name, mode='r') as blast_file:
        #    self.load_blast_data(blast_file)

if __name__=='__main__':
    App().mainloop()
