# AI Skin Analyzer

An application that analyses a face image to detect acne and recommends suitable skincare products based on the result. Built as a Software Engineering course project.

## Features
- Upload a face photo and detect acne
- Face detection step before analysis
- Product recommendations based on the detected skin condition
- Web interface (Glowra UI)
- [Live camera input: add only if it works, otherwise put it under Future work]

## How it works
1. The user uploads a face image through the web app.
2. The face is detected and the skin region is analysed by a model trained on the **ACNE04** acne dataset.
3. The detected condition is mapped to suitable skincare products.
4. The result and recommendations are shown to the user.

## Tech stack
- Language: Python
- Model: [model type, e.g. YOLO object detection, trained on ACNE04. Confirm from `requirements.txt` and `train_acne04.py`]
- Web app: [Flask / Streamlit, confirm in `app.py`] with HTML templates and the Glowra UI
- Libraries: [list from `requirements.txt`]

## Project structure
```
app.py                 Web application
skin_analyzer.py       Core analysis and recommendation logic
face_detection.py      Face detection
prepare_acne04.py      Prepares the ACNE04 dataset
train_acne04.py        Trains the model
inspect_acne_dataset.py  Dataset inspection
download_datasets.py   Dataset download helper
templates/ static/ glowra-ui/   Front-end
REPORT.md              Project report
```

## How to run
1. Clone the repository.
2. Install requirements: `pip install -r requirements.txt`
3. Download the trained model `best.pt` from the **Releases** page and place it [in the project folder, check the path used in `app.py`].
4. Run: `[python app.py]`
5. Open [http://localhost:5000, or the address shown in the terminal].

## Dataset
Trained on the ACNE04 dataset, which is not included in this repository. 

## Limitations and future work
- Accuracy depends on image quality, lighting and the training data, so it is not a medical diagnosis tool.
- Planned: live camera input, more skin conditions and skin tones, and a larger, more diverse dataset.

## Note
Made for learning purposes. Recommendations are general and not medical advice.
