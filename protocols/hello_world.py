
from EvoScriPy.protocol_steps import Protocol
import EvoScriPy.Instructions as Itr

class HelloWorld(Protocol):

    name = "Hello World"

    def __init__(self, GUI = None):
        Protocol.__init__(self, GUI= GUI, output_filename = '../current/tests/hello_world')

    def Run(self):
        self.CheckList()
        Itr.userPrompt("Hello World!").exec()
        self.done()


if __name__ == "__main__":
    HelloWorld().Run()
