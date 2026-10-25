"""
model_trainer.py
навчання моделі для Snake
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "raw_game_data.csv"
MODEL_FILE = BASE_DIR / "data" / "snake_model.joblib"


# Ознаки, які описують поточний стан гри
# (назви збігаються з колонками з data_collector.py)
FEATURE_COLUMNS = [
    "food_dx",
    "food_dy",
    "distance_to_food",
    "snake_length",
    "current_direction",
    "danger_up",
    "danger_down",
    "danger_left",
    "danger_right",
]

# Логічні колонки (True/False), які перетворюємо на 0/1
DANGER_COLUMNS = [
    "danger_up",
    "danger_down",
    "danger_left",
    "danger_right",
]

# current_direction у CSV записується текстом, тому кодуємо числами.
# "none" - початок гри, коли змійка ще не рухалась.
DIRECTION_MAP = {
    "none": 0,
    "left": 1,
    "right": 2,
    "up": 3,
    "down": 4,
}

# Дія, яку модель повинна прогнозувати:
# left, right, up або down
TARGET_COLUMN = "action"


def load_data():
    """Завантажує датасет із CSV-файлу."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Файл raw_game_data.csv не знайдено. "
            "Спочатку запустіть гру та зберіть дані."
        )

    df = pd.read_csv(DATA_FILE)

    print("Перші рядки датасету:")
    print(df.head())

    print("\nКількість рядків:")
    print(len(df))

    print("\nКількість прикладів кожної дії:")
    print(df[TARGET_COLUMN].value_counts())

    return df


def encode_features(df):
    """Перетворює текстові та логічні колонки на числа."""

    df = df.copy()

    df["current_direction"] = (
        df["current_direction"]
        .map(DIRECTION_MAP)
    )

    for column in DANGER_COLUMNS:
        df[column] = df[column].astype(int)

    return df


def prepare_data(df):
    """Готує ознаки та цільову колонку."""

    required_columns = (
        FEATURE_COLUMNS
        + [TARGET_COLUMN]
    )

    # Залишаємо тільки потрібні для моделі колонки
    df = df[required_columns].copy()

    # На початку гри напрямку ще немає (порожнє значення в CSV)
    df["current_direction"] = (
        df["current_direction"]
        .fillna("none")
    )

    # Видаляємо рядки з іншими порожніми значеннями
    df = df.dropna()

    df = encode_features(df)

    # X містить стани гри
    X = df[FEATURE_COLUMNS]

    # y містить дії гравця
    y = df[TARGET_COLUMN]

    return X, y


def split_data(X, y):
    """Розділяє дані на навчальну та тестову частини."""

    if len(X) < 30:
        raise ValueError(
            "У датасеті замало рядків. "
            "Зіграйте ще декілька разів."
        )

    if y.nunique() < 2:
        raise ValueError(
            "У датасеті повинні бути щонайменше "
            "дві різні дії."
        )

    action_counts = y.value_counts()

    if action_counts.min() < 2:
        raise ValueError(
            "Кожна дія повинна зустрічатися "
            "хоча б два рази."
        )

    return train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )


def train_model(X_train, y_train):
    """Створює та навчає дерево рішень."""

    model = DecisionTreeClassifier(
        max_depth=6,
        class_weight="balanced",
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model


def evaluate_model(
    model,
    X_train,
    X_test,
    y_train,
    y_test,
):
    """Перевіряє точність навченої моделі."""

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    train_accuracy = model.score(
        X_train,
        y_train,
    )

    print("\nРезультати навчання")
    print("-------------------")

    print(
        "Навчальних прикладів:",
        len(X_train),
    )

    print(
        "Тестових прикладів:",
        len(X_test),
    )

    print(
        "Точність на train:",
        round(train_accuracy, 2),
    )

    print(
        "Точність на test:",
        round(accuracy, 2),
    )

    results = pd.DataFrame({
        "real_action": y_test,
        "predicted_action": predictions,
    })

    print("\nПерші прогнози:")
    print(results.head(10))

    print("\nТаблиця помилок:")
    print(
        pd.crosstab(
            results["real_action"],
            results["predicted_action"],
        )
    )


def test_new_state(model):
    """Прогнозує дію для нового стану гри."""

    new_state = pd.DataFrame(
        [
            {
                "food_dx": 120,
                "food_dy": -60,
                "distance_to_food": 180,
                "snake_length": 6,
                "current_direction": DIRECTION_MAP["left"],
                "danger_up": 0,
                "danger_down": 0,
                "danger_left": 0,
                "danger_right": 0,
            }
        ]
    )

    new_state = new_state[FEATURE_COLUMNS]

    predicted_action = model.predict(
        new_state
    )[0]

    print("\nНовий стан гри:")
    print(new_state)

    print(
        "\nПрогнозована дія:",
        predicted_action,
    )


def save_model(model):
    """Зберігає модель, список ознак і кодування напрямків."""

    model_data = {
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "direction_map": DIRECTION_MAP,
    }

    joblib.dump(
        model_data,
        MODEL_FILE,
    )

    print(
        "\nМодель збережено у файл:",
        MODEL_FILE,
    )


def main():
    df = load_data()

    X, y = prepare_data(df)

    (
        X_train,
        X_test,
        y_train,
        y_test,
    ) = split_data(X, y)

    model = train_model(
        X_train,
        y_train,
    )

    evaluate_model(
        model,
        X_train,
        X_test,
        y_train,
        y_test,
    )

    test_new_state(model)

    save_model(model)

main()