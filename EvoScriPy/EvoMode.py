__author__ = 'elisa.reader'


class EvoMode:
    Tip_tNum = 4
    def exec(self, instr):
        pass


class AdvancedWorkList (EvoMode):
    def __init__(self, filename):
        self.filename=filename
        self.f = open (filename,'a')

    def exec(self, instr):
        s="\n" + str(instr)
        print (s)
        self.f.write(s)


class EvoCOM (EvoMode):
    pass


class EvoScript (EvoMode):
    pass


CurEvo = None

