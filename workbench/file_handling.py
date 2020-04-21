with open("users_test.txt", "a") as af:
    af.seek(15)
    af.write("HELLO WORLD!")
