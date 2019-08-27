import socket
import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import time
import ctypes
import PyHook3 as pyHook
import win32gui
import bluetooth

if __name__ == "__main__":
    path = "\\".join(sys.argv[0].split("\\")[:-1]) + "\\"
    print(path)

class button(): 
    #Create the buttons.
    
    def __init__(self, color, x,y,width,height, text='', size=40, outlineColor = (255,255,255)):
        self.color = color
        self.colorB = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text 
        self.size = size
        self.outlineColor = outlineColor

    def draw(self,win): 
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0) 
        pygame.draw.rect(win, self.outlineColor, (self.x,self.y,self.width,self.height),2) 
        if self.text != '':
            font = pygame.font.SysFont('comicsans', self.size) 
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2))) 

    def isOver(self, pos): 
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True 
        return False

class textSurface():

    def __init__(self, win, color, x, y, size):
        self.color = color
        self.x = x
        self.y = y
        self.size = size
        self.win = win

    def print(self, text):
        font = pygame.font.SysFont('comicsans', self.size)
        text1 = font.render(text, 1, self.color)
        self.win.blit(text1, (self.x, self.y))

bluetoothBool = False

def sendMessage(sock, message):
    # Send data to the server. And return True if the connexion failed.
    
    for _ in range(5-len(message)):
        message += "_"
    if not bluetoothBool:
        message = str.encode(message)
    try:
        if not bluetoothBool:
            sock.sendall(message)
        else:
            sock.send(message)
        return False
    except:
        return True

n = 0
stop = False
keysDown = []
keys = {"lwin" : "0x5b", "lmenu" : "0x38", "tab" : "0xf_"}
def OnKeyboardDEvent(event):
    global n
    if event.Key.lower() in ['lwin', 'tab', 'lmenu'] and win32gui.GetActiveWindow() == PID and not stop:
        if event.Key.lower() not in keysDown:
            sendMessage(sock, "p" + keys[event.Key.lower()])
            keysDown.append(event.Key.lower())
            n += 1
        return False
    else:
        return True

def OnKeyboardUEvent(event):
    if event.Key.lower() in ['lwin', 'tab', 'lmenu'] and win32gui.GetActiveWindow() == PID and not stop:
        if event.Key.lower() in keysDown:
            sendMessage(sock, "r" + keys[event.Key.lower()])
            keysDown.remove(event.Key.lower())
        
        return False
    else:
        return True


with open(path + "config.txt", "r") as f:
    IP = f.readline().replace("\n","").split(": ")[1]
    PORT = int(f.readline().replace("\n","").split(": ")[1])
    BLUETOOTH_PORT = int(f.readline().replace("\n","").split(": ")[1])
    record = int(f.readline().replace("\n","").split(": ")[1])
    bluetoothBool = f.readline().replace("\n","").split(": ")[1] in ["True", "true", "1"]

SAVE_PORT = PORT

print("Bluetooth =", bluetoothBool)
if bluetoothBool:

    #Seaching for devices nearby.
    print("Bluetooth : Searching for devices.")
    nearby_devices = bluetooth.discover_devices(lookup_names = True)

    for i in range(4-len(nearby_devices)):
        nearby_devices += [("---","---")]

    print("Please choose your computer in the list.")

    #Asking USER to choose a device.
    pygame.init()

    screen = pygame.display.set_mode((500, 450))
    screen.fill((255,255,255))

    intermediate = pygame.surface.Surface((500, 100*len(nearby_devices) + 25))

    i_a = intermediate.get_rect()

    x1 = i_a[0]
    y1 = i_a[1]

    x2 = x1 + i_a[2]
    y2 = y1 + i_a[3]

    #Draw the background.
    for line in range(y1,y2):
        color = (255,255,255)
        pygame.draw.line(intermediate, color, (x1, line),(x2, line))

    #Draw the buttons
    y = 25
    listB = []
    for l in range(len(nearby_devices)):
        listB += [[button((255,255,255), 0, y + l*100, x2, 100, nearby_devices[l][1], 40, (0,0,0)), nearby_devices[l][0]]]

    scroll_y = 0
    clock = pygame.time.Clock()    
    quit = False
    while not quit:
        quit = pygame.event.get(pygame.QUIT)
        if quit:
            sys.exit()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4: scroll_y = min(scroll_y + 15, 0)
                if e.button == 5: scroll_y = max(scroll_y - 15, -(len(nearby_devices)-4.5)*100 - 50)#-300)

            if e.type == pygame.MOUSEBUTTONUP and e.button == 1 :
                pos = pygame.mouse.get_pos()
                pos1 = (pos[0], pos[1] - scroll_y)
                for b in listB:
                    if b[0].isOver(pos1) and b[1] != "---":
                        IP = b[1].lower()
                        PORT = BLUETOOTH_PORT
                        quit = True
        for b in listB:
            b[0].draw(intermediate)

        screen.blit(intermediate, (0, scroll_y))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

server_address = (IP, PORT)

#Create the two buttons
color = (255,255,155)
b = button(color, 50, 25, 400, 100, "Debug")
b1 = button(color, 50, 135, 400, 100, "Turn OFF - Client")
b2 = button(color, 50, 245, 400, 100, "Turn OFF - Client & Server")

hm = pyHook.HookManager()
hm.KeyDown = OnKeyboardDEvent
hm.KeyUp = OnKeyboardUEvent
hm.HookKeyboard()                     

while not stop:
    # Create a TCP/IP socket
    if not bluetoothBool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDRESS_TYPE = "IP"
    else:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        ADDRESS_TYPE = "MAC ADDRESS"
    
    try:
        #Try to connect to the server.
        print(f"Connecting to the server:\n\t{ADDRESS_TYPE} = {IP}\n\tPort = {PORT}")
        sock.connect(server_address)
        
        #Initialise pygame.
        pygame.init()
        pygame.display.set_caption("Keyboards - Connect by Emile Duquennoy")
        screen = pygame.display.set_mode((500, 450))
        #Get Pygame window ID
        PID = win32gui.GetActiveWindow()
        #Create the text surface
        text = textSurface(screen, (255,255,255), 50, 355, 60)
        Record = textSurface(screen, (255,255,255), 50, 400, 40)
        #Register the number of events
        n = 0
        
        #Loop over the events and draw the buttons.
        done = False
        while not done:
            
            if win32gui.GetActiveWindow() == PID:
                screen.fill((60,179,113))
            else:
                screen.fill((244,164,96))
            #Draw the buttons.
            b.draw(screen)
            b1.draw(screen)
            b2.draw(screen)

            #Get the events of the keyboard and the mouse.
            for event in pygame.event.get():
                
                #If the user closed the window.
                if event.type == pygame.QUIT:
                    done = True
                    
                #If the user pressed or released a key, then we send the scancode of the key to the server.
                if "Key" in str(event):
                    try:
                        if event.type == pygame.KEYUP:
                            prefix = "r"
                        else:
                            prefix = "p"
                            n += 1
                        done = sendMessage(sock, prefix + hex(event.scancode))
                    except:
                        print("Error: Couldn't send the key. The server seems disconnected. Try again")
                #If the mouse clicked on one of the two button.
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    try:
                        if b.isOver(pos):
                            done = sendMessage(sock, "ddddd")
                        if b1.isOver(pos):
                            sendMessage(sock, "sssss")
                            done = True
                            stop = True
                        if b2.isOver(pos):
                            sendMessage(sock, "SSSSS")
                            done = True
                            stop = True
                    except:
                        print("Error: Couldn't send the command. The server seems disconnected. Try again.")
            if n > record:
                record = n
            text.print("Keys pressed : " + str(n))
            Record.print("Your record : " + str(record))
            #Render the screen.
            pygame.display.flip()

            
        sock.close()
        print("Connexion closed.")
        pygame.quit()
        with open(path + "config.txt", "w") as f:
            f.write("SERVER IP: " + IP + "\n")
            f.write("SERVER IP PORT: " + str(SAVE_PORT) + "\n")
            f.write("SERVER BLUETOOTH PORT: " + str(BLUETOOTH_PORT) + "\n")
            f.write("RECORD: " + str(record) + "\n")
            f.write("BLUETOOTH MODE: " + str(bluetoothBool))
        time.sleep(1)
    
    except:
        print("Error : Couldn't connect to the server.")
        time.sleep(1)
