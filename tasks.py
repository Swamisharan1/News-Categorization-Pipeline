import logging
from sqlalchemy import create_engine, Column, String, Integer, DateTime, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from celery import Celery
from transformers import BertTokenizerFast
import tensorflow as tf
import feedparser
from dateutil import parser
from bs4 import BeautifulSoup
import sqlalchemy
from sqlalchemy.pool import QueuePool

# Configure logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Load the pre-trained model and tokenizer
try:
    model = tf.keras.models.load_model('C:/Users/swami/Documents/datascience/data intern assignment/trained model/')
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-uncased')
except Exception as e:
    logging.error(f"Error loading model or tokenizer: {e}")

# Set up the Celery app
try:
    app = Celery('myapp', broker='amqp://pzfuaogi:6gS39PKAPp1iZ8jkGrFpEVcyy2-n7Ji9@hawk.rmq.cloudamqp.com/pzfuaogi')
except Exception as e:
    logging.error(f"Error setting up Celery app: {e}")

# Set up the database
try:
    engine = create_engine('postgresql://hlebjvxl:rpgyeSgIO6xCDHOn7Puyx3S3QE3lxwv-@kashin.db.elephantsql.com/hlebjvxl',
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=5)
    Session = sessionmaker(bind=engine)
except Exception as e:
    logging.error(f"Error setting up database: {e}")

# Defining Article model 
Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String)
    description = Column(String)
    published = Column(DateTime)
    category = Column(String)

    def to_dict(self):  # Convert the Article object to a dictionary
        return {c.key: getattr(self, c.key)
                for c in sqlalchemy.inspect(self).mapper.column_attrs}

# Create all tables
try:  
    Base.metadata.create_all(engine)
except Exception as e:
    logging.error(f"Error creating tables: {e}") # Log any errors that occur while creating the tables

def classify(text):  # Classify the text into one of the predefined categories
    if text is None:
        return None
    inputs = tokenizer(text, return_tensors='tf', truncation=True, padding=True)
    outputs = model(inputs, training=False)
    logits = outputs['logits']
    predicted_category = tf.argmax(logits, axis=1).numpy()[0]
    categories = {
        0: 'Terrorism / protest / political unrest / riot',
        1: 'Positive/Uplifting',
        2: 'Natural Disasters',
        3: 'Others'
    }
    return categories[predicted_category]

@app.task
def process_article(article_dict): # Process an article and add it to the database
    session = Session()
    description = article_dict['description'] if article_dict['description'] else ''
    category = classify(description)
    try:
        article = Article(
            title=article_dict['title'],
            link=article_dict['link'],
            description=article_dict['description'],
            published=article_dict['published'],
            category=category
        )
        session.add(article)
        session.commit()
    except Exception as e:
        logging.error(f"Error processing article: {e}")  # Log any errors that occur while processing the article
    finally:
        session.close()

def parse_rss(url, seen_articles):
     # Parse an RSS feed and add any new articles to the database
    session = Session()
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link not in seen_articles:
                seen_articles.add(entry.link)
                published = parser.parse(entry.published) if 'published' in entry else None
                soup = BeautifulSoup(entry.description, 'html.parser') if 'description' in entry else None
                description = soup.get_text() if soup else None
                article = Article(
                    title=entry.title,
                    link=entry.link,
                    description=description,
                    published=published,
                    category=None
                )
                session.add(article)
                session.commit() # Commit the transaction to save the changes in the database
                process_article.delay(article_dict=article.to_dict())  # Add the article to the processing queue
    except Exception as e:
        logging.error(f"Error parsing RSS feed: {e}") # Log any errors that occur while parsing the RSS feed
    finally:
        session.close() # Close the database session

def main():
    # Initialize a set to keep track of articles that have already been seen
    seen_articles = set()
    # List of RSS feeds to parse
    rss_feeds = [
        'http://rss.cnn.com/rss/cnn_topstories.rss',
        'http://qz.com/feed',
        'http://feeds.foxnews.com/foxnews/politics',
        'http://feeds.reuters.com/reuters/businessNews',
        'http://feeds.feedburner.com/NewshourWorld',
        'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
    ]
     # Parse each RSS feed
    for url in rss_feeds:
        parse_rss(url, seen_articles)

if __name__ == "__main__":
    main()
