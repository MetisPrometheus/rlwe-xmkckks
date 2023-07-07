import numpy as np
from .Rq import Rq
from .utils import crange


class RLWE:
    def __init__(self, n, p, t, std):
        assert np.log2(n) == int(np.log2(n))
        self.n = n
        self.p = p
        self.t = t
        self.std = std
        #custom
        self.a = None
        self.b = None
        self.e = None
        self.s = None
        self.v = None


    def generate_vector_a(self):
        self.a = discrete_uniform(self.n, self.p)

    def set_vector_a(self, vector):
        self.a = vector

    def get_vector_a(self):
        return self.a
    
    def list_to_poly(self, list, mod="t"):
        if mod == "t":
            return Rq(list, self.t)
        if mod == "q":
            return Rq(list, self.p)

    def generate_keys(self):
        #self.s = discrete_gaussian(self.n, self.p, std=self.std)
        self.s = discrete_gaussian(1, self.p, std=self.std)
        self.e = discrete_gaussian(self.n, self.p, std=self.std)

        #a = discrete_uniform(self.n, self.p)
        self.b = -1 * (self.a * self.s + self.t * self.e)
        #self.b = -1 * (self.a * self.s + self.e)

        return (self.s, (self.b, self.a))  # (secret, public)

    def encrypt(self, m, pub):
        '''
        # Args:
            m: plaintext (mod t)
            a: public key (a0, a1)
        '''
        b, a = pub
        e = [discrete_gaussian(self.n, self.p, std=self.std)
             for _ in range(3)]

        self.v = e[0]
        m = Rq(m.poly.coeffs, self.p)

        # From the math in the study e[0] = v_i <- chi
        #return (m + b * self.v + self.t * e[2], a * self.v + self.t * e[1])
        #return (m + b * self.v + e[2], a * self.v + e[1])
        return (m + b.poly.coeffs.tolist()[0] * self.v + self.t * e[2], a.poly.coeffs.tolist()[0] * self.v + self.t * e[1])
        #return (m + b.poly.coeffs.tolist()[0] * self.v + e[2], a.poly.coeffs.tolist()[0] * self.v + e[1])

    """
    def decrypt(self, c, s):
        '''
        # Args:
            c: ciphertext (c0, c1, ..., ck)
            s: secret key
        '''
        c = [ci * s**i for i, ci in enumerate(c)]

        m = c[0]
        for i in range(1, len(c)):
            m += c[i]

        m = Rq(m.poly.coeffs, self.t)
        return m
    """

    def decrypt(self, c, s, e):
        '''
        # Args:
            c: ciphertext (c0, c1, ..., ck)
            s: secret key
            e: error distribution
        '''

        pardec = c * s + e
        pardec = Rq(pardec.poly.coeffs, self.t)
        #pardec = Rq(pardec.poly.coeffs, self.t)
        return pardec


    def add(self, c0, c1):
        '''
        # Args:
            c0: ciphertext (c0, c1, ..., ck)
            c1: ciphertext (c'0, c'1, ..., c'k')
        '''
        c = ()

        k0 = len(c0)  # not necessary to compute (len - 1)
        k1 = len(c1)

        if k0 > k1:
            (c0, c1) = (c1, c0)  # c0 is always shorter

        for _ in range(abs(k0 - k1)):
            c0 += (Rq([0], self.p),)  # add 0 to shorter ciphertext

        for i in range(len(c0)):
            c += (c0[i] + c1[i],)

        return c

    def mul(self, c0, c1):
        '''
        # Args:
            c0: ciphertext (c0, c1, ..., ck)
            c1: ciphertext (c'0, c'1, ..., c'k')
        '''
        c = ()

        k0 = len(c0) - 1
        k1 = len(c1) - 1

        for _ in range(k1):
            c0 += (Rq([0], self.p),)

        for _ in range(k0):
            c1 += (Rq([0], self.p),)

        for i in range(k0 + k1 + 1):
            _c = Rq([0], self.p)
            for j in range(i+1):
                _c += c0[j] * c1[i-j]
            c += (_c,)

        return c


def discrete_gaussian(n, q, mean=0., std=1.):
    coeffs = np.round(std * np.random.randn(n))
    return Rq(coeffs, q)


def discrete_uniform(n, q, min=0., max=None):
    if max is None:
        max = q
    coeffs = np.random.randint(min, max, size=n)
    return Rq(coeffs, q)