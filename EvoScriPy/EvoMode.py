__author__ = 'qPCR4vir'

# from Instruction_Base import ScriptONLY

class EvoMode:
    ''' (Base class) Define how we want to "interact" with the physical robot, or what kind of output we want from
    this script generator. Some options are: A worklist; a full Evoware script; only comments, etc.
    One import option is to create many of this outputs from a single run.
    '''
    encoding = 'Latin-1'
    # Tip_tNum = 4
    def exec(self, instr):
        pass

        #   def allowed(self, instr):
        #       return True

    def __del__(self):
        pass


class EvoString(EvoMode):
    ''' (Base class) Create an string representation of the instructions.
    '''
    def exec(self, instr):
        s = str(instr)
        return s


class EvoComments(EvoString):
    '''  Create a list with all (and only with) the comments. Useful to be shown immediately after generation,
    but also to the final user just before the actual physical run.
    '''
    def __init__(self):
        self.comments = []

    def exec(self, instr):
        from Instructions import comment

        if isinstance(instr, comment):
            self.comments.append("  " + instr.arg[0].data)


class EvoStdOut(EvoString):
    ''' Specially useful during debugging.
    '''
    def exec(self, instr):
        s = EvoString.exec(self, instr)
        print(s)
        return s


class multiEvo(EvoMode):
    ''' A collection (list) of all the "modes" to be generated in a single run
    '''
    def __init__(self, EvoList=[]):
        self.EvoList = EvoList

    def addMode(self, mode):
        self.EvoList += [mode]

    def exec(self, instr):
        for m in self.EvoList:
            instr.exec(m)


class inFile(EvoString):
    ''' (Base class) For modes with uses a file for output
    '''
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'w', encoding=EvoMode.encoding)

    def exec(self, instr):
        s = EvoString.exec(self, instr) + "\n"  #\r
        self.f.write(s)  #.encode('Latin-1')
        return s  # or f ?

    def done(self):
        if self.f is not None:
            self.f.close()
            self.f = None
            #print(self.filename + " done")

    def open(self):
        if self.f is None:
            self.f = open(self.filename, 'a', encoding=EvoMode.encoding)

    def __del__(self):
        self.done()


class AdvancedWorkList(inFile):
    def exec(self, instr):
        self.f.write("B;")  #.encode('Latin-1')
        return inFile.exec(self, instr)


class ScriptBody(inFile):
    pass


class EvoCOM(EvoMode): #todo Implement an online control of the evo soft using windows-COM automation
    pass


class EvoScript(ScriptBody):
    ''' Create a full and executable script for the evoware soft. Take an existing script or script-template as a base.
    '''
    def __init__(self, filename, template, arms):
        ScriptBody.__init__(self, filename)
        import Robot

        Robot.curRobot = Robot.Robot(templateFile=template, arms=arms)
        self.templateNotAdded = True

    def exec(self, instr):
        if self.templateNotAdded:
            from Robot import curRobot

            for line in curRobot.worktable.template:
                self.f.write((line[:-1] + "\n"))  #.encode('Latin-1')  \r
            self.templateNotAdded = False
        ScriptBody.exec(self, instr)


CurEvo = None

