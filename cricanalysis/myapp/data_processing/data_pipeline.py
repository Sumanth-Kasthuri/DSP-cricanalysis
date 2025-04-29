"""
Data Pipeline for Cricket Match Prediction Features
This module processes raw cricket data to extract features for match prediction models
"""
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import csv
import re

# Base project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths for input data
IPL_MATCHES_PATH = os.path.join(BASE_DIR, 'data', 'ipl data', 'matches.csv')
INTERNATIONAL_DATA_DIR = os.path.join(BASE_DIR, 'data', 'intl-team data')
INTERNATIONAL_TEAM_DATA_DIR = os.path.join(BASE_DIR, 'data', 'international team data')
T20I_MATCHES_PATH = os.path.join(INTERNATIONAL_TEAM_DATA_DIR, 't20i_Matches_Data.csv')
ODI_MATCHES_PATH = os.path.join(INTERNATIONAL_TEAM_DATA_DIR, 'odi_Matches_Data.csv')
TEST_MATCHES_PATH = os.path.join(INTERNATIONAL_TEAM_DATA_DIR, 'test_Matches_Data.csv')

# Output paths
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'processed')
IPL_FEATURES_PATH = os.path.join(OUTPUT_DIR, 'ipl_match_features.csv')
T20I_FEATURES_PATH = os.path.join(OUTPUT_DIR, 't20i_match_features.csv')
ODI_FEATURES_PATH = os.path.join(OUTPUT_DIR, 'odi_match_features.csv')
TEST_FEATURES_PATH = os.path.join(OUTPUT_DIR, 'test_match_features.csv')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_ipl_data():
    """Process IPL match data to extract features for prediction models"""
    print("Processing IPL match data...")
    
    try:
        # Load IPL match data
        ipl_matches = pd.read_csv(IPL_MATCHES_PATH)
        
        # Create a dataframe to store features
        match_features = []
        
        # Get unique teams
        teams = pd.concat([ipl_matches['team1'], ipl_matches['team2']]).unique()
        
        # Process each match
        for index, match in ipl_matches.iterrows():
            if index < 5:  # Skip first few matches as they don't have history
                continue
                
            team1 = match['team1']
            team2 = match['team2']
            
            # Filter past matches for team head-to-head
            past_matches = ipl_matches.iloc[:index]
            
            # Head-to-head records (last 10 matches)
            head_to_head = past_matches[((past_matches['team1'] == team1) & (past_matches['team2'] == team2)) | 
                                        ((past_matches['team1'] == team2) & (past_matches['team2'] == team1))]
            head_to_head = head_to_head.iloc[-10:] if len(head_to_head) > 10 else head_to_head
            
            team1_wins_h2h = len(head_to_head[head_to_head['winner'] == team1])
            team2_wins_h2h = len(head_to_head[head_to_head['winner'] == team2])
            
            # Recent form (last 25 matches)
            team1_matches = past_matches[(past_matches['team1'] == team1) | (past_matches['team2'] == team1)]
            team1_matches = team1_matches.iloc[-25:] if len(team1_matches) > 25 else team1_matches
            team1_wins = len(team1_matches[team1_matches['winner'] == team1])
            
            team2_matches = past_matches[(past_matches['team1'] == team2) | (past_matches['team2'] == team2)]
            team2_matches = team2_matches.iloc[-25:] if len(team2_matches) > 25 else team2_matches
            team2_wins = len(team2_matches[team2_matches['winner'] == team2])
            
            # Win percentages
            team1_win_pct_h2h = team1_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
            team2_win_pct_h2h = team2_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
            
            team1_win_pct = team1_wins / len(team1_matches) if len(team1_matches) > 0 else 0
            team2_win_pct = team2_wins / len(team2_matches) if len(team2_matches) > 0 else 0
            
            # Create feature row
            feature = {
                'match_id': match['id'],
                'season': match['season'],
                'team1': team1,
                'team2': team2,
                'team1_wins_h2h': team1_wins_h2h,
                'team2_wins_h2h': team2_wins_h2h,
                'team1_win_pct_h2h': team1_win_pct_h2h,
                'team2_win_pct_h2h': team2_win_pct_h2h,
                'team1_recent_wins': team1_wins,
                'team2_recent_wins': team2_wins,
                'team1_win_pct': team1_win_pct,
                'team2_win_pct': team2_win_pct,
                'winner': match['winner']
            }
            
            match_features.append(feature)
        
        # Convert to DataFrame and save
        features_df = pd.DataFrame(match_features)
        features_df.to_csv(IPL_FEATURES_PATH, index=False)
        print(f"IPL features saved to {IPL_FEATURES_PATH}")
        return features_df
        
    except Exception as e:
        print(f"Error processing IPL data: {e}")
        return None

def process_international_matches(file_path, output_path, format_name):
    """Process international cricket match data from CSV files"""
    print(f"Processing {format_name} match data...")
    
    try:
        # Load match data
        matches_df = pd.read_csv(file_path)
        
        # Check if 'Match Date' column exists, for Test matches use 'Match Start Date' instead
        date_column = 'Match Date'
        if date_column not in matches_df.columns:
            if 'Match Start Date' in matches_df.columns and format_name.upper() == 'TEST':
                date_column = 'Match Start Date'
                print(f"Using 'Match Start Date' column for {format_name} data instead of 'Match Date'")
            else:
                print(f"Error: Date column not found in {format_name} data. Available columns: {matches_df.columns.tolist()}")
                return None
        
        # Print some sample dates to understand the format
        print(f"Sample {format_name} dates before conversion:", matches_df[date_column].head().tolist())
        
        # Try to handle various date formats
        def parse_date(date_str):
            if pd.isna(date_str) or date_str == '':
                return pd.NaT
                
            date_formats = [
                '%Y-%m-%d',      # 2022-01-15
                '%d-%m-%Y',      # 15-01-2022
                '%d/%m/%Y',      # 15/01/2022
                '%m/%d/%Y',      # 01/15/2022
                '%Y/%m/%d',      # 2022/01/15
                '%d %b %Y',      # 15 Jan 2022
                '%d-%b-%Y',      # 15-Jan-2022
                '%d %B %Y',      # 15 January 2022
                '%B %d, %Y'      # January 15, 2022
            ]
            
            for date_format in date_formats:
                try:
                    return pd.to_datetime(date_str, format=date_format)
                except (ValueError, TypeError):
                    continue
            
            # If no format works, return NaT
            print(f"Warning: Could not parse date: '{date_str}' in {format_name} data")
            return pd.NaT
        
        # Apply the custom parser to the date column
        try:
            matches_df['Match Date'] = matches_df[date_column].apply(parse_date)
        except Exception as e:
            print(f"Error converting dates in {format_name} data: {e}")
            # Try an alternative approach with flexible parsing
            try:
                matches_df['Match Date'] = pd.to_datetime(matches_df[date_column], errors='coerce', infer_datetime_format=True)
            except Exception as e2:
                print(f"Secondary error parsing dates: {e2}")
        
        # Print how many dates were successfully converted
        valid_dates = matches_df['Match Date'].notna().sum()
        total_dates = len(matches_df)
        print(f"Successfully parsed {valid_dates} out of {total_dates} dates in {format_name} data")
        
        # Filter out rows with invalid dates
        matches_df = matches_df.dropna(subset=['Match Date'])
        print(f"Kept {len(matches_df)} matches with valid dates out of {total_dates} total matches")
        
        # Sort by date
        matches_df = matches_df.sort_values(by='Match Date')
        
        # Create a dataframe to store features
        match_features = []
        
        # Get unique teams
        teams = pd.concat([matches_df['Team1 Name'], matches_df['Team2 Name']]).unique()
        
        # Process each match (skip first few matches as they don't have history)
        for index, match in matches_df.iloc[10:].iterrows():
            team1 = match['Team1 Name']
            team2 = match['Team2 Name']
            match_date = match['Match Date']
            
            # Skip matches with missing date information
            if pd.isna(match_date):
                continue
                
            # Filter past matches
            past_matches = matches_df[matches_df['Match Date'] < match_date]
            
            # Head-to-head records (last 10 matches)
            head_to_head = past_matches[((past_matches['Team1 Name'] == team1) & (past_matches['Team2 Name'] == team2)) | 
                                       ((past_matches['Team1 Name'] == team2) & (past_matches['Team2 Name'] == team1))]
            head_to_head = head_to_head.iloc[-10:] if len(head_to_head) > 10 else head_to_head
            
            # Count wins in head-to-head matches
            team1_wins_h2h = 0
            team2_wins_h2h = 0
            draws_h2h = 0  # Track draws specifically for Test matches
            
            for _, h2h_match in head_to_head.iterrows():
                if h2h_match['Match Winner'] == team1:
                    team1_wins_h2h += 1
                elif h2h_match['Match Winner'] == team2:
                    team2_wins_h2h += 1
                elif format_name.upper() == 'TEST' and h2h_match['Match Winner'] == 'Draw':
                    # Count draws in Test matches
                    draws_h2h += 1
            
            # Recent form (last 25 matches)
            team1_matches = past_matches[(past_matches['Team1 Name'] == team1) | (past_matches['Team2 Name'] == team1)]
            team1_matches = team1_matches.iloc[-25:] if len(team1_matches) > 25 else team1_matches
            
            team2_matches = past_matches[(past_matches['Team1 Name'] == team2) | (past_matches['Team2 Name'] == team2)]
            team2_matches = team2_matches.iloc[-25:] if len(team2_matches) > 25 else team2_matches
            
            # Count wins in recent matches
            team1_wins = 0
            team1_draws = 0  # Track draws for Test matches
            for _, t1_match in team1_matches.iterrows():
                if t1_match['Match Winner'] == team1:
                    team1_wins += 1
                elif format_name.upper() == 'TEST' and t1_match['Match Winner'] == 'Draw':
                    team1_draws += 1
                    
            team2_wins = 0
            team2_draws = 0  # Track draws for Test matches
            for _, t2_match in team2_matches.iterrows():
                if t2_match['Match Winner'] == team2:
                    team2_wins += 1
                elif format_name.upper() == 'TEST' and t2_match['Match Winner'] == 'Draw':
                    team2_draws += 1
            
            # Win percentages - for Test matches, consider draws in the calculation
            if format_name.upper() == 'TEST':
                team1_win_pct_h2h = team1_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
                team2_win_pct_h2h = team2_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
                
                team1_win_pct = team1_wins / len(team1_matches) if len(team1_matches) > 0 else 0
                team2_win_pct = team2_wins / len(team2_matches) if len(team2_matches) > 0 else 0
            else:
                team1_win_pct_h2h = team1_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
                team2_win_pct_h2h = team2_wins_h2h / len(head_to_head) if len(head_to_head) > 0 else 0
                
                team1_win_pct = team1_wins / len(team1_matches) if len(team1_matches) > 0 else 0
                team2_win_pct = team2_wins / len(team2_matches) if len(team2_matches) > 0 else 0
            
            # Match result
            match_winner = match['Match Winner']
            
            # Create feature row
            feature = {
                'match_id': match['Match ID'],
                'match_date': match['Match Date'],
                'format': format_name,
                'team1': team1,
                'team2': team2,
                'team1_wins_h2h': team1_wins_h2h,
                'team2_wins_h2h': team2_wins_h2h,
                'team1_win_pct_h2h': team1_win_pct_h2h,
                'team2_win_pct_h2h': team2_win_pct_h2h,
                'team1_recent_wins': team1_wins,
                'team2_recent_wins': team2_wins,
                'team1_win_pct': team1_win_pct,
                'team2_win_pct': team2_win_pct,
                'venue': match['Match Venue (Stadium)'],
                'venue_country': match['Match Venue (Country)'],
                'winner': match_winner
            }
            
            # Add Test-specific stats if applicable
            if format_name.upper() == 'TEST':
                feature['draws_h2h'] = draws_h2h
                feature['team1_recent_draws'] = team1_draws
                feature['team2_recent_draws'] = team2_draws
            
            match_features.append(feature)
        
        # Convert to DataFrame and save
        features_df = pd.DataFrame(match_features)
        features_df.to_csv(output_path, index=False)
        print(f"{format_name} features saved to {output_path}")
        return features_df
        
    except Exception as e:
        print(f"Error processing {format_name} data: {e}")
        # Print more information about the exception
        import traceback
        traceback.print_exc()
        return None

def process_data():
    """Process all cricket data to extract features"""
    
    # Process IPL data
    ipl_features = process_ipl_data()
    
    # Process international data
    t20i_features = process_international_matches(T20I_MATCHES_PATH, T20I_FEATURES_PATH, "T20I")
    odi_features = process_international_matches(ODI_MATCHES_PATH, ODI_FEATURES_PATH, "ODI")
    test_features = process_international_matches(TEST_MATCHES_PATH, TEST_FEATURES_PATH, "Test")
    
    return {
        'ipl': ipl_features,
        't20i': t20i_features,
        'odi': odi_features,
        'test': test_features
    }

if __name__ == "__main__":
    process_data()