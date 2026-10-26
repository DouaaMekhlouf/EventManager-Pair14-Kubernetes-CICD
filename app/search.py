def filter_events_by_location(events, location: str):
    return [e for e in events if location.lower() in e.location.lower()]


def filter_events_by_title(events, title: str):
    return [e for e in events if title.lower() in e.title.lower()]