"""Who buys things.

Covers:  2.3 Methods and self  ·  2.4 Class Attributes
         2.5 Encapsulation and @property  ·  3.1 Inheritance  ·  3.4 Dunders
"""


class User:
    user_count = 0                      # class attribute (2.4)

    def __init__(self, name, email):
        # --- The three visibility levels (2.4 / 2.5) ------------------
        self.name = name                # public    -- anyone may touch it
        self._email = email             # protected -- reached via the property
        self.__password = None          # private   -- name-mangled
        User.user_count += 1

    # --- @property: read like an attribute, runs like a method (2.5) ---
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        # This is the whole point of encapsulation: a plain attribute
        # cannot check anything before the value sticks.
        if "@" not in new_email:
            raise ValueError("Invalid email address")
        self._email = new_email

    def set_password(self, raw_password):
        """Controlling the door -- validate before storing."""
        if len(raw_password) < 8:
            raise ValueError("Password must be at least 8 characters")
        self.__password = raw_password

    def has_password(self):
        return self.__password is not None

    def discount_rate(self):
        """Subclasses override this. No discount by default."""
        return 0.0

    def greet(self):
        """A method that reads its own instance's data (2.3)."""
        return f"Hello, {self.name}!"

    # --- Dunder methods (3.4) -----------------------------------------
    def __str__(self):
        return f"{type(self).__name__}({self.name})"

    def __eq__(self, other):
        """Same person = same email, even if the display name differs."""
        return self.email == other.email


class Customer(User):
    """A regular shopper. Earns a discount once they are loyal enough."""

    def __init__(self, name, email, loyalty_points=0):
        super().__init__(name, email)
        self.loyalty_points = loyalty_points

    def discount_rate(self):
        return 0.05 if self.loyalty_points >= 100 else 0.0


class StaffUser(User):
    """Works here. Always gets the staff discount."""

    staff_discount = 0.25

    def discount_rate(self):
        return StaffUser.staff_discount
