import os, sys, signal, argparse
import sensor

#################---------------ROBOT---------------#################

class Robot:
    def __init__(self, identifier: int, position: list, battery: int, room):
        self._position = position
        self._battery = battery
        self._identifier = identifier
        self._sensor = sensor.Sensor(room)
        self._suspended = False

    def get_position(self):
        return self._position

    def get_battery(self):
        return self._battery

    def get_suspended(self):
        return self._suspended

    def get_identifier(self):
        return self._identifier

    def change_battery(self, change):
        self._battery += change

    def change_suspended(self, change):
        self._suspended = change

    def check_obstacles(self):
        return self._sensor.with_obstacle(*self._position)

    def max_battery(self):
        self._battery = 100

    def tr(self):
        if self._sensor.with_treasure(*self._position):
            return "Treasure"
        else:
            return "Water"

    def mv(self, direction):
        if self._suspended == True:
            # Changed so it matches the master program logic. It can be removed but master won't work.
            print("KO")
            return None
        elif self._battery <= 4:
            print("KO")
            return None
        else:
            self.change_battery(-5)
        #Check the tile you want to move is within the room dimensions
        if direction.lower() == "up" and self._position[0] != 0:
            #Check the if there is and obstacle where you want to move
            if not self._sensor.with_obstacle(self._position[0] - 1, self._position[1]):
                self._position[0] -= 1
                print("OK")
            else:
                print("KO")
        elif direction.lower() == "down" and self._position[0] != self._sensor.dimensions()[0]-1:
            if not self._sensor.with_obstacle(self._position[0] + 1, self._position[1]):
                self._position[0] += 1
                print("OK")
            else:
                print("KO")
        elif direction.lower() == "right" and self._position[1] != self._sensor.dimensions()[1]-1:
            if not self._sensor.with_obstacle(self._position[0], self._position[1] + 1):
                self._position[1] += 1
                print("OK")
            else:
                print("KO")
        elif direction.lower() == "left" and self._position[1] != 0:
            if not self._sensor.with_obstacle(self._position[0], self._position[1] - 1):
                self._position[1] -= 1
                print("OK")
            else:
                print("KO")
        else:
            # Changed so it matches master program logic. Need to know what type of KO is.
            print("KOUT")

#################---------------SIGNAL HANDLER---------------#################

def sig_handler(signo, frame):
    if (signo==signal.SIGINT):
        robot.change_suspended(True)
    elif(signo==signal.SIGQUIT):
        robot.change_suspended(False)
    elif(signo==signal.SIGTSTP):
        print(robot.get_identifier(), robot.get_position(), robot.get_battery())
    elif(signo==signal.SIGUSR1):
        robot.max_battery()
    elif(signo==signal.SIGALRM):
        if robot.get_battery() <= 0:
            robot.change_suspended(True)
        if robot.get_suspended() == False:
            robot.change_battery(-1)
        signal.alarm(1)

#################---------------MAIN---------------#################

def main():
    #Arguments using argparser
    parser = argparse.ArgumentParser(description='RCP: Robot Control Program')
    #Add the possible arguments for our program
    parser.add_argument('identifier', type=int, help='Robot identifier')
    parser.add_argument('f', type=str, help='File name of the room.txt')
    parser.add_argument('-pos', '--position', metavar=('row', 'column'), type=int, nargs=2, default= [0,0], help='Position tuple where robots start. Default: [0, 0]')
    parser.add_argument('-b', '--battery', type=int, default= 100, help= 'Initial battery level of the robot. Default: 100')

    #Create an instance of the class parse_args() in args, which holds the given arguments
    args = parser.parse_args()
    #Uncomment to check how arguments can be accessed from args                     DELETE
    #print(args.identifier, args.f, args.position, args.battery)
    #Print PID in stderr
    print("PID:",os.getpid(), file= sys.stderr)

    #Create an instance of the robot with the attributes given
    global robot
    robot = Robot(args.identifier, args.position, args.battery, args.f)

    #Change the signals functionality
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGTSTP, sig_handler)
    signal.signal(signal.SIGUSR1, sig_handler)
    signal.signal(signal.SIGALRM, sig_handler)


    #Set up the alarm
    signal.alarm(1)
    Active = True
    if robot.check_obstacles() == True:
        Active = False
        print("Invalid initial position", file=sys.stderr)
        return -1

    while Active:

        commands = input()
        if commands.lower().split()[0] == "mv":
            robot.mv(commands.split()[1])
        elif commands.lower() == "tr":
            print(robot.tr())
        elif commands.lower() == "bat":
            print(robot.get_battery())
        elif commands.lower() == "pos":
            print(robot.get_position())
        elif commands.lower() == "exit":
            Active = False
            print(robot.get_position(), robot.get_battery())
        else:
            print("Invalid command", file=sys.stderr)


if __name__ == "__main__":
    main()


