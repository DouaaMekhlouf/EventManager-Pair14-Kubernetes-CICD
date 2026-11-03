from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Event
from ..schemas import Event as EventSchema
from ..schemas import EventCreate, EventUpdate


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_filter_events_by_location__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_filter_events_by_location__mutmut)
def filter_events_by_location(events, location: str):
    """Case-insensitive match on the event location."""
    return [e for e in events if location.lower() in e.location.lower()]


def x_filter_events_by_location__mutmut_orig(events, location: str):
    """Case-insensitive match on the event location."""
    return [e for e in events if location.lower() in e.location.lower()]


def x_filter_events_by_location__mutmut_1(events, location: str):
    """Case-insensitive match on the event location."""
    return [e for e in events if location.upper() in e.location.lower()]


def x_filter_events_by_location__mutmut_2(events, location: str):
    """Case-insensitive match on the event location."""
    return [e for e in events if location.lower() not in e.location.lower()]


def x_filter_events_by_location__mutmut_3(events, location: str):
    """Case-insensitive match on the event location."""
    return [e for e in events if location.lower() in e.location.upper()]

mutants_x_filter_events_by_location__mutmut['_mutmut_orig'] = x_filter_events_by_location__mutmut_orig # type: ignore # mutmut generated
mutants_x_filter_events_by_location__mutmut['x_filter_events_by_location__mutmut_1'] = x_filter_events_by_location__mutmut_1 # type: ignore # mutmut generated
mutants_x_filter_events_by_location__mutmut['x_filter_events_by_location__mutmut_2'] = x_filter_events_by_location__mutmut_2 # type: ignore # mutmut generated
mutants_x_filter_events_by_location__mutmut['x_filter_events_by_location__mutmut_3'] = x_filter_events_by_location__mutmut_3 # type: ignore # mutmut generated
mutants_x_filter_events_by_title__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_filter_events_by_title__mutmut)
def filter_events_by_title(events, title: str):
    """Case-insensitive match on the event title."""
    return [e for e in events if title.lower() in e.title.lower()]


def x_filter_events_by_title__mutmut_orig(events, title: str):
    """Case-insensitive match on the event title."""
    return [e for e in events if title.lower() in e.title.lower()]


def x_filter_events_by_title__mutmut_1(events, title: str):
    """Case-insensitive match on the event title."""
    return [e for e in events if title.upper() in e.title.lower()]


def x_filter_events_by_title__mutmut_2(events, title: str):
    """Case-insensitive match on the event title."""
    return [e for e in events if title.lower() not in e.title.lower()]


def x_filter_events_by_title__mutmut_3(events, title: str):
    """Case-insensitive match on the event title."""
    return [e for e in events if title.lower() in e.title.upper()]

mutants_x_filter_events_by_title__mutmut['_mutmut_orig'] = x_filter_events_by_title__mutmut_orig # type: ignore # mutmut generated
mutants_x_filter_events_by_title__mutmut['x_filter_events_by_title__mutmut_1'] = x_filter_events_by_title__mutmut_1 # type: ignore # mutmut generated
mutants_x_filter_events_by_title__mutmut['x_filter_events_by_title__mutmut_2'] = x_filter_events_by_title__mutmut_2 # type: ignore # mutmut generated
mutants_x_filter_events_by_title__mutmut['x_filter_events_by_title__mutmut_3'] = x_filter_events_by_title__mutmut_3 # type: ignore # mutmut generated


router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.post(
    "/",
    response_model=EventSchema,
    status_code=status.HTTP_201_CREATED
)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    if event.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Event date cannot be in the past."
        )

    db_event = Event()
    for key, value in event.model_dump().items():
        setattr(db_event, key, value)

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return db_event


@router.get(
    "/",
    response_model=list[EventSchema]
)
def list_events(
    search: str | None = Query(default=None),
    location: str | None = Query(default=None),
    title: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Event)

    # Preserve the existing search parameter
    if search:
        query = query.filter(
            Event.title.ilike(f"%{search}%")
        )

    events = query.order_by(Event.date).all()

    if location:
        events = filter_events_by_location(events, location)

    if title:
        events = filter_events_by_title(events, title)

    return events


@router.get(
    "/{event_id}",
    response_model=EventSchema
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    return event


@router.put(
    "/{event_id}",
    response_model=EventSchema
)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    if event_data.date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Event date cannot be in the past."
        )

    for key, value in event_data.model_dump().items():
        setattr(event, key, value)

    db.commit()
    db.refresh(event)

    return event


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    db.delete(event)
    db.commit()