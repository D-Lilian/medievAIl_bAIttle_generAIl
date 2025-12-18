import os, pickle
from datetime import datetime
from Model.scenario import Scenario 

class SaveLoad:
    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario

    def save_game(self) -> str | None:
            """Save the current game state"""
            try:
                data = {
                    'scenario': {
                        'units': self.scenario.units,
                        'units_a': self.scenario.units_a,
                        'units_b': self.scenario.units_b,
                        'size_x': self.scenario.size_x,
                        'size_y': self.scenario.size_y,
                        'general_a': self.scenario.general_a,
                        'general_b': self.scenario.general_b
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
                return filename

            except Exception as e:
                print(f"Error saving game: {e}")

    @staticmethod
    def load_game(file_path: str) -> Scenario | None:
        """Load a saved game state and return a Scenario."""
        try:
            if not file_path.endswith(".pkl"):
                file_path += ".pkl"

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

            scenario = Scenario(
                units=units,
                units_a=scenario_data.get("units_a"),
                units_b=scenario_data.get("units_b"),
                general_a=scenario_data.get("general_a"),
                general_b=scenario_data.get("general_b"),
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
