import arcade
import requests
import math
import os
from openai import OpenAI
from gpt4all import GPT4All
from assets.param_humain import Noms, Images
from classes.humain import Humain, PNJ, Player
from classes.interaction import Interaction
from assets.param_map import WINDOW_WIDTH, WINDOW_HEIGHT, WALL_SCALING, PLAYER_SCALING, MOVEMENT_SPEED
from assets.param_humain import IbmI_personnage

class GameView(arcade.View):
    def __init__(self, environnement_instance):
        super().__init__()
        self.environnement = environnement_instance

        # Pour la map
        self.tile_map = None
        self.scene = None
        self.physics_engine = None

        # Pour les jouers
        self.player_sprite = None
        self.pnj_sprite = []

        # Pour le model
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../model/")
        self.slm = GPT4All("Mistral-7B-Instruct-v0.3.Q3_K_M.gguf", model_path=model_path, allow_download=False)
        self.api_key = "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"
        self.current_pnj = None
        self.current_input = ""
        self.last_response = ""
        self.is_typing = False

    """ Fonction pour récupérer les élements de la map """
    def setup(self):
        # Chemin vers la carte TMX
        map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../map/PHL_L.tmx")

        # Charger la carte TMX
        self.tile_map = arcade.load_tilemap(map_path, scaling=1.0)

        # Créer la scène à partir de la tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        # Créer le joueur
        humain = Humain(charisme=0.3, rigidite=0.3, intensite_boof=0.3, receptif_boof=0.3)
        self.player_sprite = Player(humain, "Kyle", "assets/images/player_d.png", scale=PLAYER_SCALING)
        self.player_sprite.center_x = WINDOW_WIDTH // 2
        self.player_sprite.center_y = 50
        self.scene.add_sprite("Player", self.player_sprite)

        #Creer les PNJs
        pnj = Humain(charisme=0.3, rigidite=0.3, intensite_boof=0.3, receptif_boof=0.3)
        louis = PNJ("Mael", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        louis.center_x=WINDOW_WIDTH//2 + 165
        louis.center_y=WINDOW_HEIGHT//2 + 40
        mael = PNJ("Louis", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        mael.center_x=WINDOW_WIDTH//2 + 24 
        mael.center_y=WINDOW_HEIGHT//2 + 40
        thomas = PNJ("Thomas", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        thomas.center_x=WINDOW_WIDTH//2 + 24 
        thomas.center_y=WINDOW_HEIGHT//2 - 104
        kyle = PNJ("Kyle", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        kyle.center_x=WINDOW_WIDTH//2 + 165 
        kyle.center_y=WINDOW_HEIGHT//2 - 104
        self.pnj_sprite.append(louis)
        self.pnj_sprite.append(mael)
        self.pnj_sprite.append(thomas)
        self.pnj_sprite.append(kyle)
        self.scene.add_sprite("Pnj", louis)
        self.scene.add_sprite("Pnj", mael)
        self.scene.add_sprite("Pnj", thomas)
        self.scene.add_sprite("Pnj", kyle)

        obstacles = arcade.SpriteList()
        obstacles.extend(self.pnj_sprite)
        obstacles.extend(self.scene["Meuble_H"])
        obstacles.extend(self.scene["Mur"])

        # Moteur physique sur les element de la map
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite,
            obstacles
        )

    """ Fonction pour déssiner la map """
    def on_draw(self):
        self.clear()
        self.scene.draw()

        for pnj in self.pnj_sprite:
            distance = arcade.get_distance_between_sprites(self.player_sprite, pnj)
            if distance < 50:
               arcade.draw_text("LALT : Discuter", pnj.center_x - 40, pnj.center_y - 40, arcade.color.LIGHT_GREEN, 14) 
               arcade.draw_text(pnj.get_nom(), pnj.center_x - 40, pnj.center_y + 40, arcade.color.ALLOY_ORANGE, 14) 

        if self.is_typing or self.last_response:
            box_height = 100
            margin = 10       
            arcade.draw_lrbt_rectangle_filled(
                left=0,
                right=WINDOW_WIDTH,
                top=box_height,
                bottom=0,
                color=arcade.color.WHITE
            )
        # Affichage du texte du joueur (input)
        if self.is_typing:
            arcade.draw_text(
                f"{self.player_sprite.nom} : " + self.current_input,
                margin, box_height - 30, arcade.color.BLACK, 14
            )
        # Affichage de la réponse du PNJ
        if self.last_response:
            arcade.draw_text(
                f"{self.current_pnj.nom} : " + self.last_response,
                margin, box_height - 60, arcade.color.LIGHT_GREEN, 14
            )    

    """ Fonction qui met à jour la map """
    def on_update(self, delta_time):
        self.physics_engine.update()
        self.scene.update(delta_time)

    """ Fonction pour gérer les touches """
    def on_key_press(self, key, modifiers):
        # Fermer la discussion si le joueur bouge
        if self.is_typing and key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            self.is_typing = False
            self.last_response = ""
            self.current_input = ""
            self.current_pnj = None
        if key == arcade.key.UP:                            # Pour la touche fléche du haut
            self.player_sprite.change_y = MOVEMENT_SPEED    # La vitesse de déplacement
            self.player_sprite.direction = "up"             # La direction
            self.player_sprite.toggle_texture()             # appelle la fonction pour animer la marche du joueur
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = - MOVEMENT_SPEED
            self.player_sprite.direction = "down"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = - MOVEMENT_SPEED
            self.player_sprite.direction = "left"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
            self.player_sprite.direction = "right"
            self.player_sprite.toggle_texture()
        elif key == arcade.key.LALT:                        # Pour la touche ALT de gauche (engage la discution)
            for pnj in self.pnj_sprite:
                if arcade.get_distance_between_sprites(self.player_sprite, pnj) < 50:
                    dx = self.player_sprite.center_x - pnj.center_x
                    dy = self.player_sprite.center_y - pnj.center_y
                    if abs(dx) > abs(dy):
                        if dx > 0:
                            pnj.texture = pnj.textures["right"]
                        else:
                            pnj.texture = pnj.textures["left"]
                    else:
                        if dy > 0:
                            pnj.texture = pnj.textures["up"]
                        else:
                            pnj.texture = pnj.textures["down"]   
                    self.current_pnj = pnj                          # Identifie le PNJ avec qui on vas disvuter
                    self.is_typing = True                           # Modifier l'etat de base et active la possibiliter d'ecrire
                    self.current_input = ""                         # Initialise à vide le champ de discution
                    break
            # if not pnj_found:
            #     self.current_pnj = None
            #     self.is_typing = False
            #     self.current_input = ""
            #     self.last_response = ""
            #     for pnj in self.pnj_sprite:
            #         pnj.texture = arcade.load_texture(pnj.image_path)

        elif self.is_typing and key == arcade.key.ENTER:             # Pour la touche ENTRER
            if self.current_pnj:
                self.last_response = self.talk_model(self.current_input, self.api_key, self.current_pnj)  # Commence le dialogue en appellant la fonction
            # self.current_input = ""    

        elif self.is_typing and key == arcade.key.BACKSPACE:         # Pour la touche supprimer
            self.current_input = self.current_input[:-1]

    """ Fonction pour gerer les touches"""
    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP:                                            # Pour réinitialiser l'orsque la touche HAUT est relacher
            self.player_sprite.change_y = 0                                 # Vitesse de déplacement
            self.player_sprite.texture = self.player_sprite.textures["up"]  # Affecte l'image adapter du personnage
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = 0  
            self.player_sprite.texture = self.player_sprite.textures["down"]  
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = 0 
            self.player_sprite.texture = self.player_sprite.textures["left"]
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0        
            self.player_sprite.texture = self.player_sprite.textures["right"]

    """ Fonction pour écrire du texte pour la discution """
    def on_text(self, text):
        if self.is_typing:
            self.current_input += text

    """ Fonction pour parler avec le model (avec les PNJ) """
    def talk_model(self, message_joueur, api_key, pnj):
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            
            nom_pnj = pnj.nom
            if nom_pnj in IbmI_personnage.personnages:
                data = IbmI_personnage.personnages[nom_pnj]
                system_prompt = (
                    f"Tu est {data['nom']}, un personnage {data['type']}.\n"
                    f"Ton metier est {data['metier']}.\n"
                    f"Tu a une personalité {data['personnalite']}.\n"
                    f"Tes hobbies sont {data['hobbie']}.\n"
                    f"Repond court, sans émoji."
                )
            else:
                system_prompt = "Tu es un personnage mystérieux. Reste vague et mystérieux. Ne révéle jamais ton personnage"

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_joueur}
            ]
            
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://votre-site.fr",
                    "X-Title": "NomDuJeuRP",
                },
                extra_body={},
                model="qwen/qwen3-coder:free",
                messages=messages,
                max_tokens=30,
                temperature=1.2
            )
            
            response = completion.choices[0].message.content.strip()
            print("Response complète :", completion)
            return response
        except Exception as e:
            print(f"Erreur API : {e}")
            return "Erreur lors de la requête."
    

