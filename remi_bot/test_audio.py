import pygame

pygame.init()

pygame.mixer.init()
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)  # Set the end event
music_path = "response.mp3"
pygame.mixer.music.load(music_path)
pygame.mixer.music.play()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT + 1:  # SONG_END event
            print("Song ended")
            running = False