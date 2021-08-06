from mpd import MPDClient
from mpd.base import ConnectionError
from pitop.miniscreen import Miniscreen
from signal import pause
from time import sleep
import os


class StationManager:
    def __init__(self):
        self._client = MPDClient()
        self._client.timeout = 10                # network timeout in seconds (floats allowed), default: None
        self._client.idletimeout = None

        self.playlist_id = None

        #List of Radio Stations. Note that in this dictionary Keys are used to find bitmap names (name + .bmp), and Values are stream URL
        self.radio_stations = {
            "BBC Radio 1": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_one.m3u8",
            "BBC Radio 1 Xtra": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_1xtra.m3u8",
            "BBC Radio 2": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_two.m3u8",
            "BBC Radio 3": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_three.m3u8",
            "BBC Radio 4 FM": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_fourfm.m3u8",
            "BBC Radio 5 Live": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_five_live.m3u8",
            "BBC Radio 6": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_6music.m3u8",
            "BBC Asian Network": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_asian_network.m3u8",
            "BBC World Service": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_world_service.m3u8",
            "BBC Radio Scotland FM": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_scotland_fm.m3u8",
            "BBC Radio Wales FM": "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/ak/bbc_radio_wales_fm.m3u8",
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
        radio_names_list = list(self.radio_stations) #create indexed list of all keys from radio_stations dict
        # print(f"Attempting to get current station name")

        while radio_station_name == "Unknown" and attempts < 6:
            try:
                #radio_station_name = self.get_client_currentsong()['name']
                radio_station_name = radio_names_list[int(self.get_client_currentsong()['pos'])]

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

        if self.get_client_status()['state'] == 'pause':
            print("Starting playback...")
            play_pause_state = 'playing'
        else:
            print("Stopping playback...")
            play_pause_state = 'stopped'

        self.client.pause()
        return play_pause_state

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
    #image_file_path = os.path.dirname(__file__)
    image_file_path = os.path.join(os.path.dirname(__file__), 'RadioIcons/') + station_manager.current_station_name + ".bmp"
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


def toggle_play():
    if station_manager.toggle() == 'stopped':
        image_file_path = os.path.join(os.path.dirname(__file__),'RadioIcons/') + "Pause.bmp"
        try:
                miniscreen.display_image_file(image_file_path)
        except:
            print("Couldn't find image file for '" + image_file_path + "'")
            miniscreen.display_multiline_text("Paused", font_size=15)
    else:
        display_station()

def exit_radio():
    print("Exiting")
    miniscreen.display_multiline_text("Exiting...", font_size=15)
    station_manager.exit()


def main():
    #print(os.getcwd())
    #print(__file__)
    miniscreen.display_multiline_text("Loading...", font_size=15)

    miniscreen.up_button.when_pressed = prev_station
    miniscreen.down_button.when_pressed = next_station
    miniscreen.select_button.when_pressed = toggle_play #station_manager.toggle
    miniscreen.cancel_button.when_pressed = exit_radio

    station_manager.play()
    display_station()

    pause()

main()