"""
Report Bot
"""
# pylint: disable=C0103
# pylint: disable=E0401
import time
import praw
import keys

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

def check_if_twitter_link(subreddit_info):
    """
    Checks if link is a tweet
    """
    keywords = ["twitter.com/"]
    rule = "All tweets must be self posts."
    try:
        for submission in subreddit_info.new(limit=3):
            for keyword in keywords:
                if keyword in submission.url:
                    print "[bot] %s is Twitter link!" % str(submission.url)
                    print "[bot] Found " + keyword + " in " + submission.url
                    submission.report("Breaks subreddit rule: " + rule + " [Reported by /u/HHHBot]")
                    print "[bot] Submission reported. (Reason: Twitter link)"
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)

def check_if_valid_tag(subreddit_info):
    """
    Checks if tag is valid
    """
    validTags = ["[FRESH]", "[HYPE]", "[ORIGINAL]", "[LEAK]", "[MIXTAPE]", "[DISCUSSION]",
                 "[SHOTS FIRED]", "[WAVY WEDNESDAY]", "[THROWBACK THURSDAY]",
                 "[OFFICIAL DISCUSSION]", "[FRESH ALBUM]", "[FRESH MIXTAPE]", "[FRESH VIDEO]",
                 "[ORIGINIAL]", "[OC]", "[FRESH EP]", "[FRESH ORIGINAL]", "[FRESH ORIGINIAL]",
                 "[FRESH OC]", "[THROWBACK]"]
    rule = "Invalid tag: "
    valid = False
    try:
        for submission in subreddit_info.new(limit=5):
            title = submission.title
            if title[0] == "[":
                secondBracket = title.index(']')
                actualTag = title[:secondBracket+1]
                for tag in validTags:
                    if tag in title:
                        # print "[bot] Found Valid Tag " + tag + " in " + title
                        valid = True
                    elif tag.title() in title:
                        # print "[bot] Found Valid Tag " + tag + " in " + title
                        valid = True
                    elif tag.lower() in title:
                        # print "[bot] Found Valid Tag " + tag + " in " + title
                        valid = True
                if not valid:
                    print "[bot] FOUND INVALID TAG: " + actualTag
                    submission.report("Breaks subreddit rule: " + rule + actualTag +
                                      " [Reported by /u/HHHBot]")
                    print "[bot] Submission reported. (Reason: Invalid Tag)"
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)
    except UnicodeEncodeError as e:
        print e

def check_if_image_post(subreddit_info):
    """
    Checks if image post
    """
    keywords = ["imgur.com", "i.redd.it", "i.reddituploads.com", "twimg.com"]
    rule = "No Image Posts"
    try:
        for submission in subreddit_info.new(limit=5):
            for keyword in keywords:
                if keyword in submission.url:
                    print "[bot] %s is Image Post!" % str(submission.url[:30])
                    print "[bot] Found " + keyword + " in " + submission.url[:30]
                    submission.report("Breaks subreddit rule: " + rule + " [Reported by /u/HHHBot]")
                    print "[bot] Submission reported. (Reason: Image Link)"
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)

def check_if_snippet(subreddit_info):
    """
    Checks if snippet
    """
    keywords = ["snippet", "Snippet", "SNIPPET"]
    rule = "No Snippets"
    try:
        for submission in subreddit_info.new(limit=5):
            for keyword in keywords:
                if keyword in submission.title:
                    print "[bot] %s is a Snippet!" % str(submission.title[:30])
                    print "[bot] Found " + keyword + " in " + submission.title[:30]
                    submission.report("Breaks subreddit rule: " + rule + " [Reported by /u/HHHBot]")
                    print "[bot] Submission reported. (Reason: Snippet)"
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)
    except UnicodeEncodeError as e:
        print e

def check_if_ranking_question(subreddit_info):
    """
    Check if question is a "ranking question"
    """
    rule = "No 'Ranking' questions."
    keyphrases = ["What's your favorite", "What's the best", "Whats the best", "Whats your favorite"]
    try:
        for submission in subreddit_info.new(limit=5):
            for keyphrase in keyphrases:
                if keyphrase in submission.title:
                    print "[bot] %s is a Ranking Questions!" % str(submission.title[:30])
                    print "[bot] Found " + keyphrase + " in " + submission.title[:30]
                    submission.report("Breaks subreddit rule: " + rule + " [Reported by /u/HHHBot]")
                    print "[bot] Submission reported. (Reason: 'Ranking Question')"
    # pylint: disable=E0712
    except praw.exceptions as e:
        print "--------------REDDIT Praw ERROR---------------"
        print e
        time.sleep(30)
    except UnicodeEncodeError as e:
        print e

def main():
    """
    Run our loop to stay logged in and refreshing the subreddit.
    """
    subreddit = setup_connection_reddit('hiphopheads')
    while 1:
        check_if_twitter_link(subreddit)
        check_if_valid_tag(subreddit)
        check_if_image_post(subreddit)
        check_if_snippet(subreddit)
        print '[sleep] .................Refreshing in 10 sec.................'
        time.sleep(10)

if __name__ == '__main__':
    main()
