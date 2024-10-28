import argparse
import json
import sys
import cv2
from glasses_detector import GlassesClassifier


def analyze(image_path):
    """
    Analyzes an image to determine face position, size, and whether the person is wearing glasses.
    Returns: dict with analysis results
    """
    try:
        # Read image
        img = cv2.imread(image_path)

        # Get image dimensions
        height, width = img.shape[:2]
        img_area = height * width

        # Detect face
        face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return {
                "success": False,
                "error": "No face detected in image"
            }

        if len(faces) > 1:
            return {
                "success": False,
                "error": "Multiple faces detected - only one face allowed"
            }

        # Get face dimensions
        x, y, w, h = faces[0]
        face_area = w * h
        face_area_ratio = face_area / img_area
        face_height_ratio = h / height

        # Check if the person is wearing opaque or semi-transparent glasses
        classifier = GlassesClassifier(kind="sunglasses")
        wearing_glasses = classifier.process_file(
            input_path=image_path,
            format="bool"
        )

        # Calculate image center
        img_center_x = width // 2
        img_center_y = height // 2

        # Calculate face center
        face_center_x = x + w//2
        face_center_y = y + h//2

        # Add face position assessment
        offset_x = abs(face_center_x - img_center_x) / width
        offset_y = abs(face_center_y - img_center_y) / height

        # Create results dictionary
        results = {
            "success": True,
            "face_detected": True,
            "face_area_ratio": face_area_ratio,
            "face_height_ratio": face_height_ratio,
            "horizontal_offset": offset_x,
            "vertical_offset": offset_y,
            "wearing_glasses": wearing_glasses
        }

        return results

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def validate_headshot(image_path):
    """
    Checks if an image is a valid headshot: The face must be visible,
    sufficiently large, centered, and the person must not be wearing
    opaque/semi-transparent glasses obstructing the eyes.
    Returns: 0 if headshot is valid, 1 if headshot is invalid
    """
    # Read configuration from config.json
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    print(f"\nAnalyzing {image_path}...")
    results = analyze(image_path)

    if results["success"]:
        # Check if the face meets the size requirement
        face_size_requirement = results["face_area_ratio"] > config["face_area_ratio_threshold"] and results[
            "face_height_ratio"] > config["face_height_ratio_threshold"]
        face_centered_requirement = results["horizontal_offset"] < config[
            "horizontal_offset_threshold"] and results["vertical_offset"] < config["vertical_offset_threshold"]
        if face_size_requirement and face_centered_requirement and not results['wearing_glasses']:
            print("Headshot is valid")
            return 0
        else:
            print("Headshot is invalid")
            return 1
    else:
        print(f"Error: {results['error']}")
        print("Image is invalid")
        return 1


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--image-path', type=str,
                        help='Path to the image file', required=True)
    args = parser.parse_args()
    # Run the analysis
    valid = validate_headshot(args.image_path)
    sys.exit(valid)
