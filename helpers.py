from cs50 import SQL
import os
import requests
import urllib.parse
import random

from flask import redirect, render_template, request, session
from functools import wraps


# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///squad.db")


# initializing global variables
pers = ["San", "Cho", "Phl", "Mel"]
per = [0, 0, 0, 0]
a = {"san": 1, "cho": 2, "phl": 3, "mel": 4}
b = {"san": 2, "cho": 3, "phl": 4, "mel": 1}
c = {"san": 3, "cho": 4, "phl": 1, "mel": 2}
d = {"san": 4, "cho": 1, "phl": 2, "mel": 3}


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/admin")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def dominant(per):
    per = [10, 20, 4, 45, 99] 
    fmax=max(per[0],per[1]) 
    smax=min(per[0],per[1]) 
    
    if list[0] == fmax:
        df = 0
        ds = 1
    else:
        df = 1
        ds = 0

    for i in range(2,len(per)): 
        if per[i]>fmax: 
            smax=fmax
            df = i
            ds = i - 1
            fmax=per[i] 
        else: 
            if per[i]>smax:
                ds = i
                smax=per[i]
    return pers[df] + "-" + pers[ds]

# def savepersonality(answer, dur, alias):
#     for ans in answer:
#         if ans == 'a':
#             per[0] += a['san']
#             per[1] += a['cho']
#             per[2] += a['phl']
#             per[3] += a['mel']
#         elif ans == 'b':
#             per[0] += b['san']
#             per[1] += b['cho']
#             per[2] += b['phl']
#             per[3] += b['mel']
#         elif ans == 'c':
#             per[0] += c['san']
#             per[1] += c['cho']
#             per[2] += c['phl']
#             per[3] += c['mel']
#         else:
#             per[0] += d['san']
#             per[1] += d['cho']
#             per[2] += d['phl']
#             per[3] += d['mel']
#     total = sum(per)
#     # finding personality score
#     per[0] = round((per[0]/total) * 100)
#     per[1] = round((per[1]/total) * 100)
#     per[2] = round((per[2]/total) * 100)
#     per[3] = round((per[3]/total) * 100)
#     answers = "".join(answer)
#     try:
#         # update to personality scores db
#         # db.execute("UPDATE users SET (san = :san, cho = :cho, phl = :phl, mel = :mel) WHERE id = userid", 
#         #             san=per[0], cho=per[1], phl=per[2], mel=per[3], userid = userid)
#         id = db.execute("INSERT INTO users (alias, san, cho, phl, mel, answers, dur) VALUES (:alias, :san, :cho, :phl, :mel, :answers, :dur)",
#                     alias=alias, san=per[0], cho=per[1], phl=per[2], mel=per[3], answers=answers, dur=dur)
#         # finding personality type
#         type = dominant(per)

#         # update personality type to db
#         db.execute("Update users SET verdict = :type WHERE id = :id", type=type, id=id)

#         # generate key
#         key = generateKey(id)
#         db.execute("UPDATE users SET key = :key WHERE id = :id",key=key, id=userid)
#         return "".join(key)
#     except Exception:
#         return "failed"

# def generateKey(id):
#     user = db.execute("SELECT * from users WHERE id = :id", id=id)
#     if not len(user) == 1:
#         return "Invalid UserId"
#     if not user['verdict']:
#         return "User has not taken the test"
#     b = True
#     while b:
#         key = random.randint(1111, 9999)
#         chk = db.execute("SELECT * FROM users WHERE key = :key", key=key)
#         if len(chk) == 0:
#             b = False
#     return key

def bestMatch(matches, control):
    cv1 = control['verdict'].split("-")[0]
    cv2 = control['verdict'].split("-")[1]

    # get percentage of most dominant personalities of user
    dom1 = control[cv1]
    dom2 = control[cv2]

    diff = [abs((match[cv1] - dom1) + (match[cv2] + dom2)) for match in matches]

    # for match in matches:
    #     diff.append(abs((match[cv1] - dom1) + (match[cv2] + dom2)))
    
    # return the element at the index with the least difference in dominant personality type
    return matches[diff.index(min(diff))]