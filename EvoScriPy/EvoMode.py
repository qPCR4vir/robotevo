__author__ = 'qPCR4vir'

#from Instruction_Base import ScriptONLY

class EvoMode:
    # Tip_tNum = 4
    def exec(self, instr):
        pass

 #   def allowed(self, instr):
 #       return True

    def __del__(self):
        pass

class EvoString(EvoMode):
    def exec(self, instr):
        s= str(instr)
        return s

class EvoComments(EvoString):
    def __init__(self):
        self.comments=[]
    def exec(self, instr):
        from Instructions import comment
        if isinstance(instr, comment):
            self.comments.append("  "+instr.arg[0].data)


class EvoStdOut(EvoString):
    def exec(self, instr):
        s=EvoString.exec(self,instr)
        print(s)
        return s

class multiEvo(EvoMode):
    def __init__(self, EvoList = []):
        self.EvoList=EvoList
    def addMode(self, mode):
        self.EvoList+=[mode]
    def exec(self, instr):
        for m in self.EvoList:
            instr.exec(m)

class inFile (EvoString):
    def __init__(self, filename):
        self.filename=filename
        self.f = open (filename,'wb')

    def exec(self, instr):
        s=EvoString.exec(self,instr) + "\r\n"
        self.f.write(s.encode('Latin-1'))
        return s   # or f ?

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
        self.f.write("B;".encode('Latin-1'))
        return inFile.exec(self,instr)

class ScriptBody (inFile):
    pass

class EvoCOM (EvoMode):
    pass


class EvoScript (ScriptBody):
    def __init__(self, filename, template, arms):
        ScriptBody.__init__(self,filename)
        import Robot
        Robot.curRobot=Robot.Robot(templateFile=template, arms=arms)
        self.templateNotAdded=True

    def exec(self, instr):
        if self.templateNotAdded:
            from Robot import curRobot
            for line in curRobot.worktable.template:
                self.f.write((line[:-1]+"\r\n").encode('Latin-1'))
            self.templateNotAdded=False
        ScriptBody.exec(self,instr)


CurEvo = None

