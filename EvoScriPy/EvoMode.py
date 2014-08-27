__author__ = 'elisa.reader'


class EvoMode:
    Tip_tNum = 4
    def exec(self, instr):
        pass

    def __del__(self):
        pass

class AdvancedWorkList (EvoMode):
    def __init__(self, filename):
        self.filename=filename
        self.f = open (filename,'a')

    def exec(self, instr):
        s="\n" + str(instr)
        print (s)
        self.f.write(s)

    def done(self):
        if self.f is not None:
            self.f.close()
            self.f=None
            #print(self.filename + " done")

    def open(self):
        if self.f is None:
            self.f = open (self.filename,'a')

    def __del__(self):
        self.done()




class EvoCOM (EvoMode):
    pass


class EvoScript (EvoMode):
    pass


CurEvo = None

