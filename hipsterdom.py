import logging
import time
import msvcrt
import os
import string
import ascii as ASC
import pygame.mixer as mix

def image_to_ascii(stop,pause_sound=False):
    '''
    separate image_to_ascii function to have guessing game.
    image_folder: where the images are stored
    (All images need to have 3-letter formats a.k.a. .jpegs won't work)
    img: string from stop.attrs
    img_txt: possible text string that would've already been generated
    '''
    logging.debug('image_to_ascii function entered.')
    global hashes
    global ats
    image_folder = os.listdir('images/')
    logging.debug('Image folder found.')
    img = str(stop.attrs["im"]).strip(string.whitespace)
    img_txt = img[:-4]+'.txt'
    logging.info(img_txt) #log image text for debugging
    play_music(stop)
    boss_kw = str(stop.attrs["nomen"]).strip(string.whitespace)
    #shorten this in game_play2
    if img_txt in image_folder:
        with open('images/'+img_txt) as f:
            lines = f.read()
            print "Guess ascii by pressing enter!"

            for l in lines.split('\t'):

                while not msvcrt.kbhit():
                    time.sleep(.2)
                    break
                print l

                while msvcrt.kbhit():
                    msvcrt.getch()
                    play_music(stop,True)
                    print "-----------------------------------------------"
                    print "What's your guess?"
                    boss_guess = raw_input(">>")

                    if boss_guess == boss_kw:
                        print "You guessed right! Here are 5 hashes and ats for your prowess!"
                        hashes += 5
                        ats += 5
                    else:
                        mix.play()
    else:
        ascii_string = ASC.image_diff('images/'+img)
        print type(ascii_string)
        fin = open('images/'+img_txt,'w')
        print "file opened"
        for i in range(len(ascii_string)):
            fin.write(ascii_string[i]+'\t')
        fin.close()

def play_music(stop, pause_sound=False):
    #sound_delay = str(stop.attrs["delay"]).strip(string.whitespace)
    try:
        sound_file = "sounds/"+str(stop.attrs["sd"]).strip(string.whitespace)

        mix.music.load(sound_file)
        logging.info('music loaded')
        if not pause_sound:
            mix.music.play()
        else:
            mix.music.pause()
    except:
        print "No music found"