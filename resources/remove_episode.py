import sys
import json
import xbmc
import xbmcgui
import xbmcvfs


def main():
    if len(sys.argv) < 3:
        xbmc.log('remove_episode.py: episodeid and filepath arguments required', xbmc.LOGERROR)
        return

    try:
        episodeid = int(sys.argv[1])
    except ValueError:
        xbmc.log('remove_episode.py: invalid episodeid "{}"'.format(sys.argv[1]), xbmc.LOGERROR)
        return

    filepath = sys.argv[2]

    result = xbmc.executeJSONRPC(json.dumps({
        'jsonrpc': '2.0',
        'method': 'VideoLibrary.GetEpisodeDetails',
        'params': {
            'episodeid': episodeid,
            'properties': ['title', 'season', 'episode', 'showtitle']
        },
        'id': 1
    }))

    details = json.loads(result).get('result', {}).get('episodedetails', {})
    showtitle = details.get('showtitle', '')
    season    = details.get('season', 0)
    episode   = details.get('episode', 0)
    title     = details.get('title', 'this episode')

    if showtitle:
        label = '{} - S{:02d}E{:02d} - {}'.format(showtitle, season, episode, title)
    else:
        label = title

    quick_delete = xbmc.getCondVisibility('Skin.HasSetting(LibraryPVRQuickDelete)')

    if quick_delete:
        if not xbmcgui.Dialog().yesno('Remove & Delete', 'Remove "{}" from library and delete the file?'.format(label)):
            return
    else:
        if not xbmcgui.Dialog().yesno('Remove from library', 'Remove "{}" from library?'.format(label)):
            return

    xbmc.executeJSONRPC(json.dumps({
        'jsonrpc': '2.0',
        'method': 'VideoLibrary.RemoveEpisode',
        'params': {'episodeid': episodeid},
        'id': 2
    }))

    if quick_delete or xbmcgui.Dialog().yesno('Delete file', 'Delete the recording file from disk?'):
        xbmcvfs.delete(filepath)

    xbmc.executebuiltin('Container.Refresh')


main()
