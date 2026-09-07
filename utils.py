from datetime import datetime

DATETIME_TEMPLATE = "%d de %B de %Y às %H:%M"

format_datetime = lambda x: datetime.fromisoformat(x).strftime(DATETIME_TEMPLATE)
