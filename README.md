# News-Categorization-Pipeline

## Overview
The News-Categorization-Pipeline is a Python-based project that leverages various technologies to collect and categorize news articles from multiple RSS feeds. The application parses the feeds, extracts relevant information from each news article, and classifies them into predefined categories using a pre-trained BERT model. The categorized articles are then stored in a PostgreSQL database for further use.

## Implementation
The project uses several libraries including `logging`, `sqlalchemy`, `celery`, `transformers`, `tensorflow`, `feedparser`, `dateutil`, and `bs4`. It also utilizes cloud-based solutions like `CloudAMQP` and `ElephantSQL` for task management and data storage, respectively.

## Files
- `tasks.py`: Contains the main code for the assignment. It includes the setup for the database, the Celery app, and the pre-trained model. It also defines the `Article` model and the functions for classifying text and processing articles.
- `Demo_code.ipynb`: A Jupyter notebook with demo code showing the approach towards the problem. It includes the code for the model that was trained and used for category prediction, and the rest of the code written for parsing, creating the database, storing data into it, processing, and viewing the table.

## Setup
1. Clone the repository using `https://github.com/Swamisharan1/News-Categorization-Pipeline.git`.
2. Install the necessary dependencies.
3. Run the `tasks.py` script to start the application.

## Limitations and Future Improvements
The project has some limitations due to the use of free plans for cloud-based servers and a limited dataset for training the BERT model. Future improvements could include upgrading the server plan, retraining the model with a larger and more diverse set of news articles, and maintaining a consistent environment using a virtual environment.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
