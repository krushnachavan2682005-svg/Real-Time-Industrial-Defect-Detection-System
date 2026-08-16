import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from pydantic import BaseModel, ValidationError


class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float

class AnnotationObject(BaseModel):
    class_name: str
    bbox: BoundingBox

class ImageAnnotation(BaseModel):
    image_filename: str
    image_width: int
    image_height: int
    objects: List[AnnotationObject]


class AnnotationParseError(Exception):
    """Exception raised when an annotation file cannot be parsed or is malformed."""
    pass


def read_voc_annotation(xml_path: str | Path) -> ImageAnnotation:
    """
    Reads a Pascal VOC XML annotation file and returns an internal ImageAnnotation representation.
    
    Raises:
        AnnotationParseError: If the XML is malformed or missing required fields.
    """
    path = Path(xml_path)
    if not path.exists():
        raise FileNotFoundError(f"Annotation file not found: {path}")

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        raise AnnotationParseError(f"Failed to parse XML file {path}: {e}")

    filename_elem = root.find("filename")
    if filename_elem is None or not filename_elem.text:
        raise AnnotationParseError(f"Missing <filename> in {path}")
    image_filename = filename_elem.text

    size_elem = root.find("size")
    if size_elem is None:
        raise AnnotationParseError(f"Missing <size> in {path}")

    width_elem = size_elem.find("width")
    height_elem = size_elem.find("height")

    if width_elem is None or height_elem is None or not width_elem.text or not height_elem.text:
        raise AnnotationParseError(f"Missing <width> or <height> in {path}")

    try:
        image_width = int(width_elem.text)
        image_height = int(height_elem.text)
    except ValueError:
        raise AnnotationParseError(f"Invalid <width> or <height> values in {path}")

    objects = []
    for obj_elem in root.findall("object"):
        name_elem = obj_elem.find("name")
        if name_elem is None or not name_elem.text:
            continue
            
        class_name = name_elem.text.replace("-", "_")
        
        bndbox_elem = obj_elem.find("bndbox")
        if bndbox_elem is None:
            continue

        try:
            xmin = float(bndbox_elem.findtext("xmin", default=""))
            ymin = float(bndbox_elem.findtext("ymin", default=""))
            xmax = float(bndbox_elem.findtext("xmax", default=""))
            ymax = float(bndbox_elem.findtext("ymax", default=""))

            bbox = BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)
            objects.append(AnnotationObject(class_name=class_name, bbox=bbox))
        except (ValueError, TypeError, ValidationError) as e:
            # We can optionally log here or raise, depending on how strict we want to be.
            # Given instructions say "handle malformed annotation files safely",
            # we'll raise an error to let the validator or caller decide how to proceed.
            raise AnnotationParseError(f"Malformed bounding box in {path}: {e}")

    try:
        return ImageAnnotation(
            image_filename=image_filename,
            image_width=image_width,
            image_height=image_height,
            objects=objects
        )
    except ValidationError as e:
        raise AnnotationParseError(f"Failed to create ImageAnnotation for {path}: {e}")
