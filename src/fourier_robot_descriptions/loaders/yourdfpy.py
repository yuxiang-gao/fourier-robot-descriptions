"""Load a robot description in yourdfpy."""

import os
from typing import Optional

from fourier_robot_descriptions import list_descriptions
from fourier_robot_descriptions.fourier import PACKAGE_PATH, REPOSITORY_PATH

try:
    import yourdfpy
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "This feature requires 'yourdfpy', which can be installed by `pip install yourdfpy`"
    ) from e


def load_robot_description(
    description_name: str,
    **kwargs,
) -> yourdfpy.URDF:
    """Load a robot description in yourdfpy.

    Args:
        description_name: Name of the robot description.
        commit: If specified, check out that commit from the cloned robot
            description repository.
        kwargs: arguments passed to yourdfpy.URDF.load function, including:
            build_scene_graph: Whether to build a scene graph from visual
                elements.
            build_collision_scene_graph: Whether to build a scene graph from
                collision elements.
            load_meshes: Whether to load the meshes for the visual elements.
            load_collision_meshes: Whether to load the meshes for the collision
                elements.

    Returns:
        Robot model for yourdfpy.
    """

    URDF_PATH = str(REPOSITORY_PATH / "urdf" / f"{description_name}.urdf")
    try:
        return yourdfpy.URDF.load(
            URDF_PATH,
            mesh_dir=PACKAGE_PATH,
            **kwargs,
        )
    except Exception as e:
        available_descriptions = list_descriptions()
        raise ValueError(
            f"Failed to load robot description {description_name}. Available descriptions: {available_descriptions}"
        ) from e
