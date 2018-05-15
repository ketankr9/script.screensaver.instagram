import xbmc
# import xbmcgui
import xbmcvfs
import xbmcaddon
import json, pickle, os
import insta
import requests

ADDON       =   xbmcaddon.Addon()
ADDON_ID    =   "screensaver.instagram"
ADDON_NAME  =   ADDON.getAddonInfo('name')
ADDON_PATH  =   ADDON.getAddonInfo('path').decode("utf-8")
BASE_PATH   =   xbmc.translatePath("special://userdata/addon_data/"+ADDON_ID)

def notify(line1="", line2="", line3=""):
    xbmc.executebuiltin("Notification("+ADDON_NAME+","+line1+","+line2+","+line3+")")

if __name__ == '__main__':
    _type = ""
    if int(ADDON.getSetting("usernameVStag")) == 0:
        # Extract links for a certain tag
        username = ADDON.getSetting("username1")
        # T = instaTag.HashTag(tag, tagType)
        T = insta.Username(username)
        _type = "Username"
    else:
        # Get settings data
        tag = ADDON.getSetting("tag1")
        tagType = "top_posts" if int(ADDON.getSetting("tagType1")) == 0 else "media"
        T = insta.HashTag(tag)
        _type = "hashtag"

    # Save Extracted links id succcess
    if T.status:
        filepath = os.path.join(BASE_PATH,"image_link.p")
        pickle.dump(T.links, open(filepath, "wb"))
        # Notification of update report
        notify("links refreshed " + _type)    
    else:
        notify("links refreshed " + _type)

