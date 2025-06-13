from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from my_calendar import myCalendar  # Import your event-creation logic

app = FastAPI()
Calendar = myCalendar()

class EventRequest(BaseModel):
    week_schedule: str

@app.post("/create_event")
async def create_event_endpoint(req: EventRequest):
    try:
        event = Calendar.create_schedule(req.week_schedule)
        return {"status": "success", "event": event}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))