"""What the store sells.

Covers:  2.2 Defining a Class  ·  2.4 Instance vs. Class Attributes
         3.1 Inheritance  ·  3.2 Overriding & Polymorphism  ·  3.4 Dunder Methods
"""


class Product:
    """The blueprint every product is built from."""

    # --- Class attributes (2.4) ---------------------------------------
    # ONE value, shared by every Product that will ever exist.
    tax_rate = 0.08
    product_count = 0

    def __init__(self, name, price):
        # --- Instance attributes (2.2) --------------------------------
        # Each Product gets its OWN copy of these.
        self.name = name
        self.price = price

        # Bump the counter on the CLASS, not on self.
        # `self.product_count += 1` would quietly create an instance
        # attribute and leave the shared one untouched.
        Product.product_count += 1

    def price_with_tax(self):
        """Every product shares tax_rate, but each uses its own price."""
        return self.price * (1 + Product.tax_rate)

    def shipping_cost(self):
        """Subclasses override this. Nothing to ship by default."""
        return 0.0

    def label(self):
        """Subclasses add their own detail on top of this."""
        return f"{self.name} (${self.price:.2f})"

    # --- Dunder methods (3.4) -----------------------------------------
    def __str__(self):
        # type(self).__name__ is how this base class knows which subclass
        # it actually is -- the same trick as Exercise 1's __str__.
        return f"{type(self).__name__}: {self.label()}"

    def __eq__(self, other):
        """Two products are 'the same product' when they share a name."""
        return self.name == other.name


class DigitalProduct(Product):
    """An e-book or a licence key -- there is nothing to put in a box."""

    def __init__(self, name, price, download_url):
        super().__init__(name, price)      # reuse Product's setup (3.1)
        self.download_url = download_url

    def label(self):
        return f"{super().label()} [instant download]"


class PhysicalProduct(Product):
    """Anything that ships. Overrides shipping_cost (3.2)."""

    shipping_rate_per_kg = 2.50            # a class attribute on the SUBCLASS

    def __init__(self, name, price, weight_kg):
        super().__init__(name, price)
        self.weight_kg = weight_kg

    def shipping_cost(self):
        return self.weight_kg * PhysicalProduct.shipping_rate_per_kg

    def label(self):
        return f"{super().label()} [{self.weight_kg}kg]"


class PerishableProduct(PhysicalProduct):
    """Third link in the chain:  Product -> PhysicalProduct -> PerishableProduct.

    Same shape as the Vehicle -> Car -> ElectricCar example in 3.1: each level
    calls super() and adds its own piece on top.
    """

    cold_chain_fee = 4.00

    def __init__(self, name, price, weight_kg, best_before):
        super().__init__(name, price, weight_kg)
        self.best_before = best_before

    def shipping_cost(self):
        return super().shipping_cost() + PerishableProduct.cold_chain_fee

    def label(self):
        return f"{super().label()} [keep cold, best before {self.best_before}]"
