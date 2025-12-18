from typing import Optional
import pygame
from Controller.simulation_controller import SimulationController
from View.pygame_view import PygameView
from Model.scenario import Scenario

class PygameController:
    def __init__(self, sim_controller: SimulationController, scenario: Scenario):
        self.sim_controller = sim_controller
        self.view = PygameView(scenario, sim_controller)
        self.running = False
        self.clock = pygame.time.Clock()

    def run(self):
        self.running = True
        
        while self.running:
            # Handle Input
            if not self.view.handle_input():
                self.running = False
            
            # Update View
            self.view.update()
            
            # Cap FPS
            self.clock.tick(60)
            
        pygame.quit()

