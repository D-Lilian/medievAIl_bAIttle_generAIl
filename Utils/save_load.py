import os
import pickle
from datetime import datetime
from Model.scenario import Scenario 

class SaveLoad:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def save_game(self) -> None:
            """Save the current game state"""
            try:
                data = {
                    'scenario': {
                        'units': self.scenario.units,
                        'size_x': self.scenario.size_x,
                        'size_y': self.scenario.size_y
                    }
                }

                # Ensure the save directory exists
                save_dir = "save"
                os.makedirs(save_dir, exist_ok=True)

                # Generate a timestamped filename
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = os.path.join(save_dir, f"{timestamp}.pkl")

                with open(filename, 'wb') as file:
                    pickle.dump(data, file)
                print(f"Game successfully saved to {filename}.")
            except Exception as e:
                print(f"Error saving game: {e}")

    @staticmethod
    def load_game(self, filename: str) -> Scenario | None:
            """Load a saved game state"""
            try:
                save_dir = "save"
                filepath = os.path.join(save_dir, filename + ".pkl")
                with open(filepath, 'rb') as file:
                    data = pickle.load(file)

                    # Extract scenario information
                    scenario_data = data.get("scenario")
                    if scenario_data is None:
                        raise ValueError("Invalid save file format: no scenario found.")

                    size_x = scenario_data["size_x"]
                    size_y = scenario_data["size_y"]
                    units = scenario_data["units"]

                    # Recreate scenario object
                    loaded_scenario = Scenario(size_x=size_x, size_y=size_y,units=units)
                    print(f"Game successfully loaded from {filepath}.")
                    return loaded_scenario

            except FileNotFoundError:
                print("Save file not found.")

            except Exception as e:
                print(f"Error loading game: {e}")

