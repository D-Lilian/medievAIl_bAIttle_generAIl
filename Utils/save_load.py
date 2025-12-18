# -*- coding: utf-8 -*-
"""
@file save_load.py
@brief Save and load a game

@details
Serialize the scenario object using Pickle.

"""

import os, pickle
from datetime import datetime
from Model.scenario import Scenario
from Model.general_factory import create_general

class SaveLoad:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def save_game(self) -> str | None:
            """Save the current game state"""
            try:
                general_a_name = getattr(getattr(self.scenario, 'general_a', None), 'name', None)
                general_b_name = getattr(getattr(self.scenario, 'general_b', None), 'name', None)

                data = {
                    'scenario': {
                        'units': self.scenario.units,
                        'units_a': self.scenario.units_a,
                        'units_b': self.scenario.units_b,
                        'size_x': self.scenario.size_x,
                        'size_y': self.scenario.size_y,
                        'general_a_name': general_a_name,
                        'general_b_name': general_b_name,
                    }
                }

                # Ensure the save directory exists
                save_dir = "save"
                os.makedirs(save_dir, exist_ok=True)

                # Generate a timestamped filename
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = os.path.join(save_dir, f"{timestamp}.pkl")

                with open(filename, "wb") as file:
                    pickle.dump(data, file)

                print(f"Game successfully saved to {filename}.")
                return filename

            except Exception as e:
                print(f"Error saving game: {e}")

    @staticmethod
    def load_game(file_path: str) -> Scenario | None:
        """Load a saved game state and return a Scenario."""
        try:
            if not file_path.endswith(".pkl"):
                file_path += ".pkl"

            # Ensure file exists and is not empty
            if not os.path.exists(file_path):
                raise FileNotFoundError(file_path)

            if os.path.getsize(file_path) == 0:
                raise ValueError("Empty save file (previous save failed).")

            with open(file_path, "rb") as file:
                data = pickle.load(file)

            scenario_data = data.get("scenario")
            if scenario_data is None:
                raise ValueError("Invalid save file format.")

            size_x = scenario_data["size_x"]
            size_y = scenario_data["size_y"]
            units = scenario_data["units"]

            if size_x is None or size_y is None or units is None:
                raise ValueError("Corrupted save file.")


            units_a = scenario_data.get("units_a")
            units_b = scenario_data.get("units_b")
            gen_a_name = scenario_data.get("general_a_name")
            gen_b_name = scenario_data.get("general_b_name")

            general_a = create_general(gen_a_name, units_a, units_b) if gen_a_name else None
            general_b = create_general(gen_b_name, units_b, units_a) if gen_b_name else None

            scenario = Scenario(
                units=units,
                units_a=units_a,
                units_b=units_b,
                general_a=general_a,
                general_b=general_b,
                size_x=size_x,
                size_y=size_y,
            )

            print(f"Game successfully loaded from {file_path}.")
            return scenario
        except FileNotFoundError:
            print("Save file not found.")
            return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
