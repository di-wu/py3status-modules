# -*- coding: utf-8 -*-
"""
Display song currently playing in Spotify

Spotify is a digital music service that gives you access to millions of songs.

Configuration parameters:
    fmt: Initial format to use.
        (default '{artist} - {song}')
    fmt_offline: Initial format if offline.
        (default 'Spotify Offline')

Format placeholders:
    {song} Name of song
    {artist} Artist of song

Color options:
    color_high: Spotify Offline
    color_low: Song Playing

Requires:
    spotify: https://www.spotify.com

# button numbers
1 = left click
2 = middle click
3 = right click
4 = scroll up
5 = scroll down

Example:

'''
spotify {
    button_play_pause = 1
    button_next = 4
    button_previous = 5
    scroll = false
    color_high = #FF0000
    color_low = #FFFFFF
}
'''

@author di-wu
"""

import re, dbus


def _get_spotify_data() -> object:
    try:
        session_bus = dbus.SessionBus()
        spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
        spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
        metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
        return metadata['xesam:artist'][0], metadata['xesam:title']
    except:
        return None, None


class Py3status:
    _x = 0
    _n = 0
    scroll: bool = False
    fmt = '{artist} - {song}'
    fmt_offline = 'Spotify Offline'

    button_next = None
    button_play_pause = None
    button_previous = None

    def _scroll(self, t):
        if self._x <= 0:
            return t[-self._x:self._n].ljust(self._n, " ")
        else:
            return t[0:self._n - self._x].rjust(self._n, " ")

    def on_click(self, event):
        CMD = """dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify
                 /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.{cmd}"""

        button = event['button']
        if button == self.button_play_pause:
            self.py3.command_run(CMD.format(cmd='PlayPause'))
        elif button == self.button_next:
            self.py3.command_run(CMD.format(cmd='Next'))
        elif button == self.button_previous:
            self.py3.command_run(CMD.format(cmd='Previous'))

    def spotify(self):
        artist, song = _get_spotify_data()
        if artist is None and song is None:
            full_text = self.fmt_offline
            color = self.py3.COLOR_HIGH
        else:
            data = {'artist': artist, 'song': re.sub("[\(].*?[\)]", "", song).strip()}
            full_text = self.py3.safe_format(self.fmt, data)
            color = self.py3.COLOR_LOW

            if self.scroll:
                if self._n != len(full_text[0]['full_text']):
                    self._n = len(full_text[0]['full_text'])
                    self._x = -self._n + 1

                self._x += 1
                if self._x > self._n:
                    self._x = -self._n + 1

                full_text = self.py3.safe_format(self._scroll(full_text[0]['full_text']))

        return {
            'full_text': full_text,
            'color': color,
            'cached_until': self.py3.time_in(0.2)
        }


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test

    module_test(Py3status)
