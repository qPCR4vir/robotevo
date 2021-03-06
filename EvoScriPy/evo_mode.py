# Copyright (C) 2014-2019, Ariel Vina Rodriguez ( arielvina@yahoo.es )
#  distributed under the GNU General Public License, see <http://www.gnu.org/licenses/>.
#
# author Ariel Vina-Rodriguez (qPCR4vir)
# 2014-2019
"""
RobotEvo "modes" for execution of basic instructions
====================================================

Define how we want to "interact" with the physical robot, or what kind of output we want from
    this script generator.

 - :py:class:`Mode`
 - :py:class:`ToString`: an string representation of the instructions.
 - :py:class:`Multiple`: A collection (list) of all the "modes" to be generated in a single run
 - :py:class:`ToFile`:
 - :py:class:`Comments`:
 - :py:class:`AdvancedWorkList`:
 - :py:class:`ScriptBody`:
 - :py:class:`Script`:
 - :py:class:`iRobot`: update the state of the "internal" robot to track changes produced by the execution of the instructions.
 after each instruction.
 - :py:class:`AdvancedWorkList`:




 ---------

"""

__author__ = 'qPCR4vir'

"""
Implement the "modes" in which RobotEvo execute the low levels instructions, effectively creating the corresponding
type of "output".
"""
from pathlib import Path
import logging
from EvoScriPy.robot import Robot

encoding = 'Latin-1'        # ISO/IEC 8859-1
newline = '\r\n'            # windows newline

base_dir = Path(__file__).parent.parent


class Mode:
    """
    (Base class) Define how we want to "interact" with the physical robot, or what kind of output we want from
    this script generator. Some options are: A worklist; a full Evoware script; only comments, etc.
    One important option is to create many of this outputs from a single run.
    """
    encoding = encoding
    newline = newline

    def exec(self, instr):
        pass

        # def allowed(self, instructions):
        #       return True

    def done(self):
        pass

    def __del__(self):
        self.done()
        pass


class ToString(Mode):
    """
    (Base class) Create an string representation of the instructions.
    """

    def exec(self, instr):
        s = str(instr)
        return s


class StdOut(ToString):
    """
    Specially useful during debugging.
    """

    def exec(self, instr):
        s = ToString.exec(self, instr)
        logging.debug(s)
        return s


class Multiple(Mode):
    """
    A collection (list) of all the "modes" to be generated in a single run
    """

    def __init__(self, modes=None):
        self.modes = modes if modes is not None else []

    def add_mode(self, mode):
        self.modes += [mode]

    def exec(self, instr):
        for m in self.modes:
            instr.exec(m)

    def done(self):
        for m in self.modes:
            m.done()


class ToFile(ToString):
    """
    (Base class) For modes with uses a file for output
    """

    def __init__(self, filename = None, immediate=None):
        self.immediate = immediate
        self.lines = []
        self.f = None
        self.filename = None
        self.set_file(filename)
        self.encoding = Mode.encoding
        self.newline = Mode.newline

    def exec(self, instr):
        s = ToString.exec(self, instr) + "\n"  # \r
        if self.f is not None:
            if self.immediate:
                self.lines += [s]
            else:
                self.f.write(s)  # .encode('Latin-1')
        return s  # or f ?

    def done(self):
        if self.f is not None:
            if self.immediate:
                for s in self.lines:
                    self.f.write(s)
            self.f.close()
            self.f = None
            # logging.debug(str(self.filename.relative_to(base_dir)) + " done")

    def open(self):
        if self.f is None:
            self.set_file(self.filename)

    def __del__(self):
        self.done()

    def set_file(self, filename=None):
        self.done()       # ??
        self.filename = filename
        self.f = open(filename, 'w', encoding=self.encoding, newline=self.newline) if filename is not None else None
        logging.info("Opened file for script: " + str(filename.relative_to(base_dir)))


class Comments(ToFile):
    """
    Create a list with all (and only with) the comments and the Groups.
    Useful to be shown immediately after generation,
    but also to the final user just before the actual physical run.
    """

    def __init__(self, identation_char=None, identattion_length=None, current_identation=None, filename=None):
        self.current_identation = current_identation if current_identation is not None else 0
        self.identattion_length = identattion_length or 4
        self.identation_char = identation_char or ' '
        self.comments = []
        ToFile.__init__(self, filename)

    def exec(self, instr):
        from EvoScriPy.instructions import comment, group, group_end

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

        if isinstance(instr, group_end):
            self.current_identation -= 1


class AdvancedWorkList(ToFile):
    def exec(self, instr):
        self.f.write("B;")  # .encode('Latin-1')
        return ToFile.exec(self, instr)


class ScriptBody(ToFile):
    pass


class COM_automation(Mode):  # todo Implement an online control of the evo soft using windows-COM automation
    pass


class Script(ScriptBody):
    """ Create a full and executable script for the evoware soft. Take an existing script or script-template as a base.
    """

    def __init__(self, filename=None, template=None, robot_protocol=None, robot=None):
        self.templateNotAdded = True
        ScriptBody.__init__(self, filename)
        assert isinstance(robot, Robot)
        self.robot = robot            # ?? may be None?
        self.set_template(template, robot_protocol)  # ??

    def set_template(self, template, robot_protocol):
        self.robot.set_as_current()
        self.robot.set_worktable(template, robot_protocol)       # ????
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
    """
    Used to validate instructions based on an the state of an internal model af the physical robot.
    It will check the kind and number of tips, and the volume already aspired in each tips, and the existence
    and current volume in wells in labware, etc.
    One basic use of this, is to guarantee that the robot will be actualized
    once and only once even when multiple modes are used.
    """
    def __init__(self, index,  n_tips, arms=None, tips_type=None):
        Mode.__init__(self)
        self.robot = Robot(index=index, arms=arms, n_tips=n_tips, tips_type=tips_type)
        self.set_as_current()

    def exec(self, instr):
        assert (self.robot is instr.robot)
        self.set_as_current()
        instr.actualize_robot_state()

    def set_as_current(self):
        self.robot.set_as_current()


current = None   # Intended to be the principal mode of the current protocol. Mostly mulitiple
