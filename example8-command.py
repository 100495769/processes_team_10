import os,sys

def main():
    r_pipe, w_pipe = os.pipe()
    try:
        childpid = os.fork()
    except OSError as e:
        print (e)
        print("Error executing fork\n")
        sys.exit(1)
    
    if childpid == 0:
        os.close(sys.stdout.fileno()) 
        os.dup2(w_pipe, sys.stdout.fileno())
        os.close(r_pipe)
        os.close(w_pipe)
        try:
            os.execl("/bin/ls", "ls", "-l")
        except OSError as e:
            print (e)
            print("Error executing execl (ls)\n")
            sys.exit(1)
    else:
        os.close(sys.stdin.fileno())
        os.dup2(r_pipe, sys.stdin.fileno())
        os.close(r_pipe)
        os.close(w_pipe)
        try:
            os.execl("/usr/bin/sort", "sort", "-r")
        except OSError as e:
            print (e)
            print("Error executing execl (sort)\n")
            sys.exit(1)
if __name__ == "__main__":
    main()
