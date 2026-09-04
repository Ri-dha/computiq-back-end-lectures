"""Run the whole lecture, in order:  python main.py

Each block below prints the section it comes from, so you can follow along
with the slides. Read the module it imports from to see how it works.
"""

from store.orders import Order
from store.people import Customer, StaffUser, User
from store.products import (
    DigitalProduct,
    PerishableProduct,
    PhysicalProduct,
    Product,
)
from store import reports


def section(number, title):
    print(f"\n{'=' * 62}\n{number}  {title}\n{'=' * 62}")


# ----------------------------------------------------------------------
section("2.2 / 2.3", "Defining a class, and methods that use self")

amina = Customer("Amina", "amina@example.com", loyalty_points=120)
karim = Customer("Karim", "karim@example.com")
print(amina.greet())                 # the method reads THIS instance's name
print(karim.greet())                 # ...and this one reads its own
print("Two independent objects:", amina.name, "and", karim.name)


# ----------------------------------------------------------------------
section("2.4", "Instance vs. class attributes")

print("amina.loyalty_points (instance, hers alone):", amina.loyalty_points)
print("User.user_count      (class, shared by all):", User.user_count)
print("Product.tax_rate     (shared config):       ", Product.tax_rate)


# ----------------------------------------------------------------------
section("2.5", "Encapsulation: the door is controlled")

print("Read through @property:", amina.email)
amina.email = "amina@newmail.com"          # runs the setter's validation
print("After a valid change: ", amina.email)

try:
    amina.email = "not-an-email"           # the setter refuses it
except ValueError as error:
    print("Rejected by the setter:", error)

try:
    amina.set_password("short")
except ValueError as error:
    print("Rejected by set_password:", error)

amina.set_password("a-long-enough-password")
print("Password accepted:", amina.has_password())
print("__password is name-mangled, so this is what it really is:",
      amina._User__password)


# ----------------------------------------------------------------------
section("3.1", "Inheritance -- each level adds one piece")

catalogue = [
    DigitalProduct("Python Course", 39.00, "https://example.com/dl/1"),
    PhysicalProduct("Keyboard", 45.00, weight_kg=0.9),
    PhysicalProduct("Mouse", 20.00, weight_kg=0.2),
    PerishableProduct("Coffee Beans", 12.50, weight_kg=1.0,
                      best_before="2026-12-01"),
]

for product in catalogue:
    print(" ", product.label())

print("\nThe chain that built the last one:")
print(" ", " -> ".join(c.__name__ for c in type(catalogue[-1]).__mro__[:-1]))


# ----------------------------------------------------------------------
section("3.2", "Polymorphism -- one loop, three different answers")

for product in catalogue:
    print(f"  {product.name:<15} ships for ${product.shipping_cost():.2f}")

print("\nThe loop never asks what kind of product it has.")


# ----------------------------------------------------------------------
section("3.3", "Composition -- an Order HAS a customer and HAS products")

order = Order(amina)
order.add_product(catalogue[1])       # Keyboard
order.add_product(catalogue[2])       # Mouse
order.add_product(catalogue[3])       # Coffee Beans

staff_order = Order(StaffUser("Lina", "lina@example.com"))
staff_order.add_product(catalogue[0])  # the digital course

print("Subtotal:      $", round(order.subtotal(), 2))
print("Shipping:      $", round(order.shipping(), 2))
print("Customer gets:  ", f"{amina.discount_rate():.0%} off (120 loyalty points)")
print("Total:         $", round(order.total(), 2))


# ----------------------------------------------------------------------
section("3.4", "Dunder methods -- __str__, __len__ and __eq__")

print("__str__ :", order)
print("__len__ :", len(order), "items in the order")

print("__eq__  :", Product("Mouse", 20.00) == Product("Mouse", 99.00),
      "(same name, so the same product -- price is irrelevant)")
print("        ", Customer("Amina K.", "amina@newmail.com") == amina,
      "(same email, so the same person -- display name is irrelevant)")


# ----------------------------------------------------------------------
section("4.1", "Functions are values you can pass around")

print("apply_twice(add_tax, 100.00) =", reports.apply_twice(reports.add_tax, 100.00))

orders = [order, staff_order]
print("\nA dispatch table -- look the function up by name, then call it:")
for report_name in reports.REPORTS:
    print(f"  run_report({report_name!r}) ->", reports.run_report(report_name, orders))


# ----------------------------------------------------------------------
section("4.3 / 4.4", "map + filter, and the same thing as a comprehension")

print("filter() then map():", reports.affordable_names_functional(catalogue, 40))
print("comprehension:      ", reports.affordable_names(catalogue, 40))
print("identical result:   ",
      reports.affordable_names_functional(catalogue, 40)
      == reports.affordable_names(catalogue, 40))

print("\nThe catalogue was not touched by either one:",
      len(catalogue), "products still there")


# ----------------------------------------------------------------------
section("4.2", "sorted() with a lambda key")

for product in reports.by_price_then_name(catalogue):
    print(f"  ${product.price:>6.2f}  {product.name}")


# ----------------------------------------------------------------------
section("4.4", "A dict comprehension as a lookup table")

lookup = reports.index_by_name(catalogue)
print("Keys:", list(lookup))
print("lookup['Keyboard'] ->", lookup["Keyboard"].label())
print("No loop needed to find it.")

print()
