import argparse
import os
from ultralytics import YOLO

def main():
    # १. युझरकडून इमेजचा पाथ घेण्यासाठी सेटअप
    parser = argparse.ArgumentParser(description="Test YOLO model on a single image.")
    parser.add_argument("--image", type=str, required=True, help="Path to the image file")
    args = parser.parse_args()

    image_path = args.image

    if not os.path.exists(image_path):
        print(f"Error: इमेज सापडली नाही - {image_path}")
        return

    # २. आपले ट्रेन झालेले मॉडेल लोड करा
    model_path = "models/pytorch/baseline_yolov8n/best.pt"
    if not os.path.exists(model_path):
        print(f"Error: मॉडेल फाईल सापडली नाही - {model_path}")
        return

    print("मॉडेल लोड होत आहे...")
    model = YOLO(model_path)

    # ३. इमेजवर प्रेडिक्शन करा
    print(f"इमेज टेस्ट करत class शोधत आहे: {image_path}\n")
    results = model.predict(source=image_path, save=True, conf=0.25, verbose=False)

    # ४. रिझल्ट्स स्क्रीनवर दाखवा
    print("-" * 50)
    print("डिटेक्शन रिझल्ट्स (Detection Results):")
    print("-" * 50)
    
    for result in results:
        boxes = result.boxes
        if len(boxes) == 0:
            print("या इमेजमध्ये कोणताही डिफेक्ट (Defect) सापडला नाही! (No defects found)")
        else:
            for box in boxes:
                # Class ID (उदा. 0, 1, 2)
                class_id = int(box.cls[0].item())
                # Class चे नाव (उदा. crazing, patches)
                class_name = model.names[class_id]
                # Confidence Score (खात्री)
                conf = box.conf[0].item() * 100
                
                print(f"-> सापडलेला डिफेक्ट: **{class_name}** (खात्री: {conf:.2f}%)")
                
    print("-" * 50)
    print("टीप: ज्या इमेजवर बॉक्स काढले आहेत ती इमेज 'runs/detect/predict' या फोल्डरमध्ये सेव्ह झाली आहे.")

if __name__ == "__main__":
    main()
