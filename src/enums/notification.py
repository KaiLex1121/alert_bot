import enum


# Определяем Enum для типов частоты
class FrequencyType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly" # Осторожно с месяцами разной длины
    YEARLY = "yearly"
    CUSTOM = "custom"
