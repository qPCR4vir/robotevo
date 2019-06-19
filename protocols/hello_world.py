
from EvoScriPy.protocol_steps import Protocol
import EvoScriPy.Instructions as Itr

class HelloWorld(Protocol):

    name = "Hello World"

    def __init__(self, GUI = None):
        Protocol.__init__(self,
                          GUI                           = GUI,
                          output_filename               = '../current/tests/hello_world',
                          worktable_template_filename   = '../EvoScripts/wt_templates/Prefill_VEW1_ElutB_and_VEW2.ewt')

    def Run(self):
        self.check_list()
        Itr.userPrompt("Hello World!").exec()
        self.done()


if __name__ == "__main__":
    HelloWorld().Run()
