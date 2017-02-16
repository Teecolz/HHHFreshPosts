"""
@HHHFreshPosts
"""
# pylint: disable=C0103
# pylint: disable=E0401
import time
import string
import codecs
import praw
import prawcore
import tweepy
import keys

def strip_title(title):
    """
    Makes sure title isn't too long to tweet
    """
    if len(title) < 90:
        return title
    else:
        return title[:89] + "..."


def valid_link(link):
    """
    Checks if submission link is considered valid, if it is from a known website.
    """
    if ("soundcloud") or ("youtu") or ("bandcamp") or ("piff") in link:
        valid = True
        print link + " is a valid link."
    else:
        valid = False
        print link + " is invalid link."
    return valid


def decide_upvotes(title):
    """
    Decides number of upvotes needed to tweet based on a few different factors.
    """
    knwnVotes = ["Freestyle", "FREESTYLE", "Snippet", "SNIPPET", "LIVE", "Live",
                 "VIDEO]", "Video]", "[FRESH SPOTIFY]", "[Fresh Spotify]"]
    # unkVotes = ["Freestyle"]
    if known_artist(title):
        if any(substring in title for substring in knwnVotes):
            needed = 9
            return needed
        else:
            needed = 4
    else:
        if "Freestyle" in title:
            needed = 12
            return needed
        else:
            needed = 9
    return needed


def banned_authors(author):
    """
    Makes sure our submission author isn't on our banned list.
    """
    with codecs.open('banned_authors.txt', 'r', 'utf8', errors='ignore') as authors:
        for line in authors:
            line = line.strip()
            if line in author:
                print "BANNED AUTHOR: " + author
                return True
            else:
                return False


def tweet_creator(subreddit_info):
    """
    Search the subreddit and assemble our tweet if it's FRESH and has enough upvotes.
    """
    post_dict = {}
    post_ids = []
    bannedWords = ["ORIGINAL", "Original", "[OC]"]
    requiredWords = ["[FRESH", "[Fresh"]
    print "[bot] ..............Getting Fresh posts from HHH.............."
    # pylint: disable=R0101
    try:
        for submission in subreddit_info.new(limit=10):
            if submission.title[0] == "[":
                if any(substring in submission.title for substring in requiredWords):
                    if all(substring not in submission.title for substring in bannedWords):
                        needed = decide_upvotes(submission.title)
                        if submission.score > needed:
                            if not banned_authors(submission.author.name):
                                post_dict[strip_title(
                                    submission.title)] = submission.url
                                post_ids.insert(0, submission.id)
                        else:
                            print ("[found fresh post with %s upvotes, it needs %s]"
                                   % (str(submission.score), str(needed + 1)))
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)
    except prawcore.PrawcoreException as e:
        print "--------------REDDIT Prawcore ERROR---------------"
        print e
        time.sleep(30)

    mini_post_dict = {}
    for post in post_dict:
        post_title = post
        post_link = post_dict[post]
        mini_post_dict[post_title] = post_link
    return mini_post_dict, post_ids


def setup_connection_reddit(subreddit):
    """
    Log in to reddit
    """
    print "[bot] setting up connection with Reddit"
    red = praw.Reddit(client_id=keys.CLIENT_ID, client_secret=keys.CLIENT_SECRET,
                      password=keys.password, user_agent=keys.USER_AGENT, username=keys.username)
    subreddit = red.subreddit(subreddit)
    print red.user.me()
    return subreddit


def known_artist(title):
    """
    Checks if artist is in our Known Artists list
    """
    known = False
    with codecs.open('artist_list.txt', 'r', 'utf8', errors='ignore') as artists:
        for line in artists:
            line = line.strip()
            title2 = title.title()
            try:
                if line in title:
                    print title[:40] + " is KNOWN artist."
                    known = True
                    return known
                if line in title2:
                    print title[:40] + " is KNOWN artist (using title2)."
                    known = True
                    return known
            except UnicodeEncodeError as e:
                print e
                print "UnicodeEncodeError"
                known = False
                return known
    if not known:
        try:
            print title[:40] + " is UNKNOWN."
        except UnicodeEncodeError as e:
            print e
    return known


def duplicate_check(postID):
    """
    [DEPRECIATED]
    One method of duplication check:
        Checks if Post ID is in our posted_posts list.
    """
    found = 0
    with open('posted_posts.txt') as posted:
        for line in posted:
            if postID in line:
                print "[DUP] " + postID + " is a duplicate"
                found = 1
    return found


def add_id_to_file(postID):
    """
    Adds Post ID to our posted_posts so we can check later if it's a duplicate
    """
    with open('posted_posts.txt', 'a') as posted:
        posted.write(str(postID) + "\n")


def main():
    """
    Run our loop to stay logged in and refreshing the subreddit.
    """
    subreddit = setup_connection_reddit('hiphopheads')
    while 1:
        post_dict, post_ids = tweet_creator(subreddit)
        tweeter(post_dict, post_ids)
        print '[sleep] .................Refreshing in 10 sec.................'
        time.sleep(10)


def tweeter(post_dict, post_ids):
    """
    Handles all access to Twitter and tweeting once we've decided what to tweet.
    """
    auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
    auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    for post, post_id in zip(post_dict, post_ids):
        try:
            found = duplicate2(api, post)
            if found == 0:
                print "[POSTING] Posting " + post
                print post + " " + post_dict[post] + " #fresh #hiphopheads"
                api.update_status(
                    post + " " + post_dict[post] + " #fresh #hiphopheads")
        except tweepy.error.TweepError as e:
            print "--------TWEEPY ERROR--------"
            print e
            print "---------END ERROR----------"
            if e.api_code == 187:
                found = 1
                print "[dup] --- added " + str(post_id) + " to already posted ---"
                print "[dup] Attempted to post a duplicate, caught error"
            else:
                time.sleep(60)
        else:
            if found == 0:
                print "Successfully posted tweet: " + post[:40] + " w/ id " + post_id
                time.sleep(10)


def duplicate2(api, post):
    """
    Improved method of determining duplicates without Post ID.
    This method allows us to check duplicates on both Reddit and Twitter, as opposed
    to the other method only being able to check if we've tweeted that specific
    Reddit post (by its ID).
    """
    timeline = api.user_timeline(
        screen_name='HHHFreshPosts', include_rts=False, count=10)
    isDuplicate = 0
    for tweet in timeline:
        try:
            body = tweet.text
            bodyUpper = tweet.text.upper()
            hyphen = post.index('-')
            secondBracket = post.index(']')
            title = str(post[hyphen + 1:hyphen + 6]).strip()
            artist = str(post[secondBracket + 2:hyphen]).strip()
            artistNoAmp = string.replace(artist, '&', '&amp;')
            if artistNoAmp in body[:55]:
                print "[DUP] FOUND: " + artist + " ~~in~~ " + body[:55]
                if title in body[hyphen + 1:]:
                    print "[DUP] FOUND: " + title + " ~in~ " + body[hyphen + 1:55]
                    isDuplicate = 1
                elif title.upper() in body[hyphen + 1:]:
                    print "[DUP] (title upper) FOUND: " + title + " ~in~ " + body[hyphen + 1:55]
                    isDuplicate = 1
                else:
                    print "Different title: " + title + " for " + body[hyphen + 1:55]
            if artistNoAmp in bodyUpper[:55]:
                print "[DUP] (upper) FOUND: " + artist + " ~~in~~ " + bodyUpper[:55]
                if title in bodyUpper[hyphen + 1:]:
                    print "[DUP] (upper) FOUND: " + title + " ~in~ " + bodyUpper[hyphen + 1:55]
                    isDuplicate = 1
                elif title.upper() in bodyUpper[hyphen + 1:]:
                    print "[DUP] (title upper) FOUND: " + title + " ~in~ " + bodyUpper[hyphen + 1:55]
                    isDuplicate = 1
                else:
                    print "Different title: " + title + " for " + bodyUpper[hyphen + 1:55]
        # pylint: disable=W0703
        except Exception as e:
            print e
            print "CANT FIND HYPHEN, Treating as duplicate"
            isDuplicate = 1
    if isDuplicate == 0:
        print "[New Post!] " + post + " is new!"
    else:
        print "[DUP] " + post[:40] + " is a duplicate."
    return isDuplicate


if __name__ == '__main__':
    main()
