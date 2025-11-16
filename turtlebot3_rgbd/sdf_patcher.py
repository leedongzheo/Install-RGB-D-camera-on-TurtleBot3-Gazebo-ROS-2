"""SDF patching helpers for adding an RGB-D camera to TurtleBot3 models."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence
import argparse
import textwrap
import xml.etree.ElementTree as ET


@dataclass(slots=True)
class RGBDCameraConfig:
    """Configuration for the RGB-D camera insertion."""

    parent_link: str = "base_link"
    link_name: str = "rgbd_camera_link"
    joint_name: str = "rgbd_camera_joint"
    sensor_name: str = "rgbd_camera"
    pose: Sequence[float] = (0.0, 0.0, 0.2, 0.0, 0.0, 0.0)
    mass: float = 0.15
    inertial_diagonal: Sequence[float] = (1e-4, 1e-4, 1e-4)
    size: Sequence[float] = (0.05, 0.05, 0.03)
    update_rate: float = 30.0
    horizontal_fov: float = 1.047
    image_width: int = 640
    image_height: int = 480
    clip_near: float = 0.05
    clip_far: float = 10.0
    depth_near: float = 0.1
    depth_far: float = 10.0
    namespace: str = "/turtlebot3"
    color_topic: str = "image"
    depth_topic: str = "image/depth"
    point_cloud_topic: str = "points"
    frame_name: str = "rgbd_camera_link"

    def pose_str(self) -> str:
        if len(self.pose) != 6:
            raise ValueError("pose must have 6 values")
        return " ".join(str(float(v)) for v in self.pose)


class SDFPatcher:
    """Modify TurtleBot3 SDF trees with RGB-D sensor elements."""

    def __init__(self, tree: ET.ElementTree):
        self.tree = tree
        self.model = self._find_model()

    def _find_model(self) -> ET.Element:
        model = self.tree.find(".//model")
        if model is None:
            raise ValueError("Could not find <model> element in SDF")
        return model

    def _find_or_create(self, parent: ET.Element, tag: str, **attrs: str) -> ET.Element:
        elem = parent.find(f"{tag}[@name='{attrs.get('name')}']") if "name" in attrs else None
        if elem is None:
            elem = ET.Element(tag, attrib={k: str(v) for k, v in attrs.items() if v is not None})
            parent.append(elem)
        return elem

    def has_link(self, link_name: str) -> bool:
        return self.model.find(f".//link[@name='{link_name}']") is not None

    def has_joint(self, joint_name: str) -> bool:
        return self.model.find(f".//joint[@name='{joint_name}']") is not None

    def ensure_rgbd_camera(self, config: RGBDCameraConfig) -> bool:
        """Ensure the RGB-D camera elements exist. Returns True if modified."""

        modified = False
        if not self.has_link(config.link_name):
            self.model.append(self._build_link(config))
            modified = True
        if not self.has_joint(config.joint_name):
            self.model.append(self._build_joint(config))
            modified = True
        return modified

    def _build_link(self, config: RGBDCameraConfig) -> ET.Element:
        link = ET.Element("link", {"name": config.link_name})
        pose = ET.SubElement(link, "pose")
        pose.text = config.pose_str()
        inertial = ET.SubElement(link, "inertial")
        mass = ET.SubElement(inertial, "mass")
        mass.text = str(config.mass)
        inertia = ET.SubElement(inertial, "inertia")
        for axis, value in zip(["ixx", "iyy", "izz"], config.inertial_diagonal):
            elem = ET.SubElement(inertia, axis)
            elem.text = str(value)
        visual = ET.SubElement(link, "visual", {"name": f"{config.link_name}_visual"})
        geometry = ET.SubElement(visual, "geometry")
        box = ET.SubElement(geometry, "box")
        size = ET.SubElement(box, "size")
        size.text = " ".join(str(v) for v in config.size)
        material = ET.SubElement(visual, "material")
        script = ET.SubElement(material, "script")
        uri = ET.SubElement(script, "uri")
        uri.text = "file://media/materials/scripts/gazebo.material"
        name = ET.SubElement(script, "name")
        name.text = "Gazebo/Grey"
        collision = ET.SubElement(link, "collision", {"name": f"{config.link_name}_collision"})
        geometry_col = ET.SubElement(collision, "geometry")
        box_col = ET.SubElement(geometry_col, "box")
        size_col = ET.SubElement(box_col, "size")
        size_col.text = size.text
        link.append(self._build_sensor(config))
        return link

    def _build_sensor(self, config: RGBDCameraConfig) -> ET.Element:
        sensor = ET.Element(
            "sensor",
            {
                "name": config.sensor_name,
                "type": "depth",
            },
        )
        sensor.append(self._text_element("pose", config.pose_str()))
        sensor.append(self._text_element("update_rate", config.update_rate))
        sensor.append(self._text_element("visualize", 1))
        sensor.append(self._camera_element(config))
        sensor.append(self._depth_camera_element(config))
        sensor.append(self._plugin_element(config))
        return sensor

    def _camera_element(self, config: RGBDCameraConfig) -> ET.Element:
        camera = ET.Element("camera")
        camera.append(self._text_element("horizontal_fov", config.horizontal_fov))
        image = ET.SubElement(camera, "image")
        image.append(self._text_element("width", config.image_width))
        image.append(self._text_element("height", config.image_height))
        clip = ET.SubElement(camera, "clip")
        clip.append(self._text_element("near", config.clip_near))
        clip.append(self._text_element("far", config.clip_far))
        return camera

    def _depth_camera_element(self, config: RGBDCameraConfig) -> ET.Element:
        depth_camera = ET.Element("depth_camera")
        clip = ET.SubElement(depth_camera, "clip")
        clip.append(self._text_element("near", config.depth_near))
        clip.append(self._text_element("far", config.depth_far))
        return depth_camera

    def _plugin_element(self, config: RGBDCameraConfig) -> ET.Element:
        plugin = ET.Element(
            "plugin",
            {
                "name": "gazebo_ros_rgbd_camera",
                "filename": "libgazebo_ros_depth_camera.so",
            },
        )
        ros = ET.SubElement(plugin, "ros")
        ros.append(self._text_element("namespace", config.namespace))
        ros.append(self._text_element("argument", f"camera:={config.color_topic}"))
        ros.append(self._text_element("argument", f"depth:={config.depth_topic}"))
        ros.append(self._text_element("argument", f"points:={config.point_cloud_topic}"))
        plugin.append(self._text_element("frame_name", config.frame_name))
        plugin.append(self._text_element("output", "screen"))
        return plugin

    def _build_joint(self, config: RGBDCameraConfig) -> ET.Element:
        joint = ET.Element(
            "joint",
            {
                "name": config.joint_name,
                "type": "fixed",
            },
        )
        joint.append(self._text_element("parent", config.parent_link))
        joint.append(self._text_element("child", config.link_name))
        joint.append(self._text_element("pose", "0 0 0 0 0 0"))
        return joint

    @staticmethod
    def _text_element(tag: str, value: object) -> ET.Element:
        elem = ET.Element(tag)
        elem.text = str(value)
        return elem

    def write(self, path: Path) -> None:
        self.tree.write(path, encoding="utf-8", xml_declaration=True)


def load_tree(path: Path) -> ET.ElementTree:
    return ET.parse(path)


def patch_file(
    path: Path,
    *,
    config: RGBDCameraConfig | None = None,
    dry_run: bool = False,
    output: Path | None = None,
) -> bool:
    """Patch a model.sdf file in-place or to an output path."""

    config = config or RGBDCameraConfig()
    tree = load_tree(path)
    patcher = SDFPatcher(tree)
    modified = patcher.ensure_rgbd_camera(config)
    if modified and not dry_run:
        destination = output or path
        patcher.write(destination)
    return modified


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inject an RGB-D camera into a TurtleBot3 model.sdf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """Example::
                python -m turtlebot3_rgbd.cli ~/ros2_ws/src/turtlebot3/turtlebot3_description/urdf/model.sdf \\
                    --namespace /tb3 --pose 0 0 0.2 0 0 0
            """
        ),
    )
    parser.add_argument("sdf", type=Path, help="Path to the model.sdf file")
    parser.add_argument("--parent-link", default="base_link")
    parser.add_argument("--link-name", default="rgbd_camera_link")
    parser.add_argument("--joint-name", default="rgbd_camera_joint")
    parser.add_argument("--sensor-name", default="rgbd_camera")
    parser.add_argument("--namespace", default="/turtlebot3")
    parser.add_argument("--pose", nargs=6, type=float, default=(0.0, 0.0, 0.2, 0.0, 0.0, 0.0))
    parser.add_argument("--dry-run", action="store_true", help="Only report if patching is needed")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path")
    parser.add_argument("--color-topic", default="image")
    parser.add_argument("--depth-topic", default="image/depth")
    parser.add_argument("--points-topic", default="points")
    parser.add_argument("--image-width", type=int, default=640)
    parser.add_argument("--image-height", type=int, default=480)
    parser.add_argument("--update-rate", type=float, default=30.0)
    return parser


def parse_config(args: argparse.Namespace) -> RGBDCameraConfig:
    return RGBDCameraConfig(
        parent_link=args.parent_link,
        link_name=args.link_name,
        joint_name=args.joint_name,
        sensor_name=args.sensor_name,
        namespace=args.namespace,
        pose=tuple(args.pose),
        color_topic=args.color_topic,
        depth_topic=args.depth_topic,
        point_cloud_topic=args.points_topic,
        image_width=args.image_width,
        image_height=args.image_height,
        update_rate=args.update_rate,
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = parse_config(args)
    modified = patch_file(
        args.sdf,
        config=config,
        dry_run=args.dry_run,
        output=args.output,
    )
    if modified:
        print("RGB-D camera configuration inserted")
        return 0
    print("RGB-D camera already configured; no changes made")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
