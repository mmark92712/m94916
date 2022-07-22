#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib.resources import contents
import helper as h
from random import randrange
import time
from tbot import Tbot

__carefull__ = False
__counter__ = 0
__max_replays__ = 2

def iterate(tbot, c):

    global __max_replays__
    global __carefull__
    global __counter__

    max_replys = __max_replays__

    # iterate through bots

    for i in range(0, len(c.bots)):

        h.colors.info(f"Info: Checking bot {h.colors.cbold}{c.bots[i]}")

        # get new tweets
        last_tweets, last_tweets_text = tbot.get_tweets_newer_than_id(c.bots[i], c.last_tweet_ids[i])

        iters = len(last_tweets)
        if len(last_tweets) > 0:
            if len(last_tweets) > max_replys: iters = max_replys

            # for each of last "max_reply" tweets, generate a reply
            for j in range(0, iters):

                # check for relevance
                relevant = h.check_post_relevance(last_tweets_text[j])

                if relevant:

                    if __carefull__:
                        h.colors.warn(f"Tweet: {last_tweets_text[j]}")
                        res = input(">>> Type n/N to cancel: ")
                        if res == 'n' or res == 'N':
                            continue

                    # randomly pick a post
                    article_num = len(c.articles)
                    article = randrange(0, article_num)

                    reply_text = c.text[article] + "\n" + c.articles[article]
                    tweet_id = str(last_tweets[j])
                    h.colors.info(f"Info: Replying to {c.bots[i]}, tweet id: {tweet_id}. Posted text: {h.colors.cbold}{c.text[article]}")
                    tbot.reply_on_tweet(reply_text, tweet_id)
                    __counter__ += 1


                elif __carefull__:
                    h.colors.warn(f"Warning: Tweet from {c.bots[i]} not matching the criteria. Tweet id: {str(last_tweets[j])}. Tweet text: {h.colors.cbold}{last_tweets_text[j]}")

                    # fix boilerplate
                    res = input(">>> Type y/Y to reply anyway: ")
                    if res != 'y' and res != 'Y':
                        continue

                    # randomly pick a post
                    article_num = len(c.articles)
                    article = randrange(0, article_num)

                    reply_text = c.text[article] + "\n" + c.articles[article]
                    tweet_id = str(last_tweets[j])
                    h.colors.info(f"Info: Replying to {c.bots[i]}, tweet id: {tweet_id}. Posted text: {h.colors.cbold}{c.text[article]}")
                    tbot.reply_on_tweet(reply_text, tweet_id)
                    __counter__ += 1


                # update last_tweets
            c.last_tweet_ids[i] = last_tweets[0]


def main():
    h.print_banner()
    config = h.Config()
    content = h.Content(config.bots_file, config.articles_file)

    tbot = Tbot(config.consumer_key, config.consumer_secret, config.access_token, config.access_token_secret, config.bearer_token)

    # Example 1: get recent tweets from a user
    # username = "some_twitter_user_name"
    # r = tbot.get_recent_tweets_for_user(username)
    # if r is not None: print(r)

    # Example 2: post a tweet
    # text = """Ukraine war: Kyiv’s emergence from the shadow of war
    # https://www.bbc.com/news/world-europe-61671917?xtor=AL-72-%5Bpartner%5D-%5Bbbc.news.twitter%5D-%5Bheadline%5D-%5Bnews%5D-%5Bbizdev%5D-%5Bisapi%5D&at_custom4=B3D51B6A-E2F7-11EC-B1FD-E48E4744363C&at_custom1=%5Bpost+type%5D&at_campaign=64&at_custom2=twitter&at_medium=custom7&at_custom3=%40BBCWorld
    # """
    # tbot.create_tweet(text)

    # Example 3: reply to a tweet
    # reply_text = "https://www.aspistrategist.org.au/putins-empire-of-lies/"
    # tweet_id = "1532656026578714624"
    # tbot.reply_on_tweet(reply_text, tweet_id)

    # Example 4: get last tweet id for a user
    # user_id = "1499749818415075335"
    # id = tbot.get_last_tweet_id(user_id)
    # print(id)
    
    # get bots ids
    h.colors.info("Info: Acquiring bots ids.")
    content.bots_id = tbot.get_user_id(content.bots)

    # get their last tweet ids
    # and save it to content.last_tweet_ids
    h.colors.info("Info: Acquiring bots last tweet ids.")
    for i in range(0, len(content.bots_id)):
        id = tbot.get_last_tweet_id(content.bots_id[i])
        content.last_tweet_ids.extend([id])


    h.colors.info("Info: Initiating loop ...")
    while (1):
        h.colors.warn("Warning: Starting new iteration ...")

        iterate(tbot, content)
        h.colors.warn(f"Warning: Total {__counter__} replyes posted.")
        h.colors.info(f"Info: Next iteration in {config.sleep} seconds.")
        time.sleep(config.sleep)

    
if __name__ == "__main__":
    main()
