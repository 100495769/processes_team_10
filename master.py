import os, sys, signal, argparse
import sensor


def mv():
    pass
def print():
    pass
def bat():
    pass
def pos():
    pass
def suspend():
    pass
def resume():
    pass
def exit():
    pass



def main():
    print(os.getpid())
    pid = os.fork()
    if pid== 0:
        os.execv("./robot.py", "1 room.txt")


if __name__ == "__main__":
    main()