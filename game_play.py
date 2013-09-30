import game
import twitter as TW
import ascii as ASC
import msvcrt
import os
import time
import logging
import pygame.mixer as mix
import string
import Q2logging

mix.init()
logging.basicConfig(filename='game_play.log',logging=logging.DEBUG)
#sys.path.insert(0,'C:/Users/nwatkins/PycharmProjects/PusherMan')

stops = dict()
finds = dict()
sounds= dict() # keep track of which sounds have been played

battles = dict()
#initialize hashes and ats
g_map = None
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
    # construct global dicts: stops and battles
    global stops # possible positions
    for stop in g_map.stop:
        nomen = stop.attrs["nomen"]
        stops[nomen] = stop
    stop = g_map.stop[0] #inital stop
    # battles is a dict of twitter battle result descriptions
    global battles
    for scenario in g_map.scenario: # load scenarios into dict with ats, hashes
        ats = scenario.attrs['ats']
        hashes = scenario.attrs['hashes']
        battles[(ats,hashes)] = scenario
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
    if len(extras)>0:
        if 'stop_name' in extras:
            print stop.attrs["nomen"].upper(), "STATION"

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
        current_sound.pause()
        current_sound = mix.Sound()
        mix.music.load(sound_file)
        logging.info('music loaded')
        if not pause_sound:
            mix.music.play()
        else:
            mix.music.pause()
    except:
        print "No music found"

def twitter_data(stop,boss_kw):
    '''
    call_prompt: users input keyword
    hash_diff: difference in hashtags for a RT boss
    ats_diff: difference in ats for a RT boss
    hashes: currently tabulated hashes
    ats: currently tabulated hashes
    '''
    global hashes
    global ats
    print "It's a glare from", boss_kw
    call_prompt = raw_input("What's your call against this mean muggin?!")

    hash_diff, at_diff = battle(boss_kw,call_prompt)
    finds[boss_kw] = hash_diff,at_diff
    #maybe use get function here to define
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
    return hashes,ats

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

    places, items, fights, descs = get_data(stop)
    logging.debug("Places:", places, type(places))
    logging.debug("Items:", items, type(items))
    logging.debug("Fights:", fights, type(fights))
    logging.debug("Descs:", descs, type(descs))

    extras = []
    if len(command) == 0:
        logging.info('Pressed Enter.')
        enter_command(stop,descs)
        return stop
    else:
        verb, noun = parse(command)
        if verb == "go":
            return go_command(stop,places,noun)
        elif verb == "describe":
            return describe_command(stop,items,places,fights,noun)
        elif verb== "take":
            return take_command(stop,items,fights,noun)
        elif verb == "load": #loads game from save directory
            return load_command(stop)
        elif verb == "score": #score board functionality
            return score_command(stop)
        elif verb =="cur":
            print "Hashes:", hashes
            print "Ats:",ats
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
        print "\n\n You have reached the end of this info. Try typing 'describe around' to learn options."
        desc_ct = 0
    else: # the beginning of the descs
        desc_ct=0
    extras = ['stop_desc']
    return stop

def go_command(stop,places,noun):
    '''
    places: dictionary of the form: places[noun]: pl object, acess string
    '''
    global desc_ct
    global extras
    try:
        pl,access = places.get(noun)
    except:
        print "Not a place!"

    if access == "":
        desc_ct = 0
        link = pl.attrs["link"]
        stop = stops[link]
        extras =['stop_name','stop_desc','pause_music']
        return stop

    elif pl and finds[access]== True:
        print "found finds"
        desc_ct = 0
        link = pl.attrs["link"]
        stop = stops[link]
        extras =['stop_name','stop_desc','pause_music']
        return stop

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
                    finds[noun]=True

            print "You get the " + noun
        return stop
    except:
        print "This item does not exist at this stop!"
        return stop

def describe_command(stop,items,places,fights, noun):
    pl,access = places.get(noun,(False,True))
    itm,access,ascii,sd = items.get(noun,("a","a","a","a"))
    boss_kw = noun
    global extras
    if noun == "around": #functionality to show current landscape.
        extras = ["around"]

    elif fights.get(boss_kw) == 'true':
        #this loops checks to
        if finds.get(boss_kw,False):
            print "You already Twitter Battled the", boss_kw.upper(),"!"
        else:
            hashes, ats = twitter_data(boss_kw)
            print "You now have", hashes,"ounces of hash"
            print "And",ats, "holler-ats!"
            finds[boss_kw] = hashes,ats
    elif pl:
        print "Not everybody's trying to hustle a hustler!"
        print pl.desc[0].value

    elif itm and not bool(itm): #checks to make sure it's not a string as well...
        print "Grab it!"
        print itm.desc[0].value
    return stop

def restart_command(stop):
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
    # player.attrs["hollers"]= hollers
    # player.attrs["lifelines"] =lifelines

    player.attrs["hashes"] = hashes
    player.attrs["ats"] = ats

    for itm in player.item:
        if itm.attrs["boss_kw"] in finds.keys():
            itm.attrs["finds"] = 'true'
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
        else:
            game_file = "game.xml"
            return stop
    else:
        print "\n\t\tCould not find any saved games!"
        print "\n\t\tType start or exit!"
        game_file = 'game.xml'
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
    with open('../save/'+game_file) as f:
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

def get_data(stop): #can also pass stop and will have same result!
    places = dict()
    fights = dict()
    items = dict()
    descs = dict()
    desc_ct=0

    for pl in stop.place:
        nomen = pl.attrs["nomen"]
        dirs = pl.attrs.get("dir")
        access = pl.attrs.get("access")
        fight = pl.attrs.get("fight", "False")
        places[nomen] = pl,access
        places[dirs] = pl,access
        fights[nomen] = fight

    for itm in stop.item:
        nomen = itm.attrs["nomen"]
        access = itm.attrs["access"]
        sd = itm.attrs["sd"]
        ascii = itm.attrs["im"]
        fight = itm.attrs.get("fight", "False")
        items[nomen] = itm,access,ascii,sd
        fights[nomen] = fight

    for d in stop.desc:
        descs[desc_ct] = d.value
        desc_ct+=1
    return places, items, fights, descs

def parse(cmd):
    cmd = one_word_cmds.get(cmd, cmd)
    print cmd
    words = cmd.split()
    verb = words[0]
    verb = translate_verb.get(verb, "BAD_VERB")
    noun = " ".join(words[1:])
    noun = translate_noun.get(noun, noun)
    return verb, noun

def battle(boss_kw, call_prompt):
    '''
    Input: boss_kw and prompt for 'call' or 'gang call'
    Output: hashes_diff, ats_diff
    '''
    boss_ats = TW.retweets()[1]
    boss_hashes = TW.retweets()[2]
    player_ats = TW.recent_tweets([call_prompt],1)[1]
    player_hashes = TW.recent_tweets([call_prompt],1)[2]
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
    print battles[(ats_winner,hashes_winner)].desc[0].value
    return hashes_diff, ats_diff

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