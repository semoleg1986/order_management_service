from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities.order import Order, OrderStatus
from src.domain.value_object.order_item import OrderItem

# --- Фикстуры ---


@pytest.fixture
def product_id():
    """Генерация случайного ID продукта для тестов."""
    return uuid4()


@pytest.fixture
def empty_order():
    """Создание пустого заказа в статусе NEW."""
    return Order()


@pytest.fixture
def order_with_item(product_id):
    """Создание заказа с одной добавленной позицией."""
    order = Order()
    order.add_item(product_id=product_id, quantity=1, price="100.00")
    return order


# --- Группа 1: Создание и инициализация ---


def test_create_order(empty_order):
    """Проверка корректности инициализации нового заказа по умолчанию."""
    assert empty_order.status == OrderStatus.NEW
    assert empty_order.items == ()
    assert empty_order._version == 1


def test_order_id_is_immutable(empty_order):
    """Проверка защиты идентификатора заказа от изменения."""
    with pytest.raises(AttributeError):
        empty_order.order_id = uuid4()


# --- Группа 2: Управление составом заказа ---


def test_add_item_to_order(empty_order, product_id):
    """Проверка успешного добавления нового товара в заказ."""
    order_item = empty_order.add_item(product_id=product_id, quantity=2, price="10.50")

    assert len(empty_order.items) == 1
    assert order_item.product_id == product_id
    assert order_item.quantity == 2
    assert order_item.price == Decimal("10.50")


def test_add_item_merge_same_product_and_price(empty_order, product_id):
    """
    Проверка автоматического слияния позиций
    при добавлении одинакового продукта с той же ценой.
    """
    empty_order.add_item(product_id=product_id, quantity=2, price="10.50")
    empty_order.add_item(product_id=product_id, quantity=3, price=Decimal("10.50"))

    assert len(empty_order.items) == 1
    assert empty_order.items[0].quantity == 5


# --- Группа 3: Жизненный цикл и статусы ---


def test_confirm_order(order_with_item):
    """Проверка перехода заказа в статус CONFIRMED и инкремента версии."""
    order_with_item.confirm()
    assert order_with_item.status == OrderStatus.CONFIRMED
    assert order_with_item._version == 3  # Init(1) + Add(1) + Confirm(1)


def test_confirm_order_with_prefilled_items():
    """
    Проверка подтверждения заказа,
    созданного со списком товаров через конструктор.
    """
    item = OrderItem(product_id=uuid4(), quantity=1, price="50.00")
    order = Order(items=[item])
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    assert order._version == 2


def test_cannot_confirm_empty_order(empty_order):
    """Проверка бизнес-правила: нельзя подтвердить заказ без товаров."""
    with pytest.raises(ValueError):
        empty_order.confirm()


def test_cannot_add_item_to_confirmed_order(order_with_item):
    """Проверка неизменяемости состава заказа после его подтверждения."""
    order_with_item.confirm()
    with pytest.raises(ValueError):
        order_with_item.add_item(uuid4(), 1, "5.00")


def test_cancel_order(empty_order):
    """Проверка возможности отмены нового заказа."""
    empty_order.cancel()
    assert empty_order.status == OrderStatus.CANCELLED
    assert empty_order._version == 2


def test_cannot_cancel_confirmed_order(order_with_item):
    """Проверка бизнес-правила: подтвержденный заказ нельзя отменить."""
    order_with_item.confirm()
    with pytest.raises(ValueError, match="cannot be cancelled"):
        order_with_item.cancel()


# --- Группа 4: Идентичность и Хеширование (Entity Behavior) ---


def test_orders_with_same_id_are_equal_despite_different_state():
    """
    Проверка реализации Entity: равенство объектов определяется по ID,
    а не по состоянию.
    """
    order_id = uuid4()
    o1 = Order(order_id=order_id)
    o2 = Order(order_id=order_id)

    o1.add_item(uuid4(), 1, "10.00")
    o1.confirm()

    assert o1 == o2
    assert hash(o1) == hash(o2)


def test_order_hash_is_stable_across_mutations(empty_order):
    """
    Проверка стабильности хеша при изменении состояния объекта
    (важно для hash-map коллекций).
    """
    h1 = hash(empty_order)
    empty_order.add_item(uuid4(), 1, "10.00")
    empty_order.confirm()

    assert hash(empty_order) == h1


def test_order_can_be_dict_key_after_mutation(empty_order):
    """
    Проверка возможности поиска объекта в
    словаре по ключу после изменения данных объекта.
    """
    data = {empty_order: "valid"}
    empty_order.add_item(uuid4(), 1, "10.00")
    empty_order.confirm()

    assert data[empty_order] == "valid"


# --- Группа 5: Расчет стоимости ---


def test_order_total_price_empty(empty_order):
    """Проверка, что общая стоимость пустого заказа равна нулю."""
    assert empty_order.total_price() == Decimal("0")


def test_order_total_price_single_item(empty_order):
    """Проверка расчета суммы для одной позиции с количеством больше единицы."""
    empty_order.add_item(product_id=uuid4(), quantity=3, price="150.50")
    # 3 * 150.50 = 451.50
    assert empty_order.total_price() == Decimal("451.50")


def test_order_total_price_multiple_items(empty_order):
    """Проверка суммирования стоимостей нескольких различных позиций в заказе."""
    empty_order.add_item(product_id=uuid4(), quantity=2, price="100.00")  # 200.00
    empty_order.add_item(product_id=uuid4(), quantity=1, price="50.25")  # 50.25
    empty_order.add_item(product_id=uuid4(), quantity=10, price="5.00")  # 50.00

    # Итого: 200.00 + 50.25 + 50.00 = 300.25
    assert empty_order.total_price() == Decimal("300.25")


def test_order_total_price_after_merge(empty_order, product_id):
    """Проверка корректности общей суммы после объединения товаров в одну позицию."""
    empty_order.add_item(product_id=product_id, quantity=1, price="100.00")
    empty_order.add_item(product_id=product_id, quantity=1, price="100.00")

    # Должно быть 2 * 100.00 = 200.00
    assert empty_order.total_price() == Decimal("200.00")
