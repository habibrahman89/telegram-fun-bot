import os
import time

def create_multi_dirs():
    path = "C:\\Users\Habib Rahman\\Desktop\\telegram_fun_bot\\New folder"
    os.chdir(path)

    print(f"Creating 3 directories here: {path}")
    time.sleep(1)

    my_dir = ["handlers", "services", "database", "utils"]

    for dir in my_dir:
        os.mkdir(dir)
    print("Directories Created!")

create_multi_dirs()