import os, sys, signal, argparse
from importlib.metadata import files
from time import sleep

import sensor


def mv():
    for i in range(self._sensor.rows):
        for j in range(self._sensor.columns):
           if self._sensor.rows[i], self._sensor.columns[j] == pass:
              pass
           elif:
               pass
           else:
               print("?")

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

def initial_positions(robots_file):
    robot_positions = []
    with open(robots_file, 'r') as file:
        for i, line in enumerate (file):
            position = tuple(map(int, line.strip()[1:-1].split(',')))
            ###quitamos paréntesis y espacios y lo convertimos en una tupla (,)
            robot_positions.append(robot_id=(i+1),position)
            ### i+1 para q los robots empiecen en 1 y la lista tenga ambos "id" y posicion
            ### no entendemos muy bien como hace esto

    return robot_positions

def initialize_robots(robot_positions):
    robots = []
    for robot_id, position in robot_positions:
        robots.append([robot_id, position, 50, 'False'])
    return robots

def receive_robots(r_pipe):
    try:
        data = os.read(r_pipe,1024).decode()
        return eval(data)
    except:
        print("Error", file=sys.stderr)
        return None


def update(robots, robot_id, r_pipe):
    new = receive_robots(r_pipe)
    if new:
        new_pos, new_bat, new_stat = new
        for robot in robots:
            if robot[0] == robot_id:
                robot[1] = new_pos
                robot[2] = new_bat
                robot[3] = new_stat
                break

'''esto es lo q queriamos q pasara:
estabamos centrados en la manera de almacenar y gestionar la info de todos los robots
hemos creado:
initial_positions para q master lea robots.txt y crea una lista con tantas posiciones como lineas en robot.txt
    la lista tiene ids q empiezan desde 1 y la posicion (x,y)
initialize_robots crea la lista donde vamos a almacenar todos los robots y instaura todos los valores de id, posicion, bat y estado 
    bat y estado como si estuvieran de fabrica
receive es para q coja la info de robot.py, queremos q sea con pipes y no sabemos como funciona el q hemos hecho
update es para q la lista se actualice cada vez q se lo pidamos
    suponemos como funciona pero no estamos seguros de como recibe la info
'''

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
       ### print("Soy una patata", file= sys.stdout)
    else:
        while True:
            os.dup2(w_pipe, sys.stdout.fileno())
            print("mv up")
            print("bat")
            sleep(1)

if __name__ == "__main__":
    main()