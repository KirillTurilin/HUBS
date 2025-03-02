# HUBs Messenger

A web-based messenger application built with Flask, HTML, CSS, and JavaScript.

## Features

- User registration and authentication
- Chat with other users by username
- Profile customization
- Dark/Light theme toggle
- Navigation between chats, profile, and search

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the application:
   ```
   python app.py
   ```
6. Open your browser and navigate to `http://127.0.0.1:5000`

## Project Structure

- `app.py`: Main Flask application
- `models.py`: Database models
- `forms.py`: Form definitions
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates 