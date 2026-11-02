#file and folder handling project using CRUD funciton

from pathlib import Path
import os
import shutil

def create_folder():
    name = input("tell your folder name :- ")
    p = Path(name)
    if p.exists():
        print("this folder name already exists please try again")
        create_folder()
    else:
        p.mkdir()
        print("new folder created sucessfully")

def read_folder():
    p = Path("")
    items = list(p.rglob("*"))
    return items    
    
def update_folder():
    items = read_folder()
    # This method is only use for getting only folders
    for i in items:
            i = str(items)
            for j in i:
                if j == ".":
                    break
                else:
                    print(i)
    name = input("which folder you want to update :- ")
    old_p = Path(name)

    if old_p.exists():
        new_name = input("enter your new name for folder :- ")
        new_p = Path(new_name)
        old_p.rename(new_p)
        print("updated succesfully")
    else:
        print("sorry this folder name does not exists")
        update_folder()

def delete_folder():
    items = read_folder()
    # show only folders
    for i in items:
        if Path(i).is_dir():
            print(i)

    name = input("tell your folder name :- ")
    p = Path(name)

    if not p.exists() or not p.is_dir():
        print("this folder name does not exists please try again")
        delete_folder()
    else:
        # check whether the folder has anything inside it
        if any(p.iterdir()):
            confirm = input("this folder is not empty. Delete it with all its files? (y/n) :- ")
            if confirm.lower() != "y":
                print("delete cancelled")
                return
            shutil.rmtree(p)      # deletes folder + everything inside
        else:
            p.rmdir()             # empty folder
        print("folder deleted sucessfully")

def create_file():
    name = input("Tell your file name with extension :- ")
    p = Path(name)
    if p.exists() and p.is_file():
        print("file name already exists please try again with another name.")
        create_file()
    else:
        with open(p,"w") as fs:
            data = input("what do you want to write :- ")
            fs.write(data)
            print("file created succesfully")

def read_file():
    items = read_folder()
    for i in items:
        p = Path(i)
        if p.is_file():
            print(i)

    name = input("Which file do you wnat to read :- ")
    p = Path(name)
    if p.exists() and p.is_file():
        with open(p,"r") as fs:
            data = fs.read()
            print("/n/n/n your file content is :-/n/n/n/n")
            print(data)
    else:
        print("no such file exist please try again")
        read_file()

def update_file():
    items = read_folder()
    for i in items:
        p = Path(i)
        if p.is_file():
            print(i)
    name = input("Tell me your file name you want to update :- ")
    p = Path(name)
    if p.exists and p.is_file():
        print("choose one option")
        print("press 1 to change the name of file")
        print("press 2 to overwrite the file content")
        print("press 3 to append new content in file.")

        res = int(input("tell me your response :- "))
        if res == 1:
            new_name = input("tell new name with file extension :- ")
            new_p = Path(new_name)
            p.rename(new_p)
            print("file name change succesfully")

        elif res == 2:
            with open(p,"w") as fs:
                data = input("what you want to overwrite :- ")
                fs.write(data)
                print("overwritten successfully")

        elif res == 3:
                    with open(p,"a") as fs:
                        data = input("what you want to append :- ")
                        fs.write(data)
                        print("file append successfully")
        
def delete_file():
    items = read_folder()
    for i in items:
        p = Path(i)
        if p.is_file():
            print(i)
     
    name = input("tell your file name :- ")
    p = Path(name)
    if p.exists() and p.is_file():
        os.remove(p)
        print("File deleted suceesfully")
    else:
        print("No such file exists please try again")
        delete_file()


print("Press 1 - for creating a folder")
print("Press 2 - for reading a folder")
print("Press 3 - for updting a folder")
print("Press 4 - for deleting a folder")
print("Press 5 - for creating a file")
print("Press 6 - for reading a file")
print("Press 7 - for updting a file")
print("Press 8 - for deleting a file")

res = int(input("Tell your response :- "))

if res == 1:
    create_folder()

if res == 2:
    items = read_folder()
    for i in range(len(items)):
            print(f"{i + 1} : {items[i]}")

if res == 3:
    update_folder()

if res == 4:
    delete_folder()

if res == 5:
    create_file()

if res == 6:
    read_file()

if res == 7:
    update_file()

if res == 8:
    delete_file()


