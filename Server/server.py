import socket
import sys
import os
import time
import pynput, ctypes
from pynput.keyboard import Key, Controller

import win32.lib.win32con as win32con
import win32.win32api as win32api

import bluetooth

if __name__ == "__main__":
    path = "\\".join(sys.argv[0].split("\\")[:-1]) + "\\"

n = 0
numEntries = 0
keysPressed = {}
SendInput = ctypes.windll.user32.SendInput
timeL = time.time()

def PressKeyPynput(hexKeyCode):
    global numEntries, keysPressed
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    keysPressed[str(hexKeyCode)] = 1


def ReleaseKeyPynput(hexKeyCode):
    global numEntries
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    
    numEntries += 1
    
    try:
        keysPressed[str(hexKeyCode)] = 0
    except:
        print("Error: Couldn't release the key", str(hexKeyCode))



with open(path + "config.txt", "r") as f:
    IP = f.readline().replace("\n","").split(": ")[1]
    PORT = int(f.readline().replace("\n","").split(": ")[1])
    BLUETOOTH_PORT = int(f.readline().replace("\n","").split(": ")[1])
    bluetoothBool = f.readline().replace("\n","").split(": ")[1] in ["True", "true", "1"]

# Bind the socket to the port
server_address = (IP, PORT)

    
# try:
print("Bluetooth =", bluetoothBool)
if not bluetoothBool:

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Starting up on IP --> %s:%s' % server_address)
    sock.bind(server_address)

else:
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.bind(("",BLUETOOTH_PORT))

# except:
#     print("Error: The IP is wrong. Change it in the config file.")
#     os.system("pause")
#     sys.exit()

# Listen for incoming connections
sock.listen(1)
done = False
while not done:

    print('Waiting for a connexion...')
    try:
        connection, client_address = sock.accept()
    except:
        print("Error: Couldn't retrieve data from the client.")
    try:
        
        print(f"{client_address[0]}:{client_address[1]} is now connected to the server.")

        while True:
            
            data = connection.recv(5)
            
            if data:
                
                key1 = data.decode('utf-8')
                key = key1.replace("_","")
                try:
                    if key[0] == "p":
                        if key[1:] != "0x5b":
                            PressKeyPynput(eval(key[1:]))
                        else:
                            win32api.keybd_event(0x5b,0,0,0)                
                    if key[0] == "r":
                        if key[1:] != "0x5b":
                            ReleaseKeyPynput(eval(key[1:]))
                        else:
                            win32api.keybd_event(0x5b,0,win32con.KEYEVENTF_KEYUP ,0) 
                    if key == "ddddd":
                        print("Debugging the keyboard...")
                        for keyHEX, eta in keysPressed.items():
                            if eta == 1:
                                ReleaseKeyPynput(eval(keyHEX))
                                print(f"{keyHEX} - Released.")
                        print("Done.")
                    
                    elif key == "aaaaa":
                        print("Advanced debugging of the keyboard:")
                        for keyID in range(0, 255):
                            try:
                                ReleaseKeyPynput(hex(keyID))
                            except:
                                pass
                        print("Done.")
                    elif key == "sssss":
                        print("The client asked to be disconnected.")
                        break
                    elif key == "SSSSS":
                        print("The client asked to be disconnected AND to shutdown the server.")
                        done = True
                        break
                except:
                    print('Error: data errored.', key[1:])
            else:
                print("Error: Connexion lost.")
                break
    finally:
        print(f'Number of entries: {numEntries}')
        time.sleep(3)
        connection.close()