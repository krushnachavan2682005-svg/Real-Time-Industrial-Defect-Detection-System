import pytest
from src.data.annotation_validator import validate_annotation, AnnotationValidationError
from src.data.annotation_reader import ImageAnnotation, AnnotationObject, BoundingBox

@pytest.fixture
def valid_classes():
    return {
        "crazing": 0,
        "inclusion": 1,
        "patches": 2
    }

def test_validate_annotation_valid(valid_classes):
    annotation = ImageAnnotation(
        image_filename="test.jpg",
        image_width=200,
        image_height=200,
        objects=[
            AnnotationObject(
                class_name="crazing",
                bbox=BoundingBox(xmin=10, ymin=10, xmax=50, ymax=50)
            )
        ]
    )
    errors = validate_annotation(annotation, valid_classes)
    assert len(errors) == 0

def test_validate_annotation_invalid_dims(valid_classes):
    annotation = ImageAnnotation(
        image_filename="test.jpg",
        image_width=0,
        image_height=200,
        objects=[]
    )
    with pytest.raises(AnnotationValidationError):
        validate_annotation(annotation, valid_classes)

def test_validate_annotation_unknown_class(valid_classes):
    annotation = ImageAnnotation(
        image_filename="test.jpg",
        image_width=200,
        image_height=200,
        objects=[
            AnnotationObject(
                class_name="unknown",
                bbox=BoundingBox(xmin=10, ymin=10, xmax=50, ymax=50)
            )
        ]
    )
    errors = validate_annotation(annotation, valid_classes)
    assert len(errors) == 1
    assert "Unknown class 'unknown'" in errors[0]

def test_validate_annotation_invalid_bbox(valid_classes):
    annotation = ImageAnnotation(
        image_filename="test.jpg",
        image_width=200,
        image_height=200,
        objects=[
            AnnotationObject(
                class_name="crazing",
                bbox=BoundingBox(xmin=50, ymin=50, xmax=10, ymax=10) # Reversed
            )
        ]
    )
    errors = validate_annotation(annotation, valid_classes)
    assert len(errors) == 1
    assert "Invalid bounding box" in errors[0]

def test_validate_annotation_out_of_bounds(valid_classes):
    annotation = ImageAnnotation(
        image_filename="test.jpg",
        image_width=200,
        image_height=200,
        objects=[
            AnnotationObject(
                class_name="crazing",
                bbox=BoundingBox(xmin=250, ymin=250, xmax=300, ymax=300) # Completely outside
            )
        ]
    )
    errors = validate_annotation(annotation, valid_classes)
    assert len(errors) == 1
    assert "completely outside image boundaries" in errors[0]
