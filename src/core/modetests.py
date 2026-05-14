import json
from pathlib import Path
from functools import lru_cache

import pandas as pd


MODE_PROFILES = {
    "test": [
        {
            "label": "Cauã Nogueira",
            "username_original": "user6442803380426375169",
            "metodo": 1,
            "value": "user6442803380426375169_m1",
        },
        {
            "label": "Marcos Vinícius",
            "username_original": "user2959087468848087041",
            "metodo": 1,
            "value": "user2959087468848087041_m1",
        },
        {
            "label": "Isadora Machado",
            "username_original": "user6442803380426375169",
            "metodo": 2,
            "value": "user6442803380426375169_m2",
        },
        {
            "label": "Mirella Peixoto",
            "username_original": "user2959087468848087041",
            "metodo": 2,
            "value": "user2959087468848087041_m2",
        },
    ],

    "train": [
        {
            "label": "Juliana Meireles",
            "username_original": "user1002410981378228225",
            "metodo": 1,
            "value": "user1002410981378228225_m1",
        },
        {
            "label": "Beatriz Lemos",
            "username_original": "user4549114572627247105",
            "metodo": 1,
            "value": "user4549114572627247105_m1",
        },
        {
            "label": "Camila Viana",
            "username_original": "user1002410981378228225",
            "metodo": 2,
            "value": "user1002410981378228225_m2",
        },
        {
            "label": "Breno Assunção",
            "username_original": "user4549114572627247105",
            "metodo": 2,
            "value": "user4549114572627247105_m2",
        },
    ],
}


SPECIAL_MODES = set(MODE_PROFILES.keys())


MODE_USER_OPTIONS = {
    mode: [
        {
            "label": profile["label"],
            "value": profile["value"],
        }
        for profile in profiles
    ]
    for mode, profiles in MODE_PROFILES.items()
}


MODE_LABEL_BY_VALUE = {
    mode: {
        profile["value"]: profile["label"]
        for profile in profiles
    }
    for mode, profiles in MODE_PROFILES.items()
}


TEST_PROFILES = MODE_PROFILES["test"]
TEST_USER_OPTIONS = MODE_USER_OPTIONS["test"]
TEST_LABEL_BY_VALUE = MODE_LABEL_BY_VALUE["test"]

TRAIN_PROFILES = MODE_PROFILES["train"]
TRAIN_USER_OPTIONS = MODE_USER_OPTIONS["train"]
TRAIN_LABEL_BY_VALUE = MODE_LABEL_BY_VALUE["train"]


def get_mode_options(mode):
    return MODE_USER_OPTIONS.get(mode, [])


def get_label_by_value(mode):
    return MODE_LABEL_BY_VALUE.get(mode, {})


def _get_json_path(course_id, method_number):
    filename = f"metodo{method_number}-curso{course_id}.json"
    return Path(__file__).resolve().parents[2] / "data" / filename


@lru_cache(maxsize=10)
def _load_only_mode_users(mode, course_id, method_number):
    path = _get_json_path(course_id, method_number)

    if not path.exists():
        print(f"Arquivo não encontrado: {path}")
        return pd.DataFrame()

    profiles_this_method = {
        profile["username_original"]: profile
        for profile in MODE_PROFILES.get(mode, [])
        if profile["metodo"] == method_number
    }

    rows = []

    with open(path, "r", encoding="utf-8") as file:
        course = json.load(file)

    course_id_real = course.get("courseid")

    for user in course.get("users", []):
        username_original = str(user.get("username"))

        if username_original not in profiles_this_method:
            continue

        profile = profiles_this_method[username_original]

        for session in user.get("user_sessions", []):
            sessao_id = session.get("sessao_id")

            for event in session.get("events", []):
                rows.append(
                    {
                        "courseid": course_id_real,
                        "username": profile["value"],
                        "username_original": username_original,
                        "display_name": profile["label"],
                        "metodo": method_number,
                        "sessao_id": sessao_id,
                        "eventname": event.get("eventname"),
                        "class": event.get("class"),
                        "timecreated": event.get("timecreated"),
                        "datetime": event.get("timecreated"),
                    }
                )

    df = pd.DataFrame(rows)

    if not df.empty:
        df["datetime"] = (
            pd.to_datetime(df["datetime"], unit="s", utc=True, errors="coerce")
            .dt.tz_convert("America/Recife")
            .dt.tz_localize(None)
        )

    return df


@lru_cache(maxsize=10)
def get_special_mode_data(mode, course_id=10464):
    frames = []

    for method_number in [1, 2]:
        df = _load_only_mode_users(mode, course_id, method_number)

        if not df.empty:
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


@lru_cache(maxsize=10)
def get_special_mode_sessions(mode, course_id=10464):
    df = get_special_mode_data(mode, course_id)

    if df.empty:
        return pd.DataFrame()

    sessions = (
        df.groupby(
            ["username", "display_name", "metodo", "sessao_id"],
            as_index=False,
        )
        .agg(
            inicio=("datetime", "min"),
            fim=("datetime", "max"),
            eventos=("datetime", "count"),
        )
    )

    sessions["session_id"] = sessions["sessao_id"]

    return sessions


def get_test_mode_data(course_id=10464):
    return get_special_mode_data("test", course_id)


def get_test_sessions(course_id=10464):
    return get_special_mode_sessions("test", course_id)


def get_train_mode_data(course_id=10464):
    return get_special_mode_data("train", course_id)


def get_train_sessions(course_id=10464):
    return get_special_mode_sessions("train", course_id)