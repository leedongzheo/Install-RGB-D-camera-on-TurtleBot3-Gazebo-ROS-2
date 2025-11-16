from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET

from pathlib import Path

import pytest

from turtlebot3_rgbd import RGBDCameraConfig, patch_file


SIMPLE_SDF = """<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='turtlebot3_waffle'>
    <link name='base_link'/>
  </model>
</sdf>
"""


def write_sdf(path: Path) -> None:
    path.write_text(SIMPLE_SDF)


def read_tree(path: Path) -> ET.ElementTree:
    return ET.parse(path)


def test_patch_adds_rgbd_camera(tmp_path: Path) -> None:
    sdf = tmp_path / "model.sdf"
    write_sdf(sdf)

    modified = patch_file(sdf)

    assert modified is True
    tree = read_tree(sdf)
    model = tree.find(".//model")
    assert model is not None
    link = model.find(".//link[@name='rgbd_camera_link']")
    joint = model.find(".//joint[@name='rgbd_camera_joint']")
    assert link is not None
    assert joint is not None
    sensor = link.find("sensor[@type='depth']")
    assert sensor is not None
    plugin = sensor.find("plugin[@filename='libgazebo_ros_depth_camera.so']")
    assert plugin is not None


def test_patch_is_idempotent(tmp_path: Path) -> None:
    sdf = tmp_path / "model.sdf"
    write_sdf(sdf)

    first = patch_file(sdf)
    second = patch_file(sdf)

    assert first is True
    assert second is False

    tree = read_tree(sdf)
    sensors = tree.findall(".//sensor[@name='rgbd_camera']")
    assert len(sensors) == 1


def test_cli_dry_run_reports_status(tmp_path: Path) -> None:
    sdf = tmp_path / "model.sdf"
    write_sdf(sdf)

    cmd = [
        sys.executable,
        "-m",
        "turtlebot3_rgbd.cli",
        str(sdf),
        "--dry-run",
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "RGB-D camera configuration inserted" in result.stdout

    # After patch the CLI should indicate no change
    patch_file(sdf)
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    assert "already configured" in result.stdout
