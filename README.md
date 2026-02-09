📌 README.md (Copy Everything Below)
# 🩺 Skin Cancer Classification Web Application

A deep learning–based web application for **skin cancer classification** using dermoscopic images.  
This project uses a trained Convolutional Neural Network (CNN) model and provides a simple web interface for image upload and prediction.

---

## 🚀 Features
- Skin cancer classification using deep learning
- Web-based interface for image upload
- Prediction using a trained CNN model
- Flask-based backend
- Clean and modular project structure

---

## 🛠️ Tech Stack
- **Programming Language:** Python  
- **Framework:** Flask  
- **Deep Learning:** TensorFlow / Keras  
- **Frontend:** HTML, CSS  
- **Dataset:** HAM10000 (not included in repository)

---

## 📂 Project Structure


Skin_Cancer_Classification_Web_Using_DeepLearning/
│
├── app.py # Main Flask application
├── templates/ # HTML templates
├── static/ # CSS and static files
├── requirements.txt # Project dependencies
├── README.md # Project documentation
├── how to run.txt # Execution steps
└── skin-cancer-classification.ipynb # Model training notebook


---

## ⚠️ Important Note
> Due to GitHub size limitations, **dataset files and trained model files (.h5 / .keras)** are **not included** in this repository.

- Dataset used: **HAM10000 Skin Lesion Dataset**
- Trained models are excluded for repository cleanliness

---

## ▶️ How to Run the Project

1. Clone the repository:
```bash
git clone https://github.com/Swadhin1232/skin-cancer-prediction.git


Navigate to the project folder:

cd Skin_Cancer_Classification_Web_Using_DeepLearning-master


Create and activate virtual environment:

python -m venv venv
venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Run the application:

python app.py
