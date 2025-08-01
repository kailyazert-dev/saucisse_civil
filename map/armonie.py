import arcade
import os
from openai import OpenAI
from assets.param_humain import Noms, Images
from classes.humain import Humain, PNJ, Player
from classes.interaction import Interaction
from assets.param_map import WINDOW_WIDTH, WINDOW_HEIGHT, CAMERA_HEIGHT, CAMERA_WIDTH, WALL_SCALING, PLAYER_SCALING, MOVEMENT_SPEED
from assets.param_humain import IbmI_personnage

class GameView(arcade.View):
    def __init__(self, environnement_instance):
        super().__init__()
        self.environnement = environnement_instance

        # Pour la map
        self.tile_map = None
        self.scene = None
        self.physics_engine = None
        self.camera_sprites = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()
        self.camera_speed = 0.1

        # Pour les jouers
        self.player_sprite = None
        self.pnj_sprite = []
        self.strategique_sprite = []

        # Pour les PNJ
        self.current_pnj = None         # Pour le PNJ en face

        # Pour les strategiques
        self.current_strategique = None         # Pour le strategique en face

        # Pour le model et les discution
        self.api_key = "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"
        self.current_input = ""           # Le message du player
        self.last_response = ""           # La reponse du model
        self.is_typing = False            # Ouverture du champ du dialogue 

    """ Fonction pour récupérer les élements de la map """
    def setup(self):

        # Chemin vers la carte TMX
        self.phl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../map/PHL.tmx")
        self.tma = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../map/TMA.tmx")

        self.current_map = self.phl

        # Charger la carte TMX
        self.tile_map = arcade.load_tilemap(self.tma, scaling=1.0)

        # Créer la scène à partir de la tilemap
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        
        # Créer le joueur
        humain = Humain(charisme=0.3, rigidite=0.3, intensite_boof=0.3, receptif_boof=0.3)
        self.player_sprite = Player(humain, "Kyle", "assets/images/player_d.png", scale=PLAYER_SCALING)
        self.player_sprite.center_x = 550
        self.player_sprite.center_y = 750
        self.scene.add_sprite("Player", self.player_sprite)

        #Creer les PNJs
        pnj = Humain(charisme=0.3, rigidite=0.3, intensite_boof=0.3, receptif_boof=0.3)
        louis = PNJ("Mael", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        louis.center_x = 556
        louis.center_y = 940
        mael = PNJ("Louis", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        mael.center_x = 694 
        mael.center_y = 940
        thomas = PNJ("Thomas", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        thomas.center_x = 556 
        thomas.center_y = 790
        kyle = PNJ("Kyle", pnj, "Male", "assets/images/player_d.png", PLAYER_SCALING)
        kyle.center_x = 694 
        kyle.center_y = 790
        self.pnj_sprite.append(louis)
        self.pnj_sprite.append(mael)
        self.pnj_sprite.append(thomas)
        self.pnj_sprite.append(kyle)
        self.scene.add_sprite("Pnj", louis)
        self.scene.add_sprite("Pnj", mael)
        self.scene.add_sprite("Pnj", thomas)
        self.scene.add_sprite("Pnj", kyle)

        # Creer les strategiques
        hotesse = PNJ("Hotesse", pnj, "Femelle", "assets/images/hotesse.png", PLAYER_SCALING)
        hotesse.center_x = 2850 
        hotesse.center_y = 1848
        self.strategique_sprite.append(hotesse)
        self.scene.add_sprite("Pnj", hotesse)

        # Creer les obstacles
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
        self.camera_sprites.use()
        self.scene.draw()

        # Pour dialoguer avec les strategiques
        for strategique in self.strategique_sprite:
            distance = arcade.get_distance_between_sprites(self.player_sprite, strategique)
            if distance < 100:
               arcade.draw_text("RALT : Aller à la TMA", strategique.center_x - 40, strategique.center_y - 40, arcade.color.LIGHT_GREEN, 18) 
               arcade.draw_text(strategique.get_nom(), strategique.center_x - 40, strategique.center_y + 40, arcade.color.ALLOY_ORANGE, 18) 

        # Pour dialoguer avec les PNJ
        for pnj in self.pnj_sprite:
            distance = arcade.get_distance_between_sprites(self.player_sprite, pnj)
            if distance < 50:
               arcade.draw_text("LALT : Discuter", pnj.center_x - 40, pnj.center_y - 40, arcade.color.LIGHT_GREEN, 18) 
               arcade.draw_text(pnj.get_nom(), pnj.center_x - 40, pnj.center_y + 40, arcade.color.ALLOY_ORANGE, 18) 
        # Déssine la boite de dialogue
        arcade.get_window().use()
        if self.is_typing or self.last_response:
            margin = 15
            left=self.player_sprite.center_x - CAMERA_WIDTH // 2
            right=self.player_sprite.center_x + CAMERA_WIDTH // 2
            top=self.player_sprite.center_y - 100
            bottom=self.player_sprite.center_y - (CAMERA_WIDTH // 2) - 100 
            
            arcade.draw_lrbt_rectangle_filled(
                left=left,
                right=right,
                top=top,
                bottom=bottom,
                color=arcade.color.WHITE
            )
        # Affiche le message du jouer
        if self.is_typing:
            arcade.draw_text(
                f"{self.player_sprite.nom} : " + self.current_input,
                left + margin, top - margin - 15, arcade.color.BLACK, 14
            )
        # Affichage de la réponse du PNJ
        if self.last_response:
            arcade.draw_text(
                f"{self.current_pnj.nom} : " + self.last_response,
                left + margin, top - margin - 40, arcade.color.LIGHT_GREEN, 14
            )

        # Déssine la camera
        self.camera_gui.use()    

        # arcade.draw_rect_filled(arcade.rect.XYWH(self.width // 2, 20, self.width, 40),
        #                         arcade.color.ALMOND)
        # text = f"Scroll value: ({self.camera_sprites.position[0]:5.1f}, " \
        #        f"{self.camera_sprites.position[1]:5.1f})"
        # arcade.draw_text(text, 10, 10, arcade.color.BLACK_BEAN, 20) 


    """ Fonction qui met à jour la map """
    def on_update(self, delta_time):
        self.physics_engine.update()
        self.scene.update(delta_time)

        # Scroll the screen to the player
        self.scroll_to_player()

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

        elif self.is_typing and key == arcade.key.ENTER:             # Pour la touche ENTRER
            if self.current_pnj:
                self.last_response = self.talk_model(self.current_input, self.api_key, self.current_pnj)  # Commence le dialogue en appellant la fonction
            self.current_input = ""    

        elif self.is_typing and key == arcade.key.BACKSPACE:         # Pour la touche supprimer
            self.current_input = self.current_input[:-1]

        elif self.is_typing and key == arcade.key.RALT:
            self.current_map = self.tma    

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

    """ Fonction pour que la camera suit le joueur"""
    def scroll_to_player(self):
        """
        Scroll the window to the player.

        if CAMERA_SPEED is 1, the camera will immediately move to the desired
        position. Anything between 0 and 1 will have the camera move to the
        location with a smoother pan.
        """

        position = (self.player_sprite.center_x, self.player_sprite.center_y)
        self.camera_sprites.position = arcade.math.lerp_2d(
            self.camera_sprites.position, position, self.camera_speed,
        )

    """ Fonction pour redimensionner la fenêtre """
    def on_resize(self, width: int, height: int):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        super().on_resize(width, height)
        self.camera_sprites.match_window()

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
    

