import csv
from pathlib import Path
from uuid import uuid4

class SnakeDataCollector:
    FIELDNAMES = [
        "session_id",
        "step",
        "head_x",
        "head_y",
        "food_x",
        "food_y",
        "food_dx",
        "food_dy",
        "distance_to_food",
        "snake_length",
        "score",
        "current_direction",
        "danger_up",
        "danger_down",
        "danger_left",
        "danger_right",
        "action",
    ]

    def __init__(self, csv_path):
        self.csv_path = Path(csv_path)

        self.csv_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.session_id = uuid4().hex[:8]
        self.rows_in_session = 0

    def collect(self, snake, food, action):
        if food is None:
            return

        self.rows_in_session += 1

        head_x, head_y = snake.rect.center
        food_x, food_y = food.rect.center

        food_dx = food_x - head_x
        food_dy = food_y - head_y

        row = dict.fromkeys(self.FIELDNAMES)
        row.update({
            "session_id": self.session_id,
            "step": self.rows_in_session,
            "head_x": head_x,
            "head_y": head_y,
            "food_x": food_x,
            "food_y": food_y,
            "food_dx": food_dx,
            "food_dy": food_dy,
            "distance_to_food": (
                abs(food_dx) + abs(food_dy)
            ),
            "snake_length": snake.length,
            "score": snake.score,
            "current_direction": snake.direction_name,
            "danger_up": snake.would_collide("up"),
            "danger_down": snake.would_collide("down"),
            "danger_left": snake.would_collide("left"),
            "danger_right": snake.would_collide("right"),
            "action": action,
        })

        self._append_row(row)

    def _append_row(self, row):
        file_has_data = (
            self.csv_path.exists()
            and self.csv_path.stat().st_size > 0
        )

        with self.csv_path.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDNAMES,
            )

            if not file_has_data:
                writer.writeheader()

            writer.writerow(row)