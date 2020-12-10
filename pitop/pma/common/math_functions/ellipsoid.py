import numpy as np

class EllipsoidTool:
    """Some stuff for playing with ellipsoids"""

    def __init__(self):
        pass

    def getMinVolEllipse(self, P=None, tolerance=0.01):
        """ Find the minimum volume ellipsoid which holds all the points

        Based on work by Nima Moshtagh
        http://www.mathworks.com/matlabcentral/fileexchange/9542
        and also by looking at:
        http://cctbx.sourceforge.net/current/python/scitbx.math.minimum_covering_ellipsoid.html
        Which is based on the first reference anyway!

        Here, P is a numpy array of N dimensional points like this:
        P = [[x,y,z,...], <-- one point per line
             [x,y,z,...],
             [x,y,z,...]]

        Returns:
        (center, radii, rotation)

        """
        (N, d) = np.shape(P)
        d = float(d)

        # Q will be our working array
        Q = np.vstack([np.copy(P.T), np.ones(N)])
        QT = Q.T

        # initializations
        err = 1.0 + tolerance
        u = (1.0 / N) * np.ones(N)

        # Khachiyan Algorithm
        while err > tolerance:
            V = np.dot(Q, np.dot(np.diag(u), QT))
            M = np.diag(np.dot(QT, np.dot(np.linalg.inv(V), Q)))  # M the diagonal vector of an NxN matrix
            j = np.argmax(M)
            maximum = M[j]
            step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
            new_u = (1.0 - step_size) * u
            new_u[j] += step_size
            err = np.linalg.norm(new_u - u)
            u = new_u

        # center of the ellipse
        center = np.dot(P.T, u)

        U = np.diag(u)

        # A = np.linalg.inv(P * U * P.T - (P * u) * (P * u).T)
        A = (1 / d) * np.linalg.inv(np.dot(P.T, np.dot(U, P)) - np.outer(center, center))

        # Get the values we'd like to return
        U, s, rotation = np.linalg.svd(A)
        radii = 1.0 / np.sqrt(s)

        return center, radii, rotation, A

    def getEllipsoidVolume(self, radii):
        """Calculate the volume of the blob"""
        return 4. / 3. * np.pi * radii[0] * radii[1] * radii[2]

    def plotEllipsoid(self, center, radii, rotation, ax=None, plotAxes=False, cageColor='b', cageAlpha=0.2):
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


def fitEllipsoid(magX, magY, magZ):
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


def plot_ellipsoid(M, n, d):
    a = M[0, 0]
    b = M[1, 1]
    c = M[2, 2]
    f = M[2, 1]
    g = M[0, 2]
    h = M[0, 1]

    p = n[0]
    q = n[1]
    r = n[2]

    Amat = np.array(
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
    # Center the ellipsoid at the origin
    Tofs = np.eye(4)
    Tofs[3, 0:3] = center
    R = np.dot(Tofs, np.dot(Amat, Tofs.T))
    R3 = R[0:3, 0:3]














