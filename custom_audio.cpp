#include <portaudio.h>
#include <cmath>
#include <vector>

extern "C" {
    // Initialize & Terminate
    int audio_init() {
        return Pa_Initialize() == paNoError ? 1 : 0;
    }
    void audio_terminate() {
        Pa_Terminate();
    }

    // Device Information
    int get_device_count() {
        return Pa_GetDeviceCount();
    }
    const char* get_device_name(int index) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(index);
        return info ? info->name : "";
    }
    int get_device_max_input_channels(int index) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(index);
        return info ? info->maxInputChannels : 0;
    }
    int get_device_host_api(int index) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(index);
        return info ? info->hostApi : -1;
    }
    double get_device_default_low_output_latency(int index) {
        const PaDeviceInfo* info = Pa_GetDeviceInfo(index);
        return info ? info->defaultLowOutputLatency : 0.0;
    }

    // Stream Handling Struct
    typedef struct {
        PaStream* stream;
    } AudioStream;

    AudioStream* open_stream(int device_index, int sample_rate, int chunk_size) {
        PaStreamParameters inputParams;
        if (device_index < 0) {
            inputParams.device = Pa_GetDefaultInputDevice();
        } else {
            inputParams.device = device_index;
        }

        if (inputParams.device == paNoDevice) return nullptr;

        inputParams.channelCount = 1;
        inputParams.sampleFormat = paInt16;
        inputParams.suggestedLatency = Pa_GetDeviceInfo(inputParams.device)->defaultLowInputLatency;
        inputParams.hostApiSpecificStreamInfo = nullptr;

        PaStream* stream;
        PaError err = Pa_OpenStream(&stream, &inputParams, nullptr, sample_rate, chunk_size, paNoFlag, nullptr, nullptr);
        if (err != paNoError) return nullptr;

        err = Pa_StartStream(stream);
        if (err != paNoError) {
            Pa_CloseStream(stream);
            return nullptr;
        }

        AudioStream* s = new AudioStream;
        s->stream = stream;
        return s;
    }

    // Calculates loudness inside C++ (supew fast!)
    double get_loudness(AudioStream* s, int chunk_size) {
        if (!s || !s->stream) return 0.0;
        
        std::vector<short> buffer(chunk_size);
        PaError err = Pa_ReadStream(s->stream, buffer.data(), chunk_size);
        
        if (err != paNoError && err != paInputOverflowed) return 0.0;

        double sum = 0;
        for (int i = 0; i < chunk_size; ++i) {
            sum += std::abs(buffer[i]);
        }
        return sum / chunk_size;
    }

    void close_stream(AudioStream* s) {
        if (s && s->stream) {
            Pa_StopStream(s->stream);
            Pa_CloseStream(s->stream);
            delete s;
        }
    }
}