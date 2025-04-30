"""
Match Prediction Module
This module provides functionality to predict cricket match outcomes
using machine learning models trained on historical match data.
"""
import os
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

class MatchPredictor:
    """
    Class to handle cricket match outcome predictions using machine learning
    """
    def __init__(self):
        """Initialize the match predictor with paths to models and data"""
        # Get base directory paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        
        # Data paths
        self.data_dir = os.path.join(self.base_dir, 'data', 'processed')
        
        # Model file paths
        self.odi_model_path = os.path.join(self.model_dir, 'odi_model.pkl')
        self.t20i_model_path = os.path.join(self.model_dir, 't20i_model.pkl')
        self.test_model_path = os.path.join(self.model_dir, 'test_model.pkl')
        self.ipl_model_path = os.path.join(self.model_dir, 'ipl_model.pkl')
        
        # Initialize models
        self.odi_model = None
        self.t20i_model = None
        self.test_model = None
        self.ipl_model = None
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load models if they exist
        self.load_models()
    
    def load_models(self):
        """Load pre-trained models if they exist"""
        try:
            if os.path.exists(self.odi_model_path):
                with open(self.odi_model_path, 'rb') as f:
                    self.odi_model = pickle.load(f)
                print("ODI model loaded successfully")
            
            if os.path.exists(self.t20i_model_path):
                with open(self.t20i_model_path, 'rb') as f:
                    self.t20i_model = pickle.load(f)
                print("T20I model loaded successfully")
                    
            if os.path.exists(self.test_model_path):
                with open(self.test_model_path, 'rb') as f:
                    self.test_model = pickle.load(f)
                print("Test match model loaded successfully")
                    
            if os.path.exists(self.ipl_model_path):
                with open(self.ipl_model_path, 'rb') as f:  # Fixed typo here
                    self.ipl_model = pickle.load(f)
                print("IPL model loaded successfully")
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def train_all_models(self):
        """Train all models using the processed CSV data"""
        self.train_odi_model()
        self.train_t20i_model()
        self.train_test_model()
        self.train_ipl_model()
    
    def train_odi_model(self):
        """Train a model using ODI match data"""
        odi_data_path = os.path.join(self.data_dir, 'odi_match_features.csv')
        self._train_model(odi_data_path, self.odi_model_path, 'ODI')
    
    def train_t20i_model(self):
        """Train a model using T20I match data"""
        t20i_data_path = os.path.join(self.data_dir, 't20i_match_features.csv')
        self._train_model(t20i_data_path, self.t20i_model_path, 'T20I')
    
    def train_test_model(self):
        """Train a model using Test match data"""
        test_data_path = os.path.join(self.data_dir, 'test_match_features.csv')
        self._train_model(test_data_path, self.test_model_path, 'TEST')
    
    def train_ipl_model(self):
        """Train a model using IPL match data"""
        ipl_data_path = os.path.join(self.data_dir, 'ipl_match_features.csv')
        self._train_model(ipl_data_path, self.ipl_model_path, 'IPL')
    
    def _train_model(self, data_path, model_path, format_name):
        """Train a model using the specified data file and save it"""
        print(f"Training {format_name} model...")
        try:
            if not os.path.exists(data_path):
                print(f"Data file not found for {format_name}: {data_path}")
                return False
                
            # Read data
            df = pd.read_csv(data_path)
            
            # Drop rows with missing winner information
            df = df.dropna(subset=['winner'])
            
            print(f"Training {format_name} model with {len(df)} matches")
            
            # Prepare features and target
            X = df[[
                'team1_wins_h2h', 'team2_wins_h2h', 
                'team1_win_pct_h2h', 'team2_win_pct_h2h',
                'team1_recent_wins', 'team2_recent_wins', 
                'team1_win_pct', 'team2_win_pct'
            ]]
            
            # Create label encoder for target
            le = LabelEncoder()
            y = le.fit_transform(df['winner'])
            
            # Train random forest classifier
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Save the model and label encoder
            model_dict = {
                'model': model,
                'label_encoder': le,
                'team_names': df[['team1', 'team2']].values.flatten().tolist()
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_dict, f)
                
            # Update instance model
            if format_name == 'ODI':
                self.odi_model = model_dict
            elif format_name == 'T20I':
                self.t20i_model = model_dict
            elif format_name == 'TEST':
                self.test_model = model_dict
            elif format_name == 'IPL':
                self.ipl_model = model_dict
                
            print(f"Successfully trained and saved {format_name} model")
            return True
        except Exception as e:
            print(f"Error training {format_name} model: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_team_stats(self, team1, team2, match_format):
        """
        Fetch team statistics for prediction
        
        Args:
            team1 (str): Name of team 1
            team2 (str): Name of team 2
            match_format (str): 'ODI', 'T20I', 'TEST', or 'IPL'
            
        Returns:
            tuple: (team1_stats, team2_stats) or None if data not found
        """
        try:
            # Determine which data file to use
            if match_format == 'ODI':
                data_path = os.path.join(self.data_dir, 'odi_match_features.csv')
            elif match_format == 'T20I' or match_format == 'T20':
                data_path = os.path.join(self.data_dir, 't20i_match_features.csv')
            elif match_format == 'TEST':
                data_path = os.path.join(self.data_dir, 'test_match_features.csv')
            elif match_format == 'IPL':
                data_path = os.path.join(self.data_dir, 'ipl_match_features.csv')
            else:
                print(f"Unknown match format: {match_format}")
                return None
                
            # Check if data file exists
            if not os.path.exists(data_path):
                print(f"Data file not found: {data_path}")
                return None
                
            # Read data
            df = pd.read_csv(data_path)
            
            # Look for recent matches between these teams
            recent_matches = df[
                ((df['team1'] == team1) & (df['team2'] == team2)) | 
                ((df['team1'] == team2) & (df['team2'] == team1))
            ].sort_values(by='match_id', ascending=False)
            
            if len(recent_matches) > 0:
                # Found previous matches between these teams
                last_match = recent_matches.iloc[0]
                
                # Check if teams are in same order as in the data
                if last_match['team1'] == team1 and last_match['team2'] == team2:
                    # Teams match the order in data
                    team1_stats = {
                        'wins_h2h': last_match['team1_wins_h2h'],
                        'win_pct_h2h': last_match['team1_win_pct_h2h'],
                        'recent_wins': last_match['team1_recent_wins'],
                        'win_pct': last_match['team1_win_pct']
                    }
                    team2_stats = {
                        'wins_h2h': last_match['team2_wins_h2h'],
                        'win_pct_h2h': last_match['team2_win_pct_h2h'],
                        'recent_wins': last_match['team2_recent_wins'],
                        'win_pct': last_match['team2_win_pct']
                    }
                else:
                    # Teams are in reverse order in data
                    team1_stats = {
                        'wins_h2h': last_match['team2_wins_h2h'],
                        'win_pct_h2h': last_match['team2_win_pct_h2h'],
                        'recent_wins': last_match['team2_recent_wins'],
                        'win_pct': last_match['team2_win_pct']
                    }
                    team2_stats = {
                        'wins_h2h': last_match['team1_wins_h2h'],
                        'win_pct_h2h': last_match['team1_win_pct_h2h'],
                        'recent_wins': last_match['team1_recent_wins'],
                        'win_pct': last_match['team1_win_pct']
                    }
                
                return team1_stats, team2_stats
            else:
                # No direct matches found, look for overall team performance
                team1_matches = df[(df['team1'] == team1) | (df['team2'] == team1)].sort_values(by='match_id', ascending=False)
                team2_matches = df[(df['team1'] == team2) | (df['team2'] == team2)].sort_values(by='match_id', ascending=False)
                
                if len(team1_matches) > 0 and len(team2_matches) > 0:
                    # Both teams have played matches
                    team1_last_match = team1_matches.iloc[0]
                    team2_last_match = team2_matches.iloc[0]
                    
                    # Get team 1 stats based on whether it was team1 or team2 in the last match
                    if team1_last_match['team1'] == team1:
                        team1_stats = {
                            'wins_h2h': 0,  # No direct history
                            'win_pct_h2h': 0,  # No direct history
                            'recent_wins': team1_last_match['team1_recent_wins'],
                            'win_pct': team1_last_match['team1_win_pct']
                        }
                    else:
                        team1_stats = {
                            'wins_h2h': 0,  # No direct history
                            'win_pct_h2h': 0,  # No direct history
                            'recent_wins': team1_last_match['team2_recent_wins'],
                            'win_pct': team1_last_match['team2_win_pct']
                        }
                    
                    # Get team 2 stats based on whether it was team1 or team2 in the last match
                    if team2_last_match['team1'] == team2:
                        team2_stats = {
                            'wins_h2h': 0,  # No direct history
                            'win_pct_h2h': 0,  # No direct history
                            'recent_wins': team2_last_match['team1_recent_wins'],
                            'win_pct': team2_last_match['team1_win_pct']
                        }
                    else:
                        team2_stats = {
                            'wins_h2h': 0,  # No direct history
                            'win_pct_h2h': 0,  # No direct history
                            'recent_wins': team2_last_match['team2_recent_wins'],
                            'win_pct': team2_last_match['team2_win_pct']
                        }
                    
                    return team1_stats, team2_stats
                else:
                    # One or both teams have no match history
                    # Use default values
                    team1_stats = {
                        'wins_h2h': 0,
                        'win_pct_h2h': 0,
                        'recent_wins': 0,
                        'win_pct': 0.5  # Default to 50% win rate
                    }
                    team2_stats = {
                        'wins_h2h': 0,
                        'win_pct_h2h': 0,
                        'recent_wins': 0,
                        'win_pct': 0.5  # Default to 50% win rate
                    }
                    return team1_stats, team2_stats
        except Exception as e:
            print(f"Error getting team stats: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def predict_match(self, match_format, team1, team2, team1_stats=None, team2_stats=None):
        """
        Predict the outcome of a match
        
        Args:
            match_format (str): 'ODI', 'T20I', 'TEST', or 'IPL'
            team1 (str): Name of team 1
            team2 (str): Name of team 2
            team1_stats (dict, optional): Stats for team 1 (wins_h2h, win_pct_h2h, recent_wins, win_pct)
            team2_stats (dict, optional): Stats for team 2 (wins_h2h, win_pct_h2h, recent_wins, win_pct)
            
        Returns:
            dict: Prediction results with probabilities
        """
        # If stats are not provided, try to fetch them from data
        if team1_stats is None or team2_stats is None:
            stats = self.get_team_stats(team1, team2, match_format)
            if stats:
                team1_stats, team2_stats = stats
            else:
                # If stats cannot be fetched, use default values
                team1_stats = {
                    'wins_h2h': 0,
                    'win_pct_h2h': 0,
                    'recent_wins': 0,
                    'win_pct': 0.5
                }
                team2_stats = {
                    'wins_h2h': 0,
                    'win_pct_h2h': 0,
                    'recent_wins': 0,
                    'win_pct': 0.5
                }
        
        # Select the appropriate model based on match format
        model_dict = None
        if match_format == 'ODI':
            model_dict = self.odi_model
        elif match_format == 'T20I' or match_format == 'T20':
            model_dict = self.t20i_model
        elif match_format == 'TEST':
            model_dict = self.test_model
        elif match_format == 'IPL':
            model_dict = self.ipl_model
        
        if not model_dict:
            # No model available, use simple heuristic instead
            print(f"No model available for {match_format} matches, using heuristic")
            return self._heuristic_prediction(team1, team2, team1_stats, team2_stats)
        
        try:
            # Create feature array
            features = np.array([[
                team1_stats['wins_h2h'], team2_stats['wins_h2h'],
                team1_stats['win_pct_h2h'], team2_stats['win_pct_h2h'],
                team1_stats['recent_wins'], team2_stats['recent_wins'],
                team1_stats['win_pct'], team2_stats['win_pct']
            ]])
            
            # Get model and label encoder
            model = model_dict['model']
            le = model_dict['label_encoder']
            
            # Get prediction probabilities
            proba = model.predict_proba(features)[0]
            
            # Get class labels
            classes = le.classes_
            
            # Find team indices using more flexible matching
            team1_idx = None
            team2_idx = None
            
            # First try exact match
            for i, team in enumerate(classes):
                if team == team1:
                    team1_idx = i
                elif team == team2:
                    team2_idx = i
            
            # If not found, try case-insensitive match
            if team1_idx is None or team2_idx is None:
                for i, team in enumerate(classes):
                    if team1_idx is None and team.lower() == team1.lower():
                        team1_idx = i
                    if team2_idx is None and team.lower() == team2.lower():
                        team2_idx = i
            
            # If still not found, try with partial match
            if team1_idx is None or team2_idx is None:
                # Get the set of unique teams in the model
                unique_teams = set(classes)
                print(f"Available teams in {match_format} model: {sorted(unique_teams)}")
                
                # Try to find best matches
                if team1_idx is None:
                    for i, team in enumerate(classes):
                        if team1.lower() in team.lower() or team.lower() in team1.lower():
                            team1_idx = i
                            print(f"Matched '{team1}' to '{team}' in model")
                            break
                
                if team2_idx is None:
                    for i, team in enumerate(classes):
                        if team2.lower() in team.lower() or team.lower() in team2.lower():
                            team2_idx = i
                            print(f"Matched '{team2}' to '{team}' in model")
                            break
            
            # Debug output for team matching
            print(f"Team1: {team1}, idx: {team1_idx}")
            print(f"Team2: {team2}, idx: {team2_idx}")
            
            # If either team is still not found in the training data, use a fallback heuristic
            if team1_idx is None or team2_idx is None:
                print(f"Teams not found in model: {team1} or {team2}, using heuristic")
                return self._heuristic_prediction(team1, team2, team1_stats, team2_stats)
            
            # Get probabilities for each team
            team1_prob = proba[team1_idx]
            team2_prob = proba[team2_idx]
            
            # Normalize probabilities to sum to 1
            total = team1_prob + team2_prob
            if total > 0:
                team1_prob = team1_prob / total
                team2_prob = team2_prob / total
            else:
                team1_prob = 0.5
                team2_prob = 0.5
            
            # Apply custom weights to favor recent performance over head-to-head
            h2h_weight = 0.4  # 40% weight for head-to-head
            recent_form_weight = 0.6  # 60% weight for recent form
            
            # Calculate weighted prediction
            team1_h2h_strength = team1_stats['win_pct_h2h']
            team2_h2h_strength = team2_stats['win_pct_h2h']
            team1_form_strength = team1_stats['win_pct']
            team2_form_strength = team2_stats['win_pct']
            
            # Get weighted win probabilities
            team1_weighted_prob = (h2h_weight * team1_h2h_strength + recent_form_weight * team1_form_strength)
            team2_weighted_prob = (h2h_weight * team2_h2h_strength + recent_form_weight * team2_form_strength)
            
            # Combine model prediction with weighted stats (50/50)
            team1_final_prob = (team1_prob * 0.5) + (team1_weighted_prob * 0.5)
            team2_final_prob = (team2_prob * 0.5) + (team2_weighted_prob * 0.5)
            
            # Normalize final probabilities
            total = team1_final_prob + team2_final_prob
            if total > 0:
                team1_final_prob = team1_final_prob / total
                team2_final_prob = team2_final_prob / total
            else:
                team1_final_prob = 0.5
                team2_final_prob = 0.5
            
            # Determine predicted winner
            predicted_winner = team1 if team1_final_prob > team2_final_prob else team2
            
            return {
                'team1_probability': team1_final_prob,
                'team2_probability': team2_final_prob,
                'predicted_winner': predicted_winner,
                'confidence': max(team1_final_prob, team2_final_prob),
                'feature_importances': {
                    'h2h_wins': h2h_weight,
                    'recent_form': recent_form_weight
                }
            }
        except Exception as e:
            print(f"Error making prediction: {e}")
            import traceback
            traceback.print_exc()
            return self._heuristic_prediction(team1, team2, team1_stats, team2_stats)
    
    def _heuristic_prediction(self, team1, team2, team1_stats, team2_stats):
        """
        Make a prediction based on simple heuristics when the model is not available
        
        Args:
            team1 (str): Name of team 1
            team2 (str): Name of team 2
            team1_stats (dict): Stats for team 1
            team2_stats (dict): Stats for team 2
            
        Returns:
            dict: Prediction results with probabilities
        """
        # Use weighted combination of stats to calculate team strength
        # Give 40% weight to head-to-head records and 60% weight to recent form
        h2h_weight = 0.4
        recent_form_weight = 0.6
        
        team1_strength = (
            h2h_weight * team1_stats['win_pct_h2h'] + 
            recent_form_weight * team1_stats['win_pct'] 
        )
        
        team2_strength = (
            h2h_weight * team2_stats['win_pct_h2h'] + 
            recent_form_weight * team2_stats['win_pct'] 
        )
        
        # Calculate probabilities
        total = team1_strength + team2_strength
        if total == 0:
            team1_prob = 0.5
            team2_prob = 0.5
        else:
            team1_prob = team1_strength / total
            team2_prob = team2_strength / total
        
        # Ensure probabilities are within reasonable bounds
        team1_prob = max(0.1, min(0.9, team1_prob))
        team2_prob = max(0.1, min(0.9, team2_prob))
        
        # Normalize to sum to 1
        total = team1_prob + team2_prob
        team1_prob = team1_prob / total
        team2_prob = team2_prob / total
        
        # Determine predicted winner
        predicted_winner = team1 if team1_prob > team2_prob else team2
        
        return {
            'team1_probability': team1_prob,
            'team2_probability': team2_prob,
            'predicted_winner': predicted_winner,
            'confidence': max(team1_prob, team2_prob),
            'method': 'heuristic',
            'feature_importances': {
                'h2h_wins': h2h_weight,
                'recent_form': recent_form_weight
            }
        }