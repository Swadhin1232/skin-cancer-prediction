from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import io
import logging
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure static folder
app.static_folder = 'static'

try:
    model = load_model('model.h5')
    logger.info("Model loaded successfully")
    logger.info(f"Model input shape: {model.input_shape}")
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    model = None

# Define the class names and mappings
class_names = ['akiec', 'bcc', 'bkl', 'df', 'nv', 'vasc', 'mel']

# Mappings for categorical variables
sex_mapping = {
    'male': 0,
    'female': 1
}

localization_mapping = {
    'scalp': 0, 'ear': 1, 'face': 2, 'back': 3, 'trunk': 4, 
    'chest': 5, 'upper_extremity': 6, 'abdomen': 7, 'lower_extremity': 8,
    'genital': 9, 'neck': 10, 'hand': 11, 'foot': 12, 'acral': 13
}

def get_skin_condition_info(class_name):
    """Return information about skin conditions based on class name"""
    skin_info = {
        'akiec': {
            'name': 'Actinic Keratoses & Intraepithelial Carcinoma',
            'risk_level': 'Medium to High',
            'description': "Precancerous lesions arising from prolonged UV exposure. Can progress to intraepithelial carcinoma/Bowen's disease, where atypical cells invade the epidermis.",
            'treatments': [
                'Topical treatments (Fluorouracil, imiquimod, diclofenac)',
                'Photodynamic therapy (PDT)',
                'Surgical excision',
                'Cryotherapy',
                'Curettage and electrodesiccation'
            ]
        },
        'bcc': {
            'name': 'Basal Cell Carcinoma',
            'risk_level': 'High',
            'description': 'The most common type of skin cancer that causes lumps, bumps or lesions on the epidermis. Appears in sun-exposed areas. Types include nodular, superficial spreading, sclerosing, and pigmented.',
            'treatments': [
                'Electrodessication and curettage',
                'Surgery',
                'Cryotherapy',
                'Chemotherapy',
                'Photodynamic therapy',
                'Laser therapy'
            ]
        },
        'bkl': {
            'name': 'Benign Keratosis-like Lesions',
            'risk_level': 'Low',
            'description': 'Common, harmless skin growths appearing as small, dark or light brown patches or bumps. Includes solar lentigines, seborrheic keratoses, and lichen-planus like keratoses.',
            'treatments': [
                'Electrodesiccation and curettage',
                'Cryosurgery',
                'Topical 5-Fluorouracil',
                'Laser resurfacing',
                'Dermabrasion',
                'Observation (if asymptomatic)'
            ]
        },
        'df': {
            'name': 'Dermatofibroma',
            'risk_level': 'Low',
            'description': 'Common benign fibrous nodule usually found on the legs. Size varies from 0.5-1.5 cm diameter. Shows characteristic dimpling when pinched. Can appear pink to light brown in white skin, and dark brown to black in dark skin.',
            'treatments': [
                'Surgical removal (if symptomatic)',
                'Cryotherapy',
                'Shave biopsy',
                'Laser treatments',
                'Observation (most cases)'
            ]
        },
        'mel': {
            'name': 'Melanoma',
            'risk_level': 'Very High',
            'description': 'The most dangerous type of skin cancer that begins in melanocytes (pigment-making cells). Can develop in eyes, mouth, genitals, and anal area. Early detection is crucial for successful treatment.',
            'treatments': [
                'Surgery to remove cancerous lesion',
                'Chemotherapy',
                'Targeted therapy',
                'Immunotherapy (biologic therapy)',
                'Regular monitoring post-treatment'
            ]
        },
        'nv': {
            'name': 'Melanocytic Nevi',
            'risk_level': 'Low to Medium',
            'description': 'Common benign skin lesions (moles) due to local proliferation of pigment cells (melanocytes). Can be present at birth (congenital) or appear later (acquired). Contains melanin pigment.',
            'treatments': [
                'Excision biopsy (for suspicious moles)',
                'Shave biopsy',
                'Electrosurgical destruction',
                'Laser treatment',
                'Regular monitoring'
            ]
        },
        'vasc': {
            'name': 'Vascular Lesions',
            'risk_level': 'Low to Medium',
            'description': 'Abnormal growths of blood vessels in the skin. Includes angiomas (cherry hemangiomas), angiokeratomas, pyogenic granulomas, and hemorrhage conditions.',
            'treatments': [
                'Observation for benign angiomas',
                'Surgical excision',
                'Cryotherapy',
                'Laser therapy',
                'Treatment of underlying cause for hemorrhage'
            ]
        }
    }
    return skin_info.get(class_name, None)

def preprocess_user_inputs(age, sex, localization):
    """Preprocess user inputs to match model expectations"""
    # Scale age (assuming the model was trained with StandardScaler)
    scaler = StandardScaler()
    age_scaled = scaler.fit_transform([[float(age)]])[0][0]
    
    # Encode categorical variables
    sex_encoded = sex_mapping.get(sex.lower(), 0)
    localization_encoded = localization_mapping.get(localization.lower(), 0)
    
    # Create a 4-element array to match model input shape
    return np.array([[age_scaled, sex_encoded, localization_encoded, 0]])  # Added padding

def preprocess_image(img_bytes):
    """Preprocess image to match model input shape (28x28x3)"""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # Resize to 28x28 to match model input shape
        img = img.resize((28, 28))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = img_array / 255.0
        return img_array
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict_page():
    return render_template('predict.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        logger.info("Received prediction request")
        
        if model is None:
            return jsonify({'error': 'Model not initialized'}), 500

        # Get image file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        image_file = request.files['image']
        
        # Get user inputs
        age = request.form.get('age', '30')
        sex = request.form.get('sex', 'male')
        localization = request.form.get('localization', 'back')
        
        # Preprocess image
        img_bytes = image_file.read()
        if not img_bytes:
            return jsonify({'error': 'Empty image content'}), 400
        processed_image = preprocess_image(img_bytes)
        
        # Preprocess user inputs
        user_inputs = preprocess_user_inputs(age, sex, localization)
        
        # Debug logging
        logger.debug(f"Image shape: {processed_image.shape}")
        logger.debug(f"User inputs shape: {user_inputs.shape}")
        
        # Make prediction
        predictions = model.predict([processed_image, user_inputs], verbose=0)
        
        # Get top 3 predictions
        top_indices = np.argsort(predictions[0])[-3:][::-1]
        
        results = []
        for idx in top_indices:
            class_name = class_names[idx]
            probability = float(predictions[0][idx])
            condition_info = get_skin_condition_info(class_name)
            
            if condition_info:  # Check if condition_info exists
                results.append({
                    'diagnosis': condition_info['name'],
                    'probability': probability,
                    'riskLevel': condition_info.get('risk_level', 'Medium'),
                    'description': condition_info['description'],
                    'treatments': condition_info['treatments']
                })
        
        response = {
            'predictions': results,
            'userInputs': {
                'age': age,
                'sex': sex,
                'localization': localization,
            },
            'recommendations': [
                'Consult with a healthcare professional for proper diagnosis',
                'Regular skin examinations are recommended',
                'Document any changes in skin lesions'
            ]
        }
        
        logger.info("Successfully generated prediction response")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)