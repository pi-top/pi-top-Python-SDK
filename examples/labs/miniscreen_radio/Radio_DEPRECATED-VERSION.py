from mpd import MPDClient
from mpd.base import ConnectionError
from pitop.miniscreen import Miniscreen
from signal import pause
from time import sleep
class StationManager:
    def __init__(self):
        self._client = MPDClient()
        self._client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self._client.idletimeout = None
        self.playlist_id = None
        self.radio_stations = {
            "BBC Radio 1": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p",
            "BBC Radio 1 Xtra": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1xtra_mf_p",
            "BBC Radio 2": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p",
            "BBC Radio 3": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p",
            "BBC Radio 4": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p",
            "BBC Radio 5 live": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio5live_mf_p",
            "BBC Radio 6": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_6music_mf_p",
            "BBC Asian Network": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_asianet_mf_p",
            "BBC World Service UK stream": "http://bbcwssc.ic.llnwd.net/stream/bbcwssc_mp1_ws-eieuk",
            "BBC Radio Scotland": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_scotlandfm_mf_p",
            "BBC Radio Wales": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_walesmw_mf_p",
        }
        #Add radio streams
        self.client.clear()
        for radio in self.radio_stations.values():
            self.client.add(radio)
    def get_from_client(self, func):
        attempts = 0
        thing = None
        while thing is None and attempts < 6:
            try:
                thing = func()
            except (ConnectionError, KeyError):
                attempts = attempts + 1
                sleep(0.5)
        if attempts != 0:
            print(f"Took {attempts+1} attempts to get thing")
        return thing
    def get_client_currentsong(self):
        return self.get_from_client(self.client.currentsong)
    def get_client_status(self):
        return self.get_from_client(self.client.status)
    def get_client_stats(self):
        return self.get_from_client(self.client.stats)
    def get_client_playlistid(self):
        return self.get_from_client(self.client.playlistid)
    def debug(self):
        print(f"currentsong: {self.get_client_currentsong()}")
        print(f"status: {self.get_client_status()}")
        print(f"stats: {self.get_client_stats()}")
        print(f"playlistid: {self.get_client_playlistid()}")
    @property
    def current_station_name(self):
        attempts = 0
        radio_station_name = "Unknown"
        # print(f"Attempting to get current station name")
        while radio_station_name == "Unknown" and attempts < 6:
            try:
                radio_station_name = self.get_client_currentsong()['name']
            except KeyError:
                attempts = attempts + 1
                sleep(0.5)
        if attempts != 0:
            print(f"Took {attempts+1} attempts to get current station name")
        return radio_station_name
    def client_status(self):
        try:
            return self.get_client_status()
        except ConnectionError as e:
            print(e)
    @property
    def current_station_no(self):
        try:
            return int(self.get_client_status()['song'])
        except ConnectionError as e:
            print(e)
    @property
    def no_of_stations(self):
        return int(self.get_client_status()['playlistlength'])
    def next(self):
        if self.current_station_no == self.no_of_stations-1:
            print("End of playlist - going to start")
            self.client.play(0)
        else:
            self.client.next()
    def previous(self):
        if self.current_station_no == 0:
            print("Start of playlist - going to end")
            self.client.play(self.no_of_stations-1)
        else:
            self.client.previous()
    def toggle(self):
        if self.get_client_status()['state'] == 'stop:'
            print("Stopping playback...")
        else:
            print("Starting playback...")
        self.client.pause()
    def play(self):
        try:
            self.client.play(self.current_station_no)
        except KeyError:
            self.client.play(0)
    def exit(self):
        self.client.stop()
        self.client.close()
        self.client.disconnect()
    @property
    def client(self):
        try:
            self._client.connect("localhost", 6600)
        except ConnectionError as e:
            # print(e)
            pass
        return self._client
miniscreen = Miniscreen()
station_manager = StationManager()
def display_station():
    print(f"Playing station: {station_manager.current_station_name}")
    image_file_path = "./Desktop/" + station_manager.current_station_name + ".bmp"
    try:
        miniscreen.display_image_file(image_file_path)
    except:
        print("Couldn't find image file for '" + image_file_path + "'")
        miniscreen.display_multiline_text(station_manager.current_station_name, font_size=15)
def prev_station():
    miniscreen.display_multiline_text("Loading...", font_size=15)
    station_manager.previous()
    display_station()
def next_station():
    miniscreen.display_multiline_text("Loading...", font_size=15)
    station_manager.next()
    display_station()
def exit_radio():
    print("Exiting")
    miniscreen.display_multiline_text("Exiting...", font_size=15)
    station_manager.exit()
def main():
    miniscreen.display_multiline_text("Loading...", font_size=15)
    miniscreen.up_button.when_pressed = prev_station
    miniscreen.down_button.when_pressed = next_station
    miniscreen.select_button.when_pressed = station_manager.toggle
    miniscreen.cancel_button.when_pressed = exit_radio
    station_manager.play()
    display_station()
    pause()
main()