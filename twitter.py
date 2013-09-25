

import os
from TwitterSearch import *
import string

def keywords(name):
    '''
    name: list of keywords to search for in a tweet
    tweet: list meant to be passed in to term_tweet function
    '''
    tweet = []
    try:
        for word in name.split():
            tweet.append(word)
    except:
        tweet.append(name)

    return tweet

def recent_tweets(term,amt): #takes in term and
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

