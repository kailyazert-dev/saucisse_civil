import arcade
from map import PHL_L, armonie
from classes import environnement
from assets.param_map import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
import os

def main():

    # Création d'une instance d'Environnement
    travaille = environnement.Environnement("Bureau", tension_sociale=0.7, densite_sociale=0.5, regles_sociale="formelles")
    bar = environnement.Environnement("Bar", tension_sociale=0.2, densite_sociale=0.8, regles_sociale="informelles")

    # Crée la fenêtre arcade
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Crée et configure la vue du jeu, en passant l'environnement
    game = armonie.GameView(bar)
    game.setup()

    # Affiche la vue sur la fenêtre
    window.show_view(game)

    # Lance la boucle de jeu arcade
    arcade.run()

if __name__ == "__main__":
    main()
