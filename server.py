from ezy_multiplayer import *
import pickle, os, praw, time, traceback
from thread import start_new_thread

def load_settings():
    try:
        if os.name == "nt":
            return pickle.load(open("settings.data", "rb"))
        else:
            return pickle.load(open("/root/settings.data", "rb"))
    except Exception as e:
        return "False"

def send_msg(reddit, user, title, message):
    reddit.redditor(user).message(title, message)

def save_settings(everything):
    try:
        if os.name == "nt":
            pickle.dump(everything, open("settings.data", "wb"))
        else: 
            pickle.dump(everything, open("/root/settings.data", "wb"))
        return "True"
    except Exception as e:
        print(e)
        return "False"

def send_back(data):
    if data == "get_everything":
        return load_settings()
    elif type(data) == dict:
        return save_settings(data["set_everything"])
    return data

def save_id(myid):
    if os.name == "nt":
        pickle.dump(myid, open("redditid.data", "wb"))
    else:
        pickle.dump(myid, open("/root/redditid.data", "wb"))

def reddit_logic():
    print("Starting reddit...")
    while True:
        try:
            settings = load_settings()
            if settings == "False":
                continue
            reddit = praw.Reddit(client_id=settings[2],
                             client_secret=settings[3],
                             user_agent='Python AUTOJOBFINDER Bot',
                             username = settings[0],
                             password = settings[1])
        except Exception as e:
            print("-Error-")
            time.sleep(5)
            continue
        try:
            if os.name == "nt":
                all_id = pickle.load(open("redditid.data", "rb"))
            else:
                all_id = pickle.load(open("/root/redditid.data", "rb"))
        except:all_id = []
        try:
            for submission in reddit.subreddit(settings[4]).new(limit=100):
                if submission.id not in all_id:
                    all_id.append(submission.id)
                    title = submission.title.lower()
                    alltext = title + " " + submission.selftext.lower()
                    if "[task]" in alltext or "[hiring]" in alltext or "[paid]" in title.lower() or "(paid)" in title.lower():
                        if "[for hire]" not in alltext:
                            found = False
                            for keyword in settings[5]:
                                if keyword in alltext:
                                    found = True
                            if found == True:
                                if submission.subreddit != "forhire":
                                    submission.reply(settings[6])
                                message = settings[8]
                                if "*nl*" in message:
                                    message = message.replace("*nl*", "\n\n")
                                if "*ln*" in message:
                                    message = message.replace("*ln*", str(submission.url))
                                if "*un*" in message:
                                    message = message.replace("*un*", str(submission.author.name))
                                send_msg(reddit, submission.author.name, settings[7], message) ##############
            time.sleep(60)
        except KeyboardInterrupt:
            print("Stopping...")
            save_id(all_id)
            time.sleep(2)
            exit()
            
        except Exception as e:
            traceback.print_exc()
            print("ADVICE: *Check Wifi*")
            save_id(all_id)
            time.sleep(5)
            
        save_id(all_id)

if os.name == "nt":
    port = get_free_port()
else:
    port = 8080

print("Local  Hostname: " + get_ip())
print("Global Hostname: " + get_ip("global"))
print("Port: %s" % str(port))

start_new_thread(reddit_logic,())

newLobby(port, send_back)
while True:pass