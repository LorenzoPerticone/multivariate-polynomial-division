# multivariate-polynomial-division
This short library provides multivariate polynomials with long division, based on the idea of fixing a Groebner basis 
when setting up the polynomial framework itself.

This library should be fairly easy to use, needing almost no "boilerplate code" for dealing with polinomials.
Here is a (very basic) example of usage of this library:

```python
from polynomials import Variable

x = Variable()
y = Variable
p1 = 2*x*y + 7*y**2
p2 = y**2 * (x**2 + x + 1)

print(p1 + p2)
print(divmod(p2, p1)
```

TODO: implement evaluation.
