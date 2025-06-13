import datetime
import pytz

EVENT_TITLE = "Χτύπα κάρτα Πρόεδρε!"

BASIC_EVENT = {
    "summary": EVENT_TITLE,
    "location": "",
    "description": "",
    "start": {
        "dateTime": "",  # Format: YYYY-MM-DDTHH:MM:SS
        "timeZone": "Europe/Athens",
    },
    "end": {
        "dateTime": "",
        "timeZone": "Europe/Athens",
    },
    "attendees": [],
    "reminders": {
        "useDefault": False,
        "overrides": [
            {"method": "popup", "minutes": 0},  # 0 mins before
        ],
    },
    'colorId': '1',  # Red
}

SHIFTS = {
    "π": {"start": 5, "end": 14},
    "ε": {"start": 7, "end": 16},
    "α": {"start": 14, "end": 22},
    "β": {"start": 17, "end": 1},
    "π1": {"start": 6, "end": 14},
    "ε1": {"start": 9, "end": 18},
    "ε2": {"start": 7, "end": 11},
    "ε3": {"start": 11, "end": 19},
}

DAYS = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
        }

def get_next_day(day):
    if day == "monday": return "tuesday"
    if day == "tuesday": return "wednesday"
    if day == "wednesday": return "thursday"
    if day == "thursday": return "friday"
    if day == "friday": return "saturday"
    if day == "saturday": return "sunday"
    if day == "sunday": return "monday"

def get_datetime_for_weekday(day_name, hour, minute, week='this', tz_name='Europe/Athens'):

    day_name = day_name.lower()
    if day_name not in DAYS:
        raise ValueError("Invalid day name")

    today = datetime.datetime.now()
    current_weekday = today.weekday()

    # Find the Monday of this week
    start_of_week = today - datetime.timedelta(days=current_weekday)
    if week == 'next':
        start_of_week += datetime.timedelta(weeks=1)
    elif week != 'this':
        raise ValueError("Week must be 'this' or 'next'")

    target_weekday = DAYS[day_name]
    target_date = start_of_week + datetime.timedelta(days=target_weekday)

    # Create the datetime at 2 AM
    target_datetime = datetime.datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=hour,
        minute=minute
    )

    # Localize to timezone
    tz = pytz.timezone(tz_name)
    localized_datetime = tz.localize(target_datetime)

    return localized_datetime.isoformat()