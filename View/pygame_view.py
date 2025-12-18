from time import sleep

import pygame
import sys
import os
from View.report_generator import ReportGenerator
from View.stats import Stats
from View.unit_cache import UnitCacheManager
from Utils.save_load import SaveLoad
from Model.units import Team

# Constantes
BASE_TILE_WIDTH = 64
BASE_TILE_HEIGHT = 32
MAP_SIZE = 120
MIN_ZOOM = 0.4
MAX_ZOOM = 3.0
ZOOM_STEP = 0.1
FPS = 60

# Couleurs
BG_COLOR = (20, 20, 25)
TEXT_COLOR = (255, 255, 255)
GROUND_COLOR = (34, 139, 34)
MINIMAP_BG = (20, 80, 20)
MINIMAP_BORDER = (255, 255, 255)
PAUSE_TEXT_COLOR = (255, 0, 0)


class PygameView:
    def __init__(self, scenario, simulation_controller, width=1600, height=1200):

        pygame.init()
        self.min_width = 800
        self.min_height = 600
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("Simulation de bataille")

        self._init_pygame()
        self._init_window(width, height)

        self.scenario = scenario
        self.simulation_controller = simulation_controller

        self.zoom_level = 0.8
        self.cam_x = 0
        self.cam_y = 0
        self.paused = False

        self.dragging = False
        self.last_mouse_pos = (0, 0)

        self.last_unit_positions = {}
        self.flipped_units = {}

        self.last_avg_x = 0
        self.last_avg_y = 0

        self.camera_velocity = [0, 0]
        self.camera_speed = 300
        self.show_hud = True
        self.show_minimap = True

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14, bold=True)

        self.sprites = {}
        self.debug = False
        self.ground_tile = None
        self._load_resources()

        self.ground_cache = {}
        self.last_zoom_cache = 0.0

        self._initial_camera_setup()

        self.report_generator = ReportGenerator(scenario.size_x, scenario.size_y)
        self.stats = Stats()
        self.unit_cache = UnitCacheManager()

        self.save_load = SaveLoad(scenario)
        self.as_save = 0

    def _init_pygame(self):
        """Initialise Pygame avec les paramètres optimaux"""
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()

        pygame.event.set_blocked([pygame.ACTIVEEVENT, pygame.JOYAXISMOTION])

    def _init_window(self, width, height):
        """Initialise la fenêtre et force le focus"""
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        pygame.display.set_caption("MedievAIl Battle - 2.5D")

        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = pygame.display.get_wm_info()['window']
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

    def _load_resources(self):
        """Charge toutes les ressources graphiques"""
        self._load_ground()
        self._load_unit_sprites()

    def _load_unit_sprites(self):
        """Charge les sprites BMP des unités avec recoloration par équipe"""
        from Model.units import UnitType

        unit_types = [UnitType.KNIGHT, UnitType.PIKEMAN, UnitType.CROSSBOWMAN]

        for unit_type in unit_types:
            sprite_path = os.path.join("assets", f"{unit_type.value}stand001.bmp")

            if os.path.exists(sprite_path):
                try:
                    sprite_base = pygame.image.load(sprite_path).convert()
                    sprite_base.set_colorkey((255, 0, 255))
                    self.sprites[unit_type] = {}
                    self.sprites[unit_type][Team.B] = sprite_base

                    sprite_red = self._recolor_sprite(sprite_base)
                    sprite_red.set_colorkey((255, 0, 255))
                    self.sprites[unit_type][Team.A] = sprite_red

                except pygame.error as e:
                    self.sprites[unit_type] = None
            else:
                self.sprites[unit_type] = None

    def _load_ground(self):
        """Charge la texture du sol"""
        ground_path = os.path.join("assets", "ground.png")
        if os.path.exists(ground_path):
            try:
                img = pygame.image.load(ground_path).convert_alpha()
                self.ground_tile = pygame.transform.scale(
                    img, (BASE_TILE_WIDTH, BASE_TILE_HEIGHT)
                )
            except pygame.error as e:
                self.ground_tile = None

    def _initial_camera_setup(self):
        """Centre la caméra sur le champ de bataille"""
        if self.scenario.units:
            avg_x = sum(u.x for u in self.scenario.units) / len(self.scenario.units)
            avg_y = sum(u.y for u in self.scenario.units) / len(self.scenario.units)
            self.center_camera_on(avg_x, avg_y)
        else:
            self.center_camera_on(self.scenario.size_x / 2, self.scenario.size_y / 2)

    def cart_to_iso(self, x, y):
        """Convertit coordonnées cartésiennes en isométriques"""
        tile_w = BASE_TILE_WIDTH * self.zoom_level
        tile_h = BASE_TILE_HEIGHT * self.zoom_level
        iso_x = (x - y) * (tile_w / 2)
        iso_y = (x + y) * (tile_h / 2)
        return iso_x + self.cam_x, iso_y + self.cam_y

    def center_camera_on(self, target_x, target_y):
        """Centre la caméra sur une position"""
        tile_w = BASE_TILE_WIDTH * self.zoom_level
        tile_h = BASE_TILE_HEIGHT * self.zoom_level
        iso_x = (target_x - target_y) * (tile_w / 2)
        iso_y = (target_x + target_y) * (tile_h / 2)

        screen_w, screen_h = self.screen.get_size()
        self.cam_x = (screen_w / 2) - iso_x
        self.cam_y = (screen_h / 2) - iso_y

    def handle_input(self):
        """Gère tous les événements utilisateur"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                return self._handle_keydown(event)

            elif event.type == pygame.MOUSEWHEEL:
                self._handle_mousewheel(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouseup(event)

        if self.dragging:
            self._update_camera_drag()

        return True

    def _handle_keydown(self, event):
        """Traite les événements clavier"""
        if event.key == pygame.K_ESCAPE:
            return False

        elif event.type == pygame.QUIT:
            os._exit(0)

        elif event.key == pygame.K_d and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            self.debug = not self.debug

        elif event.key == pygame.K_p:
            self.paused = not self.paused
            self.simulation_controller.toggle_pause()

        elif event.key == pygame.K_F9:
            return "SWITCH"

        elif event.key == pygame.K_F4:
            self.show_hud = not self.show_hud

        elif event.key == pygame.K_F5:
            self.show_minimap = not self.show_minimap

        elif event.key == pygame.K_c:
            self.center_camera_on(self.last_avg_x, self.last_avg_y)

        elif event.key == pygame.K_KP_PLUS:
            self.simulation_controller.increase_tick()

        elif event.key == pygame.K_KP_MINUS:
            self.simulation_controller.decrease_tick()

        elif event.key == pygame.K_TAB:
            self.report_generator.generate(self.unit_cache.units, self.stats)

        elif event.key == pygame.K_e:
            if not self.paused:
                self.simulation_controller.toggle_pause()
            sleep(0.1)
            self.save_load.save_game()
            self.as_save = 120

        return True

    def _update_camera_movement(self, dt):
        """Met à jour le déplacement de la caméra selon les touches pressées"""
        keys = pygame.key.get_pressed()

        speed_multiplier = 2.5 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 1.0
        speed = self.camera_speed * dt * speed_multiplier

        if keys[pygame.K_z] or keys[pygame.K_UP]:
            self.cam_y += speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.cam_y -= speed
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            self.cam_x += speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.cam_x -= speed

    def _handle_mousewheel(self, event):
        """Gère le zoom avec la molette vers la position de la souris"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        old_zoom = self.zoom_level
        if event.y > 0:
            self.zoom_level = min(MAX_ZOOM, self.zoom_level + ZOOM_STEP)
        else:
            self.zoom_level = max(MIN_ZOOM, self.zoom_level - ZOOM_STEP)

        zoom_ratio = self.zoom_level / old_zoom
        self.cam_x = mouse_x - (mouse_x - self.cam_x) * zoom_ratio
        self.cam_y = mouse_y - (mouse_y - self.cam_y) * zoom_ratio

    def _handle_mousedown(self, event):
        """Démarre le drag de la caméra"""
        if event.button == 1:
            self.dragging = True
            self.last_mouse_pos = event.pos

    def _handle_mouseup(self, event):
        """Arrête le drag de la caméra"""
        if event.button == 1:
            self.dragging = False

    def _update_camera_drag(self):
        """Met à jour la position de la caméra pendant le drag"""
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - self.last_mouse_pos[0]
        dy = mouse_pos[1] - self.last_mouse_pos[1]
        self.cam_x += dx
        self.cam_y += dy
        self.last_mouse_pos = mouse_pos

    def update(self):
        """Met à jour l'affichage (sans déplacement caméra, géré dans run)"""
        if hasattr(self, 'simulation_controller') and hasattr(self.simulation_controller, 'simulation'):
            self.unit_cache.update(self.simulation_controller.simulation, self.stats)

        self.screen.fill(BG_COLOR)

        self._draw_ground()
        self._draw_units()

        if self.show_minimap:
            self._draw_minimap()

        if self.show_hud:
            self._draw_hud()
            self._draw_controls()

        pygame.display.flip()
        return True

    def _draw_ground(self):
        """Dessine le sol avec culling et cache optimisé"""
        p1 = self.cart_to_iso(0, 0)
        p2 = self.cart_to_iso(self.scenario.size_x, 0)
        p3 = self.cart_to_iso(self.scenario.size_x, self.scenario.size_y)
        p4 = self.cart_to_iso(0, self.scenario.size_y)
        pygame.draw.polygon(self.screen, GROUND_COLOR, [p1, p2, p3, p4])

        if not self.ground_tile or self.zoom_level < 0.15:
            return

        curr_w = int(BASE_TILE_WIDTH * self.zoom_level) + 1
        curr_h = int(BASE_TILE_HEIGHT * self.zoom_level) + 1

        scaled_ground = self._get_cached_ground_tile(curr_w, curr_h)
        half_w = curr_w // 2
        screen_w, screen_h = self.screen.get_size()
        margin = 50

        for x in range(self.scenario.size_x):
            for y in range(self.scenario.size_y):
                sx, sy = self.cart_to_iso(x, y)
                if (-curr_w - margin < sx < screen_w + margin and
                        -curr_h - margin < sy < screen_h + margin):
                    self.screen.blit(scaled_ground, (sx - half_w, sy))

    def _get_cached_ground_tile(self, width, height):
        """Récupère ou crée une tuile de sol mise en cache selon le zoom"""
        zoom_key = round(self.zoom_level, 2)

        if zoom_key != self.last_zoom_cache:
            self.ground_cache = {}
            self.last_zoom_cache = zoom_key

        if zoom_key not in self.ground_cache:
            self.ground_cache[zoom_key] = pygame.transform.smoothscale(
                self.ground_tile, (width, height)
            )

        return self.ground_cache[zoom_key]

    def _draw_units(self):
        """Dessine toutes les unités vivantes"""
        visible_units = [u for u in self.scenario.units if u.hp > 0]
        visible_units.sort(key=lambda u: u.x + u.y)

        if visible_units:
            self.last_avg_x = sum(u.x for u in visible_units) / len(visible_units)
            self.last_avg_y = sum(u.y for u in visible_units) / len(visible_units)

        curr_h = int(BASE_TILE_HEIGHT * self.zoom_level) + 1

        for unit in visible_units:
            ix, iy = self.cart_to_iso(unit.x, unit.y)

            if not (-100 < ix < self.width + 100 and -100 < iy < self.height + 100):
                continue

            self._draw_unit(unit, ix, iy, curr_h)

    def _draw_unit(self, unit, screen_x, screen_y, tile_height):
        """Dessine une unité avec sprite BMP et sa barre de vie"""
        sprite_dict = self.sprites.get(unit.unit_type)

        sprite = None
        if sprite_dict and isinstance(sprite_dict, dict):
            sprite = sprite_dict.get(unit.team)

        if sprite:
            scaled_width = int(sprite.get_width() * self.zoom_level)
            scaled_height = int(sprite.get_height() * self.zoom_level)

            if scaled_width > 0 and scaled_height > 0:
                sprite_scaled = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                offset_y = tile_height / 2
                sprite_rect = sprite_scaled.get_rect()
                sprite_rect.midbottom = (screen_x, screen_y + offset_y)
                self.screen.blit(sprite_scaled, sprite_rect)

                if unit.hp < unit.hp_max:
                    self._draw_health_bar(unit, sprite_rect)
        else:
            color = (255, 0, 0) if unit.team == Team.A else (0, 150, 255)
            rect_width = int(20 * self.zoom_level)
            rect_height = int(30 * self.zoom_level)
            offset_y = tile_height / 2
            rect = pygame.Rect(0, 0, rect_width, rect_height)
            rect.midbottom = (screen_x, screen_y + offset_y)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)

            if unit.hp < unit.hp_max:
                self._draw_health_bar(unit, rect)

        if self.debug:
            cx, cy = int(screen_x), int(screen_y)
            radius = max(3, int(8 * self.zoom_level) * (1 + unit.size))
            pygame.draw.circle(self.screen, (255, 255, 0), (cx, cy), radius, 2)

            cx, cy = int(screen_x), int(screen_y)
            radius = max(3, int(10 * self.zoom_level) * (1 + unit.range))
            pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), radius, 2)

    def _recolor_sprite(self, sprite):
        """Remplace une couleur par une autre dans un sprite en préservant le magenta"""
        sprite_copy = sprite.copy()
        pixels = pygame.surfarray.pixels3d(sprite_copy)
        r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]

        is_blue = (
                (b > r + 30) &
                (b > g + 30) &
                (b > 100) &
                ~((r > 250) & (g < 10) & (b > 250))
        )

        if is_blue.any():
            blue_intensity = b[is_blue].astype(float) / 255.0

            pixels[is_blue, 0] = (blue_intensity * 220).astype('uint8')
            pixels[is_blue, 1] = (b[is_blue] * 0.15).astype('uint8')
            pixels[is_blue, 2] = (b[is_blue] * 0.15).astype('uint8')

        del pixels
        return sprite_copy

    def _draw_health_bar(self, unit, rect):
        """Dessine la barre de vie d'une unité"""
        hp_pct = unit.hp / unit.hp_max

        if hp_pct > 0.5:
            bar_color = (0, 255, 0)
        elif hp_pct > 0.25:
            bar_color = (255, 200, 0)
        else:
            bar_color = (255, 0, 0)

        bar_width = 32 * self.zoom_level
        bar_height = 4 * self.zoom_level
        bar_x = rect.centerx - bar_width / 2
        bar_y = rect.top - bar_height - 4

        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, bar_color, (bar_x, bar_y, bar_width * hp_pct, bar_height))

    def _draw_minimap(self):
        """Dessine la minimap"""
        if not self.show_minimap:
            return

        screen_w, screen_h = self.screen.get_size()
        minimap_size = 150
        margin = 10

        # Position en bas à droite
        minimap_x = screen_w - minimap_size - margin
        minimap_y = screen_h - minimap_size - margin - 50

        minimap_surf = pygame.Surface((minimap_size, minimap_size))
        minimap_surf.fill(MINIMAP_BG)

        ratio_x = minimap_size / self.scenario.size_x
        ratio_y = minimap_size / self.scenario.size_y

        # Dessine les unités
        for unit in self.scenario.units:
            if unit.hp <= 0:
                continue

            mx = int(unit.x * ratio_x)
            my = int(unit.y * ratio_y)
            color = (255, 50, 50) if unit.team == Team.A else (0, 255, 255)
            pygame.draw.rect(minimap_surf, color, (mx, my, 3, 3))

        view_cx = self.last_avg_x * ratio_x
        view_cy = self.last_avg_y * ratio_y
        rect_size = 40 / self.zoom_level
        camera_rect = pygame.Rect(0, 0, rect_size, rect_size)
        camera_rect.center = (view_cx, view_cy)
        pygame.draw.rect(minimap_surf, MINIMAP_BORDER, camera_rect, 1)

        dest_rect = pygame.Rect(minimap_x, minimap_y, minimap_size, minimap_size)

        self._handle_minimap_click(dest_rect)

        pygame.draw.rect(self.screen, MINIMAP_BORDER, dest_rect.inflate(4, 4), 2)
        self.screen.blit(minimap_surf, dest_rect)

    def _handle_minimap_click(self, minimap_rect):
        """Gère le clic sur la minimap pour centrer la caméra"""
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and minimap_rect.collidepoint(mouse_pos):
            rel_x = (mouse_pos[0] - minimap_rect.x) / minimap_rect.width
            rel_y = (mouse_pos[1] - minimap_rect.y) / minimap_rect.height
            self.center_camera_on(rel_x * self.scenario.size_x, rel_y * self.scenario.size_y)

    def _draw_hud(self):
        """Dessine l'interface utilisateur"""
        from Model.units import UnitType

        fps = int(self.clock.get_fps())

        # Comptage des unités par équipe
        alive_team_a = sum(1 for u in self.scenario.units if u.hp > 0 and u.team == Team.A)
        alive_team_b = sum(1 for u in self.scenario.units if u.hp > 0 and u.team == Team.B)
        total_alive = alive_team_a + alive_team_b

        # Comptage par type pour Team A
        knights_a = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.A and u.unit_type == UnitType.KNIGHT)
        pikemen_a = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.A and u.unit_type == UnitType.PIKEMAN)
        crossbow_a = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.A and u.unit_type == UnitType.CROSSBOWMAN)

        # Comptage par type pour Team B
        knights_b = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.B and u.unit_type == UnitType.KNIGHT)
        pikemen_b = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.B and u.unit_type == UnitType.PIKEMAN)
        crossbow_b = sum(
            1 for u in self.scenario.units if u.hp > 0 and u.team == Team.B and u.unit_type == UnitType.CROSSBOWMAN)

        # Ligne 1: Stats générales
        hud_text = (
            f"FPS: {fps} | "
            f"Zoom: {int(self.zoom_level * 100)}% | "
            f"Tick speed: {self.simulation_controller.get_tick_speed()} | "
            f"Tick: {self.simulation_controller.get_tick()} | "
            f"Unités: {total_alive} (A:{alive_team_a} | B:{alive_team_b})"
        )

        text_surf = self.font.render(hud_text, True, TEXT_COLOR)
        self.screen.blit(text_surf, (10, 10))

        # Ligne 2: Détail des unités Team A
        detail_a = f"Team A - Knights: {knights_a} | Pikemen: {pikemen_a} | Crossbowmen: {crossbow_a}"
        detail_a_surf = self.font.render(detail_a, True, (255, 50, 50))
        self.screen.blit(detail_a_surf, (10, 30))

        # Ligne 3: Détail des unités Team B
        detail_b = f"Team B - Knights: {knights_b} | Pikemen: {pikemen_b} | Crossbowmen: {crossbow_b}"
        detail_b_surf = self.font.render(detail_b, True, (50, 100, 255))
        self.screen.blit(detail_b_surf, (10, 50))

        screen_w = self.screen.get_size()[0]

        if self.paused:
            pause_surf = self.font.render(
                "PAUSED - Appuyez sur 'P' pour reprendre",
                True,
                PAUSE_TEXT_COLOR
            )
            pause_x = screen_w // 2 - pause_surf.get_width() // 2
            self.screen.blit(pause_surf, (pause_x, 10))

        if self.as_save >= 0:
            save_surf = self.font.render(
                "La partie a été enregistrée",
                True,
                PAUSE_TEXT_COLOR
            )
            save_x = screen_w // 2 - save_surf.get_width() // 2
            self.screen.blit(save_surf, (save_x, 30))
            self.as_save -= 1

        # Vérifier si la bataille est terminée
        if alive_team_a == 0 and alive_team_b > 0:
            victory_text = f"VICTOIRE - Team 2 a gagné : {self.scenario.general_b.name} !"
            victory_color = (50, 100, 255)
        elif alive_team_b == 0 and alive_team_a > 0:
            victory_text = f"VICTOIRE - Team 1 a gagné : {self.scenario.general_a.name} !"
            victory_color = (255, 50, 50)
        else:
            victory_text = None

        if victory_text:
            victory_surf = self.font.render(victory_text, True, victory_color)
            victory_x = screen_w // 2 - victory_surf.get_width() // 2
            self.screen.blit(victory_surf, (victory_x, 50))

    def _draw_controls(self):
        """Affiche les instructions de contrôle en bas de l'écran"""
        controls1 = [
            "ZQSD/Flèches: Déplacer caméra",
            "Shift: Accélérer",
            "Molette: Zoom",
            "Clic: Drag",
            "+/-: Vitesse",
        ]
        controls2 = [
            "C: Centrer",
            "Tab: Rapport",
            "E: Sauvegarder",
            "P: Pause",
            "F4: HUD",
            "F5: Minimap",
            "F9: Changer vue",
            "Échap: Quitter"
        ]

        screen_w, screen_h = self.screen.get_size()
        control_height = 50
        bg_rect = pygame.Rect(0, screen_h - control_height, screen_w, control_height)
        bg_surface = pygame.Surface((screen_w, control_height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 128))
        self.screen.blit(bg_surface, bg_rect)

        # Première ligne
        control_text1 = " | ".join(controls1)
        text_surf1 = self.font.render(control_text1, True, TEXT_COLOR)
        text_x1 = screen_w // 2 - text_surf1.get_width() // 2
        text_y1 = screen_h - control_height + 5
        self.screen.blit(text_surf1, (text_x1, text_y1))

        # Deuxième ligne
        control_text2 = " | ".join(controls2)
        text_surf2 = self.font.render(control_text2, True, TEXT_COLOR)
        text_x2 = screen_w // 2 - text_surf2.get_width() // 2
        text_y2 = screen_h - control_height + 25
        self.screen.blit(text_surf2, (text_x2, text_y2))

    def run(self):
        """Boucle principale"""
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0

            result = self.handle_input()
            if not result or result == "SWITCH":
                return result

            self._update_camera_movement(dt)

            if not self.paused:
                result = self.update()
                if not result:
                    return result
            else:
                self.screen.fill(BG_COLOR)
                self._draw_ground()
                self._draw_units()

                if self.show_minimap:
                    self._draw_minimap()

                if self.show_hud:
                    self._draw_hud()
                    self._draw_controls()

                pygame.display.flip()

        return False

    def cleanup(self):
        """Nettoie les ressources Pygame"""
        pygame.quit()