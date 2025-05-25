import logging
import math

# Configure logging
logger = logging.getLogger(__name__)

def calculate_live_prediction(match_details):
    """
    Calculate win probability based on live match situation during second innings
    
    Args:
        match_details (dict): Current match details including:
            - match_format: Format of the match (ODI, T20I, TEST, IPL)
            - team1_score: First innings score (dict with runs, wickets, overs)
            - team2_score: Second innings score (dict with runs, wickets, overs)
            - team1_name: Name of team 1 (first innings batting team)
            - team2_name: Name of team 2 (second innings batting team)
    
    Returns:
        dict: Live prediction results including win probabilities for both teams
    """
    # Check if match details contain all required information
    if not match_details or not all(k in match_details for k in 
                                   ['match_format', 'team1_score', 'team2_score']):
        logger.warning("Incomplete match details for live prediction")
        return None
    
    # Get match format
    match_format = match_details.get('match_format', '').upper()
    
    # Get team scores
    team1_score = match_details.get('team1_score', {})
    team2_score = match_details.get('team2_score', {})
    
    # Check if both innings have started
    if not team1_score.get('runs') or team1_score.get('overs') is None:
        logger.info("First innings data incomplete, cannot make live prediction")
        return None
    
    # First innings completed and second innings started
    if team2_score.get('runs') is not None and team2_score.get('overs') is not None:
        # Extract match situation details
        target_runs = team1_score.get('runs', 0) + 1  # Target is first innings score + 1
        current_runs = team2_score.get('runs', 0)
        current_wickets = team2_score.get('wickets', 0)
        wickets_left = 10 - current_wickets
        
        # Extract overs information
        total_overs = get_format_overs(match_format)
        current_overs_raw = team2_score.get('overs', 0)
        current_overs = float(current_overs_raw)
        # Calculate the whole overs and balls separately
        whole_overs = int(current_overs)
        balls_in_current_over = int((current_overs - whole_overs) * 10)
        total_balls = (whole_overs * 6) + balls_in_current_over
        
        # Calculate remaining resources
        if match_format in ['ODI', 'T20I', 'T20', 'IPL']:
            remaining_overs = total_overs - current_overs
            remaining_balls = (total_overs * 6) - total_balls
            
            # Calculate required runs
            runs_needed = target_runs - current_runs
            
            if runs_needed <= 0:
                # Batting team has already won
                return create_win_prediction(
                    batting_team_probability=100,
                    bowling_team_probability=0,
                    match_situation={
                        'target': target_runs,
                        'runs_scored': current_runs,
                        'runs_needed': 0,
                        'wickets_lost': current_wickets,
                        'wickets_left': wickets_left,
                        'overs_played': current_overs,
                        'overs_left': 0,
                        'required_run_rate': 0
                    },
                    explanation="Batting team has already achieved the target."
                )
            
            if remaining_balls == 0:
                # No balls left, bowling team wins or it's a tie
                if runs_needed > 0:
                    return create_win_prediction(
                        batting_team_probability=0,
                        bowling_team_probability=100,
                        match_situation={
                            'target': target_runs,
                            'runs_scored': current_runs,
                            'runs_needed': runs_needed,
                            'wickets_lost': current_wickets,
                            'wickets_left': wickets_left,
                            'overs_played': current_overs,
                            'overs_left': 0,
                            'required_run_rate': float('inf')
                        },
                        explanation="No balls remaining, bowling team wins."
                    )
                else:
                    # It's a tie
                    return create_win_prediction(
                        batting_team_probability=50,
                        bowling_team_probability=50,
                        match_situation={
                            'target': target_runs,
                            'runs_scored': current_runs,
                            'runs_needed': 0,
                            'wickets_lost': current_wickets,
                            'wickets_left': wickets_left,
                            'overs_played': current_overs,
                            'overs_left': 0,
                            'required_run_rate': 0
                        },
                        explanation="Match tied."
                    )
            
            # Calculate required run rate
            required_run_rate = (runs_needed / remaining_overs) if remaining_overs > 0 else float('inf')
            
            # Different calculation logic based on match format
            if match_format in ['T20I', 'T20', 'IPL']:
                return calculate_t20_win_probability(
                    runs_needed, wickets_left, remaining_balls, required_run_rate
                )
            elif match_format == 'ODI':
                return calculate_odi_win_probability(
                    runs_needed, wickets_left, remaining_balls, required_run_rate
                )
        elif match_format == 'TEST':
            return calculate_test_win_probability(
                match_details, current_runs, target_runs, current_wickets
            )
        else:
            logger.warning(f"Unsupported match format for live prediction: {match_format}")
            return None
    else:
        logger.info("Second innings has not started yet, cannot make live prediction")
        return None

def get_format_overs(match_format):
    """Get total overs based on match format"""
    if match_format in ['T20I', 'T20', 'IPL']:
        return 20
    elif match_format == 'ODI':
        return 50
    elif match_format == 'TEST':
        return 90  # Approximate, not strictly limited in Test matches
    else:
        return 50  

def calculate_t20_win_probability(runs_needed, wickets_left, balls_left, required_run_rate):
    """
    Calculate win probability for T20 matches
    
    Args:
        runs_needed (int): Runs needed to win
        wickets_left (int): Wickets remaining for batting team
        balls_left (int): Balls remaining
        required_run_rate (float): Required run rate per over
    
    Returns:
        dict: Win probability for both teams
    """
    # Base probability starts at 50/50
    batting_team_prob = 50
    
    # Adjust based on required run rate
    if required_run_rate <= 6:
        # Very manageable in T20
        batting_team_prob += 20
    elif required_run_rate <= 8:
        # Quite manageable in T20
        batting_team_prob += 10
    elif required_run_rate <= 10:
        # Challenging but doable
        batting_team_prob -= 5
    elif required_run_rate <= 12:
        # Difficult
        batting_team_prob -= 15
    elif required_run_rate <= 15:
        # Very difficult
        batting_team_prob -= 25
    else:
        # Extremely difficult
        batting_team_prob -= 35
    
    # Adjust based on wickets left
    if wickets_left >= 9:
        batting_team_prob += 15
    elif wickets_left >= 7:
        batting_team_prob += 10
    elif wickets_left >= 5:
        batting_team_prob += 5
    elif wickets_left == 4:
        batting_team_prob -= 5
    elif wickets_left == 3:
        batting_team_prob -= 15
    elif wickets_left == 2:
        batting_team_prob -= 25
    else:  # 1 or 0 wickets
        batting_team_prob -= 35
    
    # Adjust based on balls remaining vs runs needed
    runs_per_ball_needed = runs_needed / max(balls_left, 1)
    
    if runs_per_ball_needed <= 1.0:
        # Easy pace
        batting_team_prob += 10
    elif runs_per_ball_needed <= 1.5:
        # Moderate pace
        batting_team_prob += 0
    elif runs_per_ball_needed <= 2.0:
        # Fast pace
        batting_team_prob -= 10
    else:
        # Very fast pace needed
        batting_team_prob -= 30
    
    # Ensure probability is within bounds
    batting_team_prob = max(min(batting_team_prob, 99), 1)
    
    # Create explanation
    if required_run_rate >= 12:
        explanation = f"Challenging chase with required rate of {required_run_rate:.2f} runs per over."
    elif wickets_left <= 3:
        explanation = f"Limited batting resources with only {wickets_left} wickets remaining."
    elif runs_per_ball_needed >= 1.5:
        explanation = f"High pressure situation requiring {runs_per_ball_needed:.2f} runs per ball."
    else:
        explanation = f"T20 chase with {runs_needed} runs needed from {balls_left} balls with {wickets_left} wickets in hand."
    
    return create_win_prediction(
        batting_team_probability=batting_team_prob,
        bowling_team_probability=100 - batting_team_prob,
        match_situation={
            'runs_needed': runs_needed,
            'balls_left': balls_left,
            'wickets_left': wickets_left,
            'required_run_rate': required_run_rate,
            'runs_per_ball_needed': runs_per_ball_needed
        },
        explanation=explanation
    )

def calculate_odi_win_probability(runs_needed, wickets_left, balls_left, required_run_rate):
    """
    Calculate win probability for ODI matches
    
    Args:
        runs_needed (int): Runs needed to win
        wickets_left (int): Wickets remaining for batting team
        balls_left (int): Balls remaining
        required_run_rate (float): Required run rate per over
    
    Returns:
        dict: Win probability for both teams
    """
    # Base probability starts at 50/50
    batting_team_prob = 50
    
    # Adjust based on required run rate - ODIs have different thresholds than T20s
    if required_run_rate <= 4:
        # Very manageable in ODI
        batting_team_prob += 25
    elif required_run_rate <= 5:
        # Quite manageable in ODI
        batting_team_prob += 15
    elif required_run_rate <= 6:
        # Standard and achievable
        batting_team_prob += 5
    elif required_run_rate <= 7:
        # Challenging
        batting_team_prob -= 5
    elif required_run_rate <= 8:
        # Difficult
        batting_team_prob -= 15
    elif required_run_rate <= 10:
        # Very difficult
        batting_team_prob -= 25
    else:
        # Extremely difficult
        batting_team_prob -= 35
    
    # Adjust based on wickets left - more important in ODIs than T20s
    if wickets_left >= 9:
        batting_team_prob += 15
    elif wickets_left >= 7:
        batting_team_prob += 10
    elif wickets_left >= 5:
        batting_team_prob += 0
    elif wickets_left == 4:
        batting_team_prob -= 10
    elif wickets_left == 3:
        batting_team_prob -= 20
    elif wickets_left == 2:
        batting_team_prob -= 30
    else:  # 1 or 0 wickets
        batting_team_prob -= 40
    
    # Adjust based on balls remaining vs runs needed
    runs_per_ball_needed = runs_needed / max(balls_left, 1)
    
    if runs_per_ball_needed <= 0.75:
        # Easy pace
        batting_team_prob += 15
    elif runs_per_ball_needed <= 1.0:
        # Moderate pace
        batting_team_prob += 5
    elif runs_per_ball_needed <= 1.25:
        # Fast pace
        batting_team_prob -= 10
    elif runs_per_ball_needed <= 1.5:
        # Very fast pace
        batting_team_prob -= 25
    else:
        # Extremely fast pace
        batting_team_prob -= 40
    
    # Add more emphasis on match stage for ODIs
    overs_left = balls_left / 6
    if overs_left >= 30:
        # Plenty of time
        batting_team_prob += 10
    elif overs_left <= 5:
        # End-game pressure
        batting_team_prob -= 10
    
    # Ensure probability is within bounds
    batting_team_prob = max(min(batting_team_prob, 99), 1)
    
    # Create explanation
    if required_run_rate >= 8:
        explanation = f"Challenging ODI chase with required rate of {required_run_rate:.2f} runs per over."
    elif wickets_left <= 3:
        explanation = f"Limited batting resources with only {wickets_left} wickets remaining."
    elif overs_left <= 5:
        explanation = f"End-game pressure with {runs_needed} runs needed in just {overs_left:.1f} overs."
    else:
        explanation = f"ODI chase with {runs_needed} runs needed from {balls_left} balls ({overs_left:.1f} overs) with {wickets_left} wickets in hand."
    
    return create_win_prediction(
        batting_team_probability=batting_team_prob,
        bowling_team_probability=100 - batting_team_prob,
        match_situation={
            'runs_needed': runs_needed,
            'balls_left': balls_left,
            'overs_left': overs_left,
            'wickets_left': wickets_left,
            'required_run_rate': required_run_rate,
            'runs_per_ball_needed': runs_per_ball_needed
        },
        explanation=explanation
    )

def calculate_test_win_probability(match_details, current_runs, target_runs, current_wickets):
    """
    Calculate win probability for Test matches
    
    Args:
        match_details (dict): Full match details
        current_runs (int): Current runs in the 4th innings
        target_runs (int): Target runs to win
        current_wickets (int): Current wickets lost
    
    Returns:
        dict: Win probability for both teams
    """
    # Check which inning we're in
    is_fourth_innings = True  
    
    if is_fourth_innings:
        runs_needed = target_runs - current_runs
        wickets_left = 10 - current_wickets
        
        # Base probability starts at 50/50
        batting_team_prob = 50
        
        # In Test cricket, wickets are extremely important
        if wickets_left >= 9:
            batting_team_prob += 30
        elif wickets_left >= 7:
            batting_team_prob += 20
        elif wickets_left >= 5:
            batting_team_prob += 10
        elif wickets_left == 4:
            batting_team_prob -= 10
        elif wickets_left == 3:
            batting_team_prob -= 20
        elif wickets_left == 2:
            batting_team_prob -= 30
        else:  # 1 or 0 wickets
            batting_team_prob -= 40
        
        # Adjust based on runs needed
        if runs_needed <= 50:
            batting_team_prob += 25
        elif runs_needed <= 100:
            batting_team_prob += 15
        elif runs_needed <= 150:
            batting_team_prob += 5
        elif runs_needed <= 200:
            batting_team_prob -= 5
        elif runs_needed <= 250:
            batting_team_prob -= 15
        elif runs_needed <= 300:
            batting_team_prob -= 25
        else:
            batting_team_prob -= 35
        
        # Ensure probability is within bounds
        batting_team_prob = max(min(batting_team_prob, 99), 1)
        
        # Create explanation
        if runs_needed > 200 and wickets_left <= 5:
            explanation = f"Difficult Test match chase with {runs_needed} runs needed and only {wickets_left} wickets remaining."
        elif runs_needed > 100 and wickets_left <= 3:
            explanation = f"Very challenging Test match situation with {runs_needed} runs needed and only {wickets_left} wickets left."
        elif runs_needed <= 50 and wickets_left >= 5:
            explanation = f"Favorable Test match position with just {runs_needed} runs needed and {wickets_left} wickets in hand."
        else:
            explanation = f"Test match chase with {runs_needed} runs needed with {wickets_left} wickets remaining."
        
        return create_win_prediction(
            batting_team_probability=batting_team_prob,
            bowling_team_probability=100 - batting_team_prob,
            match_situation={
                'runs_needed': runs_needed,
                'wickets_left': wickets_left,
                'format': 'TEST'
            },
            explanation=explanation
        )
    else:
        # For other innings in Test matches, complex logic is needed
        return None

def create_win_prediction(batting_team_probability, bowling_team_probability, match_situation, explanation):
    """
    Create a structured prediction result
    
    Args:
        batting_team_probability (float): Win probability for batting team
        bowling_team_probability (float): Win probability for bowling team
        match_situation (dict): Details about the match situation
        explanation (str): Human-readable explanation of the prediction
    
    Returns:
        dict: Structured prediction result
    """
    return {
        'batting_team_win_probability': batting_team_probability,
        'bowling_team_win_probability': bowling_team_probability,
        'prediction_factors': match_situation,
        'explanation': explanation
    }