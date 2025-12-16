from typing import Optional

from Controller.simulation_controller import SimulationController
from View.pygame_view import PygameView
from Model.scenario import Scenario


class TerminalController:

    def __init__(self, simulation_controller: SimulationController, scenario: Scenario, view: Optional[PygameView] = None):
        self.simulation_controller = simulation_controller
        if view:
            self.view = view
        else:
            self.view = PygameView(scenario, simulation_controller, width=800, height=600)
        self.running = False

    def run(self):
        try:
            self.view.init_curses()
            self.running = True
            while self.running:
                self.running = self.view.update()
                if self.view.tick_speed != self.simulation_controller.get_tick_speed():
                    while self.simulation_controller.get_tick_speed() < self.view.tick_speed:
                        self.simulation_controller.increase_tick()
                    while self.simulation_controller.get_tick_speed() > self.view.tick_speed:
                        self.simulation_controller.decrease_tick()
                if self.view.paused != self.simulation_controller.simulation.paused:
                    self.simulation_controller.toggle_pause()
        finally:
            self.view.cleanup()


def run_terminal_view(sim_controller: SimulationController, scenario: Scenario) -> None:
    controller = TerminalController(sim_controller, scenario)
    controller.run()
