import sys
import xbmc
import xbmcgui
import xbmcaddon

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


# Skin string key names per path index
_DISPLAY_KEYS = {1: 'LibraryPVRPathDisplay', 2: 'LibraryPVRPath2Display', 3: 'LibraryPVRPath3Display'}
_PATH_KEYS    = {1: 'LibraryPVRPath',        2: 'LibraryPVRPath2',        3: 'LibraryPVRPath3'}


def _rule(path):
    """Single startswith rule for one path, with backslashes JSON-escaped."""
    escaped = path.replace('\\', '\\\\').replace('"', '\\"')
    return '{{"field":"path","operator":"startswith","value":["{p}"]}}'.format(p=escaped)


def build_url(content_type, paths, order_method, order_dir, titles_view=False):
    rules = [_rule(p) for p in paths]
    logic = 'and' if len(rules) == 1 else 'or'
    rules_json = '{{"{l}":[{r}]}}'.format(l=logic, r=','.join(rules))

    base = 'videodb://tvshows/titles/' if titles_view else 'videodb://tvshows/titles/-1/-1/'
    json_str = (
        '{{"type":"{t}","rules":{r},"order":{{"direction":"{d}","method":"{m}"}}}}'
        .format(t=content_type, r=rules_json, d=order_dir, m=order_method)
    )
    return '{base}?xsp={xsp}'.format(base=base, xsp=quote(json_str, safe=''))


def rebuild_urls(addon, paths):
    """Build all three URL variants and store them as skin strings."""
    active = [p for p in paths if p]
    if not active:
        for key in ('LibraryPVRURL_Episodes_Date', 'LibraryPVRURL_Episodes_Air', 'LibraryPVRURL_Shows'):
            addon.setSetting(key, '')
            xbmc.executebuiltin('Skin.SetString({},)'.format(key))
        return

    urls = {
        'LibraryPVRURL_Episodes_Date': build_url('episodes', active, 'dateadded', 'descending'),
        'LibraryPVRURL_Episodes_Air':  build_url('episodes', active, 'year',      'descending'),
        'LibraryPVRURL_Shows':         build_url('tvshows',  active, 'sorttitle', 'ascending', titles_view=True),
    }
    for key, url in urls.items():
        addon.setSetting(key, url)
        xbmc.executebuiltin('Skin.SetString({},{})'.format(key, url))


def main():
    idx   = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    addon = xbmcaddon.Addon('skin.theGreenButton')

    disp_key = _DISPLAY_KEYS[idx]
    path_key = _PATH_KEYS[idx]

    current = xbmc.getInfoLabel('Skin.String({})'.format(disp_key))
    if not current:
        current = addon.getSetting(disp_key)

    if current:
        choice = xbmcgui.Dialog().contextmenu(['Browse\u2026', 'Clear'])
        if choice == -1:
            return
        if choice == 1:
            path = ''
        else:
            path = xbmcgui.Dialog().browse(0, 'DVR Source {}'.format(idx), 'files', '', False, False, current)
            if not path:
                return
    else:
        path = xbmcgui.Dialog().browse(0, 'DVR Source {}'.format(idx), 'files', '', False, False, '')
        if not path:
            return

    # Persist display and raw path
    addon.setSetting(disp_key, path)
    addon.setSetting(path_key, path)
    xbmc.executebuiltin('Skin.SetString({},{})'.format(disp_key, path))
    xbmc.executebuiltin('Skin.SetString({},{})'.format(path_key, path))

    # Gather all three display paths and rebuild pre-built URLs
    paths = [addon.getSetting(_DISPLAY_KEYS[i]) or
             xbmc.getInfoLabel('Skin.String({})'.format(_DISPLAY_KEYS[i]))
             for i in (1, 2, 3)]
    # Overwrite the just-set index with the fresh value
    paths[idx - 1] = path

    rebuild_urls(addon, paths)


main()
