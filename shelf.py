import inspect
from typing import Callable
from collections import OrderedDict

class CommandError(Exception):
    pass


class Command:

    def __init__(self, prefix:str, func:Callable):
        """Creates a new command based on the given function and having the
        specified prefix. The prefix defines the non-variable component of the
        command occuring at the start, and the function defines the command
        arguments and their types (based on type annotations). If an argument
        is not type annotated, the argument type will default to str. The
        specified types must readily accept single values. Commands do not
        support optional or named arguments - all arguments are positional.

        Usage:
        def get(a:int, b:str):
            return a, b

        class Rectangle:
            def __init__(self, height:int, width:int):
                ...

            def set_dimensions(self, height:int, width:int):
                self.height = height
                self.width = width

        >> command = Command("get", get)
        >> command.parse("get 1 new")
        (1, "new")
        >> rect = Rectangle(5, 10)
        >> command = Command("rect set", rect.set_dimension)
        >> command.parse("rect set 20 30")
        >> rect.height
        20

        Arguments:
            prefix {str}: Prefix of command
            func {Callable}: Function to be called upon parsing. Defines
                command arguments
        """
        self.prefix = prefix
        self._prefix_len = len(prefix.split(" "))
        self.func = func
        self._args = OrderedDict()
        
        self._signature = prefix
        parameters = inspect.signature(func).parameters
        for name, param in parameters.items():
            if name == "self":
                continue
            if param.annotation == inspect.Parameter.empty:
                annotation = str
            else:
                annotation = param.annotation
            self._args[name] = annotation
            self._signature += f" <{name}:{annotation.__name__}>"


    def parse(self, text:str):
        """Parses the given command text and returns the result of the
        consequent function call using the command arguments.
        
        Arguments:
            text {str}: Command text to be parsed

        Returns:
            Result of function call using command arguments
        """
        text = text.strip()
        elements = text.split(" ")[self._prefix_len:]
        start = end = 0
        for i, x in enumerate(elements):
            if x.startswith("\""):
                start = i
            if x.endswith("\""):
                end = i
                break
        if start != end:
            quoted = " ".join(elements[start:end+1])
            elements = elements[:start] + [quoted]
         
        if not self.matches(text, elements):
            raise CommandError(f"\"{text}\" does not match \"{self._signature}\"")
        
        arg_values = {}
        arg_order = []
        for i, arg in enumerate(self._args):
            annotation = self._args[arg]
            target = elements[i]
            try:
                value = annotation(target)
                arg_values[arg] = value 
                arg_order.append(value) 
            except (ValueError, TypeError):
                raise CommandError(f"\"{target}\" invalid as \"{arg}\" for \"{self._signature}\"")
        return self.func(**arg_values)

    def partial(self, text:str):
        text = text.strip()
        return text.startswith(self.prefix)

    def matches(self, text: str, elements) -> bool:
        """
        Determines if the given command text matches this command. Does not
        perform any type checking.

        Arguments:
            text {str}: Command text to match

        Returns:
            True if the given command text matches this command, otherwise
            false
        """
        return self.partial(text) and len(self._args) == len(elements)

    def __repr__(self) -> str:
        return f"Command(signature=\"{self._signature}\")"

    def __str__(self) -> str:
        return self.__repr__()

class CommandParser:
    """Parser for internal commands. Parses command strings and executes the
    corresponding functions using the command arguments.
    """

    def __init__(self):
        """Creates a new, empty CommandParser"""
        self.commands = []

    def add_command(self, prefix:str, func:Callable):
        """Adds a command to this parser having the specified prefix and based
        on the given function. See Command for further description of
        arguments.

        Arguments:
            prefix {str}: Prefix of command
            funct {Callable}: Base function of command
        """
        command = Command(prefix, func)
        self.commands.append(command)

    def parse(self, text:str):
        """Parses the given command text. See Command.parse for more details.

        Arguments:
            text {str}: Command text to parse

        Returns:
            Result of subsequent command call
        """
        for command in self.commands:
            if command.partial(text):
                return command.parse(text)
        else:
            raise CommandError(f"\"{text}\" does not match any command")

