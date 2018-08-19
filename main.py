from cmdLine import cl

if len(sys.argv) > 1 and sys.argv[1] == 'robot':
    cl.start_robot()
    time.sleep(10000000)
    cl.stop_robot()
    cl.exit()

while True:
    cl.help_menu()
    try:
        opt = int(input("your select:"))
    except:
        continue

    if opt <= len(cl.help_list):
        cl.help_list[opt][0]()

