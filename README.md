# shelf

Easily create a custom shell for your application.

## Usage

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

```python
>> command = Command("get", get)
>> command.parse("get 1 new")
(1, "new")
>> rect = Rectangle(5, 10)
>> command = Command("rect set", rect.set_dimension)
>> command.parse("rect set 20 30")
>> rect.height
20
```