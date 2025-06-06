#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron
# Copyright 2023 Inria

"""Load a robot description in Pinocchio."""

import os
from importlib import import_module  # type: ignore
from typing import Optional, Union

import pinocchio as pin

from fourier_robot_descriptions.fourier import PACKAGE_PATH, REPOSITORY_PATH

from .._package_dirs import get_package_dirs

PinocchioJoint = Union[  # noqa: UP007
    pin.JointModelRX,
    pin.JointModelRY,
    pin.JointModelRZ,
    pin.JointModelPX,
    pin.JointModelPY,
    pin.JointModelPrismatic,
    pin.JointModelFreeFlyer,
    pin.JointModelSpherical,
    pin.JointModelSphericalZYX,
    pin.JointModelPlanar,
    pin.JointModelTranslation,
]


def load_robot_description(
    description_name: str,
    root_joint: PinocchioJoint | None = None,
    commit: str | None = None,
) -> pin.RobotWrapper:
    """Load a robot description in Pinocchio.

    Args:
        description_name: Name of the robot description.
        root_joint (optional): First joint of the kinematic chain, for example
            a free flyer between the floating base of a mobile robot and an
            inertial frame. Defaults to no joint, i.e., a fixed base.
        commit: If specified, check out that commit from the cloned robot
            description repository.

    Returns:
        Robot model for Pinocchio.
    """
    URDF_PATH = str(PACKAGE_PATH / f"{description_name}.urdf")
    robot = pin.RobotWrapper.BuildFromURDF(
            filename=URDF_PATH,
            package_dirs=get_package_dirs(PACKAGE_PATH),
            root_joint=root_joint,
        )
    return robot
