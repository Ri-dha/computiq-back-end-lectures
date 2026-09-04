"""Putting a customer and some products together.

Covers:  2.4 the mutable-class-attribute gotcha  ·  3.2 Polymorphism in use
         3.3 Composition  ·  3.4 Dunder Methods
"""


class Order:
    order_count = 0

    def __init__(self, customer):
        # --- Composition (3.3) ----------------------------------------
        # An Order HAS-A customer and HAS-MANY products. An Order is not
        # a Customer and is not a Product, so inheritance would be wrong.
        self.customer = customer

        # Built fresh inside __init__ on purpose. A class attribute
        # `products = []` would be shared by every Order ever made -- the
        # exact bug from the 2.4 gotcha slide.
        self.products = []

        Order.order_count += 1
        self.id = Order.order_count

    def add_product(self, product):
        self.products.append(product)

    def subtotal(self):
        return sum(p.price for p in self.products)

    def shipping(self):
        # --- Polymorphism (3.2) ---------------------------------------
        # This line never asks what KIND of product it is holding.
        # Each product knows its own shipping cost, and answers for itself.
        return sum(p.shipping_cost() for p in self.products)

    def total(self):
        taxed = sum(p.price_with_tax() for p in self.products)
        # The customer answers for their own discount -- polymorphism again.
        discount = taxed * self.customer.discount_rate()
        return taxed - discount + self.shipping()

    # --- Dunder methods (3.4) -----------------------------------------
    def __len__(self):
        """Makes the built-in len(order) work on our own class."""
        return len(self.products)

    def __str__(self):
        return (
            f"Order #{self.id} for {self.customer.name} "
            f"-- {len(self)} items, ${self.total():.2f}"
        )
