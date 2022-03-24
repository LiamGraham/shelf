import difflib
import inspect
from nis import match
from shutil import ExecError
from typing import Callable, List
from collections import OrderedDict

class CommandParsingError(Exception):
    pass

class NoMatchingCommandError(Exception):
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
        self._prefix_len = len(prefix.split())
        self.func = func
        self._args = OrderedDict()
        
        self.signature = prefix
        parameters = inspect.signature(func).parameters
        for name, param in parameters.items():
            if name == "self":
                continue
            if param.annotation == inspect.Parameter.empty:
                annotation = str
            else:
                annotation = param.annotation
            self._args[name] = annotation
            self.signature += f" <{name}:{annotation.__name__}>"


    def parse(self, text:str):
        """Parses the given command text and returns the result of the
        consequent function call using the command arguments.
        
        Arguments:
            text {str}: Command text to be parsed

        Returns:
            Result of function call using command arguments
        """
        text = text.strip()
        elements = text.split()[self._prefix_len:]
         
        if not self.matches(text, elements):
            raise CommandParsingError(f"\"{text}\" does not match \"{self.signature}\"")
        
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
                raise CommandParsingError(f"\"{target}\" invalid as \"{arg}\" for \"{self.signature}\"")
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
        return f"Command(signature=\"{self.signature}\")"

    def __str__(self) -> str:
        return self.__repr__()

class CommandParser:
    """Parser for internal commands. Parses command strings and executes the
    corresponding functions using the command arguments.
    """

    def __init__(self):
        """Creates a new, empty CommandParser"""
        self.commands: List[Command] = []
        self.prefixes = {}

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
        self.prefixes[command.prefix] = command

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
            raise NoMatchingCommandError(f"\"{text}\" does not match any command")
        
    def help(self):
        command_list = '\n'.join([f'  - {command.signature}' for command in self.commands])
        return f"Commands:\n\n{command_list}"
    
    def get_close_commands(self, text: str, n: int = 3, cutoff: float = 0.3) -> Command:
        """Returns the `n` commands from the the list of registered commands which are
        sufficiently similar to the given text.

        Arguments:
            text {str}: Text to compared against command prefixes
            n {int}: Maximum number of commands to return
            cutoff {float}: Similarity cutoff. Possibilities that don't score at least that 
                similar to word are ignored

        Returns:
            Commands which are sufficiently similar to the given text 
        """
        if not text:
            return []

        # By only using the initial 'word' within the command, and possibly omitting subsequent words
        # that might match the prefix of a valid command, we might capture other similar commands to then
        # suggest
        simple_prefix = text.split()[0]
        matches = difflib.get_close_matches(simple_prefix, self.prefixes.keys(), n, cutoff)
        return [self.prefixes[prefix] for prefix in matches] 

def shelf(parser: CommandParser, start_symbol: str = "> ", exit_command: str = "exit", help_command: str = "help"):
    """Initiates a shell using the given CommandParser. `start_symbol` is displayed before
    each new command ("> " by default). The shell can be exited by entering the given 
    `exit_command` ("exit" by default) or the ^C (KeyboardInterrupt) or ^D (EOF) 
    signals. 
    
    Arguments:
        parser {CommandParser} Parser with which user-entered commands will be parsed
        start_symbol {str}: String displayed at the start of each command
        exit_command {str}: Command that may be entered to exit the shell
    """
    while True:
        try:
            command = input(start_symbol).strip()
        except (KeyboardInterrupt, EOFError) as e:
            print()
            break

        if command == "":
            continue
        if command == help_command:
            print(parser.help(), "\n")
            continue
        if command == exit_command:
            break
        try:
            output = parser.parse(command)
            print(output)
        except NoMatchingCommandError as e:
            print("Unknown command:", e)
            closest_commands = parser.get_close_commands(command)
            if closest_commands:
                suggestions = "\n".join([f"  - {command.signature}" for command in closest_commands])
                print(f"\nThe most similar commands are:\n{suggestions}\n")
        except CommandParsingError as e:
            print(f"Invalid command: {e}\n")
        except Exception as e:
            print(f"Something went wrong. Error: {e}\n")
