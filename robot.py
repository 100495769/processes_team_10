import sensor, signal, sys
class Robot:
    def __init__(self, identifier: int, position: list, battery: int, room):
        self.position = position
        self.battery = battery
        self.identifier = identifier
        self.sensor = sensor.Sensor(room)

    def pos(self):
        return self.position

    def bat(self):
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
        global robot.change_battery(-1)

robot = 0
def main():

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGQUIT, sig_handler)
    signal.signal(signal.SIGTSTP, sig_handler)
    signal.signal(signal.SIGUSR1, sig_handler)




if __name__ == "__main__":
    main()


