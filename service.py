import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon
import json, pickle, os
import insta


ADDON_ID    =   "screensaver.instagram"
ADDON = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME  =   ADDON.getAddonInfo('name')
ADDON_PATH  =   ADDON.getAddonInfo('path').decode("utf-8")
BASE_PATH   =   xbmc.translatePath("special://userdata/addon_data/"+ADDON_ID)

def notify(line1="", line2="", line3=""):
    xbmc.executebuiltin("Notification("+ADDON_NAME+","+line1+","+line2+","+line3+")")

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    xbmc.log("hello addon! started", level=xbmc.LOGNOTICE)