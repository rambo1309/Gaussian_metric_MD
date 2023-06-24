# Copyright 2023 Franco Aquistapace
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# ----- Here we'll define some tools to help us in development and testing ------
# We'll use a functional programming approach for now, we can develop classes 
# later if we need them.

# Import modules
import tensorflow as tf


# ------ Lattice generation functions ------------
# Function that can generate a cubic structure
def gen_sc_lattice(n1, n2, n3, a):
    '''
    Params:
        n1, n2, n3 : int
            Size of the lattice in the x, y and z
            directions, respectively, in terms of
            lattice unit vectors. 
        a : float or int
            Lattice constant in A for the lattice.
    
    Output:
        Returns a TF Constant tensor of shape (N,3), 
        where N is the amount of atoms in the structure, 
        and each row is the position of an atom as
        (x, y, z). The array contains the positions
        for a simple cubic (SC) lattice, with unit 
        vectors x_hat, y_hat, z_hat, and dimensions
        (n1*a*x_hat) x (n2*a*y_hat) x (n3*a*z_hat).
    '''
    config = []
    for k in range(n3):
        for j in range(n2):
            for i in range(n1):
                # Build position and add to config
                p = [a * i, 
                     a * j,
                     a * k]
                config.append(p)

    return tf.constant(config, dtype='float32')


# ------ Lattice transformation functions --------

# Define function to scale a lattice
def scale(C, s):
    '''
    Params:
        C : tf.Tensor 
            Array containing atomic positions in 3 dimensions.
            In every case, C must be of shape (N, 3), where N 
            is the number of atoms in the configuration.
        s : iterable
            Scaling factor to apply to the configuration C. Must 
            be of shape (,3), so that each element is the scaling
            factor for a given axis x, y or z, respectively.

    Output:
        Returns a new configuration C_new as a result of a scale
        transformation of C:
            C_new = C * Ixs
        Where Ixs is a 3x3 matrix where is a diagonal matrix in 
        which the i-th diagonal element equals the i-th element
        from s.
    '''
    Ixs = tf.constant([[s[0], 0,    0],
                       [0,    s[1], 0],
                       [0,    0,    s[2]]], 
                       dtype='float32')
    return tf.matmul(C, Ixs)

# Define a function to displace a lattice
def displace(C, X_0):
    '''
    Params:
        C : tf.Tensor
            Array containing atomic positions in 3 dimensions.
            In every case, C must be of shape (N, 3), where N 
            is the number of atoms in the configuration.
        X_0 : tf.Tensor
            Array containing the x, y and z values of a 
            position vector. This vector will be used to displace
            the configuration.
    
    Output:
        Returns a new configuraion C_new as a result of a 
        displacement of C:
            C_new = C + IxX_0
        Where IxX_0 is a matrix of same shape as C in which
        each row contains the vector X_0.
    '''
    return C + X_0

# Define a function to rotate a lattice
def rotate(C, alpha, beta, gamma):
    '''
    Params:
        C : tf.Tensor
            Array containing atomic positions in 3 dimensions.
            In every case, C must be of shape (N, 3), where N 
            is the number of atoms in the configuration.
        alpha, beta, gamma : float
            x, y and z axes rotation angles, respectively. 
    
    Output:
        Returns a new configuraion C_new as a result of a 
        rotation of C:
            C_new = R x C
        Where R is a matrix of shape (3,3) defined as:
            R = R_z(gamma)*R_y(beta)*R_x(alpha)
        with R_x, R_y and R_z being rotations about the
        x, y and z axes, respectively.
    '''
    # Define each rotation
    c_alpha = tf.cos(alpha, dtype='float32')
    s_alpha = tf.sin(alpha, dtype='float32')
    R_x = tf.constant([[1., 0., 0.],
                       [0., c_alpha, -s_alpha],
                       [0., s_alpha, c_alpha]], 
                       dtype='float32')
    c_beta = tf.cos(beta, dtype='float32')
    s_beta = tf.sin(beta, dtype='float32')
    R_y = tf.constant([[c_beta, 0., s_beta],
                       [0., 1., 0.],
                       [-s_beta, 0., c_beta]], 
                       dtype='float32')
    c_gamma = tf.cos(gamma, dtype='float32')
    s_gamma = tf.sin(gamma, dtype='float32')
    R_z = tf.constant([[c_gamma, -s_gamma, 0.],
                       [s_gamma, c_gamma, 0.],
                       [0., 0., 1.]],
                       dtype='float32')
    # Build general rotation
    R = tf.matmul(R_z, tf.matmul(R_y, R_x))
    # Calculate C_new
    C_new = tf.transpose(tf.matmul(R, C, transpose_b=True))
    return C_new


# Define a function to flip a lattice
def flip(C, x, y, z):
    '''
    Params:
        C : tf.Tensor
            Array containing atomic positions in 3 dimensions.
            In every case, C must be of shape (N, 3), where N 
            is the number of atoms in the configuration.
        x, y, z : bool
            Requested flip over each axis, respectively. True 
            means that the flip will be done for its respective
            axis.
    Output:
        Returns a new configuraion C_new as a result of a 
        flip of C:
            C_new = F x C
        Where F is a matrix of shape (3,3), defined as:
            F = [[+-1,  0,    0],
                 [0,    +-1,  0],
                 [0,    0,    +-1]]
        with the + or - value of each diagonal element assigned
        according to the bool value of the respective axis.
    '''
    # Define F
    F = tf.constant([[-2*int(x)+1, 0, 0],
                     [0, -2*int(y)+1, 0],
                     [0, 0, -2*int(z)+1]],
                     dtype='float32')
    # Get C_new
    C_new = tf.transpose(tf.matmul(F, C, transpose_b=True))
    return C_new