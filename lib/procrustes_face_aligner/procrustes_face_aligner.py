import numpy as np
import cv2


def procrustes(X, Y, scaling=True, reflection='best'):
    """
    A port of MATLAB `procrustes` function to Numpy.

    Procrustes analysis determines a linear transformation (translation,
    reflection, orthogonal rotation and scaling) of the points in Y to best
    conform them to the points in matrix X, using the sum of squared errors
    as the goodness of fit criterion.

        d, Z, [tform] = procrustes(X, Y)

    Parameters
    ----------
    X, Y : numpy array
        matrices of target and input coordinates. they must have equal
        numbers of  points (rows), but Y may have fewer dimensions
        (columns) than X.

    scaling : bool
        if False, the scaling component of the transformation is forced
        to 1

    reflection : str
        if 'best' (default), the transformation solution may or may not
        include a reflection component, depending on which fits the data
        best. setting reflection to True or False forces a solution with
        reflection or no reflection respectively.

    Returns
    -------
    d : float
        the residual sum of squared errors, normalized according to a
        measure of the scale of X, ((X - X.mean(0))**2).sum()

    Z : numpy array
        the matrix of transformed Y-values

    tform : dict
        a dict specifying the rotation, translation and scaling that
        maps X --> Y

    """

    n, m = X.shape
    ny, my = Y.shape

    muX = X.mean(0)
    muY = Y.mean(0)

    X0 = X - muX
    Y0 = Y - muY

    ssX = (X0 ** 2.).sum()
    ssY = (Y0 ** 2.).sum()

    # centred Frobenius norm
    normX = np.sqrt(ssX)
    normY = np.sqrt(ssY)

    # scale to equal (unit) norm
    X0 /= normX
    Y0 /= normY

    if my < m:
        Y0 = np.concatenate((Y0, np.zeros(n, m - my)), 0)

    # optimum rotation matrix of Y
    A = np.dot(X0.T, Y0)
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    V = Vt.T
    T = np.dot(V, U.T)

    if reflection is not 'best':

        # does the current solution use a reflection?
        have_reflection = np.linalg.det(T) < 0

        # if that not what was specified, force another reflection
        if reflection != have_reflection:
            V[:, -1] *= -1
            s[-1] *= -1
            T = np.dot(V, U.T)

    traceTA = s.sum()

    if scaling:

        # optimum scaling of Y
        b = traceTA * normX / normY

        # standarised distance between X and b*Y*T + c
        d = 1 - traceTA ** 2

        # transformed coords
        Z = normX * traceTA * np.dot(Y0, T) + muX

    else:
        b = 1
        d = 1 + ssY / ssX - 2 * traceTA * normY / normX
        Z = normY * np.dot(Y0, T) + muX

    # transformation matrix
    if my < m:
        T = T[:my, :]
    c = muX - b * np.dot(muY, T)

    # transformation values
    tform = {'rotation': T, 'scale': b, 'translation': c}

    return d, Z, tform


def align_face(face, dots):
    perfect_dots = [30.2946 / 96, 51.6963 / 112,
                    65.5318 / 96, 51.5014 / 112,
                    48.0252 / 96, 71.7366 / 112,
                    33.5493 / 96, 92.3655 / 112,
                    62.7299 / 96, 92.2041 / 112]
    x10, y10, x20, y20, x30, y30, x40, y40, x50, y50 = [int(item * 256) for item in perfect_dots]
    x1, y1, x2, y2, x3, y3, x4, y4, x5, y5 = [int(item[0][0] * 256) for item in dots]
    normalized128 = cv2.resize(face, (256, 256))
    x_pts = np.asarray(
        [[x10, y10],
         [x20, y20],
         [x30, y30],
         [x40, y40],
         [x50, y50]]
    )
    y_pts = np.asarray(
        [[x1, y1],
         [x2, y2],
         [x3, y3],
         [x4, y4],
         [x5, y5]]
    )

    # Calculate transform via procrustes
    d, z_pts, t_form = procrustes(x_pts, y_pts)

    # Build and apply transform matrix
    r = np.eye(3)
    r[0:2, 0:2] = t_form['rotation']
    s = np.eye(3) * t_form['scale']
    s[2, 2] = 1
    t = np.eye(3)
    t[0:2, 2] = t_form['translation']
    m = np.dot(np.dot(r, s), t.T).T
    aligned_face = cv2.warpAffine(normalized128, m[0:2, :], (256, 256))
    del dots
    del normalized128
    del x_pts
    del y_pts
    del d, z_pts, t_form
    del r, s, t, m
    return aligned_face
