from Model.Simulation import Simulation
import multiprocessing
import copy

def run_simulation_worker(scenario, output, idx, tickSpeed=5):
    scenario_copy = copy.deepcopy(scenario)
    sim = Simulation(
        scenario_copy,
        tick_speed=tickSpeed,
        unlocked=True,
        paused = False
    )
    result = sim.simulate()
    output.append((idx, result))
    return

class SimulationController:

    def __init__(self):
        self.simulation = None
        self.isSimulationRunning = False


    def start_simulation(self, scenario, tickSpeed=5, paused=False, unlocked=False):
        self.simulation = Simulation(
            scenario,
            tick_speed=tickSpeed,
            paused=paused,
            unlocked=unlocked
        )
        return self.simulation.simulate()

    def toggle_pause(self):
        self.simulation.paused = not self.simulation.paused

    def increase_tick(self):
        self.simulation.tick_speed += 1

    def decrease_tick(self):
        if self.simulation.tick_speed > 1:
            self.simulation.tick_speed -= 1

    def start_multiple_simulations(self, scenario, number_of_simulation):
        """"""
        output = []
        jobs = []
        for p in range(number_of_simulation):
            process = multiprocessing.Process(target=run_simulation_worker, args=(scenario, output, p))
            jobs.append(process)
            process.start()

        for p in jobs:
            p.join()

        return output


