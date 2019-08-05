
from EvoScriPy.protocol_steps import Protocol
import EvoScriPy.instructions as instr


class HelloWorld(Protocol):

    name = "Hello World"

    def __init__(self, GUI                         = None,
                       output_filename             = './scripts/hello_world',
                       worktable_template_filename = 'hello_world.ewt'):

        Protocol.__init__(self,
                          GUI                           = GUI,
                          output_filename               = output_filename,
                          worktable_template_filename   = worktable_template_filename)

    def Run(self):
        self.check_list()
        instr.userPrompt("Hello World!").exec()
        self.done()


if __name__ == "__main__":
    HelloWorld().Run()
