"""The functional half of the lecture, applied to the store.

Covers:  4.1 First-Class Functions  ·  4.2 Lambdas
         4.3 map() and filter()  ·  4.4 Comprehensions

Every function here leaves its input untouched and returns something new --
the "don't mutate the input" habit from 4.3.
"""


# --- 4.1 Functions are just values ------------------------------------

def add_tax(price):
    return round(price * 1.08, 2)


def apply_twice(func, value):
    """Takes a FUNCTION as an argument -- only possible because
    functions are first-class citizens."""
    return func(func(value))


# --- 4.1 A dispatch table: a dict whose values are functions ----------
# This is a hand-rolled version of what FastAPI does internally when it
# maps @app.get("/path") to the function underneath it.

def total_revenue(orders):
    return round(sum(order.total() for order in orders), 2)


def item_count(orders):
    # len(order) works because Order defines __len__ (3.4).
    return sum(len(order) for order in orders)


def customer_names(orders):
    return [order.customer.name for order in orders]


REPORTS = {
    "revenue": total_revenue,
    "items": item_count,
    "customers": customer_names,
}


def run_report(name, orders):
    if name not in REPORTS:
        raise ValueError(f"Unknown report: {name}")
    return REPORTS[name](orders)      # look the function up, then call it


# --- 4.3 filter() then map() ------------------------------------------

def affordable_names_functional(products, limit):
    """The classic filter-then-map pipeline: narrow down, then reshape."""
    affordable = filter(lambda p: p.price < limit, products)
    return list(map(lambda p: p.name, affordable))


# --- 4.4 ...and the same thing as a comprehension ---------------------

def affordable_names(products, limit):
    """Identical result, and what most Python developers write."""
    return [p.name for p in products if p.price < limit]


def labels(products):
    """Polymorphism inside a comprehension -- each product labels itself."""
    return [p.label() for p in products]


# --- 4.2 sorted() with a lambda key -----------------------------------

def by_price_then_name(products):
    """Most expensive first, ties broken alphabetically.

    Negating the price flips that one field to descending without
    reversing the whole sort.
    """
    return sorted(products, key=lambda p: (-p.price, p.name))


# --- 4.4 A dict comprehension as a lookup table -----------------------

def index_by_name(products):
    """Turn a list into a dict keyed by name, so lookups are instant
    instead of scanning the whole list every time."""
    return {p.name: p for p in products}
