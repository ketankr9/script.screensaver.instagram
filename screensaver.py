import random, os, pickle, requests
import xbmc, xbmcaddon, xbmcvfs, xbmcgui

ADDON_ID       = 'screensaver.instagram'
ADDON  = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME     = ADDON.getAddonInfo('name')
ADDON_PATH     = (ADDON.getAddonInfo('path').decode('utf-8'))
SETTINGS_LOC   = ADDON.getAddonInfo('profile').decode('utf-8')
ADDON_VERSION  = ADDON.getAddonInfo('version')
BASE_PATH      = xbmc.translatePath("special://userdata/addon_data/"+ADDON_ID)
KODI_MONITOR   = xbmc.Monitor()

# Settings data
# ENABLE_KEYS    = True #ADDON.getSetting("Enable_Keys") == 'true'
# USER           = ADDON.getSetting("User").encode("utf-8").replace('@','')
# COLLECTION     = ADDON.getSetting("Collection").encode("utf-8")
ANIMATION      = 'nope' #if ADDON.getSetting("Animate") == 'true' else 'nope'
TIME           = 'okay' #if ADDON.getSetting("Time") == 'true' else 'nope'
TIMER          = 10 #[30,60,120,240][int(ADDON.getSetting("RotateTime"))]
# KEYWORDS       = urllib.quote(ADDON.getSetting("Keywords").encode("utf-8"))
# RES            = ['1280x720','1920x1080','3840x2160'][int(ADDON.getSetting("Resolution"))]
# PHOTO_TYPE     = ['featured','random','user','collection'][int(ADDON.getSetting("PhotoType"))]

# URL_PARAMS     = '/%s'%PHOTO_TYPE
# BASE_URL       = 'https://source.unsplash.com'

IMG_CONTROLS   = [30000,30001]

class GUI(xbmcgui.WindowXMLDialog):
    def __init__( self, *args, **kwargs ):
        self.isExiting = False
        self.imageLinks = []
        self.log("__init__")
    
    def log(self, msg, level=xbmc.LOGNOTICE):
        xbmc.log(ADDON_ID + '-' + '-' + msg, level)
            
            
    def onInit( self ):
        self.log("onInit")
        self.winid = xbmcgui.Window(xbmcgui.getCurrentWindowDialogId())
        self.winid.setProperty('instagram_animation', ANIMATION)
        self.winid.setProperty('clock', TIME)
        self.loadLinks()
        self.log(",".join(self.imageLinks[:3]))
        # self.getControl(30000).setImage(BASE_PATH + filepath)
        self.startRotation()

    def loadLinks(self):
        self.log("loadLinks")
        filepath = os.path.join(BASE_PATH, "image_link.p")
        self.log(filepath)
        if xbmcvfs.exists(filepath):
            self.log("File exists")
        else:
            self.log("File DOESN'T exists")
        self.imageLinks = pickle.load(open(filepath))
        self.log(" ".join(self.imageLinks[:5]))

    def setImage(self, id):
        self.log("loading... image")
        self.openURL(random.choice(self.imageLinks), id)
        self.log("image downloaded")
        # image = image if len(image) > 0 else self.openURL(IMAGE_URL)
        filepath = os.path.join(BASE_PATH, "image" + str(id) + ".jpg")
        if xbmcvfs.exists(filepath):
            self.log("Image exists")
        else:
            self.log("Image DOESN'T exists")
        self.log("Setting image" + str(id))
        self.getControl(id).setImage(filepath)
        self.log("image Setting finished")

    def startRotation(self):
        self.log("startRotation")
        self.currentID = IMG_CONTROLS[0]
        self.nextID    = IMG_CONTROLS[1]
        self.setImage(self.currentID)
        while not KODI_MONITOR.abortRequested():
            self.log("startRotation-loop")
            self.getControl(self.nextID).setVisible(False)
            self.getControl(self.currentID).setVisible(True)
            self.nextID, self.currentID = self.currentID, self.nextID
            self.setImage(self.currentID)
            if KODI_MONITOR.waitForAbort(TIMER) == True or self.isExiting == True: break

    # When any button is pressed do close the screensaver
    def onAction( self, action ):
        self.log("onAction:"+str(action))
        self.isExiting = True
        self.close()
        
        
    def openURL(self, url, id):
        self.log("openURL")
        try:
            self.log("openURL url = " + url)
            r = requests.get(url, timeout=15)
            filepath = os.path.join(BASE_PATH, "image" + str(id) + ".jpg")
            with open(filepath, "w") as img:
                img.write(r.content)
            # f =xbmcvfs.File (filepath, 'w', True)
            # result = f.write(buffer)
            # f.close()
            # request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
            # page = urllib2.urlopen(request, timeout = 15)
            # url = page.geturl()
            # self.log("openURL return url = " + url)
            # return r.content
        # except urllib2.URLError, e: self.log("openURL Failed! " + str(e), xbmc.LOGERROR)
        # except socket.timeout, e: self.log("openURL Failed! " + str(e), xbmc.LOGERROR)
        except Exception,e:
            self.log("connection failed! " + str(e), xbmc.LOGERROR)
        return ''

if __name__ == '__main__':
    ui = GUI("default.xml", ADDON_PATH, "default")
    ui.doModal()
    del ui