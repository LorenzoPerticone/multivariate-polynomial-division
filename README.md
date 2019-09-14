# multivariate-polynomial-division
This short library provides multivariate polynomials with long division, based on the idea of fixing a Monomial Ordering 
when setting up the polynomial framework itself, and using a "Groebner-bases-like" argument for computing long divisions.

This library should be fairly easy to use, needing almost no "boilerplate code" for dealing with polinomials.
Here is a (very basic) example of usage of this library:

```python
from polynomials import Variable

x = Variable()
y = Variable()
p1 = 2*x*y + 7*y**2
p2 = y**2 * (x**2 + x + 1)

print(p1 + p2)
print(divmod(p2, p1))
```

It now supports evaluation, derivation and integration (both definite, a.k.a. in a product of intervals, and indefinite, a.k.a. formal)

Notice for the Algebraist/Algebraic Geometer: as you will have already figured out, fixing *one* monomial ordering *once and for all* does **not** work in general: the easiest example is trying to divide `x` by `y` (with a monomial ordering such that `x > y`).

The framework will, however, let you *change* the monomial ordering by manually changing the id of all variables in a suitable way. There is no *easy* way of doing it right now, but it should be quite easy to implement.
