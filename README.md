# CricAnalysis - Cricket Match Analysis and Prediction Platform

## Digital Systems Project (DSP)

## Overview
CricAnalysis is a comprehensive cricket analytics platform designed to provide match statistics, team information, player details, and match outcome predictions using machine learning. The platform integrates real-time cricket data, weather forecasts for match venues, and predictive analytics to enhance the cricket watching experience for fans.

## Functionalities

- **Match Information**: Access detailed information about upcoming, live, and recently completed cricket matches across formats (ODI, T20I, Test, IPL).
- **Team Profiles**: Explore comprehensive team statistics, historical performance data, and current squad information.
- **Player Statistics**: View detailed player profiles with batting, bowling, and fielding statistics.
- **Match Predictions**: Leverage machine learning algorithms to predict match outcomes based on historical data and current form.
- **Weather Information**: Get real-time weather updates for match venues to understand how conditions might affect the game.
- **User Profiles**: Create personal accounts to customise experience and save favorite teams.
- **Favorite Teams**: Users can add and manage their favorite teams for quick access to relevant information.

## Pipeline

1. **Sign Up and Login**: Create an account to access personalized features and save preferences.
2. **Explore Matches**: Browse upcoming, live, and recent matches across different cricket formats.
3. **Team Analysis**: View comprehensive team statistics and historical performance data.
4. **Player Insights**: Access detailed player profiles with comprehensive statistics.
5. **Match Predictions**: Get AI-powered predictions for match outcomes based on historical data.
6. **Venue Weather**: Check weather conditions at match venues to understand potential impact.
7. **Favorite Management**: Add teams to favorites for quick access to their information.

## Machine Learning Components

CricAnalysis employs advanced machine learning models to predict cricket match outcomes:

- **Data Preprocessing**: Historical match data is processed to extract relevant features through the data pipeline module.
- **Model Training**: Random Forest Classifier models are trained for different cricket formats (ODI, T20I, Test, IPL).
- **Prediction System**: The MatchPredictor class provides predictions for upcoming matches based on team statistics and historical performance.
- **Live Updates**: For ongoing matches, the prediction model can update win probabilities based on the current match state.

## Data Sources

- Historical match data across different cricket formats
- Player statistics including batting, bowling, and fielding
- Team performance metrics and historical head-to-head statistics
- Real-time match data from cricket APIs
- Weather information from weather forecast APIs

## Technologies Used

- **Backend**: Django (Python web framework)
- **Database**: MySQL (Development)
- **Machine Learning**: scikit-learn, pandas, numpy
- **APIs**: 
  - Cricbuzz API for cricket data
  - Weather API for venue conditions
- **Frontend**: HTML, CSS, JavaScript

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DSP-cricanalysis.git
   cd DSP-cricanalysis
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Navigate to the Django project directory:
   ```bash
   cd cricanalysis
   ```

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/ in your web browser.

## API Keys Required

- **Cricbuzz API**: Required for fetching cricket match data (available from RapidAPI)
- **Weather API**: For fetching weather conditions at match venues

## Future Enhancements

- Advanced visualizations for player and team statistics
- Social sharing features for match predictions
- Mobile application for on-the-go access
- Integration with more cricket data sources
- Enhanced prediction models incorporating more features

