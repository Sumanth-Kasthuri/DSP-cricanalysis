import os
import logging
from ..machine_learning.match_predictor import MatchPredictor
from .live_prediction_service import calculate_live_prediction

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

def predict_match_outcome(team1_name, team2_name, match_format='ODI', match_details=None):
    """
    Predict the outcome of a cricket match
    
    Args:
        team1_name (str): Name of team 1
        team2_name (str): Name of team 2
        match_format (str): Format of the match ('ODI', 'T20I', 'TEST', or 'IPL')
        match_details (dict, optional): Match details for live prediction during second innings
        
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
    
    logger.info(f"Predicting {format_normalized} match: {team1_name} vs {team2_name}")
        
    try:
        # Get historical prediction first
        predictor = get_match_predictor()
        historical_prediction = predictor.predict_match(format_normalized, team1_name, team2_name)
        
        # If match details are provided, check for live match situation
        if match_details:
            # Check if second innings has started
            second_innings_in_progress = (
                match_details.get('team1_score') and 
                match_details.get('team2_score') and
                'runs' in match_details.get('team1_score', {}) and
                'runs' in match_details.get('team2_score', {})
            )
            
            if second_innings_in_progress:
                logger.info("Second innings in progress, incorporating live match data")
                # Use the live prediction service to get prediction based on match situation
                live_prediction = calculate_live_prediction(match_details)
                
                if live_prediction:
                    # Combine historical and live predictions (50% weight to each)
                    combined_prediction = combine_predictions(
                        historical_prediction, 
                        live_prediction, 
                        team1_name, 
                        team2_name
                    )
                    logger.info(f"Combined prediction result: {combined_prediction}")
                    return combined_prediction
        
        # Return historical prediction only
        logger.info(f"Historical prediction result: {historical_prediction}")
        return historical_prediction
            
    except Exception as e:
        logger.error(f"Error predicting match outcome: {e}")
        # Return a balanced prediction in case of error
        return {
            'team1_probability': 0.5,
            'team2_probability': 0.5,
            'predicted_winner': team1_name if team1_name < team2_name else team2_name,  
            'error': str(e)
        }

def combine_predictions(historical_prediction, live_prediction, team1_name, team2_name):
    """
    Combine historical prediction with live match situation prediction
    
    Args:
        historical_prediction (dict): Prediction based on historical data
        live_prediction (dict): Prediction based on live match situation
        team1_name (str): Name of team 1 (first innings team)
        team2_name (str): Name of team 2 (second innings team)
        
    Returns:
        dict: Combined prediction results
    """
    # Determine which team is batting and which is bowling in the second innings
    batting_team_name = team2_name  
    bowling_team_name = team1_name  
    
    # Get probabilities from historical prediction
    team1_historical_prob = historical_prediction['team1_probability']
    team2_historical_prob = historical_prediction['team2_probability']
    
    # Get probabilities from live prediction
    batting_team_live_prob = live_prediction['batting_team_win_probability'] / 100.0
    bowling_team_live_prob = live_prediction['bowling_team_win_probability'] / 100.0
    
    # Combine with equal weights (50% historical, 50% live)
    team2_combined_prob = (team2_historical_prob * 0.5) + (batting_team_live_prob * 0.5)
    team1_combined_prob = (team1_historical_prob * 0.5) + (bowling_team_live_prob * 0.5)
    
    # Normalise to ensure they sum to 1
    total_prob = team1_combined_prob + team2_combined_prob
    team1_combined_prob = team1_combined_prob / total_prob
    team2_combined_prob = team2_combined_prob / total_prob
    
    # Determine predicted winner based on combined probability
    predicted_winner = team1_name if team1_combined_prob > team2_combined_prob else team2_name
    
    # Create combined prediction result
    combined_prediction = {
        'team1_probability': team1_combined_prob,
        'team2_probability': team2_combined_prob,
        'predicted_winner': predicted_winner,
        'prediction_method': 'combined',
        'feature_importances': {
            'historical_data': 0.5,
            'live_match_situation': 0.5
        },
        'live_match_situation': live_prediction['prediction_factors'],
        'match_situation_explanation': live_prediction['explanation']
    }
    
    return combined_prediction

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
    
    # Determine confidence level 
    confidence = prediction.get('confidence', max(prediction['team1_probability'], prediction['team2_probability']))
    if confidence >= 0.75:
        confidence_text = 'High'
    elif confidence >= 0.6:
        confidence_text = 'Medium'
    else:
        confidence_text = 'Low'
    
    # Get feature importances if available
    feature_importances = prediction.get('feature_importances', {})
    
    # Check if this is a combined prediction (historical + live)
    is_combined_prediction = prediction.get('prediction_method') == 'combined'
    
    if is_combined_prediction:
        # For combined predictions, show weights of historical data and live situation
        h2h_weight_pct = int(round(feature_importances.get('historical_data', 0.5) * 100))
        live_situation_weight_pct = int(round(feature_importances.get('live_match_situation', 0.5) * 100))
        
        # Get the match situation explanation if available
        match_situation_explanation = prediction.get('match_situation_explanation', '')
        
        # Generate explanation text for combined prediction
        explanation = (
            f"Prediction based on {h2h_weight_pct}% historical data and {live_situation_weight_pct}% live match situation. "
            f"{match_situation_explanation}"
        )
        
        result = {
            'team1_name': team1_name,
            'team2_name': team2_name,
            'team1_probability': team1_probability,
            'team2_probability': team2_probability,
            'predicted_winner': predicted_winner,
            'confidence_text': confidence_text,
            'historical_data_weight': h2h_weight_pct,
            'live_situation_weight': live_situation_weight_pct,
            'prediction_method': 'combined',
            'explanation': explanation,
            'match_situation': prediction.get('live_match_situation', {})
        }
    else:
        # For historical predictions only
        h2h_weight_pct = int(round(feature_importances.get('h2h_wins', 0.4) * 100))
        recent_form_weight_pct = int(round(feature_importances.get('recent_form', 0.6) * 100))
        
        # Default method is ML prediction unless specified otherwise
        method = prediction.get('method', 'machine learning')
        
        # Generate explanation text
        if method == 'heuristic':
            explanation = f"Prediction based on {recent_form_weight_pct}% recent form and {h2h_weight_pct}% head-to-head records."
        else:
            explanation = f"Prediction using machine learning with {recent_form_weight_pct}% weight on recent form and {h2h_weight_pct}% on head-to-head records."
        
        result = {
            'team1_name': team1_name,
            'team2_name': team2_name,
            'team1_probability': team1_probability,
            'team2_probability': team2_probability,
            'predicted_winner': predicted_winner,
            'confidence_text': confidence_text,
            'h2h_weight': h2h_weight_pct,
            'recent_form_weight': recent_form_weight_pct, 
            'prediction_method': method,
            'explanation': explanation
        }
    
    return result

def generate_prediction_explanation(prediction, team1_name, team2_name):
    """
    Generate an explanation for the prediction based on the available features
    
    Args:
        prediction (dict): Prediction results from predict_match_outcome
        team1_name (str): Name of team 1
        team2_name (str): Name of team 2
        
    Returns:
        str: Explanation of the prediction
    """
    winner_name = prediction['predicted_winner']
    loser_name = team2_name if winner_name == team1_name else team1_name
    
    # Check if this is a combined prediction with live match situation
    if prediction.get('prediction_method') == 'combined' and 'live_match_situation' in prediction:
        match_situation = prediction['live_match_situation']
        
        if match_situation['wickets_left'] <= 3:
            return f"Prediction heavily influenced by the limited wickets remaining ({match_situation['wickets_left']}) for the chasing team."
        
        if match_situation['required_run_rate'] > 12:
            return f"Prediction reflects the challenging required run rate of {match_situation['required_run_rate']:.2f} runs per over."
        
        if match_situation['required_run_rate'] < 6:
            return f"Prediction considers the manageable required run rate of {match_situation['required_run_rate']:.2f} runs per over."
        
        return f"Prediction combines historical team performance with current match situation."
    
    # For historical predictions only
    features = prediction.get('feature_importances', {})
    
    # Base explanation
    if 'h2h_wins' in features and 'recent_form' in features:
        if features['h2h_wins'] > features['recent_form']:
            return f"Prediction based primarily on head-to-head record between the teams."
        else:
            return f"Prediction based primarily on recent team performance and current form."
    else:
        return f"Prediction based on historical performance data and current team statistics."