import pygame
import sys
import os

# Paramètres de base
BASE_TILE_WIDTH = 64
BASE_TILE_HEIGHT = 32
MAP_SIZE = 120

class PygameView:
    def __init__(self, scenario, simulation_controller, width=800, height=600):
        # 1. Centrage de la fenêtre
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        pygame.init()
        self.scenario = scenario
        self.simulation_controller = simulation_controller

        self.height = height
        self.width = width
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("MedievAIl Battle - 2.5D (Sprites Heroes II)")

        # 2. FORCE FOCUS
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = pygame.display.get_wm_info()['window']
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except: pass

        self.BG_COLOR = (20, 20, 25) 
        self.TEXT_COLOR = (255, 255, 255)
        
        # Zoom et Caméra
        self.zoom_level = 0.8 # Un peu plus zoomé pour voir les sprites
        self.cam_x = 0
        self.cam_y = 0
        
        # Mémoire pour l'effet miroir (Flip)
        # On stocke la dernière position X pour savoir si on va à gauche ou droite
        self.last_unit_positions = {} 
        self.flipped_units = {} # Mémorise qui regarde à gauche

        # Centrage initial
        if scenario.units:
            avg_x = sum(u.x for u in scenario.units) / len(scenario.units)
            avg_y = sum(u.y for u in scenario.units) / len(scenario.units)
            self.center_camera_on(avg_x, avg_y)
        else:
            self.center_camera_on(60, 60)
        
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.paused = False
        
        self.sprites = {}
        self.ground_tile = None
        self.load_sprites()

    def center_camera_on(self, target_x, target_y):
        tile_w = BASE_TILE_WIDTH * self.zoom_level
        tile_h = BASE_TILE_HEIGHT * self.zoom_level
        iso_x = (target_x - target_y) * (tile_w / 2)
        iso_y = (target_x + target_y) * (tile_h / 2)

        screen_w, screen_h = self.screen.get_size()
        self.cam_x = (screen_w / 2) - iso_x
        self.cam_y = (screen_h / 2) - iso_y

    def load_sprites(self):
        # Charge le sol
        ground_path = os.path.join("assets", "ground.png")
        if os.path.exists(ground_path):
            try:
                img = pygame.image.load(ground_path).convert_alpha()
                self.ground_tile = pygame.transform.scale(img, (BASE_TILE_WIDTH, BASE_TILE_HEIGHT))
            except: self.ground_tile = None
        
        # Charge les unités
        unit_types = ["Knight", "Pikeman", "Crossbowman"]
        teams = {"A": (0, 200, 255), "B": (255, 50, 50)}

        for u_type in unit_types:
            self.sprites[u_type] = {}
            for team_name, color in teams.items():
                path = os.path.join("assets", f"{u_type}_{team_name}.png")
                if os.path.exists(path):
                    self.sprites[u_type][team_name] = pygame.image.load(path).convert_alpha()
                    print(f"✅ Chargé : {path}")
                else:
                    # Placeholder (Carré simple) si pas d'image
                    s = pygame.Surface((48, 48), pygame.SRCALPHA)
                    pygame.draw.ellipse(s, (0,0,0, 100), (12, 36, 24, 12))
                    pygame.draw.rect(s, color, (16, 10, 16, 30))
                    self.sprites[u_type][team_name] = s

    def cart_to_iso(self, x, y):
        tile_w = BASE_TILE_WIDTH * self.zoom_level
        tile_h = BASE_TILE_HEIGHT * self.zoom_level
        iso_x = (x - y) * (tile_w / 2)
        iso_y = (x + y) * (tile_h / 2)
        return iso_x + self.cam_x, iso_y + self.cam_y

    def handle_input(self):
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.simulation_controller.toggle_pause()
                if event.key == pygame.K_F9: return "SWITCH"
                if event.key == pygame.K_c and hasattr(self, 'last_avg_x'):
                    self.center_camera_on(self.last_avg_x, self.last_avg_y)
                if event.key == pygame.K_KP_PLUS :
                    self.simulation_controller.increase_tick()
                if event.key == pygame.K_KP_MINUS :
                    self.simulation_controller.decrease_tick()

            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0: self.zoom_level = min(3.0, self.zoom_level + 0.1)
                else: self.zoom_level = max(0.4, self.zoom_level - 0.1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: self.dragging = True; self.last_mouse_pos = mouse_pos
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: self.dragging = False

        if self.dragging:
            dx = mouse_pos[0] - self.last_mouse_pos[0]
            dy = mouse_pos[1] - self.last_mouse_pos[1]
            self.cam_x += dx; self.cam_y += dy
            self.last_mouse_pos = mouse_pos
        return True

    def update(self):
        self.screen.fill(self.BG_COLOR)

        curr_w = int(BASE_TILE_WIDTH * self.zoom_level) + 1
        curr_h = int(BASE_TILE_HEIGHT * self.zoom_level) + 1
        
        scaled_ground = None
        if self.ground_tile:
            scaled_ground = pygame.transform.scale(self.ground_tile, (curr_w, curr_h))

        # --- DESSIN DU SOL ---
        p1 = self.cart_to_iso(0, 0); p2 = self.cart_to_iso(MAP_SIZE, 0)
        p3 = self.cart_to_iso(MAP_SIZE, MAP_SIZE); p4 = self.cart_to_iso(0, MAP_SIZE)
        pygame.draw.polygon(self.screen, (34, 139, 34), [p1, p2, p3, p4])

        if self.ground_tile and self.zoom_level > 0.15:
            half_w = curr_w // 2
            start_x = 0; end_x = MAP_SIZE; start_y = 0; end_y = MAP_SIZE
            for x in range(start_x, end_x): 
                for y in range(start_y, end_y):
                    sx, sy = self.cart_to_iso(x, y)
                    if -100 < sx < self.width + 100 and -100 < sy < self.height + 100:
                        self.screen.blit(scaled_ground, (sx - half_w, sy))

        # --- DESSIN DES UNITÉS ---
        visible_units = [u for u in self.scenario.units if u.hp > 0]
        visible_units.sort(key=lambda u: u.x + u.y)
        
        if visible_units:
            self.last_avg_x = sum(u.x for u in visible_units) / len(visible_units)
            self.last_avg_y = sum(u.y for u in visible_units) / len(visible_units)

        for unit in visible_units:
            ix, iy = self.cart_to_iso(unit.x, unit.y)
            
            # Culling (Si hors écran, on ignore)
            if -100 < ix < self.width + 100 and -100 < iy < self.height + 100:
                try: 
                    sprite_orig = self.sprites[unit.name][unit.team]
                except: 
                    # Fallback sur le Piquier si l'image Knight/Crossbowman manque
                    sprite_orig = self.sprites["Pikeman"][unit.team]

                # --- 1. LOGIQUE MIROIR (FLIP) ---
                # On compare la position X actuelle avec la précédente
                should_flip = self.flipped_units.get(unit, False) # Valeur par défaut
                
                if unit in self.last_unit_positions:
                    last_x = self.last_unit_positions[unit]
                    if unit.x < last_x - 0.01: # Va vers la gauche
                        should_flip = True
                    elif unit.x > last_x + 0.01: # Va vers la droite
                        should_flip = False
                
                # Mémoriser pour la prochaine fois
                self.last_unit_positions[unit] = unit.x
                self.flipped_units[unit] = should_flip

                # Si besoin, on retourne l'image
                if should_flip:
                    sprite_orig = pygame.transform.flip(sprite_orig, True, False)

                # --- 2. MISE A L'ÉCHELLE ---
                w, h = sprite_orig.get_size()
                sw = int(w * self.zoom_level); sh = int(h * self.zoom_level)
                sprite = pygame.transform.scale(sprite_orig, (sw, sh))
                
                # --- 3. AFFICHAGE ---
                offset_y = (curr_h / 2)
                rect = sprite.get_rect(midbottom=(ix, iy + offset_y))
                self.screen.blit(sprite, rect)

                # --- 4. BARRE DE VIE DYNAMIQUE ---
                if unit.hp < unit.hp_max:
                    hp_pct = unit.hp / unit.hp_max
                    
                    # Couleur dynamique
                    if hp_pct > 0.5: bar_color = (0, 255, 0)   # Vert
                    elif hp_pct > 0.25: bar_color = (255, 200, 0) # Jaune
                    else: bar_color = (255, 0, 0)             # Rouge

                    bw = 32 * self.zoom_level
                    bh = 4 * self.zoom_level
                    
                    # Fond noir
                    pygame.draw.rect(self.screen, (0,0,0), (rect.centerx - bw/2, rect.top - bh - 4, bw, bh))
                    # Vie
                    pygame.draw.rect(self.screen, bar_color, (rect.centerx - bw/2, rect.top - bh - 4, bw * hp_pct, bh))

        # --- DESSIN HUD & MINIMAP ---
        self.draw_minimap()

        fps = int(self.clock.get_fps())
        t1 = self.font.render(f"FPS: {fps} | "
                              f"Zoom: {int(self.zoom_level*100)}% | "
                              f"Tick speed: {self.simulation_controller.get_tick_speed()} | "
                              f"Tick: {self.simulation_controller.get_tick()}", True, (255,255,255))
        self.screen.blit(t1, (10, 10))

        pygame.display.flip()
        return True

    # --- MINIMAP (Code précédent inchangé) ---
    def draw_minimap(self):
        minimap_size = 200
        margin = 20
        minimap_surf = pygame.Surface((minimap_size, minimap_size))
        minimap_surf.fill((20, 80, 20)) # Vert sombre
        
        ratio = minimap_size / MAP_SIZE
        for unit in self.scenario.units:
            if unit.hp <= 0: continue
            mx = int(unit.x * ratio)
            my = int(unit.y * ratio)
            color = (0, 255, 255) if unit.team == "A" else (255, 50, 50)
            pygame.draw.rect(minimap_surf, color, (mx, my, 3, 3))

        # Cadre caméra
        view_cx = self.last_avg_x * ratio
        view_cy = self.last_avg_y * ratio
        rect_size = (40 / self.zoom_level) 
        r = pygame.Rect(0, 0, rect_size, rect_size)
        r.center = (view_cx, view_cy)
        pygame.draw.rect(minimap_surf, (255, 255, 255), r, 1)

        # Affichage écran
        dest_rect = pygame.Rect(self.width - minimap_size - margin, self.height - minimap_size - margin, minimap_size, minimap_size)
        
        # Interaction Souris Minimap (Réimplémentation rapide ici si handle_input ne le fait pas)
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and dest_rect.collidepoint(mouse_pos):
             rel_x = (mouse_pos[0] - dest_rect.x) / minimap_size
             rel_y = (mouse_pos[1] - dest_rect.y) / minimap_size
             self.center_camera_on(rel_x * MAP_SIZE, rel_y * MAP_SIZE)

        pygame.draw.rect(self.screen, (255, 255, 255), (dest_rect.x-2, dest_rect.y-2, dest_rect.w+4, dest_rect.h+4), 2)
        self.screen.blit(minimap_surf, dest_rect)

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            res = self.handle_input()
            if res is False: return False
            if res == "SWITCH": return "SWITCH"
            if not self.paused:
                result = self.update()
                if result is False:
                    running = False
                elif result == "SWITCH":
                    running = False
                    return "SWITCH"
            else:
                # Affiche juste le texte "PAUSED" centré horizontalement à partir de la taille réelle de la fenêtre
                pause_text = self.font.render("PAUSED - Appuyez sur 'P' pour reprendre", True, (255, 0, 0))
                screen_w, _ = self.screen.get_size()
                self.screen.blit(pause_text, (screen_w // 2 - pause_text.get_width() // 2, 10))
                pygame.display.flip()
        pygame.quit()
        sys.exit()

    def cleanup(self):
        pygame.quit()