# Order Management System (OMS)

---

## 1. Границы домена (что мы моделируем)

**Домен:** управление заказами в e-commerce / B2B-системе.  
**Что НЕ делаем:** платежи, доставка, UI — это вне scope и подходит для учебного проекта.

---

## 2. Ubiquitous Language (единый язык)

Это критично для DDD. Термины должны быть стабильны и использоваться в коде:

- **Order** — заказ клиента  
- **OrderItem** — позиция заказа  
- **Customer** — клиент, оформляющий заказ  
- **Product** — товар с ценой  
- **OrderStatus** — состояние заказа (`Draft`, `Confirmed`, `Cancelled`, `Shipped`)  
- **DiscountPolicy** — правило расчёта скидки  

---

## 3. Агрегаты и их роли

### 3.1. Order — главный агрегат

**Aggregate Root:** `Order`

**Внутри агрегата:**

- `OrderItem` — Value Object  
- `OrderStatus` — Value Object / Enum  

**Инварианты (важно для собеседования):**

- Нельзя добавить товар в подтверждённый заказ  
- Количество товара > 0  
- Цена фиксируется на момент добавления в заказ  
- Скидка применяется только при определённых условиях  

---

### 3.2. Customer — отдельный агрегат

**Aggregate Root:** `Customer`

- Имеет собственную идентичность  
- Не встраивается внутрь `Order` (только `customer_id`)  
- Может иметь тип (`Regular`, `Premium`)  

**Почему так:**  
Агрегаты не должны ссылаться друг на друга напрямую, только по ID.

---

### 3.3. Product — отдельный агрегат

**Aggregate Root:** `Product`

- `product_id`  
- `price`  
- `is_active`  

**Важно:**  
Product не загружается целиком в Order — в заказ копируется только `id` и `price`.

---

## 4. Бизнес-логика (что обязательно должно быть)

**Order:**

- `create(customer_id)`  
- `add_item(product_id, quantity, price)`  
- `remove_item(product_id)`  
- `calculate_total()`  
- `apply_discount(discount_policy)`  
- `confirm()`  
- `cancel()`  

> Вся эта логика находится внутри агрегата, а не в сервисах.