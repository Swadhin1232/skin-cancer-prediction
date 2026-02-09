class PredictionForm {
    constructor() {
        this.form = document.getElementById('predictionForm');
        this.uploadArea = document.getElementById('uploadArea');
        this.imagePreview = document.getElementById('imagePreview');
        this.locationSelect = document.getElementById('localization');
        this.modal = document.getElementById('resultModal');
        this.fileInput = document.getElementById('image');
        
        this.locations = [
            'Scalp', 'Ear', 'Face', 'Back', 'Trunk', 'Chest',
            'Upper Extremity', 'Abdomen', 'Lower Extremity',
            'Genital', 'Neck', 'Hand', 'Foot', 'Acral'
        ];

        this.init();
    }

    init() {
        this.populateLocations();
        this.setupEventListeners();
        this.setupImageUpload();
    }

    populateLocations() {
        this.locations.forEach(location => {
            const option = document.createElement('option');
            option.value = location.toLowerCase().replace(' ', '_');
            option.textContent = location;
            this.locationSelect.appendChild(option);
        });
    }

    setupEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        document.querySelector('.close-modal').addEventListener('click', 
            () => this.modal.style.display = 'none');
    }

    setupImageUpload() {
        this.uploadArea.addEventListener('click', (e) => {
            if (e.target !== this.fileInput) {
                this.fileInput.click();
            }
        });
        
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length) {
                this.fileInput.files = files;
                this.handleFileSelect(files[0]);
            }
        });

        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleFileSelect(e.target.files[0]);
            }
        });
    }

    handleFileSelect(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.imagePreview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <div class="image-name">${file.name}</div>
            `;
            this.imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    async handleSubmit(e) {
        e.preventDefault();
        const submitBtn = this.form.querySelector('.submit-btn');
        
        try {
            submitBtn.disabled = true;
            submitBtn.querySelector('.btn-text').textContent = 'Analyzing...';
            submitBtn.querySelector('.loading-spinner').style.display = 'block';

            const formData = new FormData(this.form);
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(await response.text());
            }

            const results = await response.json();
            this.showResults(results);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during analysis. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.querySelector('.btn-text').textContent = 'Analyze Image';
            submitBtn.querySelector('.loading-spinner').style.display = 'none';
        }
    }

    showResults(results) {
        const modal = document.getElementById('resultModal');
        const mainPrediction = results.predictions[0];
        
        modal.querySelector('.diagnosis-type').innerHTML = `
            <h4>${mainPrediction.diagnosis}</h4>
            <p class="risk-level ${mainPrediction.riskLevel.toLowerCase()}-risk">
                ${mainPrediction.riskLevel} Risk
            </p>
            <p class="user-inputs">
                Age: ${results.userInputs.age} | 
                Sex: ${results.userInputs.sex} | 
                Location: ${results.userInputs.localization}
            </p>
        `;

        const progressBar = modal.querySelector('.progress');
        progressBar.style.width = `${mainPrediction.probability * 100}%`;
        progressBar.textContent = `${Math.round(mainPrediction.probability * 100)}%`;

        modal.querySelector('.analysis-content').innerHTML = `
            <p>${mainPrediction.description}</p>
            <h4>Possible Treatments:</h4>
            <ul>
                ${mainPrediction.treatments.map(treatment => `<li>${treatment}</li>`).join('')}
            </ul>
        `;

        const recList = modal.querySelector('.recommendations-list');
        recList.innerHTML = results.recommendations
            .map(rec => `<li>${rec}</li>`)
            .join('');

        modal.style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new PredictionForm();
});