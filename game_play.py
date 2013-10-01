import game
import twitter as TW
import ascii as ASC
import msvcrt
import os
import time
import logging
import pygame.mixer as mix
import string
import sys
import Q2logging
from hipsterdom import *

mix.init()
logging.basicConfig(filename='game_play.log',logging=logging.DEBUG)

stops = dict()
challenges = dict()
finds = dict()
sounds= dict() # keep track of which sounds have been played
fights= dict()

g_map = None
global followers
followers = 10
hashes = 20
ats = 20
desc_ct = 0

def main():
    logging.info('Entering main function')
    global g_map
    # load game map
    with open("game.xml") as f:
        xml_file = f.read()
    success, g_map = game.obj_wrapper(xml_file) #turn into python object via Q2API
    if not success:
        logging.warning('obj_wrapper failed in main() before stops')
        print "no object"
        exit()
    # construct global dicts: stops
    global stops # possible positions
    for stop in g_map.stop:
        nomen = stop.attrs["nomen"]
        stops[nomen] = stop

    stop = g_map.stop[0] #inital stop
    # initialize player
    global player
    player = g_map.player[0]
    # initialize extras - list of printable items
    global extras
    extras = ['stop_desc','stop_name','sound']
    logging.info('Entering main() game loop')
    os.system('cls')
    # enter main game loop
    while True:
        describe(stop, extras)
        command = raw_input(">")
        os.system('cls') #clearing for better user experience
        #put directly after command so we can print on either side and it looks cohesive.
        stop = process_command(stop, command)
        logging.info('Command Processed')
        logging.info(str(type(stop))) #make sure that we're passing in variable into loop!

def describe(stop,extras):
    '''
    stop: current stop
    stop_name: don't print the name of the current station
    stop_desc: don't print out the stops name
    ascii: don't print the ascii
    sound: don't play the song
    desc_ct: current description
    '''
    logging.info("Current Extras",extras)
    global desc_ct
    if extras:
        if 'stop_name' in extras:
            print stop.attrs["nomen"].upper(), "STATION"
        if 'badascii' in extras:
            nomen = extras['badascii']

        if 'stop_desc' in extras:
            print stop.desc[desc_ct].value
        if 'ascii' in extras:
            image_to_ascii(stop,False)
        if 'ascii_w_sound' in extras:
            image_to_ascii(stop,True)
        if 'pause_sound' in extras:
            play_music(stop,True)
        if 'sound' in extras:
            play_music(stop)
        if 'around' in extras:
            for p in stop.place:
                    print "\n\t"+"Name for place:", p.attrs.get("nomen")+".", "Direction for place:", p.attrs.get("dir")
                    print "\n\t"+"Place description:", str(p.desc[0].value).strip(string.whitespace)
                    print "_________________________________________________________"
            for i in stop.item:
                    print "\n\t"+"Name for item:", i.attrs.get("nomen")+".", "Direction for place:", i.attrs.get("dir")
                    print "\n\t"+"Item description:", str(i.desc[0].value).strip(string.whitespace)
                    print "__________________________________________________________"
        if 'results' in extras:
            print "After that game you have",hashes, "Hashes, and",ats,"Ats."
            print "You also have", followers,"Followers."
        if 'unknown' in extras:
            print "We don't know what you're talkin' about."
    return stop

def image_to_ascii(stop,pause_sound=False, guess_name=False):
    '''
    separate image_to_ascii function to have guessing game.
    image_folder: where the images are stored
    (All images need to have 3-letter formats a.k.a. .jpegs won't work)
    img: string from stop.attrs
    img_txt: possible text string that would've already been generated
    '''
    image_folder = os.listdir('images/')
    logging.debug('Image folder found.')
    img = str(stop.attrs["im"]).strip(string.whitespace)
    img_txt = img[:-4]+'.txt'
    logging.info(img_txt) #log image text for debugging
    play_music(stop)
    if img_txt in image_folder:
        with open('images/'+img_txt) as f:
            lines = f.read()
            print "Guess ascii by pressing enter!"
            for l in lines.split('\t'):
                time.sleep(1.5)
                print l
    else:
        ascii_string = ASC.image_diff('images/'+img)
        print type(ascii_string)
        fin = open('images/'+img_txt,'w')
        print "file opened"
        for i in range(len(ascii_string)):
            fin.write(ascii_string[i]+'\t')
        fin.close()

def play_music(stop, pause_sound=False):
    global current_sound
    try:
        sound_file = "sounds/"+str(stop.attrs["sd"]).strip(string.whitespace)
        if not pause_sound:
            mix.pause()
            current_sound = mix.Sound(sound_file)
            logging.info('music loaded')
            current_sound.play()
        else:
            mix.pause()
    except:
        print "No music found"

def twitter_data(stop,noun):
    '''
    call_prompt: users input keyword
    hash_diff: difference in hashtags for a RT boss
    ats_diff: difference in ats for a RT boss
    hashes: currently tabulated hashes
    ats: currently tabulated hashes
    '''
    global hashes
    global ats
    print "It's a glare from",noun
    call_prompt = raw_input("What's your call against this mean muggin?!")
    hash_diff, at_diff = twitter_battle(call_prompt,noun)
    hashes += hash_diff
    ats += at_diff
    if hashes <0 or ats<0: #breaks if either returns zero
        print "You're as dead as a doornail."
        print "Would you like to restart?"
        restart = raw_input(">>")
        while True:
            if restart =="Y":
                return main()
            elif restart == "N":
                exit()
            else:
                print "Unknown command"
                continue
    return hashes,ats #returns to

def twitter_battle(call_prompt, boss): # add on followers and amt later
    '''
    Input: boss (boss kw) and prompt (player kw)
    Output: hashes_diff, ats_diff
    '''
    boss_ats = TW.recent_tweets([boss],2)[1]
    boss_hashes = TW.recent_tweets([boss],2)[2]
    player_ats = TW.recent_tweets([call_prompt],3)[1]
    player_hashes = TW.recent_tweets([call_prompt],3)[2]
    ats_diff = player_ats - boss_ats
    hashes_diff = player_hashes - boss_hashes
    print "Hash from battle:", hashes_diff
    print "Holler-Ats from battle:",ats_diff
    if ats_diff > 0:
        ats_winner = 'player'
    elif ats_diff == 0:
        ats_winner = 'equal'
    else:
        ats_winner = 'boss'
    if hashes_diff >0:
        hashes_winner = 'player'
    elif hashes_diff ==0:
        hashes_winner = 'equal'
    else:
        hashes_winner = 'boss'
    #add in check for followers here.
    for scen in g_map.scenario:
        if scen.attrs.get('hashes') == hashes_winner and scen.attrs.get('ats')==ats_winner:
            print scen.value
    return hashes_diff, ats_diff #returns to twitter_data

def process_command(stop, command): #can also pass stop!
    '''
    1. Parse Command
    2. Get Items and places from Command
    3. Handles Twitter Battle
    - Twitter Game play : if desc or stop, or item contains name in fight dict.
    '''
    global desc_ct
    global finds
    global hashes
    global ats
    global extras
    global logging

    descs = descs_dict(stop)
    extras = []
    if len(command) == 0:
        logging.info('Pressed Enter.')
        enter_command(stop,descs)
        return stop
    else:
        verb, noun = parse(command)
        if verb == "go":
            return go_command(stop,noun)
        elif verb == "describe":
            return describe_command(stop,player,noun)
        elif verb== "take":
            return take_command(stop,noun)
        elif verb == "load": #loads game from save directory
            return load_command(stop)
        elif verb == "score": #score board functionality
            return score_command(stop)
        elif verb =="cur":
            print "Hashes:", hashes
            print "Ats:",ats
            for item in g_map.player.item:
                print item.attrs["nomen"]
                try:
                    print "Uses:"
                    for use in item.usage:
                        print use.attrs["nomen"]
                except:
                    print "No uses..."
            return stop
        elif verb=="save":
            return save_command(stop)
        elif verb =="restart":
            return restart_command(stop)
        elif verb =="how":
            print player.item[0].desc[0].value #goal: callable from anywhere in game.
            #add to it's relevancy as you go along...
            return stop
        elif verb == "exit":
            print "Do you want to save your game? (Y,N)?"
            save_file = raw_input('>>')
            if save_file == "Y":
                process_command(stop,'save')
            elif save_file == "N":
                print "OK!"
                exit()
            else:
                print "What?! (Exit Prompt Error)"
                process_command(stop,'exit')
        else:
            print "Unrecognized command"
        return stop

def enter_command(stop,descs):
    '''
    via stop, command and descs
    desc_ct: counter of most recently printed desc
    extras: global dict of what to print next
    '''
    global desc_ct
    global extras
    max_desc = max(descs.keys())
    if max_desc > desc_ct:
        desc_ct+=1
    elif max_desc == desc_ct: # the end of the descs
        print "\n\n You have reached the end of this info. \n\n"
        print "Try typing 'describe around' to learn more options."
        desc_ct = 0
    else: # the beginning of the descs
        desc_ct=0
    extras = ['stop_desc']
    return stop

def go_command(stop,noun):
    global desc_ct
    global extras
    global hashes
    global ats

    for pl in stop.place:
        if noun in pl.attrs.get("nomen"):
            access = pl.attrs["access"]
            if access:
                for itm in player.item:
                    if itm.attrs('nomen')==access:
                        print 'You have a',access, 'To gain access to this stop use it? Use your',access,'?'
                        access_q = raw_input('>>')
                        if access_q.lower() == "y":
                            extras =['stop_name','stop_desc','pause_music']
                            desc_ct=0
                        else:
                            print "Well, then you can't go there."
                            return stop
                    else:
                        print "Well, then you can't go there."
                        return stop

            elif access == "": #if there is no access key in the xml then leave it and let them go.
                    desc_ct = 0
                    extras =['stop_name','stop_desc','pause_music']
            elif access[0] == "cost":
                hashes_cost= access[1]
                ats_cost = access[2]
                print "Do you want to pay for this?"
                print hashes_cost,"Hashes"
                print ats_cost,"Ats"
                pay_cost = raw_input('>>')
                if pay_cost.lower() == 'y':
                    hashes -= hashes_cost
                    ats -= ats_cost
                else:
                    print "Well then I guess you'll just have to find another way!"
                    return stop

            link = pl.attrs["link"]
            stop = stops[link]
            return stop
        else:
            print "This is no place."
    else:
        extras=["bad_go"]
        print "You can't go there."
        extras =['stop_name','stop_desc']
        return stop

def take_command(stop,items,fights,noun):
    global desc_ct
    global extras
    global player
    try:
        for item in stop.item:
            if item.attrs.get("nomen") == noun:
                if finds.get(noun):
                    player.item.append(item)
                    player.children.append(item)
                    stop.item.remove(item)
                    stop.children.remove(item)
                    finds[noun]="True"
            print "You get the " + noun
        return stop
    except:
        print "This item does not exist at this stop!"
        return stop

def describe_command(stop, player, noun):
    # itm,access,ascii,sd = items.get(noun,("","","",""))
    global extras
    global hashes
    global ats
    if noun == "around": #functionality to show current landscape.
        extras = ["around"]
        return stop

    for itm in stop.item:
        if itm.attrs["nomen"] == noun:
            boss= itm.attrs.get("kw")
            if itm.attrs["fights"]:
                hashes, ats = twitter_data(stop,boss)
                extras= ["hashes", "ats", "battle_results"]
                print "You now have", hashes,"ounces of hash"
                print "And",ats, "holler-ats!"

                player.item.append(itm)
                player.children.append(itm)
                stop.item.remove(itm)
                stop.children.remove(itm)
                return stop

            elif itm.attrs["challenge"]:
                extras=["ascii_game"]
                return stop

    for itm in player.item:
        if noun == itm.attrs.get("nomen"):
            print "You already Twitter Battled the", noun
        extras = ['describe_place','describe_access']
        return stop

    for pl in stop.place:
        if pl.attrs.get("nomen")==noun:
            extras= ['describe_place', 'describe_access']
            return stop
    extras = ['unknown']
    return stop

def restart_command():
    print "Restart game? (Y/N)"
    restart_game = raw_input('>>')
    if restart_game == "Y":
        print "Do you want to save first? (Y/N)"
        save_first = raw_input('>>')
        if save_first == 'Y':
            return save_command()
        else:
            return main()
    elif restart_game == "N":
        print "OK!"
        exit()
    else:
        print "Unrecognized command, I'll just let you keep playing!"

def save_command(stop):
    stop_nomen = stop.attrs["nomen"]
    player.attrs["stop"] = str(stop_nomen)
    player.attrs["hashes"] = hashes
    player.attrs["ats"]= ats
    player.attrs["followers"] = followers

    save_file = raw_input("enter a name for the save file>")
    with open("save\\" + save_file + ".xml", "w+") as f:
        f.write(g_map.flatten_self())
        print "game saved!"
    print "Continue game ? (Y/N) (Pressing N will put exit the game!)"
    continue_game = raw_input('>>')
    if continue_game == "Y":
        return stop
    elif continue_game == "N":
        print "OK!"
        exit()
    else:
        print "Unrecognized noun, I'll just let you keep playing!"

def score_command(stop):
    games = os.listdir("save")
    save_count = 0
    for i, file_name in enumerate(games): #prints the players
        if file_name[-4:]=='.xml':
            try:
                print str(i) + "\t" + file_name.split(".")[0]
            except:
                print "couldn't print game"
            try:
                print "Ats:",load_ats_hashes(file_name)[0]  + "\t" + "Hashes:",load_ats_hashes(file_name)[1]
            except:
                print "couldn't find scores"
            try:
                print "Items placeholder:"
            except:
                pass
            try:
                print "Hollers and Lifelines placeholder:"
            except:
                pass
            try:
                pass
            except:
                pass
        save_count += 1
    if save_count == 0:
        print "No saved games!"
        return stop
    return stop

def load_command(stop):
    games = os.listdir("save")
    if len(games)>1:
        for i, file_name in enumerate(games): #prints the players to console
            if file_name.split(".")[1]=='.xml':
                print str(i) + "\t" + file_name.split(".")[0]

        print "Choose a game by its number, or type new for new game.\n"
        choice = raw_input(">>")
        if choice not in ["N", "n", "new", "NEW"]:
            try:
                game_file = "save\\" + games[int(choice)]
            except:
                print "You didn't give a proper number..."
                game_file = 'game.xml'
        else:
            return stop
            #game_file = "game.xml"

    else:
        print "\n\t\tCould not find any saved games!"
        print "\n\t\tType start or exit!"
        #game_file = 'game.xml'
        return stop

    return load_game(game_file)

def load_game(game_file):
    '''
    Input: game_file from load command()
    Output: stop object from player profile.

    '''
    logging.info('Found load_game')
    with open(game_file) as f:
        xml_file = f.read()
    #wrap player map here
    success, p_map = game.obj_wrapper(xml_file)
    if not success:
        logging.info('From Q2API - Obj_wrapper failed when loading game')
        exit()
    global player #only need player from file
    global stops #grab dict from main file so that we can call current stop from nomen attribute

    player = p_map.player[0] #assign player via Q2API.xml.mk_class syntax
    nomen = player.attrs["stop"] #grab stop from player's xml file and return for game play
    stop = stops[nomen]

    for itm in player.item: #constructs finds dict from loaded player.
        if itm.attrs["finds"]=='true':

            boss_kw = itm.attrs["boss_kw"]
            logging.info('User has item:'+boss_kw)
            ats = str(itm.value).split(',')[0].strip() #returns ats from unicode
            hashes = str(itm.value).split(',')[1].strip() #returns hashes from unicode
            finds[boss_kw] = ats,hashes
        else:
            logging.info('No item found')
    logging.info('Leaving load_game')
    return stop

def load_ats_hashes(game_file):
    '''
    Loads ats and hashes from player given profile.

    '''
    logging.info('Found load_ats_hashes')
    global ats
    global hashes
    with open('save/'+game_file) as f:
        xml_file = f.read()

    success, p_map = game.obj_wrapper(xml_file)
    #call player map here because we are not altering most of the file.
    if not success:
        print "Failure to wrap object."
        exit()
    global player #only need player from file
    player = p_map.player[0]
    ats = player.attrs["ats"] #grab stop from player's xml file and return for game play
    hashes = player.attrs["hashes"]
    logging.info('Leaving load_ats_hashes')
    return ats,hashes

def descs_dict(stop): #can also pass place and will have same result
    descs = dict()
    desc_ct = 0
    for d in stop.desc:
        descs[desc_ct] = d.value
        desc_ct+=1
    return descs

def parse(cmd):
    cmd = one_word_cmds.get(cmd, cmd)
    print cmd
    words = cmd.split()
    verb = words[0]
    verb = translate_verb.get(verb, "BAD_VERB")
    noun = " ".join(words[1:])
    noun = translate_noun.get(noun, noun)
    return verb, noun



translate_verb = {"g" : "go","go" : "go","walk" : "go","jump" : "go",
                  "t" : "take", "take" : "take","grab" : "take","get":"take",
                  "l":"describe","look":"describe","describe" : "describe","desc":"describe",
                  "current":"cur","cur":"cur","give":"cur",
                  "load":"load","save":"save",
                  "how":"how","help":"how",
                  "exit":"exit",
                  "score":"score"
                  }

translate_noun = {"n": "n","north":"n",
                  "s": "s","south": "s",
                  "e" : "e","east" : "e",
                  "w" : "w","west" : "w",
                  "u" : "u", "up" : "u","surface":"u",
                  "d" : "d", "down" : "d",
                  "a" : "a","across":"a","over":"a","cross":"a",
                  "i":"i","h":"i", "inventory":"i",
                  "board":"board",
                  "start":"start",
                  }

one_word_cmds = {"n" : "describe n","s" : "describe s","e" : "describe e","w" : "describe w",
                 "u" : "describe u","up": "describe u",
                 "d" : "describe d",
                 "off" :"describe outside",
                 "on":"describe on",
                 "l":"load game","load":"load game",
                 "current": "describe around","now": "describe around","around":"describe around","describe":"describe around",
                 "i":"cur inventory","h":"cur inventory",
                 "rules":"how to","how":"how to","help":"how to",
                 "next": "go start","begin":"go start","start":"go start",
                 "score":"score board",
                 "commands":"commands",
                 }
main()