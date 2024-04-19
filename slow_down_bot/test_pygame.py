import pygame
import pygame._sdl2.audio as sdl2_audio

def get_devices():
    init_by_me = not pygame.mixer.get_init()
    if init_by_me:
        pygame.mixer.init()
    devices = tuple(sdl2_audio.get_audio_device_names(True))
    if init_by_me:
        pygame.mixer.quit()
        
    print(devices)
    return devices

get_devices()