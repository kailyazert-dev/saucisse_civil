import arcade
import random
import math
import os
from gpt4all import GPT4All
from assets.param_humain import Noms, Images
from classes.humain import Humain, PNJ, Player
from classes.interaction import Interaction
from assets.param_map import WINDOW_WIDTH, WINDOW_HEIGHT, WALL_SCALING, PLAYER_SCALING, MOVEMENT_SPEED

class GameView(arcade.View):
    def __init__(self, environnement_instance):
        super().__init__()

        # Initialisation du model
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../model")
        self.llm = GPT4All("orca-mini-3b-gguf2-q4_0", model_path=model_path)
        print(f"Modèle chargé depuis : {model_path}")
        self.current_input = ""       # Texte tapé par le joueur
        self.last_response = ""       # Dernière réponse du PNJ
        self.is_typing = False        # Mode saisie active

        # Pareltre de la carte
        self.environnement = environnement_instance   # Environement (contexte sociale)
        self.collisions = set()                       # Liste des collisions entre personnage
        self.window.set_mouse_visible(True)           # Visibilité de la sourie dans l'ecran
        self.background_color = (119, 136, 153, 255)  # Couleur du background

        # Pour les elements de la carte
        self.wall_list = arcade.SpriteList()          # Les murs
        self.windows = arcade.SpriteList()            # Les bureaux

        # Pour ne pas passer à travers les éléments de la carte
        self.physics_engines = {}                     # Un moteur par sprite  

        # Pour les PNJ
        self.all_sprites_list = arcade.SpriteList()   # Liste des PNJ en jeu
        self.humain_list = arcade.SpriteList()        # Liste des personnages    

        # Pour le personnage
        self.player_list = None                       # Liste des personnages (un seul)  
        self.player_sprite = None                     # Le personnage  
                      

    def setup(self):

        # Creation du personnage
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player(
            "assets/images/player_d.png",
            scale=PLAYER_SCALING,
        )
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Dimention des baie_vitrées
        baie_width = 42 * WALL_SCALING
        baie_height = 66 * WALL_SCALING
        # Dimention des murs
        wall_width = 48 * WALL_SCALING
        wall_height = 143 * WALL_SCALING
        # Dimention des cloisons
        cloi_width = 21 * WALL_SCALING
        cloi_height = 75 * WALL_SCALING
        # Dimention des placards
        placard_width = 49 * WALL_SCALING
        placard_height = 98 * WALL_SCALING

        # Creation de la salle de formation
        # Mis en place du mur
        num_mur_gauche = math.ceil(WINDOW_HEIGHT / wall_height)
        for i in range(num_mur_gauche):
            mur = arcade.Sprite(
                "assets/images/mur_1.png",
                scale=WALL_SCALING,
            )
            mur.center_x = wall_width / 2
            mur.center_y = i * wall_height  + wall_height  / 2  
            self.wall_list.append(mur)
        # Ajout de la 1er baie
        baie_haut = arcade.Sprite(
            "assets/images/baie_vitre_l.png",
            scale=WALL_SCALING,
        )
        baie_haut.center_x = wall_width + baie_width / 2  
        baie_haut.center_y = WINDOW_HEIGHT - baie_height / 2  # Collée en haut
        self.wall_list.append(baie_haut)
        # Ajout des baies
        start_x = baie_haut.center_x + baie_width / 2
        for i in range(6):
            baie_haut = arcade.Sprite(
                "assets/images/baie_vitre.png",  
                scale=WALL_SCALING,
            )
            baie_haut.center_x = start_x + i * baie_width + baie_width / 2
            baie_haut.center_y = WINDOW_HEIGHT - baie_height / 2
            self.wall_list.append(baie_haut)
        # Ajout de la dernière baie
        start_x = baie_haut.center_x + baie_width  
        baie_haut = arcade.Sprite(
            "assets/images/baie_vitre_r.png",
            scale=WALL_SCALING,
        )
        baie_haut.center_x = start_x  
        baie_haut.center_y = WINDOW_HEIGHT - baie_height / 2
        self.wall_list.append(baie_haut)
        # Ajout de debut de la cloison
        start_x = baie_haut.center_x + cloi_width + cloi_width / 2
        start_y = WINDOW_HEIGHT - cloi_width / 2 - 18
        # Début de la cloison
        cloi_debut = arcade.Sprite(
            "assets/images/d_baie.png",
            scale=WALL_SCALING,
        )
        cloi_debut.center_x = start_x
        cloi_debut.center_y = start_y - 2
        self.wall_list.append(cloi_debut)
        # Cloisons intermédiaires
        for i in range(1, 8):
            cloi = arcade.Sprite(
                "assets/images/i_baie.png",
                scale=WALL_SCALING,
            )
            cloi.center_x = start_x
            cloi.center_y = start_y - i * cloi_height 
            self.wall_list.append(cloi)
        # Fin de la cloison
        cloi_fin = arcade.Sprite(
            "assets/images/f_baie.png",
            scale=WALL_SCALING,
        )
        cloi_fin.center_x = start_x
        cloi_fin.center_y = start_y - (8) * cloi_height + cloi_height / 2
        self.wall_list.append(cloi_fin)   


        # Ajout de debut des baie du haut
        start_x = baie_haut.center_x + cloi_width + cloi_width / 2
        baie_haut = arcade.Sprite(
            "assets/images/baie_vitre_l.png",
            scale=WALL_SCALING,
        )
        baie_haut.center_x = start_x + cloi_width + cloi_width / 2
        baie_haut.center_y = WINDOW_HEIGHT - baie_height / 2
        self.wall_list.append(baie_haut)
        # Ajout des placards
        for i in range(1, 5):
            plac = arcade.Sprite(
                "assets/images/placard2.png",
                scale=WALL_SCALING,
            )
            plac.center_x = start_x + cloi_width / 2 + placard_width / 2
            plac.center_y = start_y - i * placard_height + 13
            self.wall_list.append(plac)
        start_xx = start_x + cloi_width / 2 + placard_width / 2
        plac = arcade.Sprite(
            "assets/images/placard1.png",
            scale=WALL_SCALING,
        )
        plac.center_x = start_xx
        plac.center_y = start_y - i * placard_height + 9 - placard_height
        self.wall_list.append(plac)    
        # Ajout de debut des baie
        start_x = baie_haut.center_x + baie_width / 2
        num_mur_haut = math.ceil(WINDOW_WIDTH / baie_width)
        for i in range(num_mur_haut):
            baie_haut = arcade.Sprite(
                "assets/images/baie_vitre.png", 
                scale=WALL_SCALING,
            )
            baie_haut.center_x = start_x + i * baie_width + baie_width / 2
            baie_haut.center_y = WINDOW_HEIGHT - baie_height / 2
            self.wall_list.append(baie_haut)

        # ⬇️ Ajoute un moteur de collision par personnage
        for sprite in self.player_list:
            engine = arcade.PhysicsEngineSimple(sprite, self.wall_list)
            self.physics_engines[sprite] = engine
        

    """ Dessine la map """
    def on_draw(self):
        self.clear()

        # 💠 Dessine les elements de la carte
        self.wall_list.draw()

        # Déssine le player
        self.player_list.draw()

        if self.is_typing:
            arcade.draw_text("Player : " + self.current_input, 10, 40, arcade.color.WHITE, 16)

        if self.last_response:
            arcade.draw_text("PNJ : " + self.last_response, 10, 10, arcade.color.LIGHT_GREEN, 16)
            

    """ Met à jour la carte """
    def on_update(self, delta_time):

        # Fonstion pour actualiser la carte
        self.player_list.update(delta_time)

        # Mise à jour des moteurs physiques pour chaque personnage
        for engine in self.physics_engines.values():
            engine.update()

    """ Pour le controle du personnage """
    def on_key_press(self, key, modifiers):

        # Si une touche de rirection est activé, 
        if key == arcade.key.UP:
            self.player_sprite.change_y = MOVEMENT_SPEED
            self.player_sprite.direction = "up"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -MOVEMENT_SPEED
            self.player_sprite.direction = "down"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
            self.player_sprite.direction = "left"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
            self.player_sprite.direction = "right"
            self.player_sprite.toggle_texture()
        # Si la touche entrer (dialogue est active)   
        elif key == arcade.key.LALT:
            self.is_typing = True
            self.current_input = ""
        elif self.is_typing and key == arcade.key.ENTER:
            self.last_response = self.talk_gpt4(self.current_input)
            self.is_typing = False 
        elif self.is_typing and key == arcade.key.BACKSPACE:
            self.current_input = self.current_input[:-1]    

    def on_key_release(self, key, modifiers):

        # If a player releases a key, zero out the speed.
        # This doesn't work well if multiple keys are pressed.
        # Use 'better move by keyboard' example if you need to
        # handle this.
        if key == arcade.key.UP:
            self.player_sprite.change_y = 0
            self.player_sprite.texture = self.player_sprite.textures["up"]
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = 0  
            self.player_sprite.texture = self.player_sprite.textures["down"]  
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = 0 
            self.player_sprite.texture = self.player_sprite.textures["left"]
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0        
            self.player_sprite.texture = self.player_sprite.textures["right"]

    def on_text(self, text):
        if self.is_typing:
            self.current_input += text

    def talk_gpt4(self, message_joueur):
        role = (
            "Tu es Same, un forgeron bourru mais honnête d’un village médiéval. "
            "Réponds toujours comme un personnage de jeu de rôle. Sois cohérent avec ce que dit l’aventurier. "
        )
        prompt = f"{role}\nAventurier : {message_joueur}\nForgeron :"
        response = self.llm.generate(prompt, max_tokens=80)
        return response.strip()
