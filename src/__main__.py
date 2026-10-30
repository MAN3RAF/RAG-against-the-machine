from src.parser import Parser
from sys import argv


def main():

    input = argv[1:]
    print(input[0])



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
