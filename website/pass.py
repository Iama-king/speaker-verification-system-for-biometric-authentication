
import os
import time
import sys

password = 'gopi'   #Set the Password

def goto(linenum):
    global line
    line = linenum

line = 1
while True:
    
    pw = input("Enter your password for Lock or Unlock your folder: ")
   
    if pw == password:
    # Change Dir Path where you have Locker Folder
        os.chdir("D:\pass")
    # If Locker folder or Recycle bin does not exist then we will be create Locker Folder 
        if not os.path.exists("Locker"):
            if not os.path.exists("Locker.{645ff040-5081-101b-9f08-00aa002f954e}"):
                os.mkdir("Locker")
            else:
                print('Folder unlocked successfully')
                os.popen('attrib -h Locker.{645ff040-5081-101b-9f08-00aa002f954e}')
                os.rename("Locker.{645ff040-5081-101b-9f08-00aa002f954e}","Locker")
                sys.exit()
        else:
            print('Folder locked successfully')
            os.rename("Locker","Locker.{645ff040-5081-101b-9f08-00aa002f954e}")
            os.popen('attrib +h Locker.{645ff040-5081-101b-9f08-00aa002f954e}')
            sys.exit()
        
    else:
        print("Wrong password!, Please Enter right password")
        time.sleep(5)
        goto(1)