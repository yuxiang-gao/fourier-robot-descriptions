#!/usr/bin/env python3
#
# SPDX-License-Identifier: Apache-2.0
# Copyright 2022 Stéphane Caron
# Copyright 2023 Inria

"""Git utility functions to clone model repositories."""

import os
import shutil
from typing import Optional, Union

import tqdm
from git import (
    GitCommandError,
    InvalidGitRepositoryError,
    RemoteProgress,
    Repo,
)

from ._repositories import REPOSITORIES


class CloneProgressBar(RemoteProgress):
    """Progress bar when cloning."""

    def __init__(self):
        """Initialize progress bar."""
        super().__init__()
        self.progress = tqdm.tqdm()

    def update(
        self,
        op_code: int,
        cur_count: str | float,
        max_count: str | float | None = None,
        message: str = "",
    ) -> None:
        """Update progress bar.

        Args:
            op_code: Integer that can be compared against Operation IDs and
                stage IDs.
            cur_count: Current item count.
            max_count: Maximum item count, or ``None`` if there is none.
            message: Unused here.
        """
        self.progress.total = max_count
        self.progress.n = cur_count
        self.progress.refresh()


def clone_to_directory(
    repo_url: str,
    target_dir: str,
    commit: str | None = None,
) -> Repo:
    """Clone a git repository to a designated directory.

    Args:
        repo_url: URL to the git repository to clone.
        target_dir: Directory to clone the repository to.
        commit: Optional commit to check out after cloning.

    Returns:
        Cloned git repository.
    """
    clone = None
    if os.path.exists(target_dir):
        try:
            clone = Repo(target_dir)
        except InvalidGitRepositoryError:
            print(f"Repository at {target_dir} is invalid, recreating it...")
            shutil.rmtree(target_dir)
            clone = None

    if clone is None:
        print(f"Cloning {repo_url}...")
        os.makedirs(target_dir)
        progress_bar = CloneProgressBar()
        clone = Repo.clone_from(
            repo_url,
            target_dir,
            progress=progress_bar.update,
        )

    if commit is not None:
        try:
            clone.git.checkout(commit)
        except GitCommandError:
            print(f"Commit {commit} not found, let's fetch origin and try again...")
            clone.git.fetch("origin")
            clone.git.checkout(commit)
            print(f"Found commit {commit} successfully!")

    return clone


def clone_to_cache(description_name: str, commit: str | None = None) -> str:
    """Get a local working directory cloned from a remote git repository.

    Args:
        description_name: Name of the robot description to clone.
        commit: If provided, checkout that specific commit of the description.

    Returns:
        Path to the resulting local working directory.

    Notes:
        By default, robot descriptions are cached to
        ``~/.cache/fourier_robot_descriptions``. This behavior can be overriden by
        setting the ``ROBOT_DESCRIPTIONS_CACHE`` environment variable to an
        alternative path.
    """
    try:
        repository = REPOSITORIES[description_name]
    except KeyError as exn:
        raise ImportError(f"Unknown description: {description_name}") from exn

    cache_dir = os.path.expanduser(
        os.environ.get(
            "ROBOT_DESCRIPTIONS_CACHE",
            "~/.cache/fourier_robot_descriptions",
        )
    )

    cache_path = repository.cache_path
    if commit is not None:
        # Requirement: the last directory in the cache path is named after the
        # cache path (more precisely the package name) so that package:// URIs
        # work in frameworks that resolve them via directories
        cache_path = f"{cache_path}-{commit}/{cache_path}"
    target_dir = os.path.join(cache_dir, cache_path)
    clone = clone_to_directory(
        repository.url,
        target_dir,
        commit=repository.commit if commit is None else commit,
    )
    return str(clone.working_dir)


def clear_cache() -> None:
    """Clears the local cache where robot descriptions are stored."""
    cache_dir = os.path.expanduser(
        os.environ.get(
            "ROBOT_DESCRIPTIONS_CACHE",
            "~/.cache/fourier_robot_descriptions",
        )
    )
    shutil.rmtree(cache_dir, ignore_errors=True)
