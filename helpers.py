import os
import requests
import urllib.parse
import random

from flask import redirect, render_template, request, session
from functools import wraps

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
            return redirect("/login")
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
    return pers[df] + pers[ds]

def savepersonality(answer, userid, duration):
    for ans in answer:
        if ans == 'a':
            per[0] += a['san']
            per[1] += a['cho']
            per[2] += a['phl']
            per[3] += a['mel']
        elif ans == 'b':
            per[0] += b['san']
            per[1] += b['cho']
            per[2] += b['phl']
            per[3] += b['mel']
        elif ans == 'c':
            per[0] += c['san']
            per[1] += c['cho']
            per[2] += c['phl']
            per[3] += c['mel']
        else:
            per[0] += d['san']
            per[1] += d['cho']
            per[2] += d['phl']
            per[3] += d['mel']
    total = sum(per)
    # finding personality score
    per[0] = round((per[0]/total) * 100)
    per[1] = round((per[1]/total) * 100)
    per[2] = round((per[2]/total) * 100)
    per[3] = round((per[3]/total) * 100)

    try:
        # update to personality scores db
        db.execute("UPDATE users SET (san = :san, cho = :cho, phl = :phl, mel = :mel) WHERE id = userid", 
                    san=per[0], cho=per[1], phl=per[2], mel=per[3], userid = userid)
        # finding personality type
        type = dominant(per)

        # update personality type to db
        db.execute("Update users SET type = :type WHERE id = :id", type=type, id=userid)

        # update quiz duration
        db.execute("Update users SET dur = :dur WHERE id = :id", dur=duration, id=userid)
        return "done"
    except Exception:
        retun "failed"

def generateKey(userid):
    user = db.execute("SELECT * from users WHERE id = :id", id=userid)
    if len(user) not 1:
        return "Invalid UserId"
    if not user['verdict']:
        return "User has not taken the test"
    b = True
    while b:
        key = random.randint(1111, 9999)
        chk = db.execute("SELECT * FROM users WHERE key = :key", key=key)
        if len(chk) == 0:
            b = False
    db.execute("UPDATE users SET key = :key WHERE id = :id", id=userid)
    return key