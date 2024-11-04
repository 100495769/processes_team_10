import os, sys, signal, argparse, numpy
from time import sleep
from sensor import Sensor


#################---------------ROBOT CREATION---------------#################

def read_robots_file(robots_file):
    # This function is used to obtain the data from robots_file and store it into a list.
    # It also sets an id for each robot.
    robots = []
    with open(robots_file, "r") as file:
        for i, line in enumerate(file):
            #Formating
            position = list(map(int, line.strip()[1:-1].split(",")))
            # Each robot is represented by a list that contains: [0] the id, [1] the position
            robots.append([str(i + 1), "50", *map(str, position)])

    return robots


def create_robot(room_txt: str, id: str, bat: str, pos_x: str, pos_y: str, sensor):
    # We check that there is not an obstacle in the said position
    if sensor.with_obstacle(int(pos_x), int(pos_y)):
        return f"Error: Obstacle in the pos of robot {id}"
    # Create pipes for communication. Establish a duplex communication channel.
    parent_to_child_read, parent_to_child_write = os.pipe()
    child_to_parent_read, child_to_parent_write = os.pipe()
    pid = os.fork()
    if pid == 0:
        # Replace stdout and stdin by the pipes.
        os.close(parent_to_child_write)
        os.close(child_to_parent_read)
        os.close(sys.stdin.fileno())
        os.close(sys.stdout.fileno())
        os.dup2(parent_to_child_read, sys.stdin.fileno())
        os.dup2(child_to_parent_write, sys.stdout.fileno())
        # Establish the execution of the robot program.
        os.execvp("python3", ["python3", "robot.py", id, room_txt, "-b", bat, "-pos", pos_x, pos_y])
    os.close(parent_to_child_read)
    os.close(child_to_parent_write)

    return id, str(pid), pos_x, pos_y, child_to_parent_read, parent_to_child_write


#################---------------ROBOT COMMUNICATION---------------#################

def write_to_robot(w_pipe, data):
    # This functions provides a way to communicate with a robot and then restoring the stdout to the original.
    original_stdout = os.dup(sys.stdout.fileno())
    os.dup2(w_pipe, sys.stdout.fileno())
    print(data)
    os.dup2(original_stdout, sys.stdout.fileno())
    return


def read_from_robot(r_pipe):
    # This functions provides a way to communicate with a robot and then restoring the stdin to the original.
    original_stdin = os.dup(sys.stdin.fileno())
    os.dup2(r_pipe, sys.stdin.fileno())
    data = input()
    os.dup2(original_stdin, sys.stdin.fileno())
    return data


#################---------------ROBOT MOVEMENT---------------#################

def _check_treasure(robot, tr_count):
    # Check wether or not there is a treasure and then update the info.
    write_to_robot(robot["W_PIPE"], "tr")
    tr = read_from_robot(robot["R_PIPE"])
    if tr == "Treasure":
        tr_count -= 1
        print(f"Treasure found by robot {robot['ID']} there are {str(tr_count)} treasures left!")
    return tr


def _move_robot(robot: dict, direction: str, room: list, robots_pos: list, tr_count: int):
    old_pos_x = int(robot["POS_X"])
    old_pos_y = int(robot["POS_Y"])
    pos_x = int(robot["POS_X"])
    pos_y = int(robot["POS_Y"])
    if direction == "left":
        pos_y -= 1
    elif direction == "right":
        pos_y += 1
    elif direction == "up":
        pos_x -= 1
    elif direction == "down":
        pos_x += 1

    # We check if there is a robot already in that position.
    if robots_pos[pos_x][pos_y] != "_":
        print(f"Collision between Cylon NO.{robot['ID']} and NO.{robots_pos[pos_x][pos_y]}")
        return
    write_to_robot(robot["W_PIPE"], "mv " + direction)

    data = read_from_robot(robot["R_PIPE"])
    if data == "OK":
        # Replace old position in robots_pos by "_". (Meaning it is empty)
        robots_pos[old_pos_x][old_pos_y] = "_"
        # Replace new position in robots_pos by the ID of the robot.
        robots_pos[pos_x][pos_y] = robot["ID"]
        # Replace old position in room by the terrain type.
        room[old_pos_x][old_pos_y] = room[old_pos_x][old_pos_y][:-1] * 2
        # Check weather there is a treasure or not and replace the terrain with it.
        room[pos_x][pos_y] = _check_treasure(robot, tr_count)[:1] + "R"
        robot["POS_X"] = pos_x
        robot["POS_Y"] = pos_y

    elif data == "KO" and robot["STATUS"] == "ACTIVE":
        # The place were we wanted to move has an obstacle so we place "OO" there indicating it.
        # And we do not move.
        room[pos_x][pos_y] = "OO"

    elif data == "KOUT":
        # The Cylon would get out of the map. :P
        # Warn this to the user.
        print(f"Oh no, you wanted NO.{robot['ID']} to escape the map? ", end="")
        sleep(1.25)
        print("You are walking on a fine line.")
        sleep(1.25)
        print("Stick to the Cylon plan and we will avoid any need for ", end="")
        sleep(1.5)
        print("adjustments...")

    elif data == "KO" and robot["STATUS"] == "SUSPENDED":
        # If it is suspended don't annoy
        print(f"Don`t you dare disrupt a NO.{robot['ID']}. We will not be denied of good sleep.")
    return


def move_robots(robots: list, direction: str, room: list, robots_pos: list, tr_count: int, ID: str):
    if ID.upper() == "ALL":
        # Since the list in is in order of ID so does the for loop.
        for i in robots:
            _move_robot(i, direction, room, robots_pos, tr_count)
    else:
        # Since in our programm ID matches with the place in the list of the robot we can do the following.
        _move_robot(robots[int(ID) - 1], direction, room, robots_pos, tr_count)


#################---------------ROBOT BATTERY---------------#################

def _battery_robot(robot: dict):
    write_to_robot(robot["W_PIPE"], "bat")
    bat = read_from_robot(robot["R_PIPE"])
    print(f"Cylon NO.{robot['ID']} battery level: {bat}")


def battery_robots(robots: list, ID: str):
    if ID.upper() == "ALL":
        # Since the list in is in order of ID so does the for loop.
        for i in robots:
            _battery_robot(i)
    else:
        # Since in our programm ID matches with the place in the list of the robot we can do the following.
        _battery_robot(robots[int(ID) - 1])


#################---------------ROBOT POSITION---------------#################

def _position_robot(robot: dict):
    write_to_robot(robot["W_PIPE"], "pos")
    pos = read_from_robot(robot["R_PIPE"])
    print(f"Cylon NO.{robot['ID']} position: {pos}")


def position_robots(robots: list, ID: str):
    if ID.upper() == "ALL":
        # Since the list in is in order of ID so does the for loop.
        for i in robots:
            _position_robot(i)
    else:
        # Since in our programm ID matches with the place in the list of the robot we can do the following.
        _position_robot(robots[int(ID) - 1])


#################---------------ROBOT SUSPENSION---------------#################

def _suspend_robot(robot: dict):
    os.kill(int(robot["PID"]), signal.SIGINT)
    robot["STATUS"] = "SUSPENDED"
    print(f"Cylon NO.{robot['ID']} suspended")


def suspension_robots(robots: list, ID: str):
    if ID.upper() == "ALL":
        # Since the list in is in order of ID so does the for loop.
        for i in robots:
            _suspend_robot(i)
    else:
        # Since in our programm ID matches with the place in the list of the robot we can do the following.
        _suspend_robot(robots[int(ID) - 1])


#################---------------ROBOT RESUME---------------#################

def _resume_robot(robot: dict):
    os.kill(int(robot["PID"]), signal.SIGQUIT)
    robot["STATUS"] = "ACTIVE"
    print(f"Cylon NO.{robot['ID']} activated")


def resume_robots(robots: list, ID: str):
    if ID.upper() == "ALL":
        # Since the list in is in order of ID so does the for loop.
        for i in robots:
            _resume_robot(i)
    else:
        # Since in our programm ID matches with the place in the list of the robot we can do the following.
        _resume_robot(robots[int(ID) - 1])


#################---------------ROBOT EXIT---------------#################

def exit_robots(robots: list):
    print("\n")
    for robot in robots:
        write_to_robot(robot["W_PIPE"], "exit")
        print(f"The last position and battery of our Cylon NO.{robot['ID']} is {read_from_robot(robot['R_PIPE'])}")


#################---------------MASTER PRINT---------------#################

def master_print(room: list, tr_count: int):
    print(f"\n----------------------------------------------------------------------\n"
          f"\nOur Cylon agents have gathered the following information so far:\nMap of the room:\n{room}\nTreasures left:"
          f" {tr_count}.\n\nIf we were merely humans we would 'have to roll the hard six'.\nBut unlike them, we do not leave things to chance.\n"
          f"\n----------------------------------------------------------------------\n")


#################---------------MASTER EXIT---------------#################
def master_exit(robots: list, tr_count: int, tr_total: int):
    exit_robots(robots)
    tr_found = str(tr_total - tr_count)
    print(f"\n Our Cylon agents have managed to find {tr_found} treasures.")
    for robot in robots:
        # Wait for each robot to finish.
        os.wait()


#################---------------MAIN---------------#################

def main():

    #################---------------ARGUMENTS---------------#################

    #Arguments using argparser
    parser = argparse.ArgumentParser(description='MASTER CONTROL PROGRAM')
    #Add the possible arguments for our program
    parser.add_argument('room_file', type=str, help='File with the room')
    parser.add_argument('robots_file', type=str, help='File where the robots are located')

    #Create an instance of the class parse_args() in args, which holds the given arguments
    args = parser.parse_args()

    #################---------------INITIAL SETUP---------------#################

    room_file = args.room_file
    robots_file = args.robots_file

    sensor = Sensor(room_file)
    dimensions = sensor.dimensions()
    # Create the room with no info. (Filled with "??") Take into account that this matrix will require 2 characters
    # in each position. No more, no less.
    room = numpy.full((int(dimensions[0]), int(dimensions[1])), "??")
    # In this matrix we store the PID of each robot in their position. This is later used in the mv command.
    # Having this matrix facilitates finding if a robot is in a given position.
    robots_pos = [["_"] * int(dimensions[1]) for i in range(int(dimensions[0]))]

    # Here we will store the number of treasures left.
    tr_count = sensor.n_treasures()

    # Here the amount of treasures in the map.
    tr_total = sensor.n_treasures()

    # robots is a list that contains dictionaries of robots. Each dictionary has the following keys:
    # ID, PID, POS_X, POS_Y, R_PIPE, W_PIPE, STATUS(ACTIVE OR SUSPENDED)
    robots = list()

    # Create robots indicated in robots_file
    for i in read_robots_file(robots_file):
        robot = create_robot(room_file, *i, sensor)
        if type(robot) == str:
            # If there is any error with the robot created, print it.
            print(robot)
        else:

            robots.append({"ID": robot[0], "PID": robot[1], "POS_X": robot[2], "POS_Y": robot[3], "R_PIPE": robot[4],
                           "W_PIPE": robot[5], "STATUS": "ACTIVE"})
            # Comprobar si en esa posicion hay tesoro o agua y escribirlo en la posición.
            room[int(robot[2])][int(robot[3])] = (_check_treasure(robots[-1], tr_count)[:1] + "R")
            # Tambien actualizamos robots_pos
            robots_pos[int(robot[2])][int(robot[3])] = robot[0]

    #################---------------SIGNAL HANDLER---------------#################
    exited = False

    def sig_handler(signo, frame):
        if (signo == signal.SIGINT):
            exit_robots(robots)
            os.kill(os.getpid(), signal.SIGKILL)
        elif (signo == signal.SIGQUIT):
            for robot in robots:
                os.kill(int(robot["PID"]), signal.SIGUSR1)
        elif (signo == signal.SIGTSTP):
            battery_robots(robots, "all")

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGTSTP, sig_handler)

    #################---------------MAIN LOOP---------------#################


    while not exited and tr_count != 0:

        command = input("By your command: ")

        if command == "exit":
            master_exit(robots, tr_count, tr_total)
            exited = True
        elif command == "print":
            master_print(room, tr_count)
        elif command[:3] == "bat":
            battery_robots(robots, command[3:].strip())
        elif command[:3] == "pos":
            position_robots(robots, command[3:].strip())
        elif command[:7] == ("suspend"):
            suspension_robots(robots, command[7:].strip())
        elif command[:6] == ("resume"):
            resume_robots(robots, command[6:].strip())
        elif command[:2] == "mv":
            move_robots(robots, command[2:].split()[0].strip(), room, robots_pos, tr_count, command[2:].split()[1].strip())
        else:
            print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
