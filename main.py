from my_calendar import myCalendar
import utils
import sys
import copy
import datetime

def main(): 
    user_input = sys.argv[1]
    user_schedule = user_input.split(',')
    if len(user_schedule) < 7:
        print("Enter a 7 day schedule.")
        exit()

    # user_schedule = ['α', 'α', 'ε', 'β', 'α', 'ρ', 'ρ']
    if datetime.datetime.now().weekday() == 6: 
        week = "next" 
    else: 
        week = "this"
    
    calendar = myCalendar()
    # Check if the events already exist
    if calendar.check_events_exist(week):
        print("Scheduled events already exist for this week.")
        exit()

    week_events = []

    for shift_type, day in zip(user_schedule, utils.days.keys()):
        
        if shift_type.lower() == 'ρ':
            continue

        # create starting reminder
        starting_event = copy.deepcopy(utils.basic_event)
        starting_time = utils.shifts[shift_type.lower()]["start"]

        starting_event["start"]["dateTime"] = utils.get_datetime_for_weekday(day, starting_time-1, 55, week) # 5 minutes earlier
        starting_event["end"]["dateTime"] = utils.get_datetime_for_weekday(day, starting_time-1, 56, week)
        starting_event["description"] = "Προσέλευση"

        # create ending reminder
        end_event = copy.deepcopy(utils.basic_event)
        end_time = utils.shifts[shift_type.lower()]["end"]
        
        if end_time > starting_time:
            end_event["start"]["dateTime"] = utils.get_datetime_for_weekday(day, end_time, 5, week) # 5 minutes later
            end_event["end"]["dateTime"] = utils.get_datetime_for_weekday(day, end_time, 6, week)
        else:
            end_event["start"]["dateTime"] = utils.get_datetime_for_weekday(utils.get_next_day(day), end_time, 5, week) # 5 minutes later
            end_event["end"]["dateTime"] = utils.get_datetime_for_weekday(utils.get_next_day(day), end_time, 6, week)
        end_event["description"] = "Αποχώρηση"
        
        week_events.extend([starting_event, end_event])

    for ev in week_events:
        calendar.create_event(ev)
    

if __name__ == "__main__":
    main()