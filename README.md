# shelf

Create a basic custom shell for your application.

## Usage

Write your application as normal. Include appropriate type annotations for all
function parameters (if no type annotation is included any arguments will be
parsed as strings). The specified type must accept a single value. 

```python
def add(a:int, b:int):
    return a + b

class Rectangle:
    def __init__(self, height:int, width:int):
        ...

    def set_dimensions(self, height:int, width:int):
        self.height = height
        self.width = width
```

Create a CommandParser and register each of your functions with a non-variable prefix
(e.g. "add").

```python
>>> from shelf import CommandParser
>>> parser = CommandParser()
>>> parser.add_command("add", add)
>>> rect = Rectangle(5, 10)
>>> parser.add_command("rect set", rect.set_dimension)
```

Parse commands using the `parse()` method to receive the corresponding output.

```python
>>> command.parse("add 1 2")
3
>>> command.parse("rect set 20 30")
>>> rect.height
20
```

Use `shelf()` to initiate a shell using a created CommandParser.

```python
>>> from shelf import shelf
>>> shelf(parser)
> add 1 2
3
```
