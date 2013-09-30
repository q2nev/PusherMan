import logging
import time
import msvcrt
import os
import string
import ascii as ASC

import pygame.mixer as mix
import game
# logging.basicConfig(filename='hipsterdom.log')
# hashes = 20
# ats = 20
# mix.init()
# with open("game.xml") as f:
#     xml_file = f.read()
# success, g_map = game.obj_wrapper(xml_file) #turn into python object via Q2API
# if not success:
#     logging.debug('obj_wrapper failed in main() before stops')
#     print "no object"
#     exit()
#
# stop = g_map.stop[1]

def ascii_challenge(stop,pause_sound=False):
    '''
    separate image_to_ascii function to have guessing game.
    image_folder: where the images are stored
    (All images need to have 3-letter formats a.k.a. .jpegs won't work)
    img: string from stop.attrs
    img_txt: possible text string that would've already been generated
    '''
    global hashes
    global ats
    global current_sound

    logging.debug('image_to_ascii function entered.')

    image_folder = os.listdir('images/')

    logging.debug('Image folder found.')

    img = str(stop.attrs["im"]).strip(string.whitespace)
    img_txt = img[:-4]+'.txt'
    logging.debug("Image Text:",img_txt) #log image text for debugging
    play_ascii(stop)
    boss_kw = str(stop.attrs["nomen"]).strip(string.whitespace)


    if img_txt in image_folder:
        with open('images/'+img_txt) as f:
            lines = f.read()
            print "Guess ascii by pressing enter!"

            for l in lines.split('\t'):

                while not msvcrt.kbhit():
                    time.sleep(1.2)
                    break
                print l

                while msvcrt.kbhit():
                    current_sound.stop()
                    msvcrt.getch()

                    print "-----------------------------------------------"
                    print "What's your guess?"
                    print boss_kw

                    boss_guess = raw_input(">>")
                    if boss_guess == boss_kw:
                        current_sound.play()
                        print "You guessed right! Here are 5 hashes and ats for your prowess!"
                        hashes += 5
                        ats += 5
                        return hashes, ats
                    else:
                        play_ascii(stop,False)
    else:
        print "Converting jpg to txt!"
        ascii_string = ASC.image_diff('images/'+img)
        print type(ascii_string)
        fin = open('images/'+img_txt,'w')
        print "file opened"
        for i in range(len(ascii_string)):
            fin.write(ascii_string[i]+'\t')
        fin.close()
    return hashes,ats

def play_ascii(stop, pause_sound=False):
    global current_sound

    try:
        sound_file = "sounds/"+str(stop.attrs["sd"]).strip(string.whitespace)
        logging.info("Soundfile:", sound_file)
        current_sound = mix.Sound(sound_file)
        # mix.music.load(sound_file)
        logging.info('music loaded')
        if not pause_sound:
            current_sound.play()
        else:
            current_sound.stop()
    except:
        print "No music found"

