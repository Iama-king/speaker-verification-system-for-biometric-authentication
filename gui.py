import os
import sp
import identification as id
import wave
import time
import threading
from  tkinter import *
from tkinter import messagebox
import sounddevice as sound
from scipy.io.wavfile import write
import wavio as wv
testdir = "D:/audio/rsp/splits 30sec/"
root=Tk()
root.geometry("600x700+400+80")
root.resizable(False,False)
root.title("Voice Recorder")
root.configure(background="#4a4a4a")
def Record():
    freq=16000
    dur=int(duration.get())
    recording=sound.rec(dur*freq,samplerate=freq,channels=2)

    try:
        temp=int(duration.get())
    except:
        print("invalid")
    while(temp>0):
        root.update()
        time.sleep(1)
        temp-=1
        if(temp==0):
            messagebox.showinfo("Time Countdown","Time's up")
        Label(text=f"{str(temp)}",font="arial 40",width=4,background="#4a4a4a").place(x=240,y=590)
    sound.wait()
    try:
        nam=str(name.get())
        print(nam)
    except:
        print("invalid")
        print(name)
    testdir1=testdir+nam
    tp=nam
    if not os.path.exists(testdir1):
        os.makedirs(testdir1)
    write(testdir1+"/"+nam+".wav",freq,recording)
    sp.main(nam)
    sc,bestsp=id.main(nam,nam+".p")
    if(nam==bestsp):
        messagebox.showinfo("Time Countdown", "result:accept")
    else:
        messagebox.showinfo("Time Countdown", "result:reject")



#icon
# image_icon = PhotoImage("mic.png")
# root.iconphoto(False,image_icon)
#logo
photo=PhotoImage(file="mic.png")
myimage=Label(image=photo,background="#4a4a4a")
myimage.pack(padx=5,pady=5)
#name
Label(text="Voice Recorder",font="arial 30 bold",background="#4a4a4a",fg="white").pack()
#entry box
duration=StringVar()
entry=Entry(root,textvariable=duration,font="arial 30",width=15).pack(pady=10)
Label(text="Enter your time in seconds",font="arial 15",background="#4a4a4a",fg="white").pack()
#name box
name = StringVar()
name1=Entry(root,textvariable=name,font="arial 30",width=15).pack(pady=10)
Label(text="Enter your name",font="arial 15",background="#4a4a4a",fg="white").pack()

#button
record=Button(root,font="arial 20",text="Record",bg="#111111",fg="white",border=0,command=Record).pack(pady=30)
root.mainloop()
