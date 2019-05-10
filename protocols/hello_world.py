
from EvoScriPy.protocol_steps import Protocol
import EvoScriPy.Instructions as Itr

class HelloWorld(Protocol):

    name = "Hello World"

    def __init__(self):
        Protocol.__init__(self, output_filename = '../current/tests/hello_world')

    def Run(self):
        self.initialize()
        Itr.userPrompt("Hello World!").exec()
        self.done()


if __name__ == "__main__":
    HelloWorld().Run()