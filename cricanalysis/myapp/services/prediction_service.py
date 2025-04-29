"""
Prediction Service
This module serves as an interface between the Django application and machine learning models.
It handles match outcome prediction requests from views.
"""
import os
import logging
from ..machine_learning.match_predictor import MatchPredictor

# Configure logging
logger = logging.getLogger(__name__)

# Singleton pattern for the match predictor
_match_predictor = None

def get_match_predictor():
    """Get or create a MatchPredictor instance (singleton pattern)"""
    global _match_predictor
    if _match_predictor is None:
        _match_predictor = MatchPredictor()
    return _match_predictor

def train_models():
    """Train all machine learning models"""
    predictor = get_match_predictor()
    return predictor.train_all_models()

def predict_match_outcome(team1_name, team2_name, match_format='ODI'):
    """
    Predict the outcome of a cricket match
    
    Args:
        team1_name (str): Name of team 1
        team2_name (str): Name of team 2
        match_format (str): Format of the match ('ODI', 'T20I', 'TEST', or 'IPL')
        
    Returns:
        dict: Prediction results with probabilities
    """
    # Normalize match format
    if match_format.upper() == 'T20' or match_format.upper() == 'T20I':
        format_normalized = 'T20I'
    elif match_format.upper() == 'ODI' or match_format.upper() == 'OD':
        format_normalized = 'ODI'
    elif match_format.upper() in ['TEST', 'TESTS', 'TEST MATCH']:
        format_normalized = 'TEST'
    elif match_format.upper() == 'IPL':
        format_normalized = 'IPL'
    else:
        logger.warning(f"Unknown match format: {match_format}, defaulting to ODI")
        format_normalized = 'ODI'
        
    try:
        predictor = get_match_predictor()
        prediction = predictor.predict_match(format_normalized, team1_name, team2_name)
        return prediction
    except Exception as e:
        logger.error(f"Error predicting match outcome: {e}")
        # Return a balanced prediction in case of error
        return {
            'team1_probability': 0.5,
            'team2_probability': 0.5,
            'predicted_winner': team1_name if team1_name < team2_name else team2_name,  # Arbitrary choice
            'error': str(e)
        }

def format_prediction_for_display(prediction, team1_name, team2_name):
    """
    Format prediction results for display in a template
    
    Args:
        prediction (dict): Prediction results from predict_match_outcome
        team1_name (str): Name of team 1
        team2_name (str): Name of team 2
        
    Returns:
        dict: Formatted prediction for display
    """
    # If there was an error in prediction
    if 'error' in prediction:
        return {
            'team1_name': team1_name,
            'team2_name': team2_name,
            'team1_probability': 50,
            'team2_probability': 50,
            'predicted_winner': 'Unknown',
            'confidence_text': 'Low',
            'error_message': prediction['error']
        }
    
    # Format probabilities as percentages for display
    team1_probability = int(round(prediction['team1_probability'] * 100))
    team2_probability = int(round(prediction['team2_probability'] * 100))
    
    # Get predicted winner
    predicted_winner = prediction['predicted_winner']
    
    # Determine confidence level text
    confidence = prediction.get('confidence', max(prediction['team1_probability'], prediction['team2_probability']))
    if confidence >= 0.75:
        confidence_text = 'High'
    elif confidence >= 0.6:
        confidence_text = 'Medium'
    else:
        confidence_text = 'Low'
    
    return {
        'team1_name': team1_name,
        'team2_name': team2_name,
        'team1_probability': team1_probability,
        'team2_probability': team2_probability,
        'predicted_winner': predicted_winner,
        'confidence_text': confidence_text
    }