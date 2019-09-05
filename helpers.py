from cs50 import SQL
import os
import requests
import urllib.parse
import random

from flask import redirect, render_template, request, session
from functools import wraps

pers = ["San", "Cho", "Phl", "Mel"]

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
    #per = [10, 20, 4, 45, 99] 
    fmax=max(per[0],per[1]) 
    smax=min(per[0],per[1]) 
    
    if per[0] == fmax:
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