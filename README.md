# shelf

Easily create a custom shell for your application.

## Usage

Write your application as normal. Include appropriate type annotations for all
function parameters (if no type annotation is included any arguments will be
parsed as strings). The specified type must accept a single value. 

```python
def get(a:int, b:str):
    return a, b

class Rectangle:
    def __init__(self, height:int, width:int):
        ...

    def set_dimensions(self, height:int, width:int):
        self.height = height
        self.width = width
```

Create a CommandParser and register each of your functions with a non-variable prefix
(e.g. "get").   

```python
>>> parser = CommandParser()
>>> parser.add_command("get", get)
>>> parser.add_command("rect set", rect.set_dimension)
```

Parse commands using the `parse()` method to receive the corresponding output.

```python
>>> command.parse("get 1 new")
(1, "new")
>>> rect = Rectangle(5, 10)
>>> command.parse("rect set 20 30")
>>> rect.height
20
```