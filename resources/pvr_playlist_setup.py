import sys
import xbmcvfs
import xbmc

PLAYLISTS = {
    'TGB_PVR_Shows': ('tvshows', 'TGB_PVR_Shows'),
    'TGB_PVR_Episodes': ('episodes', 'TGB_PVR_Episodes'),
}

def ensure_playlist(filename, playlist_type, playlist_name):
    path = xbmcvfs.translatePath(
        'special://profile/playlists/video/{}.xsp'.format(filename)
    )
    if not xbmcvfs.exists(path):
        content = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n'
            '<smartplaylist type="{}">\n'
            '    <name>{}</name>\n'
            '    <match>all</match>\n'
            '</smartplaylist>'
        ).format(playlist_type, playlist_name)
        f = xbmcvfs.File(path, 'w')
        f.write(content)
        f.close()
    return xbmcvfs.exists(path)

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'TGB_PVR_Shows'

    # Ensure both PVR playlists exist and mark each as configured
    for filename, (playlist_type, playlist_name) in PLAYLISTS.items():
        if ensure_playlist(filename, playlist_type, playlist_name):
            xbmc.executebuiltin('Skin.SetString({}Configured,yes)'.format(filename))

    # Save the episodes playlist name to the skin setting
    xbmc.executebuiltin('Skin.SetString(LibraryPVRSource,TGB_PVR_Episodes)')

    # Open the editor for the requested playlist
    xbmc.executebuiltin(
        'ActivateWindow(SmartPlaylistEditor,'
        'special://profile/playlists/video/{}.xsp,return)'.format(target)
    )

main()
