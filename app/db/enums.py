import enum

class MeetingStatus(str, enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    declined = 'declined'
    archived = 'archived'
