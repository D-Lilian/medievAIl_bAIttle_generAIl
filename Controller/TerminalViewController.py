"""
Terminal View Controller - Interface for running simulations with terminal visualization.

This controller provides a clean interface for others to use the terminal view
with the medieval battle simulation.
"""

from View.terminal_view import TerminalView
from Model.Simulation import Simulation


class TerminalViewController:
    """
    Controller to manage terminal-based visualization of battles.
    
    Provides an easy-to-use interface for running simulations with
    curses-based terminal display.
    """
    
    def __init__(self, board_width: int = 120, board_height: int = 120, tick_speed: int = 20):
        """
        Initialize the terminal view controller.
        
        Args:
            board_width: Width of the battlefield in units
            board_height: Height of the battlefield in units
            tick_speed: Display refresh rate (frames per second)
        """
        self.board_width = board_width
        self.board_height = board_height
        self.tick_speed = tick_speed
        self.view = None
        self.simulation = None
    
    def run_interactive(self, scenario, paused: bool = False):
        """
        Run a simulation with interactive terminal visualization.
        
        Args:
            scenario: Scenario object containing units and generals
            paused: Start the simulation in paused state
            
        Controls:
            P: Pause/Resume
            M: Toggle zoom
            ZQSD/Arrows: Move camera
            TAB: Generate HTML report
            ESC: Quit
        """
        # Create simulation
        self.simulation = Simulation(scenario, tick_speed=self.tick_speed, paused=paused)
        
        # Create view
        self.view = TerminalView(self.board_width, self.board_height, tick_speed=self.tick_speed)
        
        try:
            self.view.init_curses()
            
            # Main loop
            running = True
            while running:
                if not self.view.paused:
                    # Execute one simulation step
                    if hasattr(self.simulation, 'step'):
                        self.simulation.step()
                    else:
                        # Fallback if step doesn't exist
                        break
                
                # Update view and handle input
                running = self.view.update(self.simulation)
                
        except KeyboardInterrupt:
            pass
        finally:
            # Curses cleanup is handled by view.update when it returns False
            pass
    
    def run_headless(self, scenario, ticks: int = 100):
        """
        Run a simulation without visualization (for testing).
        
        Args:
            scenario: Scenario object containing units and generals
            ticks: Number of ticks to run
            
        Returns:
            dict: Snapshot of final state
        """
        self.simulation = Simulation(scenario, tick_speed=self.tick_speed, unlocked=True)
        self.view = TerminalView(self.board_width, self.board_height, tick_speed=self.tick_speed)
        
        return self.view.run_headless(self.simulation, ticks=ticks)
    
    def generate_report(self):
        """
        Generate an HTML report of the current simulation state.
        
        Requires that a simulation has been run.
        """
        if self.view is None:
            raise RuntimeError("No view initialized. Run a simulation first.")
        
        self.view.generate_html_report()


def run_battle_with_terminal_view(scenario, board_width=120, board_height=120, tick_speed=20):
    """
    Convenience function to quickly run a battle with terminal visualization.
    
    Args:
        scenario: Scenario object with units and generals
        board_width: Battlefield width
        board_height: Battlefield height
        tick_speed: Display refresh rate
    """
    controller = TerminalViewController(board_width, board_height, tick_speed)
    controller.run_interactive(scenario)
