import xbmc
import xbmcgui
import kodigui

import busy
import playlist
import windowutils
import search

from lib import util
from lib import colors

from plexnet import plexapp


class PlaylistsWindow(kodigui.BaseWindow, windowutils.UtilMixin):
    xmlFile = 'script-plex-playlists.xml'
    path = util.ADDON.getAddonInfo('path')
    theme = 'Main'
    res = '1080i'
    width = 1920
    height = 1080

    THUMB_DIMS = {
        'audio': {
            'item.thumb': (270, 270)
        },
        'video': {
            'item.thumb': (610, 344)
        }
    }

    AUDIO_PL_LIST_ID = 101
    VIDEO_PL_LIST_ID = 301

    OPTIONS_GROUP_ID = 200

    HOME_BUTTON_ID = 201
    SEARCH_BUTTON_ID = 202
    PLAYER_STATUS_BUTTON_ID = 204

    def __init__(self, *args, **kwargs):
        kodigui.BaseWindow.__init__(self, *args, **kwargs)
        self.exitCommand = None

    def onFirstInit(self):
        self.audioPLListControl = kodigui.ManagedControlList(self, self.AUDIO_PL_LIST_ID, 5)
        self.videoPLListControl = kodigui.ManagedControlList(self, self.VIDEO_PL_LIST_ID, 5)

        self.fill()
        self.setFocusId(self.AUDIO_PL_LIST_ID)

    def onAction(self, action):
        try:
            if action == xbmcgui.ACTION_CONTEXT_MENU:
                if not xbmc.getCondVisibility('ControlGroup({0}).HasFocus(0)'.format(self.OPTIONS_GROUP_ID)):
                    self.setFocusId(self.OPTIONS_GROUP_ID)
                    return
            elif action in(xbmcgui.ACTION_NAV_BACK, xbmcgui.ACTION_CONTEXT_MENU):
                if not xbmc.getCondVisibility('ControlGroup({0}).HasFocus(0)'.format(self.OPTIONS_GROUP_ID)):
                    self.setFocusId(self.OPTIONS_GROUP_ID)
                    return

        except:
            util.ERROR()

        kodigui.BaseWindow.onAction(self, action)

    def onClick(self, controlID):
        if controlID == self.HOME_BUTTON_ID:
            self.closeWithCommand('HOME')
        elif controlID == self.AUDIO_PL_LIST_ID:
            self.playlistListClicked(self.audioPLListControl)
        elif controlID == self.VIDEO_PL_LIST_ID:
            self.playlistListClicked(self.videoPLListControl)
        elif controlID == self.PLAYER_STATUS_BUTTON_ID:
            self.showAudioPlayer()
        elif controlID == self.SEARCH_BUTTON_ID:
            self.searchButtonClicked()

    def searchButtonClicked(self):
        self.processCommand(search.dialog(self))

    def playlistListClicked(self, list_control):
        mli = list_control.getSelectedItem()
        if not mli:
            return

        w = playlist.PlaylistWindow.open(playlist=mli.dataSource)

        try:
            self.processCommand(w.exitCommand)
        finally:
            del w

    def createListItem(self, obj):
        mli = kodigui.ManagedListItem(
            obj.title or '',
            util.durationToText(obj.duration.asInt()),
            thumbnailImage=obj.composite.asTranscodedImageURL(*self.THUMB_DIMS[obj.playlistType]['item.thumb']),
            data_source=obj
        )
        return mli

    @busy.dialog()
    def fill(self):
        items = {
            'audio': [],
            'video': []
        }
        playlists = plexapp.SERVERMANAGER.selectedServer.playlists()

        self.setProperty(
            'background',
            playlists[0].composite.asTranscodedImageURL(self.width, self.height, blur=128, opacity=60, background=colors.noAlpha.Background)
        )

        for pl in playlists:
            mli = self.createListItem(pl)
            if mli:
                items[pl.playlistType].append(mli)

        self.audioPLListControl.addItems(items['audio'])
        self.videoPLListControl.addItems(items['video'])
