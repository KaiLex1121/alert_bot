import enum


# Определяем Enum для типов частоты
class FrequencyType(enum.Enum):
    DAILY = "ежедневно"
    WEEKLY = "еженедельно"
    MONTHLY = "ежемесячно"
    YEARLY = "ежегодно"
    OTHER = "другое"
