# Store — Week 1 · Lecture 2 demo

Every concept from Lecture 2, in one small program that runs.

The Lecture 1 demo showed students a backend they couldn't read yet. This one is the opposite: **there is nothing in here they haven't been taught today.** No FastAPI, no database, no type hints, no external packages — just classes and functions. If a student can follow this file-by-file, they have the lecture.

---

## Running it

```bash
cd sample-project
python main.py
```

No venv needed, no `pip install` — standard library only. Run it from *this* folder, or the `from store...` imports won't resolve.

`main.py` prints the whole lecture in order, section by section, with the slide numbers as headers. Running it front-to-back takes about two seconds and is a legitimate way to close the session.

---

## The layout

```
sample-project/
├── main.py              <- runs every section in order and narrates it
└── store/               <- a PACKAGE (the shape from Lecture 1, section 4.3)
    ├── __init__.py
    ├── products.py      <- classes, class attributes, inheritance, polymorphism
    ├── people.py        <- encapsulation, @property, dunders
    ├── orders.py        <- composition, __len__, __str__
    └── reports.py       <- lambdas, map/filter, comprehensions, dispatch table
```

Four modules in one package — deliberately the same structure students built by hand in Lecture 1's Exercise 2, so the packaging is familiar and only the *contents* are new.

---

## Where each concept lives

| Section | Concept | Where to look |
|---------|---------|---------------|
| 2.2 | `__init__`, instance attributes | `products.py` — `Product.__init__` |
| 2.3 | Methods and `self` | `people.py` — `User.greet` |
| 2.4 | Class vs. instance attributes | `products.py` — `tax_rate`, `product_count` |
| 2.4 | The mutable-class-attribute bug | `orders.py` — the comment on `self.products = []` |
| 2.4 | Public / `_protected` / `__private` | `people.py` — `User.__init__`, all three in a row |
| 2.5 | Encapsulation, validation on the way in | `people.py` — `set_password` |
| 2.5 | `@property` and its setter | `people.py` — `User.email` |
| 3.1 | Inheritance and `super()` | `products.py` — `DigitalProduct`, `PhysicalProduct` |
| 3.1 | A multi-level chain | `products.py` — `Product → PhysicalProduct → PerishableProduct` |
| 3.2 | Overriding and polymorphism | `orders.py` — `Order.shipping` |
| 3.3 | Composition (has-a) | `orders.py` — `Order.__init__` |
| 3.4 | `__str__`, `__eq__`, `__len__` | `products.py`, `people.py`, `orders.py` |
| 4.1 | Functions as values | `reports.py` — `apply_twice` |
| 4.1 | Dispatch table | `reports.py` — `REPORTS` and `run_report` |
| 4.2 | `lambda` as a sort key | `reports.py` — `by_price_then_name` |
| 4.3 | `map()` and `filter()` | `reports.py` — `affordable_names_functional` |
| 4.4 | The same logic as a comprehension | `reports.py` — `affordable_names` |
| 4.4 | Dict comprehension lookup table | `reports.py` — `index_by_name` |

---

## The four moments worth stopping on

**1. The polymorphism line.** `orders.py`:

```python
return sum(p.shipping_cost() for p in self.products)
```

One line that never asks what kind of product it's holding. A digital download answers `0.00`, a keyboard answers `2.25`, refrigerated coffee answers `6.50`. Add a fifth product type tomorrow and this line does not change. That is the entire payoff of section 3.2, and it's more convincing here than in the animal-noises example because something real depends on the answer.

**2. The inheritance chain building itself up.** Run the 3.1 section and look at the last label:

```
Coffee Beans ($12.50) [1.0kg] [keep cold, best before 2026-12-01]
```

Three classes each contributed one piece of that string through `super().label()` — exactly the `Vehicle → Car → ElectricCar` pattern from slide 28, but now the students can see each layer's contribution separately.

**3. The setter refusing bad data.** The 2.5 section prints a rejected email and a rejected password. `amina.email = "not-an-email"` *looks* like a plain assignment and raises a `ValueError` instead. Worth saying out loud: **this is the mental model for Pydantic**, which is the first thing they meet next week.

**4. Same answer, two styles.** The 4.3/4.4 section runs the `filter`-then-`map` version and the comprehension version and prints `True` for their equality. Then it prints that the input list is unchanged. Both points in four lines.

---

## Teaching notes

**Where this fits.** It is not meant to be typed out in class — it's a read-along and a take-home. Two good placements:

1. **After Exercise 1 (~2:18)**, as the answer to "what is this for?" Show `products.py` and `orders.py` only. Students have just written `Dog`/`Cat`; this is the same shape doing something a business would pay for.
2. **In the recap (~3:27)**, run `main.py` top to bottom. Each section header is a learning objective, in order. It's a faster recap than reading the objectives slide, and students see their own two exercises reflected back inside a bigger program.

Placement 2 is the stronger one if you only do it once.

**Two questions this will provoke:**

- *"Why is `Order` not a subclass of `Customer`?"* — Best possible question. An order **has** a customer; it **is not** one. Say the "is-a" sentence out loud and hear how wrong it sounds. This is section 3.3 landing.
- *"Why does `Product.__eq__` ignore the price?"* — Because *we* decided "same name means same product." `__eq__` is a definition you author, not a fact Python hands you. There's no universally right answer, which is exactly the point.

**One thing to be ready for if a student experiments.** Defining `__eq__` without `__hash__` makes the class unhashable, so `set(catalogue)` raises `TypeError: unhashable type`. That's Python protecting a real invariant, not a bug in this code, but it isn't on any slide — if it comes up, name `__hash__`, say it pairs with `__eq__`, and move on.

**If you are short on time,** show only `products.py` and the 3.1/3.2 output. Inheritance and polymorphism are the concepts students find hardest and the ones the Week 2 FastAPI material leans on most.
