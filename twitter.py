import os
from TwitterSearch import *
import string

def keywords(name):
    '''
    name: list of keywords to search for in a tweet
    tweet: list meant to be passed in to term_tweet function
    '''
    tweet = [] #initialize list because keywords must be submitted to API in list.
    try:
        for word in name.split():
            tweet.append(word)
    except:
        tweet.append(name)
    return tweet

def recent_tweets(term,amt):
    '''
    tso: TwitterSearchOrder instance
    '''
    try:
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.setKeywords(term) # let's define all words we would like to have a look for
        tso.setLanguage('en') # we want to see German tweets only
        tso.setCount(7) # please dear Mr Twitter, only give us 7 results per page
        tso.setIncludeEntities(False) # and don't give us all those entity information
        # it's about time to create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key = 'anOyC9WPt8qP82BkKGt34A',
            consumer_secret = 'FzAFLwXEunP34fwu3VItB3zr1P8MTOg4URuNVEI1U',
            access_token = '307461472-FZDgkwOuqLnKXYUtUaJzyJYZpFp1Nhy4IrlBURz1',
            access_token_secret = 'hoiFrBIe85VbtyMbYcxrXjbFhqUF4a6Qjolw5qbKXc'
         )
        tweet_count = 0
        at_count = 0
        hash_count = 0
        for tweet in ts.searchTweetsIterable(tso):
            for char in tweet['text']:
                if char =="@":
                    at_count +=1
                if char == "#":
                    hash_count +=1

            tweet_count+=1
            #print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
            if tweet_count >=amt:
                break
        #print tweet_count, at_count, hash_count
        return tweet_count, at_count, hash_count
    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        #print(e)
        print "Over-exerting Twittter!! Come back in a few, you bad, bad warrior."

def retweets(): #returns ats and hashes of most recent retweet
    tweets, ats, hashes= recent_tweets(['RT'], 1)
    return tweets, ats, hashes

def twitter_battle(call_prompt, boss): # add on followers and amt later
    '''
    Input: boss (boss kw) and prompt (player kw)
    Output: hashes_diff, ats_diff
    '''
    boss_ats = recent_tweets([boss],1)[1]
    boss_hashes = recent_tweets([boss],1)[2]
    player_ats = recent_tweets([call_prompt],1)[1]
    player_hashes = recent_tweets([call_prompt],1)[2]
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
        if scen.attrs.get('hashes') and scen.attrs.get('ats'):
            print scen.value
    return hashes_diff, ats_diff #returns to twitter_data