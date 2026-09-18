"""Patent retrieval cutoff, independent of report filters and generation dates."""
from datetime import date


# Update only after a new patent retrieval has been completed and confirmed.
# Annotation corrections and website deployments do not change this date.
PATENT_DATA_CUTOFF = date(2026, 6, 1)
_ENGLISH_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
PATENT_DATA_CUTOFF_NOTE = (
    f"Patent data indexed through {PATENT_DATA_CUTOFF.day} "
    f"{_ENGLISH_MONTHS[PATENT_DATA_CUTOFF.month - 1]} {PATENT_DATA_CUTOFF.year}."
)
