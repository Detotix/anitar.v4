
import sys
import windowsettings
import os
import json
import program
import traceback
import extensions
#TODO create some comments for everything

def presettings(darkmode=False):
    app = QApplication.instance()

    new_window = QMainWindow()
    new_window.setWindowIcon(QIcon('app.ico'))
    new_window.setWindowTitle("settings")
    new_window.setGeometry(int(300*windowsettings.get_win_scale()), int(200*windowsettings.get_win_scale()), int(300*windowsettings.get_win_scale()), int(200*windowsettings.get_win_scale()))
    new_window.setFixedSize(new_window.size())
    windowsettings.darkmode(new_window, darkmode)
    windowsettings.nofullscreen(new_window)

    new_window.show()

    loop = QEventLoop()
    new_window.destroyed.connect(loop.quit)
    loop.exec_()
def settings(ev="", root="", qtv=False, darkmode=False):
    global close
    end=False
    close = False
    b = open("settings.json", "r")
    add = json.loads(b.read())["addition"]
    b.close()

    # Check if a QApplication instance already exists
    if not qtv:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    new_window = QMainWindow()
    new_window.setWindowIcon(QIcon('app.ico'))
    new_window.setWindowTitle("Settings")
    new_window.setGeometry(int(300*windowsettings.get_win_scale()), int(200*windowsettings.get_win_scale()), int(300*windowsettings.get_win_scale()), int(200*windowsettings.get_win_scale()) if not qtv else int(250*windowsettings.get_win_scale()))
    new_window.setFixedSize(new_window.size())
    windowsettings.darkmode(new_window,darkmode)
    windowsettings.nofullscreen(new_window)

    number_label = QLabel("Loudness Increment:")
    number_label.setSizePolicy(number_label.sizePolicy().Fixed, number_label.sizePolicy().Fixed)
    number_entry = QLineEdit()
    selection_label = QLabel("Select char:")
    selection_label.setSizePolicy(selection_label.sizePolicy().Fixed, selection_label.sizePolicy().Fixed)
    #getting chars for selection
    options = os.listdir("chars/")
    #character selection box
    selected_option = QComboBox()
    selected_option.addItems(options)
    selected_option.setCurrentIndex(options.index(program.shared.selection))
    #audio label
    selection_audio_device = QLabel("Selected audio device: (Work in progress)")
    selection_audio_device.setSizePolicy(selection_audio_device.sizePolicy().Fixed, selection_audio_device.sizePolicy().Fixed)
    #audio device selection box
    audio_device = QComboBox()
    audio_device.addItems(program.audio_devices.device_list)
    audio_device.setCurrentIndex(program.audio_devices.device_list.index(program.audio_devices.selected_device[0]))
    
    
    def close_p():
        global close
        close = True
        end=True
        sys.exit()
        new_window.hide()

    def close_root():
        end=True
        new_window.hide()
    def save_data():
        global close
        loudness_increment = number_entry.text()
        selected_character = selected_option.currentText()
        if not loudness_increment:
            loudness_increment = str(add)
        save = {"select": selected_character, "addition": int(loudness_increment), "selected_audio_device": str(audio_device.currentText()), "transparent": program.shared.currenttransparency}
        program.audio_devices.selected_device=[audio_device.currentText(), program.audio_devices.device_dict[audio_device.currentText()]]
        save=json.loads(open("settings.json", "r").read()) | save
        with open("settings.json", "w") as a:
            a.write(json.dumps(save, indent=4, sort_keys=True))
        program.char.reload_char()
        new_window.close()
    def togglet():
        program.shared.currenttransparency=not program.shared.currenttransparency
        global close
        loudness_increment = number_entry.text()
        selected_character = selected_option.currentText()
        if not loudness_increment:
            loudness_increment = str(add)
        save = {"select": selected_character, "addition": int(loudness_increment), "selected_audio_device": str(audio_device.currentText()), "transparent": program.shared.currenttransparency}
        program.audio_devices.selected_device=[audio_device.currentText(), program.audio_devices.device_dict[audio_device.currentText()]]
        save=json.loads(open("settings.json", "r").read()) | save
        with open("settings.json", "w") as a:
            a.write(json.dumps(save, indent=4, sort_keys=True))
        message_box = QMessageBox()
        message_box.setWindowTitle("Restart needed")
        message_box.setText("To toggle transparency you need to restart the program")
        message_box.setIcon(QMessageBox.Information)
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()
    save_button = QPushButton("Save")
    save_button.clicked.connect(save_data)
    transparency_button = QPushButton("Toggle transparency (Work in progress)")
    transparency_button.clicked.connect(togglet)
    layout = QVBoxLayout()
    layout.addWidget(number_label)
    layout.addWidget(number_entry)
    layout.addWidget(selection_label)
    layout.addWidget(selected_option)
    layout.addWidget(selection_audio_device)
    layout.addWidget(audio_device)
    layout.addWidget(transparency_button)
    layout.addWidget(save_button)
    if qtv:
        closee = QPushButton("Close programm")
        closee.clicked.connect(close_p)
        layout.addWidget(closee)
    central_widget = QWidget()
    central_widget.setLayout(layout)
    new_window.setCentralWidget(central_widget)
    new_window.show()
    if not qtv:
        # Start the application's event loop if no QApplication instance was running
        app.exec_()
    else:
        # Use a QEventLoop to wait for the window to be closed
        loop = QEventLoop()
        new_window.destroyed.connect(loop.quit)
        loop.exec_()
    return close
def charerror(knownerrors,darkmode=False):
    app = QApplication.instance()

    new_window = QMainWindow()
    new_window.setWindowIcon(QIcon('app.ico'))
    new_window.setWindowTitle("Char error menu - pre (unfinished)")
    new_window.setGeometry(0, 0, 700, 400)
    new_window.setFixedSize(new_window.size())
    windowsettings.darkmode(new_window, darkmode)
    windowsettings.nofullscreen(new_window)
    for i, error in enumerate(knownerrors):
        button=False
        error_type=error["type"].replace("-button", "")
        if "-button" in error["type"]:
            add=70
            button=True
        identifyer = QLabel("{0}".format(error_type), new_window)
        identifyer.move(60,i*21)
        errormessage = QLabel("---  {0}".format(error["message"]), new_window)
        errormessage.move(90,i*21)
        errormessage.setMinimumSize(600, 5)
        if button:
            button = QPushButton("{0}".format(error_type), new_window)
            button.setMaximumSize(50,15)
            try:
                if extensions.extensions.extensions[error["event"].split(".")[0]]["status"]=="working":
                    button.clicked.connect(lambda: extensions.extension_event(error["event"].split(".")[0],error["event"].split(".")[1]))
                else:
                    program.char.charerror("warn", "Cant do buttons anymore extension {0} is disabled".format(error["event"].split(".")[0]))
            except:
                #TODO add error message if event is not set
                pass
            button.move(0,8+i*21)

        etype=error_type.replace("warn", "#FFDE59").replace("error", "#EE4345").replace("info", "#98F5F9")
        identifyer.setStyleSheet(f"color: {etype};")
        errormessage.setStyleSheet(f"color: {etype};")

    new_window.show()

    loop = QEventLoop()
    new_window.destroyed.connect(loop.quit)
    loop.exec_()