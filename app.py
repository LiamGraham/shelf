from shelf import CommandParser

def test(a, b):
    return a, b


if __name__ == "__main__":
    parser  = CommandParser()
    parser.add_command("test", test)
    while True:
        print(parser.parse(input()))