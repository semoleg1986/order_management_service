class OrderError(Exception):
    """Базовое исключение для Order в Domain."""

    pass


class OrderValidationError(OrderError):
    """Ошибка при нарушении правил создания или обновления Order."""

    pass


class OrderAlreadyExistsError(OrderError):
    """Выбрасывается, если Order с таким именем уже существует."""

    pass


class OrderNotFoundError(OrderError):
    """Выбрасывается, если Order не найден."""

    pass


class UserNotChangedError(OrderError):
    """Выбрасывается, если не было изменено ни одно поле"""

    pass
