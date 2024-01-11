
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import dolfin as df

def get_mesh_dimensions(mesh):

    coords = mesh.coordinates()[:]

    xmax = max(coords[:,0])
    xmin = min(coords[:,0])
    ymax = max(coords[:,1])
    ymin = min(coords[:,1])

    return xmin, xmax, ymin, ymax

def get_block_coords(mesh, N):
    xmin, xmax, ymin, ymax = get_mesh_dimensions(mesh)

    xcoord = xmin - N/2
    xcoords = []

    while xcoord < xmax + N:
        xcoords.append(xcoord)
        xcoord += N
    
    ycoord = ymin - N/2
    ycoords = []

    while ycoord < ymax + N:
        ycoords.append(ycoord)
        ycoord += N

    return np.array(xcoords), np.array(ycoords)

def assign_collagen_distribution(mesh, mu=0, kappa=0, N=10):
    """

    Defines collagen alignment to points in the mesh, in the following manner:
    * Divide the (2D) domain into squares of size NxN (µm)
    * Assign an angle to those from a von Mises distribution
    * Do an interpolation on all mesh point

    """
    
    xcoords, ycoords = get_block_coords(mesh, N)
    values = np.random.vonmises(mu=mu, kappa=kappa, size=(len(xcoords), len(ycoords)))

    ip = RegularGridInterpolator(
        (xcoords, ycoords),
        values,
        bounds_error=False,
        fill_value=0,
        method="nearest",
    )

    U = df.FunctionSpace(mesh, "CG", 1)
    dist = df.Function(U, name="Collagen distribution")

    v_d = U.dofmap().dofs()
    mesh_coords = U.tabulate_dof_coordinates()[:]
    mesh_xcoords = np.array(mesh_coords[:, 0])
    mesh_ycoords = np.array(mesh_coords[:, 1])

    ip_values = ip((mesh_xcoords, mesh_ycoords))

    dist.vector()[v_d] = ip_values

    collagen_dist_mf = df.MeshFunction('double', mesh, 0)
    collagen_dist_mf.array()[:] = dist.vector()[:]
    print(len(dist.vector()[:]))
    return collagen_dist_mf
    
