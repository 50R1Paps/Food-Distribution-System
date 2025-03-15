# Food Distribution System - Setup Instructions

This document provides instructions on how to set up and run the Food Distribution System application.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository to your local machine.

2. Open a terminal and navigate to the project directory:
   ```
   cd /path/to/food-distribution-system
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the application by running:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

3. The application will be running and you can start using it.

## Offline Functionality

The application is designed to work offline. You can:

1. Export data by clicking on "Data Management" > "Export Data" in the navigation menu.
2. Import data by clicking on "Data Management" > "Import Data" in the navigation menu.

This allows you to transfer data between instances of the application or to back up your data.

## Features

- Register families and family members
- Record fingerprints for identification
- Distribute food packages
- Verify recipients to prevent duplicate distributions
- Search for families and individuals
- Export and import data for offline use

## Database

The application uses SQLite as its database, which is stored locally in the file `food_distribution.db`. This file will be created automatically when you first run the application.

## Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed correctly.
2. Check that the database file has proper permissions.
3. Restart the application if necessary.

For more detailed information about the application, refer to the main README.md file.
