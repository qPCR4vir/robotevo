# Copyright (C) 2014-2018, Ariel Vina Rodriguez ( Ariel.VinaRodriguez@fli.de , arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2018

__author__ = 'qPCR4vir'

import EvoScriPy.Robot as Rbt

encoding = 'Latin-1'      # ISO/IEC 8859-1

class Mode:
    """ (Base class) Define how we want to "interact" with the physical robot, or what kind of output we want from
    this script generator. Some options are: A worklist; a full Evoware script; only comments, etc.
    One import option is to create many of this outputs from a single run.
    """
    encoding = encoding
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

    def __init__(self, filename = None):
        self.set_file(filename)

    def exec(self, instr):
        s = toString.exec(self, instr) + "\n"  # \r
        if self.f is not None:
            self.f.write(s)  # .encode('Latin-1')
        return s  # or f ?

    def done(self):
        if self.f is not None:
            self.f.close()
            self.f = None
            # print(self.filename + " done")

    def open(self):
        if self.f is None:
            self.set_file(self.filename)

    def __del__(self):
        self.done()

    def set_file(self, filename=None):
        self.filename = filename
        self.f = open(filename, 'w', encoding=Mode.encoding) if filename is not None else None


class Comments(inFile):
    """  Create a list with all (and only with) the comments and the Groups. Useful to be shown immediately after generation,
    but also to the final user just before the actual physical run.
    """

    def __init__(self, identation_char=None, identattion_length=None, current_identation=None, filename=None):
        self.current_identation = current_identation if current_identation is not None else 0
        self.identattion_length = identattion_length or 4
        self.identation_char = identation_char or ' '
        self.comments = []
        inFile.__init__(self, filename)


    def exec(self, instr):
        from EvoScriPy.Instructions import comment, group, group_end

        if isinstance(instr, comment) or isinstance(instr, group):
            identation = self.identation_char * self.identattion_length * self.current_identation
            cmt = identation + instr.arg[0].data
            self.comments.append(cmt)
            if isinstance(instr, group):
                self.current_identation += 1
                cmt = '\n' + cmt
            if self.f is not None:
                s = cmt+"\n"
                self.f.write(s)



        if isinstance(instr, group_end): self.current_identation -= 1



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

    def __init__(self, filename=None, template=None, robot=None):
        ScriptBody.__init__(self, filename)
        assert isinstance(robot, Rbt.Robot)
        self.robot = robot            # ?? may be None?
        self.set_template(template)  # ??

    def set_template(self, template):
        self.robot.set_as_current()
        self.robot.set_worktable(template)       # ????
        self.templateNotAdded = True

    def add_template(self):
        if self.templateNotAdded:
            for line in self.robot.worktable.template:
                self.f.write((line[:-1] + "\n"))  # .encode('Latin-1')  \r
            self.templateNotAdded = False

    def exec(self, instr):
        self.robot.set_as_current()
        self.add_template()
        ScriptBody.exec(self, instr)


class iRobot(Mode):
    """ It will be used to validate instructions based on an the state of an internal model af the physical robot.
    It will check the kind and number of tips, and the volume already aspired in each tips, and the existence
    and current volume in wells in labware, etc. One basic use of this, is to garante that the robot will be actualize
    once and only once even when multiple modes are used.
    """
    def __init__(self, index,  nTips , arms=None):
        Mode.__init__(self )
        # import Robot as Rbt
        self.robot = Rbt.Robot(index=index, arms=arms, nTips=nTips)
        self.set_as_current()

    def exec(self, instr):
        assert (self.robot is instr.robot)
        self.set_as_current()
        instr.actualize_robot_state()

    def set_as_current(self):
        self.robot.set_as_current()


current = None   # Oppsss !!! Define

