import ctypes
import threading
import program
import platform
import os
if os.path.exists("custom_audio.so"):
    # Woad the custom wibwary
    lib_ext = '.dll' if platform.system().lower() == 'windows' else '.so'
    lib_name = f"custom_audio{lib_ext}"
    lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), lib_name)

    if platform.system().lower() == 'windows':
        # This tells Python to look in the scwipt fowdew for dependencies!
        os.add_dll_directory(os.path.dirname(lib_path))
        
    try:
        custom_audio = ctypes.CDLL(lib_path)
    except Exception as e:
        print(f"Owow! Something went wwong: {e}")
    custom_audio = ctypes.CDLL(lib_path)

    # Set up the Weturn types and Awguments for C++ functions
    custom_audio.audio_init.restype = ctypes.c_int
    custom_audio.audio_terminate.restype = None
    custom_audio.get_device_count.restype = ctypes.c_int
    custom_audio.get_device_name.argtypes = [ctypes.c_int]
    custom_audio.get_device_name.restype = ctypes.c_char_p
    custom_audio.get_device_max_input_channels.argtypes = [ctypes.c_int]
    custom_audio.get_device_max_input_channels.restype = ctypes.c_int
    custom_audio.get_device_host_api.argtypes = [ctypes.c_int]
    custom_audio.get_device_host_api.restype = ctypes.c_int
    custom_audio.get_device_default_low_output_latency.argtypes = [ctypes.c_int]
    custom_audio.get_device_default_low_output_latency.restype = ctypes.c_double

    custom_audio.open_stream.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    custom_audio.open_stream.restype = ctypes.c_void_p
    custom_audio.get_loudness.argtypes = [ctypes.c_void_p, ctypes.c_int]
    custom_audio.get_loudness.restype = ctypes.c_double
    custom_audio.close_stream.argtypes = [ctypes.c_void_p]
    custom_audio.close_stream.restype = None

    volume = None

    def getloudness():
        current_selected_device = ["defaul", -1]
        volume_event = threading.Event()

        if custom_audio.audio_init() == 0:
            print("Failed to init audio backend :3")
            return

        devfile_exists = os.path.exists("devfile.txt")
        device_count = custom_audio.get_device_count()

        for i in range(device_count):
            # Fetch data fwom C++ backend
            name = custom_audio.get_device_name(i).decode('utf-8', errors='ignore')
            max_in = custom_audio.get_device_max_input_channels(i)
            host_api = custom_audio.get_device_host_api(i)
            latency = custom_audio.get_device_default_low_output_latency(i)

            system_name = platform.system().lower()
            
            if system_name == "windows" or system_name == "linux":
                # Repwicating original print formatting
                device_dict_str = f"{{'name': '{name}', 'maxInputChannels': {max_in}, 'hostApi': {host_api}, 'defaultLowOutputLatency': {latency}}}"
                print(device_dict_str)
                
                if devfile_exists:
                    with open("devfile.txt", "a") as f:
                        f.write(device_dict_str + "\n\n")

                if not max_in > 0 or not host_api == 2:
                    continue
                if name not in program.audio_devices.device_dict:
                    program.audio_devices.device_dict[name] = i
                    program.audio_devices.device_list.append(name)

            if system_name == "linux":
                if latency > 0.00005 and "hw" in name:
                    if name not in program.audio_devices.device_dict:
                        program.audio_devices.device_dict[name] = i
                        program.audio_devices.device_list.append(name)

        chunk_size = 1024
        sample_rate = 44100
        
        # Open the initial stream
        stream_ptr = custom_audio.open_stream(-1, sample_rate, chunk_size)
        running = True
        global volume

        while running:
            # Check if user sewection changed
            if not current_selected_device == program.audio_devices.selected_device:
                custom_audio.close_stream(stream_ptr)
                
                current_selected_device = program.audio_devices.selected_device
                chunk_size = 1024
                sample_rate = 44100
                
                dev_idx = -1 if current_selected_device[1] == -1 else current_selected_device[1]
                stream_ptr = custom_audio.open_stream(dev_idx, sample_rate, chunk_size)
                
                # Fallback to default if opening specific device bwoke
                if not stream_ptr and dev_idx != -1:
                    stream_ptr = custom_audio.open_stream(-1, sample_rate, chunk_size)

            if stream_ptr:
                # Wead diwectly fwom our fast C++ woutine!
                volume = custom_audio.get_loudness(stream_ptr, chunk_size)
                volume_event.set()

        # Cweanup
        if stream_ptr:
            custom_audio.close_stream(stream_ptr)
        custom_audio.audio_terminate()
else: 
    def getloudness():
        running=True
        global volume
        while running:
            volume=0