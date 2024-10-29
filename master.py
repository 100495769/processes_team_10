import os, sys, signal, argparse
from importlib.metadata import files
from time import sleep

import sensor


def print(robots, treasures, water, obstacles): ### las 3 listas funcionan [0][1] = ( , ) para las posiciones, hay q crearlas en mv para almacenar los datos
    print("Our information so far is: ")

    for i in range(self._sensor.rows):
        for j in range(self._sensor.columns):
            for k in water:
                if self._sensor.rows[i] == k[0] and self._sensor.columns[j] == k[1]:
                    print("-")
            for k in treasures:
                if self._sensor.rows[i] == k[0] and self._sensor.columns[j] == k[1]:
                    print("T")
            for k in obstacles:
                if self._sensor.rows[i] == k[0] and self._sensor.columns[j] == k[1]:
                    print("X")
            for k in robots:
                position = (self._sensor.rows[i], self._sensor.columns[j])
                if position == k[1]:
                    print("R")
            else:
                print("?")

def mv(input, robots): ### aqui se deberia llamar a robot.py y q devuelva los datos del robot para guardarlo de nuevo en las listas
    pass

def bat(input, robots):
    if input != "all":
        print(robots[int (input) - 1][2])

    elif input == "all":
        for i in robots:
            print(i[2])

    else:
        print("Error", file=sys.stderr)

def pos(input, robots):
    if input != "all":
        print(robots[int(input) - 1][1])

    elif input == "all":
        for i in robots:
            print(i[1])

    else:
        print("Error", file=sys.stderr)
def suspend(input, robots):
    if input != "all":
        robots[int(input) - 1][3] = "True"

    elif input == "all":
        for i in robots:
            i[3] = "True"

    else:
        print("Error", file=sys.stderr)
def resume(input, robots):
    if input != "all":
        robots[int(input) - 1][3] = "False"

    elif input == "all":
        for i in robots:
            i[3] = "False"

    else:
        print("Error", file=sys.stderr)
def exit(robots, treasures, running):
    running = "False" ### esto esta de placeholder, crear en el main un while "True"

    for i in robots:
        print("Robot %i: position %i, battery %i" ,i[0], i[1], i[2])

    print("Treasures found in:")
    for i in treasures:
        print("(%i, %i)", i[0], i[1])

def robots_setup(robots_file):
    # This function is used to obtain the data from robots_file and store it into a list.
    # It also sets an id for each robot.
    robots = []
    with open(robots_file, 'r') as file:
        for i, line in enumerate (file):
            #Formating
            position = list(map(int, line.strip()[1:-1].split(',')))
            # Each robot is represented by a list that contains: [0] the id, [1] the position
            robots.append([i+1, position, 50, 'False'])
    return robots


def update_robot(robot, r_pipe):
    try:
        new_robot = [robot[0]]
        data = os.read(r_pipe,1024).decode('utf-8')
        new_pos, new_bat, new_stat = data.split(',')
        new_robot.append(list(map(int, new_pos[1:-1].split(','))))
        new_robot.append(int(new_bat))
        new_robot.append(bool(new_stat))
    except:
        print("Error", file=sys.stderr)
        return -1

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