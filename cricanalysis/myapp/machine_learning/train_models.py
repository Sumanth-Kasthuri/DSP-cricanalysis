"""
Script to train cricket match prediction models
Run this script to train and save the prediction models
"""
import os
import sys
import django

# Add the project directory to the Python path to allow imports
current_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if current_path not in sys.path:
    sys.path.append(current_path)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cricanalysis.settings')
django.setup()

# Import prediction module
from myapp.services.prediction_service import train_models

if __name__ == "__main__":
    print("Training cricket match prediction models...")
    result = train_models()
    print("Model training complete!")