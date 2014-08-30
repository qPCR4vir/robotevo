__author__ = 'qPCR4vir'

#from Instruction_Base import SriptONLY

class EvoMode:
    Tip_tNum = 4
    def exec(self, instr):
        pass

 #   def allowed(self, instr):
 #       return True

    def __del__(self):
        pass

class multiEvo(EvoMode):
    def __init__(self, EvoList = []):
        self.EvoList=EvoList
    def addMode(self, mode):
        self.EvoList+=[mode]
    def exec(self, instr):
        for m in self.EvoList:
            instr.exec(m)

class inFile (EvoMode):
    def __init__(self, filename):
        self.filename=filename
        self.f = open (filename,'a')

    def exec(self, instr):
#        if not self.allowed(instr):
#            return
        s="\n" + str(instr)
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


class AdvancedWorkList (inFile):

    def exec(self, instr):
#        if not self.allowed(instr):
#            return
        s="\nB;" + str(instr) + ";"
        #print (s)
        self.f.write(s)

    def allowed(self, instr):
        return not isinstance(instr,SriptONLY)


class ScriptBody (inFile):
    pass


class EvoCOM (EvoMode):
    pass


class EvoScript (EvoMode):
    pass


CurEvo = None

