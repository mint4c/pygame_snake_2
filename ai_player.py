"""
ai_player.py
AI-гравець: навчена модель керує змійкою
"""

from pathlib import Path

import joblib
import pandas as pd

import constants as c


MODEL_FILE = Path(c.DATA_DIR) / "snake_model.joblib"

# Протилежні напрямки
OPPOSITE = {
    "left": "right",
    "right": "left",
    "up": "down",
    "down": "up",
}

# True - AI не розвертається на 180° (це одразу вбило б змійку).
# False - виконується будь-який прогноз моделі без обмежень.
BLOCK_REVERSE = True

# Дані моделі (заповнюються у load_model)
model = None
feature_columns = []
direction_map = {}


def load_model():
    """Завантажує навчену модель із файлу. Повертає True, якщо вдалося."""

    global model
    global feature_columns
    global direction_map

    if not MODEL_FILE.exists():
        print(
            "Модель не знайдено:",
            MODEL_FILE,
        )
        print(
            "Запустіть model_trainer.py, "
            "щоб навчити та зберегти модель."
        )
        return False

    model_data = joblib.load(
        MODEL_FILE
    )

    model = model_data["model"]
    feature_columns = model_data["feature_columns"]
    direction_map = model_data["direction_map"]

    print(
        "Модель завантажено:",
        MODEL_FILE,
    )

    return True


def is_loaded():
    """Перевіряє, чи модель готова до роботи."""

    return model is not None


def get_game_state(snake, food):
    """
    Збирає ознаки з поточного кадру гри.

    Ознаки рахуються так само, як у data_collector.py,
    щоб збігалися з тими, на яких навчалася модель.
    """

    if food is None:
        return None

    head_x, head_y = snake.rect.center
    food_x, food_y = food.rect.center

    food_dx = food_x - head_x
    food_dy = food_y - head_y

    # На початку гри напрямку ще немає
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


def predict_action(state):
    """Передає стан у модель і повертає прогнозовану дію."""

    # columns гарантує правильні назви та порядок ознак
    state_df = pd.DataFrame(
        [state],
        columns=feature_columns,
    )

    action = model.predict(
        state_df
    )[0]

    return str(action)


def apply_action(snake, action):
    """
    Перетворює прогноз на рух змійки.

    Повертає True, якщо напрямок змінився.
    """

    if snake.direction_name == action:
        return False

    if (
        BLOCK_REVERSE
        and snake.direction_name == OPPOSITE.get(action)
    ):
        return False

    snake.set_direction(action)

    return True