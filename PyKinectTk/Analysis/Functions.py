from math import sqrt

def magnitude(A, B):
    """ Returns the magnitude of two vectors - A and B must be the same size """
    if len(A) != len(B):
        raise ArithmeticError("Vectors are not equal in size")

    dif = []
    for i in range(len(A)):
        dif.append( (A[i]-B[i])**2 )

    sigma = sum(dif)

    return sqrt(sigma)
