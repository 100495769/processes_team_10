import os, sys, signal, argparse
from importlib.metadata import files
from time import sleep

import sensor


def mv():
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
    #Arguments using argparser
    parser = argparse.ArgumentParser(description='MASTER CONTROL PROGRAM')
    #Add the possible arguments for our program
    parser.add_argument('room_file', type=str, help='File with the room')
    parser.add_argument('robots_file', type=str, help='File where the robots are located')

    #Create an instance of the class parse_args() in args, which holds the given arguments
    args = parser.parse_args()

    room_file = args.room_file
    robots_file = args.robots_file



    r_pipe, w_pipe = os.pipe()
    pid = os.fork()
    if pid== 0:
        os.close(sys.stdin.fileno())
        os.dup2(r_pipe, sys.stdin.fileno())
        os.close(r_pipe)
        os.close(w_pipe)
        os.execvp("python3",["python3", "robot.py", "1", "room.txt", "-b", "50", "-pos", "0", "1"])
        print("Soy una patata", file= sys.stdout)
    else:
        while True:
            os.dup2(w_pipe, sys.stdout.fileno())
            print("mv up")
            print("bat")
            sleep(1)

if __name__ == "__main__":
    main()