import threading
import sys
import os
# Get the path where this script is living
base_path = os.path.dirname(os.path.abspath(__file__))

# Force Python to look in this folder for other .py files
if base_path not in sys.path:
    sys.path.insert(0, base_path)
import json
from time import sleep
import program
import menus
import windowsettings
import shared
import events
import loudness
import platform
import extensions
import traceback


#TODO create some comments for everything

#creates a working dir
if not os.path.exists("workingdir"):
    os.mkdir("workingdir")

# extensions
global current_extensions
current_extensions = extensions.loadextensions()
# extensions END

#class of shared vars
t1 = threading.Thread(target=loudness.getloudness)
t1.daemon = True
t1.start()
#creates settings.json if it dosnt exist
if not os.path.exists("settings.json"):
    with open("settings.json", "w") as createsettings:
        createsettings.write('{\n"addition": 120,\n"select": "none",\n"selected_audio_device":"default","transparent":false}')

#function for keyinputs
def keyp(event):
    global close
    global window
    #opens escape menu if the escape key is pressed
    if event.key() == "ESC":
        close=menus.settings("","", qtv=True, darkmode=darkmode)
    #opens the charerror menu if F3 key is pressed
    if event.key() == "F3":
        menus.charerror(program.shared.charerrors, darkmode=darkmode)

#event update
def maineventhandler():
    global eventlist, eventdict, charbase, volume, close
    eventlist = []
    eventdict = {}
    charbase = {}
    lastmousepos=-1
    while True:
        ee = True
        sleep(0.02)
        try:
            for a, event in enumerate(eventlist):
                if event not in eventdict:
                    eventdict[event] = charbase["events"][event]
            eventlist, eventdict = events.runevents(eventlist, eventdict, charbase, volume)
        except Exception as e:
            pass

global eventdict, eventlist, charbase, lastselection, volume
eventlist = []
eventdict = {}
lastselection = ""
global darkmode
#deaktivate darkmode if platform is unknown / unsupported or if transparent mode is enabled
if platform.system().lower()=="windows" or platform.system().lower()=="linux" and json.loads(open("settings.json").read())["transparent"]:
    darkmode=True
else:
    darkmode=False
def update_image():
    global eventdict, eventlist, volume, lastselection, charbase, close
    print(eventdict)
    print(eventlist)

    #this is for moving the window during transparent mode
    if program.shared.reload_settings:
        program.shared.reload_settings=False
        program.shared.settings = json.loads(open("settings.json", "r").read())
        program.shared.selection = str(program.shared.settings["select"])
        try:
            program.audio_devices.selected_device=[program.shared.settings["selected_audio_device"], program.audio_devices.device_dict[program.shared.settings["selected_audio_device"]]]
        except:
            program.audio_devices.selected_device=["default", 0]
        if program.shared.reload_char:
            program.shared.reload_char=False
            eventlist = []
            eventdict = {}
            for nume,holderror in enumerate(program.shared.charerroronload):
                program.char.charerror(holderror["type"], holderror["message"])
                program.shared.charerroronload=program.shared.charerroronload[1:]
            program.shared.charerrors=program.shared.dntclearcharerror
            try:
                charbase = json.loads(open(f"chars/{program.shared.selection}/charbase.json", "r").read())
            except FileNotFoundError:
                try:
                    events.backwardscompatibility(program.shared.selection)
                    charbase = json.loads(open(f"chars/{program.shared.selection}/charbase.json", "r").read())
                except:
                    program.char.charerror("error", "there was an error while loading in the character using example character")
                    program.shared.settings["addition"]=120
                    program.shared.settings["select"]="beispielchar1"
                    open("settings.json", "w").write(json.dumps(program.shared.settings,indent=4))
                    charbase = json.loads(open(f"chars/beispielchar1/charbase.json", "r").read())
    winmove=False
    

    try:
        if close:
            sys.exit()
    except Exception as e:
        pass
    try:
        close=events.close
    except:
        pass
    imgs = []
    try:
        backgroundcolor=charbase["backcolor"]
    except:
        pass
    try:
        size=charbase["size"].split("x")
        #creates error if char size is below minimum or above maximum 
        if int(size[0])<300 or int(size[1])<300 or int(size[0])>900 or int(size[1])>900:
            program.char.charerror("error", "char size to small (cant be less then 300x300 or above 900x900)")
            raise "error"
        else:
            #sets window size to desired value if it is above 300x300 and below 900x900
            shared.windowxsize=int(size[0])
            shared.windowysize=int(size[1])
    except:
        #sets the window size to 400x400 if nothing is set or something bad happened
        shared.windowxsize, shared.windowysize= 400,400
    seimages = []
    if "events" not in charbase or "audio" not in charbase["events"]:
        try:
            charbase["events"]["audio"] = {"type": "audio"}
        except:
            charbase["events"] = {}
            charbase["events"]["audio"] = {"type": "audio"}
    try:
        volume=max(0,loudness.volume+program.shared.settings["addition"])
        for i, layer in enumerate(charbase["layers"]):
            try:
                layer["loudnessdifference"]
            except:
                layer["loudnessdifference"] = 0
            if layer["event"] in eventlist:
                do, xy = events.event(layer["event"], eventdict, volume, len(layer["imagefiles"]), charbase, current_extensions, layer["loudnessdifference"])
                if do.split(":")[0] == "display":
                    imgfile = layer["imagefiles"][int(do.split(":")[1])]
                    if imgfile != "nothing":
                        img_path = f'chars/{program.shared.settings["select"]}/{imgfile}'
                        img = img_path
                        imgs.append([img, xy])
                    try:
                        seimages.append(charbase["sideevents"][layer["event"]])
                    except:
                        seimages.append(0)
            else:
                eventlist.append(layer["event"])
                eventdict[layer["event"]] = charbase["events"][layer["event"]]
                if layer["event"] in eventlist:
                    do, xy = events.event(layer["event"], eventdict, volume, len(layer["imagefiles"]), charbase, current_extensions, layer["loudnessdifference"])
                    try:
                        if do.split(":")[0] == "display":
                            imgfile = layer["imagefiles"][int(do.split(":")[1])]
                            if imgfile != "nothing":
                                img_path = f'chars/{program.shared.settings["select"]}/{imgfile}'
                                img = img_path
                                imgs.append([img, xy])
                            try:
                                seimages.append(charbase["sideevents"][layer["event"]])
                            except:
                                seimages.append(0)
                    except:
                        do = "display:0"
                        if do.split(":")[0] == "display":
                            imgfile = layer["imagefiles"][int(do.split(":")[1])]
                            img_path = f'chars/{program.shared.settings["select"]}/{imgfile}'
                            img = img_path
                            imgs.append([img, xy])
                            try:
                                seimages.append(charbase["sideevents"][layer["event"]])
                            except:
                                seimages.append(0)
        for i, img in enumerate(imgs):
            x = img[1][0]
            y = img[1][1]
            img = img[0]
            print("img", x, y)
    except Exception as e:
        print(e)
        program.char.reload_char()
global window

t2 = threading.Thread(target=maineventhandler)
t2.daemon = True
t2.start()
while True:
    sleep(0.05)
    update_image()
sys.exit()