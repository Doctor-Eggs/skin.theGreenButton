import sys
import json
import xbmc
import xbmcgui


def main():
    if len(sys.argv) < 2:
        xbmc.log('remove_episode.py: no episodeid argument supplied', xbmc.LOGERROR)
        return

    try:
        episodeid = int(sys.argv[1])
    except ValueError:
        xbmc.log('remove_episode.py: invalid episodeid "{}"'.format(sys.argv[1]), xbmc.LOGERROR)
        return

    # Fetch episode details so the confirmation dialog can show a meaningful label
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

    if not xbmcgui.Dialog().yesno('Remove from library', 'Remove "{}"?'.format(label)):
        return

    xbmc.executeJSONRPC(json.dumps({
        'jsonrpc': '2.0',
        'method': 'VideoLibrary.RemoveEpisode',
        'params': {'episodeid': episodeid},
        'id': 2
    }))

    xbmc.executebuiltin('Container.Refresh')


main()
