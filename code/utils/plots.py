import numpy as np
import pyvista

import dolfinx.plot as plot


def plot_damage_state(u, alpha, load=None):
    """
    Plot the displacement and damage field with pyvista
    """
    assert u.function_space.mesh == alpha.function_space.mesh
    mesh = u.function_space.mesh

    plotter = pyvista.Plotter(
        title="damage, warped by displacement", window_size=[800, 300], shape=(1, 2)
    )

    topology, cell_types, geometry = plot.vtk_mesh(mesh)
    grid = pyvista.UnstructuredGrid(topology, cell_types, geometry)

    plotter.subplot(0, 0)
    if load is not None:
        plotter.add_text(f"displacement - load {load:3.3f}", font_size=11)
    else:
        plotter.add_text("displacement", font_size=11)

    values = np.zeros((geometry.shape[0], 3), dtype=np.float64)
    values[:, : len(u)] = u.x.array.real.reshape((geometry.shape[0], len(u)))
    grid["u"] = values
    warped = grid.warp_by_vector("u", factor=0.1)
    _ = plotter.add_mesh(warped, show_edges=False)
    plotter.view_xy()

    plotter.subplot(0, 1)
    if load is not None:
        plotter.add_text(f"damage - load {load:3.3f}", font_size=11)
    else:
        plotter.add_text("damage", font_size=11)
    grid["alpha"] = alpha.x.array.real
    grid.set_active_scalars("alpha")
    plotter.add_mesh(grid, show_edges=False, show_scalar_bar=True, clim=[0, 1])
    plotter.view_xy()
    if not pyvista.OFF_SCREEN:
        plotter.show()


def warp_plot_2d(u, cell_field=None, field_name="Field", factor=1.0, **kwargs):
    msh = u.function_space.mesh

    # Create plotter and pyvista grid
    plotter = pyvista.Plotter()

    topology, cell_types, geometry = plot.vtk_mesh(msh)
    grid = pyvista.UnstructuredGrid(topology, cell_types, geometry)

    # Attach vector values to grid and warp grid by vector
    values = np.zeros((geometry.shape[0], 3), dtype=np.float64)
    values[:, : len(u)] = u.x.array.real.reshape((geometry.shape[0], len(u)))
    grid["u"] = values
    warped_grid = grid.warp_by_vector("u", factor=factor)
    if cell_field is not None:
        warped_grid.cell_data[field_name] = cell_field.x.array
        warped_grid.set_active_scalars(field_name)
    plotter.add_mesh(warped_grid, **kwargs)
    plotter.camera_position = "xy"

    return plotter
