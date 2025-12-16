# -*- coding: utf-8 -*-
"""
@file simulation_controller.py
@brief Simulation Controller - Manages the simulation execution

@details
Handles the simulation loop, speed control, and multiprocessing for multiple simulations.
Acts as the controller in the MVC pattern.

"""
from Model.simulation import Simulation
import multiprocessing
import threading
import copy

def run_simulation_worker_multiprocessing(scenario, output, idx, tick_speed=5):
    """
    @brief Function to run a simulation in a separate process for multiprocessing.

    @param scenario Scenario instance to simulate.
    @param output List to store the results of the simulation.
    @param idx Index of the simulation (for identification in output).
    """
    scenario_copy = copy.deepcopy(scenario)
    sim = Simulation(
        scenario_copy,
        tick_speed=tick_speed,
        unlocked=True,
        paused = False
    )
    result = sim.simulate()
    output.append((idx, result, scenario_copy))
    return

class SimulationController:

    def __init__(self):
        """
        @brief Initialize the controller.

        @details Sets up initial state for the simulation controller.
        simulation is the current simulation instance.
        isSimulationRunning indicates if a simulation is currently running.
        result stores the output of the simulation.
        """
        self.simulation = None
        self.isSimulationRunning = False
        self.result = None

    def initialize_simulation(self, scenario, tick_speed=10, paused=False, unlocked=False):
        """
        @brief Initializes the simulation with the given scenario.

        @param scenario Scenario instance to simulate.
        @param tickSpeed Initial tick speed for the simulation.
        @param paused Initial paused state of the simulation.
        @param unlocked Initial unlocked state of the simulation.
        """
        self.simulation = Simulation(
            scenario,
            tick_speed=tick_speed,
            paused=paused,
            unlocked=unlocked
        )

    def start_simulation(self):
        """
        @brief Starts the simulation in a separate thread.
        """
        thread = threading.Thread(target=self.simulation.simulate, args=(self.on_simulation_end,))
        thread.start()
        self.isSimulationRunning = True
        return

    def toggle_pause(self):
        """
        @brief Toggles the paused state of the simulation.
        """
        self.simulation.paused = not self.simulation.paused

    def increase_tick(self):
        """
        @brief Increases the tick speed of the simulation.
        """
        self.simulation.tick_speed += 1

    def decrease_tick(self):
        """
        @brief Decreases the tick speed of the simulation, ensuring it doesn't go below 1.
        """
        if self.simulation.tick_speed > 1:
            self.simulation.tick_speed -= 1

    def get_tick_speed(self):
        """
        @brief Retrieves the current tick speed of the simulation.
        """
        return self.simulation.tick_speed

    def get_tick(self):
        """
        @brief Retrieves the current tick of the simulation.
        """
        return self.simulation.tick

    def on_simulation_end(self, output):
        """
        @brief Callback function when the simulation ends.
        @param output Output of the simulation.
        """
        self.isSimulationRunning = False
        self.result = output

    def start_multiple_simulations(self, scenario, number_of_simulation):
        """
        @brief Starts multiple simulations in parallel using multiprocessing.

        @param scenario Scenario instance to simulate.
        @param number_of_simulation Number of simulations to run in parallel.
        """
        output = []
        jobs = []
        self.isSimulationRunning = True
        for p in range(number_of_simulation):
            process = multiprocessing.Process(target=run_simulation_worker_multiprocessing, args=(scenario, output, p))
            jobs.append(process)
            process.start()

        for p in jobs:
            p.join()

        self.isSimulationRunning = False
        self.result = output

