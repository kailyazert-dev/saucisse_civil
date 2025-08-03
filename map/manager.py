import arcade
from map.home.HOME import GameView as homeview
from map.armonie.PHL import GameView as phlview
from map.armonie.TMA import GameView as tmaview

class MapManager:
    def __init__(self, window, environnement_instance):
        self.window = window
        self.environnement = environnement_instance
        self.current_map = "home"
        self.view = None

    def load_initial_map(self):
        self.view = homeview(self.environnement)
        self.view.set_manager(self)
        self.view.setup()
        self.window.show_view(self.view)    

    def switch_map(self):
        if self.current_map == "home":
            self.current_map = "phl"
            self.view = tmaview(self.environnement)
        elif self.current_map == "phl":
            self.current_map = "tma"
            self.view = tmaview(self.environnement)    
        else:
            self.current_map = "phl"
            self.view = phlview(self.environnement)

        self.view.set_manager(self)
        self.view.setup()
        self.window.show_view(self.view)    
