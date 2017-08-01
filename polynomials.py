#!/usr/bin/env python3

from functools import reduce

#The lambda expression checks if its argument
#has the desired type;
#
#Map applies a function to all elements of a list
#
#All is applied on a list of booleans: as long as
#it encounters a "False", it returns it; if
#no "False" is found, returns "True". Its dual is "any".
def isUniform(lst, typ):
    return all(map(lambda x: type(x) == typ, lst))

scalar = float

#if a class has a static dictionary of smaller types and
#cast functions, inheriting from this abstract mixin
#introduces a method that deduces casts for all smaller
#types.
class Deduce:
    #if the other has a smaller type, cast it
    def coerceOther(self, other):
        typ = type(other)
        if typ in self.smallerTypes:
            other = self.smallerTypes[typ](other)
        return other

#if a class has the static dictionary, a key method as described
#in the python sorting howto, and a coerce method for casting it
#to the immediately bigger type, we can deduce all rich comparisons
#operators, in a way that respects the hieracy of classes:
#if the other has the same class, compare the keys, if the other
#has smaller class, cast it. if classes are not comparable,
#coerce self and try again.
class DeduceOrder(Deduce):
    def __lt__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() < other.key()
        return self.coerce() < other

    def __gt__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() > other.key()
        return self.coerce() > other

    def __eq__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() == other.key()
        return self.coerce() == other

    def __le__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() <= other.key()
        return self.coerce() <= other

    def __ge__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() >= other.key()
        return self.coerce() >= other

    def __ne__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.key() != other.key()
        return self.coerce() != other

#if a class has the static dictionary, a coerce method and
#arithmetic operations for equal types ("add, sub, neg, mul"),
#we can deduce the extension of such operators to the hieracy
#of classes, in a way that is quite similar to DeduceOrder.
class DeduceOperations(Deduce):
    def __add__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.add(other)
        return self.coerce() + other

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.sub(other)
        return self.coerce() - other

    def __rsub__(self, other):
        return (self - other).neg()

    def __neg__(self):
        return self.neg()

    def __mul__(self, other):
        other = self.coerceOther(other)
        if type(other) == type(self):
            return self.mul(other)
        return self.coerce() * other

    def __rmul__(self, other):
        return self * other

    #because why not?
    def __pow__(self, other):
        if type(other) == int and other >= 0:
            res = 1
            for i in range(other):
                res = res * self
            return res
        raise ValueError('Unexpected non-integer power')

class Scalar(scalar, DeduceOrder, DeduceOperations):
    smallerTypes = {int: lambda x: Scalar(x),
                    float: lambda x: Scalar(x)}
    
    def __init__(self, other):
        self.finalize()
        try:
            #non vuole l'argomento, per motivi a me abbastanza oscuri...
            super(Scalar, self).__init__()
        except:
            raise ValueError('Conversion to {} failed'.format(scalar))

    @classmethod
    def finalize(cls):
        if Scalar not in cls.smallerTypes:
            cls.smallerTypes[Scalar] = Scalar

    def key(self):
        return self

    def coerce(self):
        return Monomial(self)

    def add(self, other):
        return Scalar(self + other)

    def sub(self, other):
        return Scalar(self - other)

    def neg(self):
        return Scalar(-self)

    def mul(self, other):
        return Scalar(self * other)

class Variable(DeduceOrder, DeduceOperations):
    smallerTypes = {}
    ids = []
    nextId = 0

    def __init__(self):
        self.finalize()
        self.id = self.newId()

    @classmethod
    def newId(cls):
        id = cls.nextId
        cls.ids.append(id)
        while cls.nextId in cls.ids:
            cls.nextId += 1
        return id

    def key(self):
        return self.id

    @classmethod
    def getInstances(cls):
        return cls.instances

    @classmethod
    def finalize(cls):
        if Variable not in cls.smallerTypes:
            cls.smallerTypes[Variable] = lambda x: x

    def coerce(self):
        return Monomial(1, self)

    def __repr__(self):
        return 'x_{}'.format(self.id)

    def add(self, other):
        return Monomial(1, self) + Monomial(1, other)

    def sub(self, other):
        return Monomial(1, self) - Monomial(1, other)

    def neg(self):
        return Monomial(-1, self)
    
    def mul(self, other):
        return Monomial(1, self, other)

    def eval(self, arguments):
        k = self.key()
        if k in arguments:
            return arguments[k]
        return self

class Monomial(DeduceOrder, DeduceOperations):
    smallerTypes = {int: lambda x: Monomial(x),
                    float: lambda x: Monomial(x),
                    Scalar: lambda x: Monomial(x),
                    Variable: lambda x: Monomial(1, x)}

    def __init__(self, coeff, *variables):
        self.finalize()
        self.coeff = Scalar(coeff)
        if self.coeff != 0:
            self.variables = sorted(list(variables), reverse = True)
            counts = {i: 0 for i in Variable.ids}
            for variable in variables:
                counts[variable.key()] += 1
            self.group = {i: counts[i]
                          for i in Variable.ids[::-1]}
            #self.group = [(i, counts[i])
            #              for i in Variable.ids[::-1]]
        else:
            self.variables = []
            self.group = {}

    @classmethod
    def finalize(cls):
        if Monomial not in cls.smallerTypes:
            cls.smallerTypes[Monomial] = lambda x: Monomial(x.coeff, *x.variables)

    def key(self):
        return [self.group[k] for k in self.group] + [self.coeff]

    def coerce(self):
        return Polynomial(self)

    def absRepr(self):
        coeff = self.coeff
        if coeff < 0:
            coeff = -coeff

        return repr(Monomial(coeff, *self.variables))

    def __repr__(self):
        if self.coeff == 0:
            return '0'
        elif self.coeff == 1:
            head = ''
        elif self.coeff == -1:
            head = '-'
        else:
            head = repr(self.coeff)

        useful = [(i, self.group[i])
                  for i in self.group
                  if self.group[i] != 0]
        tail = ' * '.join(map(lambda x: ('x_{}^{}'.format(x[0], x[1]) if x[1] > 1
                                         else 'x_{}'.format(x[0])),
                              useful))

        if tail == '':
            if head == '':
                return '1.0'
            return head
        if head == '':
            return tail
        return ' * '.join([head, tail])

    def add(self, other):
        if self.variables == other.variables:
            return Monomial(self.coeff + other.coeff,
                            *self.variables)
        return Polynomial(self, other)

    def sub(self, other):
        return self.add(other.neg())

    def neg(self):
        return Monomial(-self.coeff, *self.variables)

    def mul(self, other):
        return Monomial(self.coeff * other.coeff,
                        *(self.variables + other.variables))

    def eval(self, arguments):
        return reduce(lambda x, v: x * v.eval(arguments),
                      self.variables, self.coeff)

class Polynomial(DeduceOrder, DeduceOperations):
    smallerTypes = {int: lambda x: Polynomial(Monomial(x)),
                    float: lambda x: Polynomial(Monomial(x)),
                    Scalar: lambda x: Polynomial(Monomial(x)),
                    Variable: lambda x: Polynomial(Monomial(1, x)),
                    Monomial: lambda x: Polynomial(x)}
    
    def __init__(self, *monomials):
        self.finalize()
        tmpMonomials = []
        for monomial in sorted(monomials, reverse = True):
            #if this monomial differs by a scalar factor from any other
            #previously accepted monomial
            if any(map(lambda x: x.variables == monomial.variables, tmpMonomials)):
                #it is actually the last: substitute it with the sum.
                tmpMonomials[-1] = tmpMonomials[-1] + monomial
            else:
                tmpMonomials.append(monomial)

        self.monomials = []
        for monomial in tmpMonomials:
            if monomial != 0:
                self.monomials.append(monomial)
                

    @classmethod
    def finalize(cls):
        if Polynomial not in cls.smallerTypes:
            cls.smallerTypes[Polynomial] = lambda x: Polynomial(*x.monomials)

    def key(self):
        return [m.key() for m in self.monomials]

    def coerce(self):
        raise ValueError('Polynomials cannot be coerced')

    def __repr__(self):
        if self.monomials == []:
            return '0'
        m = self.monomials[0]
        ms = self.monomials[1:]
        res = repr(m)
        for m in ms:
            piece = m.absRepr()
            sep = ' + '
            if m.coeff < 0:
                sep = ' - '
            res = res + sep + piece
        return res

    def add(self, other):
        return Polynomial(*(self.monomials + other.monomials))

    def sub(self, other):
        return self + (- other)

    def neg(self):
        return Polynomial(*[-m for m in self.monomials])

    def mul(self, other):
        return Polynomial(*[m * n
                            for m in self.monomials
                            for n in other.monomials])

    def __divmod__(self, other):
        if type(other) == Variable:
            return divmod(self, Polynomial(Monomial(1, other)))
        if type(other) == Monomial:
            return divmod(self, Polynomial(other))
        return longDivision(self, other)

    def __floordiv__(self, other):
        return divmod(self, other)[0]

    def __mod__(self, other):
        return divmod(self, other)[1]

    def eval(self, arguments):
        return reduce(lambda x, m: x + m.eval(arguments),
                      self.monomials, 0)

    def __call__(self, *args):
        return self.eval({i: args[i] for i in range(len(args))})

    def derivative(self, *args):
        if not isUniform(args, Variable):
            raise ValueError('Can only derive by variables')
        res = self
        for var in args:
            res = derive(res, var)
        return res

    def integral(self, *args, formalIntegration = None):
        if isUniform(args, Variable) and (formalIntegration != False):
            res = self
            for var in args:
                res = formallyIntegrate(res, var)
            return res
        
        if isUniform(args, list) and (formalIntegration != True):
            res = self
            for i, interval in zip(Variable.ids, args):
                a, b = interval[0], interval[1]
                res = res.eval({i: b}) - res.eval({i: a})
            return res

        raise ValueError('Invalid parameters for integration')

#returns a list of the elements of lst1 that are not in lst2
#(counted with multiplicity: if lst1 = [2, 1, 1], lst2 = [1]
#then listDiff(lst1, lst2) = [2, 1]
#
#lists are assumed to be ordered decreasingly!
def listDiff(lst1, lst2):
    if lst1 == []:#trivial
        return []

    fst1, rest1 = lst1[0], lst1[1:]
    
    if lst2 == []:#trivial
        return lst1

    fst2, rest2 = lst2[0], lst2[1:]

    if fst1 == fst2:#lst1[0] appears in both: ignore
        return listDiff(rest1, rest2)

    if fst1 > fst2:#lst[1] does not appear in lst2: take it
        return [fst1] + listDiff(rest1, lst2)

    if fst1 < fst2:#lst[1] might appear later on in lst2
        return listDiff(lst1, rest2)

#short division is for monomials, and never returns
def shortDivision(dividend, divisor):
    if type(dividend) != Monomial:
        raise ValueError()
    if type(divisor) != Monomial:
        raise ValueError()
    
    if divisor > dividend:#should never ever happen!
        return Monomial(0)

    return Monomial(dividend.coeff / divisor.coeff,
                    *listDiff(dividend.variables,
                              divisor.variables))

#long division is for polynomials
def longDivision(dividend, divisor):
    quotient = 0

    leadDivisor = divisor.monomials[0]
    while dividend > divisor:
        leadDividend = dividend.monomials[0]
        partQuotient = shortDivision(leadDividend, leadDivisor)
        dividend -= partQuotient * divisor
        quotient += partQuotient

    return quotient, dividend

def deriveMonomial(monomial, variable):
    if variable not in monomial.variables:
        return Monomial(0)
    res = Monomial(monomial.coeff * monomial.group[variable.id],
                   *listDiff(monomial.variables, [variable]))
    return res
    

def derive(polynomial, variable):
    return Polynomial(*[deriveMonomial(monomial, variable)
                        for monomial in polynomial.monomials])

def formallyIntegrateMonomial(monomial, variable):
    if variable not in monomial.variables:
        return Monomial(monomial.coeff, variable,
                        *monomial.variables)
    return Monomial(monomial.coeff / (monomial.group[variable.id] + 1),
                    variable, *monomial.variables)

def formallyIntegrate(polynomial, variable):
    return Polynomial(*[formallyIntegrateMonomial(monomial, variable)
                        for monomial in polynomial.monomials])
    
if __name__ == '__main__': #some tests and use cases:
    x = Variable()
    y = Variable()
    z = Variable()
    m1 = x * 2 * y
    m2 = x**2 * (-3) * y
    print(m1)
    print(m2)
    m = m1 + m2
    print(m)
    p = m**2
    print(p)
    m, p = m + p, m * p
    print('m = {}'.format(m))
    print(p)
    q, r = divmod(p, m)
    print(q)
    print(r)
    print(m * q + r == p)
    q = p // m
    r = p % m
    print(q)
    print(r)
    print(m * q + r == p)

    print(m(1))
    print(m(1, 2))

    m = x**2 + x*y
    print(m)
    print(m.derivative(x))
    print(m.derivative(x, y))
    print(m.integral(x, y))
    print(m.integral([1, 2], [3, 4]))
