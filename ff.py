# Finite Field Arithmetic Implementation

class FiniteFieldArray():
    ### Predefined finite field characteristics
    FIELD_SIZE = 8
    PRIMITIVE_POLY = 0x1B
    GENERATOR = 0x03

    ########################################################################

    ELEMENT_NUM = 0
    ELEMENT_MASK = 0
    ff_exp_table = []
    ff_log_table = []
    ff_sqrt_table = []

    ff_mul_table = {}
    ff_div_table = {}

    ########################################################################

    ### Precomputation of finite field exponent, logarithm, and square root
    ### tables for fast multiplication, division, and square root

    @staticmethod
    def ff_precompute():
        # Setup constants associated with this field size
        FiniteFieldArray.ELEMENT_NUM = 2**FiniteFieldArray.FIELD_SIZE
        FiniteFieldArray.ELEMENT_MASK = FiniteFieldArray.ELEMENT_NUM-1
        MSB_MASK = (FiniteFieldArray.ELEMENT_MASK >> 1)+1

        # Slow finite field multiplication used to precompute exponent
        # and logarithm tables
        def ff_slow_mul(a, b):
            p = 0
            for i in range(FiniteFieldArray.FIELD_SIZE):
                if (b & 0x1):
                    p ^= a
                if (a & MSB_MASK):
                    a <<= 1
                    a &= FiniteFieldArray.ELEMENT_MASK
                    a ^= FiniteFieldArray.PRIMITIVE_POLY
                else:
                    a <<= 1
                    a &= FiniteFieldArray.ELEMENT_MASK
                b >>= 0x1
            return p

        # Precompute exponent and logarithm table
        FiniteFieldArray.ff_exp_table = [0] * FiniteFieldArray.ELEMENT_NUM
        FiniteFieldArray.ff_log_table = [0] * FiniteFieldArray.ELEMENT_NUM
        FiniteFieldArray.ff_exp_table[0] = 0x01
        for i in range(1, FiniteFieldArray.ELEMENT_NUM):
            FiniteFieldArray.ff_exp_table[i] = \
                ff_slow_mul(FiniteFieldArray.ff_exp_table[i-1], FiniteFieldArray.GENERATOR)
            FiniteFieldArray.ff_log_table[FiniteFieldArray.ff_exp_table[i]] = i

        # Slow finite field square root used to precompute square root table
        def ff_slow_sqrt(x):
            for i in range(FiniteFieldArray.ELEMENT_NUM):
                if FiniteFieldArray.ff_elem_mul_slow(i, i) == x:
                    return i
            raise ValueError("%d has no squareroot in (2**%d, 0x%02X, 0x%02X)!" \
                    % (x, FiniteFieldArray.PRIMITIVE_POLY, FiniteFieldArray.GENERATOR))

        # Precompute square root table
        FiniteFieldArray.ff_sqrt_table = [0] * FiniteFieldArray.ELEMENT_NUM
        for i in range(FiniteFieldArray.ELEMENT_NUM):
            try:
                FiniteFieldArray.ff_sqrt_table[i] = ff_slow_sqrt(i)
            except ValueError:
                FiniteFieldArray.ff_sqrt_table[i] = None

        # Precompute multiplication table
        for a in range(FiniteFieldArray.ELEMENT_NUM):
            FiniteFieldArray.ff_mul_table[a] = {}
            for b in range(FiniteFieldArray.ELEMENT_NUM):
                FiniteFieldArray.ff_mul_table[a][b] = FiniteFieldArray.ff_elem_mul_slow(a, b)

        # Precompute division table
        for a in range(FiniteFieldArray.ELEMENT_NUM):
            FiniteFieldArray.ff_div_table[a] = {}
            for b in range(FiniteFieldArray.ELEMENT_NUM-1):
                FiniteFieldArray.ff_div_table[a][b+1] = FiniteFieldArray.ff_elem_div_slow(a, b+1)

    ########################################################################
    ########################################################################

    ### Element-wise finite field addition, subtraction, multiplication,
    ### and division

    @staticmethod
    def ff_elem_add(a, b):
        return a ^ b

    @staticmethod
    def ff_elem_sub(a, b):
        return a ^ b

    @staticmethod
    def ff_elem_mul_slow(a, b):
        if a == 0 or b == 0: return 0
        # a * b = exp(log(a)) * exp(log(b)) = exp(log(a) + log(b))
        exp_index = FiniteFieldArray.ff_log_table[a] + FiniteFieldArray.ff_log_table[b]
        exp_index %= FiniteFieldArray.ELEMENT_MASK
        return FiniteFieldArray.ff_exp_table[exp_index]

    @staticmethod
    def ff_elem_mul(a, b):
        return FiniteFieldArray.ff_mul_table[a][b]

    @staticmethod
    def ff_elem_div_slow(a, b):
        if (b == 0): raise ZeroDivisionError
        # a / b = a * (1/b)
        b_inverse = FiniteFieldArray.ff_exp_table[FiniteFieldArray.ELEMENT_MASK - FiniteFieldArray.ff_log_table[b]]
        return FiniteFieldArray.ff_elem_mul(a, b_inverse)

    @staticmethod
    def ff_elem_div(a, b):
        if (b == 0): raise ZeroDivisionError
        return FiniteFieldArray.ff_div_table[a][b]

    @staticmethod
    def ff_elem_sqrt(a):
        return FiniteFieldArray.ff_sqrt_table[a]

    ########################################################################

    @staticmethod
    def ff_bytearray_to_elemarray(x):
        if FiniteFieldArray.FIELD_SIZE != 8: raise \
            ValueError("ff_bytearray_to_elemarray unimplemented for FF 2**%d" % \
            FiniteFieldArray.FIELD_SIZE)
        return list(x)

    @staticmethod
    def ff_elemarray_to_bytearray(x):
        if FiniteFieldArray.FIELD_SIZE != 8: raise \
            ValueError("ff_elemarray_to_bytearray unimplemented for FF 2**%d" % \
            FiniteFieldArray.FIELD_SIZE)
        return bytearray(x)

    ########################################################################
    ########################################################################

    def __init__(self, x = None):
        self.raw_bytes = bytearray([])
        if x is not None:
            raw_bytes = bytearray(x)
            if len(raw_bytes) % (FiniteFieldArray.FIELD_SIZE/8) != 0:
                raise ValueError("invalid byte array size for FF 2**%d" % FiniteFieldArray.FIELD_SIZE)
            self.raw_bytes = raw_bytes

    ### Overloaded operators for scalar multiplication, scalar divison,
    ### array addition, array subtraction, equality, and string
    ### representation

    # FiniteFieldArray[i] = scalar
    def __getitem__(self, index):
        return self.raw_bytes[index]

    # len(FiniteFieldArray) = len(self.raw_bytes)
    def __len__(self):
        return len(self.raw_bytes)

    # FiniteFieldArray + FiniteFieldArray = FiniteFieldArray
    def __add__(self, other):
        if not isinstance(other, FiniteFieldArray): raise TypeError("other is not a FiniteFieldArray")
        elif len(self.raw_bytes) != len(other.raw_bytes): raise ValueError("other is not same size")

        my_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(self.raw_bytes)
        other_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(other.raw_bytes)
        sum_elemarray = [FiniteFieldArray.ff_elem_add(my_elemarray[i], \
                    other_elemarray[i]) for i in range(len(my_elemarray))]
        return FiniteFieldArray(FiniteFieldArray.ff_elemarray_to_bytearray(sum_elemarray))

    # FiniteFieldArray - FiniteFieldArray = FiniteFieldArray
    def __sub__(self, other):
        return self.__add__(other)

    # FiniteFieldArray * FiniteFieldArray = scalar (inner product)
    # FiniteFieldArray * scalar = FiniteFieldArray
    def __mul__(self, other):
        if isinstance(other, FiniteFieldArray):
            if len(self.raw_bytes) != len(other.raw_bytes):
                raise ValueError("other is not same size")

            my_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(self.raw_bytes)
            other_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(other.raw_bytes)
            x = 0
            for i in range(len(my_elemarray)):
                x = FiniteFieldArray.ff_elem_add(x, FiniteFieldArray.ff_elem_mul(my_elemarray[i], other_elemarray[i]))
            return x
        elif isinstance(other, int):
            if other < 0 or other > FiniteFieldArray.ELEMENT_NUM-1:
                raise ValueError("other is outside of finite field")

            my_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(self.raw_bytes)
            mul_elemarray = [FiniteFieldArray.ff_elem_mul(my_elemarray[i], other) for i in range(len(my_elemarray))]
            return FiniteFieldArray(FiniteFieldArray.ff_elemarray_to_bytearray(mul_elemarray))
        else:
            raise TypeError("unknown other")

    # FiniteFieldArray * FiniteFieldArray = scalar (inner product)
    # scalar * FiniteFieldArray = FiniteFieldArray
    def __rmul__(self, other):
        return self.__mul__(other)

    # FiniteFieldArray / scalar = FiniteFieldArray
    def __truediv__(self, other):
        if not isinstance(other, int): raise TypeError("other is not a scalar integer")
        elif other < 0 or other > FiniteFieldArray.ELEMENT_NUM-1: raise ValueError("other is outside of finite field")

        my_elemarray = FiniteFieldArray.ff_bytearray_to_elemarray(self.raw_bytes)
        div_elemarray = [FiniteFieldArray.ff_elem_div(my_elemarray[i], other) for i in range(len(my_elemarray))]
        return FiniteFieldArray(FiniteFieldArray.ff_elemarray_to_bytearray(div_elemarray))

    # FiniteFieldArray == FiniteFieldArray
    def __eq__(self, other):
        if not isinstance(other, FiniteFieldArray): return False
        return self.raw_bytes == other.raw_bytes

    # str(FiniteFieldArray)
    def __str__(self):
        hexstr = ""
        for i in range(len(self.raw_bytes)):
            hexstr += ("%02x" % self.raw_bytes[i]) + " "
            #if i == 0: continue
            #elif (i+1) % 64 == 0 and i+1 != len(self.raw_bytes): hexstr += "\n"
            #elif (i+1) % 2 == 0: hexstr += " "
        return hexstr

def ff_rref(m, b):
    # m is an array of FiniteFieldArray rows
    # b is an array of the right hand column

    pi = 0

    # Iterate through each row
    for j in range(len(m)):
        # While we do not have a pivot for this row
        while m[j][pi] == 0:
            # Find a row below to swap with for a pivot at pi
            for k in range(j+1, len(m)):
                if m[k][pi] != 0:
                    # Swap with this row
                    (m[j], m[k]) = (m[k], m[j])
                    (b[j], b[k]) = (b[k], b[j])
                    break

            # Increment pivot index if we could not find a row to swap with
            if m[j][pi] == 0:
                pi += 1

            # If there is no pivots left, we're done reducing
            if pi == len(m[0]):
                return (m, b)

        # Divide through to have a pivot of 1
        m[j] /= m[j][pi]

        # Eliminate above & below
        for k in range(len(m)):
            if k != j and m[k][pi] != 0:
                m[k] = m[k] - (m[j]*m[k][pi])

        # Move onto the next pivot
        pi += 1
        # If there is no pivots left, we're done reducing
        if pi == len(m[0]):
            break

    return (m, b)

def ff_solutions(a, x, b):
    (ap, bp) = ff_rref(a, b)

    solved = []
    used = []
    for i in range(len(ap)):
        r = ap[i]
        # If this row has only one non-zero entry
        reduced_coefs = [r[j] != 0 for j in range(len(r))]
        if sum(reduced_coefs) == 1:
            # Add the solution to our solved list
            solved.append(x[reduced_coefs.index(True)])
            # Add the decoded LC to our used list
            used.append(b[i])

    return (solved, used)

def ff_rref_test():
    m = [   FiniteFieldArray([33, 247, 109, 71, 139]), \
            FiniteFieldArray([97, 221, 102, 127, 72]), \
            FiniteFieldArray([101, 126, 186, 90, 103]), \
            FiniteFieldArray([59, 234, 145, 197, 122]), \
            FiniteFieldArray([75, 9, 213, 9, 3])]
    b = [1,2,3,4,5]
    (mp, bp) = ff_rref(m, b)
    for i in range(len(mp)):
        print(mp[i], "\t", b[i])
    print("")

    m = [   FiniteFieldArray([33, 247, 109, 71, 139]), \
            FiniteFieldArray([97, 221, 102, 127, 72]), \
            FiniteFieldArray([101, 126, 186, 90, 103]), \
            2*FiniteFieldArray([97, 221, 102, 127, 72])]
    b = [1,2,3,4]
    (mp, bp) = ff_rref(m, b)
    for i in range(len(mp)):
        print(mp[i], "\t", b[i])
    print("")

    m = [   FiniteFieldArray([0, 247, 109, 71, 139]), \
            FiniteFieldArray([97, 221, 102, 127, 72]), \
            FiniteFieldArray([101, 126, 186, 90, 103]), \
            2*FiniteFieldArray([97, 221, 102, 127, 72])]
    b = [1,2,3,4]
    (mp, bp) = ff_rref(m, b)
    for i in range(len(mp)):
        print(mp[i], "\t", b[i])
    print("")

    m = [   FiniteFieldArray([0, 0, 0, 71, 139]), \
            FiniteFieldArray([0, 0, 1, 127, 72])]
    b = [1,2]
    (mp, bp) = ff_rref(m, b)
    for i in range(len(mp)):
        print(mp[i], "\t", b[i])
    print("")

