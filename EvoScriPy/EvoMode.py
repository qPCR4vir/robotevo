__author__ = 'qPCR4vir'

import Robot as Rbt

class Mode:
    """ (Base class) Define how we want to "interact" with the physical robot, or what kind of output we want from
    this script generator. Some options are: A worklist; a full Evoware script; only comments, etc.
    One import option is to create many of this outputs from a single run.
    """
    encoding = 'Latin-1'
    # Tip_tNum = 4
    def exec(self, instr):
        pass

        # def allowed(self, instr):
        #       return True

    def __del__(self):
        pass

class toString(Mode):
    """ (Base class) Create an string representation of the instructions.
    """

    def exec(self, instr):
        s = str(instr)
        return s


class Comments(toString):
    """  Create a list with all (and only with) the comments and the Groups. Useful to be shown immediately after generation,
    but also to the final user just before the actual physical run.
    """

    def __init__(self):
        self.comments = []

    def exec(self, instr):
        from Instructions import comment, group

        if isinstance(instr, comment) or isinstance(instr, group):
            self.comments.append("  " + instr.arg[0].data)




class StdOut(toString):
    """ Specially useful during debugging.
    """

    def exec(self, instr):
        s = toString.exec(self, instr)
        print(s)
        return s


class multiple(Mode):
    """ A collection (list) of all the "modes" to be generated in a single run
    """

    def __init__(self, EvoList=[]):
        self.EvoList = EvoList

    def addMode(self, mode):
        self.EvoList += [mode]

    def exec(self, instr):
        for m in self.EvoList:
            instr.exec(m)


class inFile(toString):
    """ (Base class) For modes with uses a file for output
    """

    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'w', encoding=Mode.encoding)

    def exec(self, instr):
        s = toString.exec(self, instr) + "\n"  # \r
        self.f.write(s)  # .encode('Latin-1')
        return s  # or f ?

    def done(self):
        if self.f is not None:
            self.f.close()
            self.f = None
            # print(self.filename + " done")

    def open(self):
        if self.f is None:
            self.f = open(self.filename, 'w', encoding=Mode.encoding)

    def __del__(self):
        self.done()


class AdvancedWorkList(inFile):
    def exec(self, instr):
        self.f.write("B;")  # .encode('Latin-1')
        return inFile.exec(self, instr)


class ScriptBody(inFile):
    pass


class COM_automation(Mode):  # todo Implement an online control of the evo soft using windows-COM automation
    pass


class Script(ScriptBody):
    """ Create a full and executable script for the evoware soft. Take an existing script or script-template as a base.
    """

    def __init__(self, filename, template, arms=None):
        ScriptBody.__init__(self, filename)
        if Rbt.Robot.current:
            Rbt.Robot.current.set_worktable(template)
        else:
            Rbt.Robot.current = Rbt.Robot(templateFile=template, arms=arms)
        self.templateNotAdded = True

    def exec(self, instr):
        if self.templateNotAdded:
            for line in Rbt.Robot.current.worktable.template:
                self.f.write((line[:-1] + "\n"))  # .encode('Latin-1')  \r
            self.templateNotAdded = False
        ScriptBody.exec(self, instr)


class iRobot(Mode):
    """ It will be used to validate instructions based on an the state of an internal model af the physical robot.
    It will check the kind and number of tips, and the volume already aspired in each tips, and the existence
    and current volume in wells in labware, etc. One basic use of this, is to garante that the robot will be actualize
    once and only once even when multiple modes are used.
    """
    def __init__(self, index,  nTips=4 , arms=None):
        Mode.__init__(self )
        # import Robot as Rbt
        Rbt.Robot.current = Rbt.Robot(index=index, arms=arms, nTips=nTips)
        Rbt.Robot.current.set_as_current()
        pass

    def exec(self, instr):
        instr.actualize_robot_state()


current = None

