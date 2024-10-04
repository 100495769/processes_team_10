import os, sys, signal, argparse
import sensor
class Robot:
    def __init__(self, identifier: int, position: list, battery: int, room):
        self.position = position
        self.battery = battery
        self.identifier = identifier
        self.sensor = sensor.Sensor(room)

    def get_position(self):
        return self.position

    def get_battery(self):
        return self.battery

    def change_battery(self, change):
        self.battery += change

    def exit(self):
        return self.position, self.battery

    def tr(self):
        return self.sensor.with_treasure(*position)

    def mv(self, direction):
        if direction == "up":
            pass
        elif direction == "down":
            pass
        elif direction == "right":
            pass
        elif direction == "left":
            pass
        else:
            print("Invalid")


def sig_handler(signo, frame):
    if (signo==signal.SIGINT):
        pass
    elif(signo==signal.SIGQUIT):
        pass
    elif(signo==signal.SIGTSTP):
        pass
    elif(signo==signal.SIGUSR1):
        pass
    elif(signo==signal.SIGALRM):
        robot.change_battery(-1)
        signal.alarm(1)



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


    #Example of the alarm working.
    signal.alarm(1)
    while True:
        signal.pause()
        print(robot.get_battery())

if __name__ == "__main__":
    main()


