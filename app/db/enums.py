import enum

class MeetingStatus(str, enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    declined = 'declined'
    archived = 'archived'

class Office(str, enum.Enum):
    all_ = 'Все офисы'
    office1 = 'Офис 1'
    office2 = 'Офис 2'
    office3 = 'Офис 3'
