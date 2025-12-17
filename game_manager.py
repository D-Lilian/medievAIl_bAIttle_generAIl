import random
import time

import Controller.simulation_controller as SimulationController
from Model.scenario import Scenario
from Model.simulation import Simulation
from Model.units import *
from Model.strategies import *
from Model.orders import OrderManager
from Model.generals import General
from Utils.logs import setup_logger
from View.pygame_view import PygameView

if __name__ == "__main__":
    setup_logger(level="INFO", modules=["Model.generals", "Model.orders", "Model.strategies", "Model.simulation" ])
    simulation_controller = SimulationController.SimulationController()
    units_a = []
    units_b = []
    units = []
    for i in range (0, 100):
        rand = random.randint(0, 2)
        temp = None
        if (rand == 0):
            temp = Knight("A", 10 + i % 20, 10 + i % 5)
        elif (rand == 1):
            temp = Pikeman("A", 10 + i % 20, 10 + i % 5)
            temp.range = 0.1
        else:
            temp = Crossbowman("A", 10 + i % 20, 10 + i % 5)
        #temp.order_manager= OrderManager()
        temp.size = 0.4
        units_a.append(temp)
        units.append(temp)


        if (rand == 0):
            temp = Knight("B", 10 + i % 20, 50 + i % 5)
        elif (rand == 1):
            temp = Pikeman("B", 10 + i % 20, 50 + i % 5)
            temp.range = 0.1
        else:
            temp = Crossbowman("B", 10 + i % 20, 50 + i % 5)
        #temp.order_manager= OrderManager()
        temp.size = 0.4
        units_b.append(temp)
        units.append(temp)

    DAFT1 = General(units_a,
                    units_b,
                    sS=None,
                    sT={
                        # UnitType.CROSSBOWMAN: StrategieBrainDead(UnitType.CROSSBOWMAN),
                        # UnitType.KNIGHT: StrategieBrainDead(UnitType.KNIGHT),
                        # UnitType.PIKEMAN: StrategieBrainDead(UnitType.PIKEMAN)
                        UnitType.CROSSBOWMAN: StrategieDAFT(UnitType.CROSSBOWMAN),
                        UnitType.KNIGHT: StrategieDAFT(UnitType.KNIGHT),
                        UnitType.PIKEMAN: StrategieDAFT(UnitType.PIKEMAN)
                    }
            )

    RPC2 = General(
        units_b,
        units_a,
        sS=None,
        sT={  # TODO: Fix the strategies to use the enum
            UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.CROSSBOWMAN, hatedTroup=None),
            UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.KNIGHT, hatedTroup=None),
            UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.PIKEMAN, hatedTroup=None),
        }
    )
    RPC1 = General(
        units_a,
        units_b,
        sS=None,
        sT={  # TODO: Fix the strategies to use the enum
            #UnitType.KNIGHT: StrategieKnightSomeIQ(),
            #UnitType.PIKEMAN: StrategiePikemanSomeIQ(),
            #UnitType.CROSSBOWMAN: StrategieCrossbowmanSomeIQ(),
            UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.CROSSBOWMAN, hatedTroup=None),
            UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.KNIGHT, hatedTroup=None),
            UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.PIKEMAN, hatedTroup=None),
        }
    )

    DUMMY2 = General(units_b,units_a,sS=None,sT=None)

    SOMEIQ = General(
        units_a,
        units_b,
        sS=None,
        sT={  # TODO: Fix the strategies to use the enum
            UnitType.KNIGHT: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.CROSSBOWMAN, hatedTroup=UnitType.PIKEMAN),
            UnitType.PIKEMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.KNIGHT, hatedTroup=UnitType.CROSSBOWMAN),
            UnitType.CROSSBOWMAN: StrategieSimpleAttackBestAvoidWorst(favoriteTroup=UnitType.PIKEMAN, hatedTroup=UnitType.KNIGHT),
        })
    SOMEIQ.sS = StrategieStartSomeIQ


    DAFT2 = General(units_b,
                    units_a,
                    sS=None,
                    sT={
                        # UnitType.CROSSBOWMAN: StrategieBrainDead(UnitType.CROSSBOWMAN),
                        # UnitType.KNIGHT: StrategieBrainDead(UnitType.KNIGHT),
                        # UnitType.PIKEMAN: StrategieBrainDead(UnitType.PIKEMAN)
                        UnitType.CROSSBOWMAN: StrategieDAFT(UnitType.CROSSBOWMAN),
                        UnitType.KNIGHT: StrategieDAFT(UnitType.KNIGHT),
                        UnitType.PIKEMAN: StrategieDAFT(UnitType.PIKEMAN)
                    }
            )

    scenario = Scenario(units, units_a, units_b, SOMEIQ, RPC2, size_x=120, size_y=120)


    RANDOMIQ1 = General(units_a, units_b, sS=None, sT=None)
    # rouge RPC
    # bleu DAFT1


    # Partie de mesure de temps d'execution
    # start_time = time.perf_counter()
    # simulation_controller.start_multiple_simulations(scenario, 6)
    # end_time = time.perf_counter()
    # print(f"\nMain execution time: {end_time - start_time:.6f} seconds")


    # sim = Simulation(
    #     scenario,
    #     tick_speed=10,
    #     unlocked=True,
    #     paused=False
    # )
    #
    # import cProfile
    # import pstats
    # with cProfile.Profile() as pr:
    #     result = sim.simulate()
    #
    #
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()

    simulation_controller.initialize_simulation(scenario)
    view = PygameView(scenario, simulation_controller, width=1000, height=700)

    simulation_controller.start_simulation()
    view.run()

    print("Simulation started")

    # while simulation_controller.get_tick() < 600:
    #     print(simulation_controller.get_tick())
    #     # sleep(1)
    #     print(simulation_controller.isSimulationRunning)
    #     if not simulation_controller.isSimulationRunning:
    #         break

    # simulation_controller.start_multiple_simulations(scenario, 20)
