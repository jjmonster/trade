from cmdLine import cl

while True:
    cl.help_menu()
    try:
        opt = int(input("your select:"))
    except:
        continue

    if opt <= len(cl.help_list):
        cl.help_list[opt][0]()

