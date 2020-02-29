with open("../data/users.txt", "r") as f:
    while True:
        line = f.readline()
        if not line:
            print("EOF")
            break
        print(line)
