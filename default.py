# Import required libraries
import urllib,urllib3,re,sys,xbmcplugin,xbmcgui,xbmcaddon,xbmc,xbmcvfs,os,requests,string

def OPEN_URL(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36')
    try:
       response = urllib.request.urlopen(req)
    except:
       print("ERROR: Unable to open requested url: " + url)
       return ""

    try:
       link=response.read().decode(response.headers.get_content_charset('utf8'))
    except:
       print("WARNING: Charset not set for: " + url)
       # If charset is not available, fall back to default for all content
       link=result.decode('utf8')

    response.close()
    return link
	

# MAIN MENU
def MAINMENU():
    addDir('[COLOR '+newfont+']'+'Searches[/COLOR]-[COLOR '+newfont+']'+'Y[/COLOR]ouTube LITE','url',5003,art+'Main/Search.png','none',1)
    addDir('[COLOR '+newfont+']'+'F[/COLOR]avorites','switch=display',2,art+'Main/favorites.png','none',1)
    setView('DEFAULT')


# MODE 2 - adds, removes, and lists favorites
def FAVORITES(switch,name,iconimage,url):
    global updateScreen

    url=url.replace(' ','%20')
    iconimage=iconimage.replace(' ','%20')

    IMAGE = os.path.join(ADDON.getAddonInfo('path'), 'icon.png')
   
    db = database.connect( db_dir );cur = db.cursor()
    if switch == 'add':
        sql = "INSERT OR REPLACE INTO favourites (track_name,iconimage,url) VALUES(?,?,?)"
        cur.execute(sql, (name,iconimage.replace(Kfolder,''),url.replace(Kfolder,'')))
        db.commit(); db.close()
        xbmc.executebuiltin('Notification('+name+',Added to Favorites,2000,'+IMAGE+')')
        xbmc.executebuiltin("Container.Refresh")
    if switch == 'delete':
        cur.execute("DELETE FROM favourites WHERE track_name='%s'"%name)
        db.commit(); db.close()
        xbmc.executebuiltin('Notification('+name.replace('  ',' ')+',Deleted from Favorites,2000,'+IMAGE+')')
        xbmc.executebuiltin("Container.Refresh")
    if switch == 'display':
        cur.execute("SELECT * FROM favourites")
        cached = cur.fetchall()
        favExists = False
        if cached:
            for name,artist,track,iconimage,url in cached:
                favExists = True
                addLink(name,url,iconimage,'')
        db.close()
        if favExists == False:
          xbmc.executebuiltin('Notification('+name.replace('  ',' ')+',No Favorites Exist,2000,'+IMAGE+')')
          updateScreen=True
          MAINMENU()
          #xbmc.executebuiltin('Container.Update(%s?mode=None&name=&url=None, true)'% (sys.argv[0]))
        else:
          updateScreen=False
          setView('VIDEO')


# List of previous search's and new search link
def FirstSearchDir():
    favs = ADDON.getSetting('favs').split(',')
    favExists = False
    for title in favs:
        if len(title)>0:
            favExists = True
            break

    if favExists == False:
      SEARCH("url")
    else:
      addDir('[COLOR '+newfont+']'+'New Search[/COLOR]-YouTube LITE','url',3,art+'Main/Search.png','none',1)
      for title in favs:
         if len(title)>0:
            addDir(title.title(),title.lower(),3,art+'Main/Search.png','none',1)

      setView('DEFAULT')


def PlayListHandler(url):
        TXT='https://www.youtube.com/watch?v=%s' % (url.replace(' ','+').replace("\\u0026","&"))
        html=OPEN_URL(TXT)
        html=html[html.find('"playlist":{"playlist"'):html.find('"currentIndex"')]

        # NOTE: the current element in the loop contains the title for the NEXT element
        link=html.split('watch?v=')
        for i, p in enumerate(link):
            nextLink = link[(i+1) % len(link)]
            p=p.replace('\\"',"")

            # Get the title from this element
            name = ""
            if '{"title":{"accessibility":{"accessibilityData":{"label":"' in p:
                name = p.split('{"title":{"accessibility":{"accessibilityData":{"label":"')[1]
            name = name.split('"')[0]
            name = str(name).replace("&#39;","'").replace("&amp;","and").replace("&#252;","u").replace("&quot;","").replace("[","").replace("]","").replace("-"," ")

            # Everything else from the next element
            if ':"buy or rent"' in nextLink.lower():
                continue

            url=nextLink.split('"')[0]
            if "\\u0026" in url:
               url=url.split("\\u0026")[0]
            if '&amp' in url:
               url = url.split('&amp')[0]
            iconimage = 'http://i.ytimg.com/vi/%s/0.jpg' % url
            if not 'video_id' in name:
                 if not '_title_' in name:
                    if not 'video search' in name.lower():
                        addLink(name,url,iconimage,'')

        setView('VIDEO')


def HtmlToResults(html):
        link=html.split('watch?v=')

        # NOTE: the current element in the loop contains the title for the NEXT element
        for i, p in enumerate(link):
            nextLink = link[(i+1) % len(link)]
            p=p.replace('\\"',"")

            # Get the title from this element
            name = ""
            if ',"title":{"simpleText":"' in p:
                name = p.split(',"title":{"simpleText":"')[1]
            if ',"title":{"runs":[{"text":"' in p:
                name = p.split(',"title":{"runs":[{"text":"')[1]
            name = name.split('"')[0]
            name = str(name).replace("&#39;","'").replace("&amp;","and").replace("&#252;","u").replace("&quot;","").replace("[","").replace("]","").replace("-"," ")

            # Everything else from the next element
            if ':"buy or rent"' in nextLink.lower():
                continue

            url=nextLink.split('"')[0]
            print("URL:" + url)
            iconimage=""
            if "\\u0026list=" in url:
                # Playlist
                iconimage="DefaultFolder.png"
                addDir(name,url,99,'DefaultFolder.png','none',1)
            else:
              if '&amp' in url:
                  url = url.split('&amp')[0]
              if '\\u0026' in url:
                  url = url.split('\\u0026')[0]
              if iconimage=="":
                 iconimage = 'http://i.ytimg.com/vi/%s/0.jpg' % url

              #xbmc.log(msg="DEBUG: " + name + ": " + iconimage, level=xbmc.LOGINFO)

              if not 'video_id' in name:
                 if not '_title_' in name:
                    if not 'video search' in name.lower():
                        addLink(name,url,iconimage,'')


def SEARCH(search_entered):
        global updateScreen

        favs = ADDON.getSetting('favs').split(',')
        if 'url' in search_entered:
            keyboard = xbmc.Keyboard('', 'YOUTUBE LITE')
            keyboard.doModal()
            if keyboard.isConfirmed() and len(keyboard.getText())>0:
               search_entered = keyboard.getText()
            else: 
               # User cancelled search
               updateScreen=True

               favExists = False
               for title in favs:
                   if len(title)>0:
                       favExists = True
                       break
               if favExists == False:
                   xbmc.executebuiltin('Container.Update(%s?mode=None&name=&url=None, "replace")'% (sys.argv[0]))
                   return True
               else:
                   return False

        updateScreen=False
        search_entered = search_entered.replace(',', '').lower()

        if len(search_entered.replace(' ','')) == 0:
            return False

        TXT='https://www.youtube.com/results?search_query=%s&hl=en-GB'  % (search_entered.replace(' ','+'))
        html=OPEN_URL(TXT)
        if not search_entered in favs:
            favs.append(search_entered.lower())
            ADDON.setSetting('favs', ','.join(favs))

        HtmlToResults(html)
        setView('VIDEO')
        return True


def addDir(name,url,mode,iconimage,fanart,number):
        u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)+"&number="+str(number)
        name = ''.join([x for x in name if x in string.printable])
        if name.replace(" ","") == "":
            return
        liz=xbmcgui.ListItem(name, offscreen=True)
        liz.setArt({'icon':'DefaultFolder.png'})
        liz.setArt({'thumb':iconimage})
        liz.setArt({'fanart':fanart})
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        menu=[]
        if (mode == 3 or mode==16) and url!='url' :
            menu.append(('[COLOR orange]Remove Search[/COLOR]','Container.Update(%s?mode=5002&name=%s&url=url)'% (sys.argv[0],name)))
            liz.addContextMenuItems(items=menu, replaceItems=False)
        if (mode == 2000)or mode==103 or mode==203:
            if mode ==203:
                liz.setProperty("IsPlayable","true")
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder=False)
        else:
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder=True)
        if not mode==1 and mode==20 and mode==19:
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)


def addLink(name,url,iconimage,fanart,showcontext=True):
    u=sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode=6003&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)+"&fanart="+urllib.parse.quote_plus(fanart)
    name = ''.join([x for x in name if x in string.printable])
    if name.replace(" ","") == "":
        return
    cmd = 'plugin://plugin.video.youtube/?path=root/video&action=download&videoid=%s' % url
    liz=xbmcgui.ListItem(name, offscreen=True)
    liz.setArt({'icon':'DefaultVideo.png'})
    liz.setArt({'thumb':iconimage})
    liz.setArt({'fanart':fanart})
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty("IsPlayable","true")
    menu = []
    if showcontext:
          if mode!=2:
              found=False
              db = database.connect( db_dir );cur = db.cursor()
              cur.execute("SELECT * FROM favourites")
              cached = cur.fetchall()
              if cached:
                  for fname,artist,track,ficonimage,furl in cached:
                     if url == furl:
                          found=True
                          menu.append(('[COLOR red]Remove[/COLOR] from YouTube LITE Favorites','RunPlugin(%s?mode=2&iconimage=%s&url=%s&name=%s&switch=%s)' %(sys.argv[0],iconimage,url,name,'delete')))
                          break
              db.close()
              if not found:
                  menu.append(('[COLOR green]Add[/COLOR] to YouTube LITE Favorites','RunPlugin(%s?mode=2&iconimage=%s&url=%s&name=%s&switch=%s)' %(sys.argv[0],iconimage,url,name,'add')))
          else:
              menu.append(('[COLOR red]Remove[/COLOR] from YouTube LITE Favorites','RunPlugin(%s?mode=2&iconimage=%s&url=%s&name=%s&switch=%s)' %(sys.argv[0],iconimage,url,name,'delete')))
						  
    liz.addContextMenuItems(items=menu, replaceItems=False)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)


def PlayYouTube(name,url,iconimage):
    url = 'https://www.youtube.com/watch?v=%s'% url
    print("YouTube Lite Playing: " + url)

    liz = xbmcgui.ListItem(name, offscreen=True)
    liz.setArt({'icon':'DefaultVideo.png'})
    liz.setArt({'thumb':iconimage})
    liz.setInfo(type='Video', infoLabels={'Title':name})
    liz.setProperty("IsPlayable","true")

    ytAddon = ADDON.getSetting('youtube_player').lower()    
    if ytAddon == "youtube addon":
        youtube='plugin://plugin.video.youtube/play/?video_id=%s'% url
        liz.setPath(str(youtube))
    else:
        from youtubedl import YDStreamExtractor
        vid = YDStreamExtractor.getVideoInfo(url)
        liz.setPath(vid.streamURL())
    
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)


def setView(viewType):
    if viewType=="VIDEO":
        xbmc.executebuiltin("Container.SetViewMode(500)")
        xbmcplugin.setContent(int(sys.argv[1]), "movies")
        xbmc.executebuiltin("Container.SetViewMode(500)")
    else:
        xbmc.executebuiltin("Container.SetViewMode(55)")


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param



# Initialize all our stuff
THESITE ='youtubelite'
Kfolder= 'youtubelite'
updateScreen=False
cacheList=False

ADDON = xbmcaddon.Addon(id='plugin.video.ytlite')
db_dir = os.path.join(xbmcvfs.translatePath("special://database"), 'YTLite.db')

datapath = xbmcvfs.translatePath(ADDON.getAddonInfo('profile'))
newfont=ADDON.getSetting('newfont').lower()

if os.path.exists(datapath)==False:
    os.mkdir(datapath) 

art= "%s/Art/"%ADDON.getAddonInfo("path")
from sqlite3 import dbapi2 as database

db = database.connect(db_dir)
db.execute('CREATE TABLE IF NOT EXISTS favourites (track_name, artist, track, iconimage, url)')
db.commit()
db.close()

params=get_params()
url=None
name=None
mode=None
iconimage=None
fanart=None

try:
        url=urllib.parse.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.parse.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.parse.unquote_plus(params["iconimage"])
except:
        pass
try:
        switch=urllib.parse.unquote_plus(params["switch"])
except:
        switch='display'
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        fanart=urllib.parse.unquote_plus(params["fanart"])
except:
        pass
try:        
        number=int(params["number"])
except:
        pass
try:        
        split=int(params["split"])
except:
        pass



# Print (Debug) All Values
#print("Mode: " + str(mode))
#print("URL: " + str(url))
#print("Name: " + str(name))
#print("IconImage: " + str(iconimage))
#print("FanartImage: " + str(fanart))
#try:print("number: " + str(number))
#except:pass



# Now we can RUN!
if mode==None or url==None or len(url)<1:
    MAINMENU()


elif mode==2:
    FAVORITES(switch,name,iconimage,url)


elif mode == 5003:
    FirstSearchDir()


elif mode==3:
    if not SEARCH(url):
       FirstSearchDir()
    else:
       cacheList=True


elif mode == 5002:
    favs = ADDON.getSetting('favs').split(",")
    try:
        favs.remove(name.lower())
        ADDON.setSetting('favs', ",".join(favs))
    except:pass
    updateScreen=True
    FirstSearchDir()


elif mode == 6003:
    PlayYouTube(name,url,iconimage)
    setView('VIDEO')
    cacheList=True

elif mode == 99:
    PlayListHandler(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=cacheList, updateListing=updateScreen)
