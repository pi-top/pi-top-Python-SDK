import numpy as np
from os import environ
if not environ.get('DISPLAY'):
    environ['DISPLAY'] = ":0"


def plot_ellipsoid(center, radii, rotation, ax=None, plotAxes=False, cageColor='b', cageAlpha=0.2):
    """Plot an ellipsoid"""
    u = np.linspace(0.0, 2.0 * np.pi, 100)
    v = np.linspace(0.0, np.pi, 100)

    # cartesian coordinates that correspond to the spherical angles:
    x = radii[0] * np.outer(np.cos(u), np.sin(v))
    y = radii[1] * np.outer(np.sin(u), np.sin(v))
    z = radii[2] * np.outer(np.ones_like(u), np.cos(v))
    # rotate accordingly
    for i in range(len(x)):
        for j in range(len(x)):
            [x[i, j], y[i, j], z[i, j]] = np.dot([x[i, j], y[i, j], z[i, j]], rotation) + center

    if plotAxes:
        # make some purdy axes
        axes = np.array([[radii[0], 0.0, 0.0],
                         [0.0, radii[1], 0.0],
                         [0.0, 0.0, radii[2]]])
        # rotate accordingly
        for i in range(len(axes)):
            axes[i] = np.dot(axes[i], rotation)

        # plot axes
        for p in axes:
            X3 = np.linspace(-p[0], p[0], 100) + center[0]
            Y3 = np.linspace(-p[1], p[1], 100) + center[1]
            Z3 = np.linspace(-p[2], p[2], 100) + center[2]
            ax.plot(X3, Y3, Z3, color=cageColor)

    # plot ellipsoid
    if ax:
        ax.plot_wireframe(x, y, z, rstride=4, cstride=4, color=cageColor, alpha=cageAlpha)


def least_squares_ellipsoid_fit(magX, magY, magZ):
    # ax^2 + by^2 + cz^2 +2fyz + 2gxz + 2hxy + px + qy + rz + d = 0
    # x_T.M.x + x_T.n + d = 0

    a1 = magX ** 2
    a2 = magY ** 2
    a3 = magZ ** 2
    a4 = 2 * np.multiply(magY, magZ)
    a5 = 2 * np.multiply(magX, magZ)
    a6 = 2 * np.multiply(magX, magY)
    a7 = 2 * magX
    a8 = 2 * magY
    a9 = 2 * magZ
    a10 = np.ones(len(magX)).T
    D = np.array([a1, a2, a3, a4, a5, a6, a7, a8, a9, a10])

    # Eqn 7, k = 4
    C1 = np.array([[-1, 1, 1, 0, 0, 0],
                   [1, -1, 1, 0, 0, 0],
                   [1, 1, -1, 0, 0, 0],
                   [0, 0, 0, -4, 0, 0],
                   [0, 0, 0, 0, -4, 0],
                   [0, 0, 0, 0, 0, -4]])

    # Eqn 11
    S = np.matmul(D, D.T)
    S11 = S[:6, :6]
    S12 = S[:6, 6:]
    S21 = S[6:, :6]
    S22 = S[6:, 6:]

    # Eqn 15, find eigenvalue and vector
    # Since S is symmetric, S12.T = S21
    tmp = np.matmul(np.linalg.inv(C1), S11 - np.matmul(S12, np.matmul(np.linalg.inv(S22), S21)))
    eigenValue, eigenVector = np.linalg.eig(tmp)
    u1 = eigenVector[:, np.argmax(eigenValue)]

    # Eqn 13 solution
    u2 = np.matmul(-np.matmul(np.linalg.inv(S22), S21), u1)

    # Total solution
    u = np.concatenate([u1, u2]).T

    M = np.array([[u[0], u[5], u[4]],
                  [u[5], u[1], u[3]],
                  [u[4], u[3], u[2]]])

    n = np.array([[u[6]],
                  [u[7]],
                  [u[8]]])

    d = u[9]

    return M, n, d


def get_ellipsoid_geometric_params(M, n, d):
    a = M[0, 0]
    b = M[1, 1]
    c = M[2, 2]
    f = M[2, 1]
    g = M[0, 2]
    h = M[0, 1]

    p = n[0][0]
    q = n[1][0]
    r = n[2][0]

    Q = np.array(
        [
            [a, h, g, p],
            [h, b, f, q],
            [g, f, c, r],
            [p, q, r, d]
        ]
    )

    Minv = np.linalg.inv(M)
    b = -np.dot(Minv, n)
    center = b.T[0]

    Tofs = np.eye(4)
    Tofs[3, 0:3] = center

    R = np.dot(Tofs, np.dot(Q, Tofs.T))

    R3 = R[0:3, 0:3]

    s1 = -R[3, 3]
    R3S = R3 / s1
    eigenvalues, eigenvectors = np.linalg.eig(R3S)

    rotation_matrix = np.linalg.inv(eigenvectors)  # inverse is actually the transpose here

    eigen_reciprocal = 1.0 / np.abs(eigenvalues)
    radii = np.sqrt(eigen_reciprocal)

    return center, radii, rotation_matrix
