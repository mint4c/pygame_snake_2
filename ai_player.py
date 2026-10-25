from pathlib import Path

import joblib
import pandas as pd

import constants as c

MODEL_FILE = Path(c.DATA_DIR) / "snake_model.joblib"

OPPOSITE = {
    "left": "right",
    "right": "left",
    "up": "down",
    "down": "up",
}

BLOCK_REVERSE = True

model = None
feauture_columns = []
direction_map = {}

def load_model():
    global model, feauture_columns, direction_map

    if not MODEL_FILE.exists():
        print(f"Модель не знайдено: {MODEL_FILE}")
        print("Спочатку натренуйте модель за допомогою model_trainer.py")
        return False
    model_data = joblib.load(MODEL_FILE)

    model = model_data["model"]
    feauture_columns = model_data["feauture_columns"]
    direction_map = model_data["direction_map"]

    print(f"Модель завантажено: {MODEL_FILE}")

    return True


def is_loaded():
    return model is not None


def get_game_state(snake, food):

    if food is None:
        return None

    head_x, head_y = snake.rect.center
    food_x, food_y = food.rect.center

    food_dx = food_x - head_x
    food_dy = food_y - head_y

    direction_name = snake.direction_name or "none"

    return {
        "food_dx": food_dx,
        "food_dy": food_dy,
        "distance_to_food": abs(food_dx) + abs(food_dy),
        "snake_length": snake.length,
        "current_direction": direction_map[direction_name],
        "danger_up": int(snake.would_collide("up")),
        "danger_down": int(snake.would_collide("down")),
        "danger_left": int(snake.would_collide("left")),
        "danger_right": int(snake.would_collide("right")),
    }

def preditct_action(state):

    state_df = pd.DataFrame(
        [state],
        columns=feauture_columns,
    )

    action = model.predict(state_df)[0]

    return str(action)

def apply_action(snake, action):

    if snake.direction_name == action:
        return False

    if BLOCK_REVERSE and snake.direction_name == OPPOSITE.get(action):
        return False

    snake.set_direction(action)

    return True