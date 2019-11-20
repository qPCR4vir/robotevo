"""
Hello World!
------------

The classical, in the the world of programming, Hello World! example.
It will just shows that message in the screen of the PC controlling the robot and will wait
for user confirmation producing a typical sound.
"""

from EvoScriPy.protocol_steps import *


class HelloWorld(Protocol):
    """
    This is a very general protocol.
    Normally you will inherit from a Protocol class adapted to your real robot.
    """
    name = "Hello World"

    def __init__(self, GUI                         = None,
                       output_filename             = None,
                       worktable_template_filename = None):
        this = Path(__file__).parent
        Protocol.__init__(self,
                          GUI                           = GUI,
                          output_filename               = output_filename or this / 'scripts' / 'hello_world',
                          worktable_template_filename   = worktable_template_filename or this / 'hello_world.ewt')

    def run(self):
        self.check_list()
        self.user_prompt("Hello World!")
        self.done()


if __name__ == "__main__":
    HelloWorld().run()
