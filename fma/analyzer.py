from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import namedtuple, defaultdict
from operator import itemgetter
from nltk.corpus import stopwords
from unidecode import unidecode

import numpy as np
import matplotlib.pyplot as plt
import datetime
import heapq
import string
import time

import parser

english_stopwords = set(stopwords.words('english'))
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze(filename):
    '''
    MESSAGE ANALYSIS
    '''

    # Load messages
    print('Reading file {0} ...'.format(filename))
    timestamp = time.clock()
    messages = parser.get_messages(filename)
    print('Loaded {0} messages in {1:.2f} seconds.'.format(len(messages), time.clock() - timestamp))

    print('Aggregating data ...')
    timestamp = time.clock()

    # Data structures to hold information about the messages 
    monthly_counts = defaultdict(int)
    monthly_sticker_counts = defaultdict(int)
    day_counts = defaultdict(int)
    hourly_counts = defaultdict(int)
    daily_counts = defaultdict(int)
    daily_sentiments = defaultdict(float)
    word_frequencies = defaultdict(int)
    first_date = None 
    last_date = None 

    # Extract information from the messages 
    for message in messages:
        # Convert message's Unix timestamp to local datetime
        date = datetime.datetime.fromtimestamp(message['timestamp'])
        month = date.strftime('%Y-%m')
        full_day = date.strftime('%Y-%m-%d')
        day = date.strftime('%A')
        hour = date.time().hour

        # Get content in message if it has any
        if 'content' in message:
            content = unidecode(message['content'])

        # Increment message counts
        monthly_counts[month] += 1
        if 'sticker' in message:
            monthly_sticker_counts[month] += 1
        daily_counts[full_day] += 1
        day_counts[day] += 1 
        hourly_counts[hour] += 1 

        # Rudimentary sentiment analysis using VADER
        sentiments = sentiment_analyzer.polarity_scores(content)
        daily_sentiments[full_day] += sentiments['pos'] - sentiments['neg']

        # Determine word frequencies
        if content: 
            # Split message up by spaces to get individual words
            for word in content.split(' '):
                # Make the word lowercase and strip it of punctuation
                new_word = word.lower().strip(string.punctuation)

                # Word might have been entirely punctuation; don't strip it
                if not new_word:
                    new_word = word.lower()
                
                # Ignore word if it in the stopword set or if it is less than 2 characters
                if len(new_word) > 1 and new_word not in english_stopwords:
                    word_frequencies[new_word] += 1 

        # Determine start and last dates of messages 
        if (first_date and first_date > date) or not first_date:
            first_date = date 
        if (last_date and last_date < date) or not last_date:
            last_date = date 

    # Take the average of the sentiment amassed for each day
    for full_day, message_count in daily_counts.items():
        daily_sentiments[full_day] /= message_count

    # Get the number of days the messages span over
    num_days = (last_date - first_date).days

    # Get most common words
    most_used_words = heapq.nlargest(100, word_frequencies.items(), key=itemgetter(1)) 

    print('Processed data in {0:.2f} seconds.'.format(time.clock() - timestamp))

    print('Preparing data for display ...')

    # Format data for graphing
    xdata_monthly = sorted(list(monthly_counts.keys()))
    ydata_monthly = [monthly_counts[x] for x in xdata_monthly]
    ydata_monthly_stickers = [monthly_sticker_counts[x] for x in xdata_monthly]
    xdata_day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    ydata_day = [float(day_counts[x]) / num_days for x in xdata_day]
    xdata_hourly = ['{0}:00'.format(i) for i in range(24)]
    ydata_hourly = [float(hourly_counts[x]) / num_days for x in range(24)]
    xdata_sentiment = sorted(list(daily_sentiments.keys()))
    ydata_sentiment = [daily_sentiments[x] for x in xdata_sentiment]

    '''
    DATA VISUALIZATION 
    '''

    print('Displaying ...')

    # Generate subplots
    fig, ax_array = plt.subplots(3, 2)
   
    # Graph shows monthly totals of messages
    def show_monthly_count_graph(ax, xdata, ydata, ydata_stickers):
        indices = np.arange(len(xdata))
        bar_width = 0.45
        
        ax.bar(indices, ydata, bar_width, 
                alpha=0.5, color='b',
                align='center',
                label='All messages')

        ax.bar(indices + bar_width, ydata_stickers, bar_width, 
                alpha=0.5, color='r',
                align='center',
                label='Facebook stickers')

        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title('Monthly Totals')
        ax.set_xticks(indices + bar_width / 2)
        ax.set_xticklabels(xdata)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
        ax.legend()

    # Graph shows daily averages of messages
    def show_daily_average_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))
        bar_width = 0.6
        
        ax.bar(indices, ydata, bar_width, 
                alpha=0.5, color='b',
                align='center',
                label='All messages')

        ax.set_xlabel('Day of the Week')
        ax.set_ylabel('Count')
        ax.set_title('Daily Averages')
        ax.set_xticks(indices)
        ax.set_xticklabels(xdata)
        ax.legend()

    # Graph shows hourly averages of messages
    def show_hourly_average_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))
        bar_width = 0.8
        
        ax.bar(indices, ydata, bar_width, 
                alpha=0.5, color='b',
                align='center',
                label='All messages')

        ax.set_xlabel('Hour')
        ax.set_ylabel('Count')
        ax.set_title('Hourly Averages')
        ax.set_xticks(indices)
        ax.set_xticklabels(xdata)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
        ax.legend()

    # Graph shows sentiment over time
    def show_daily_sentiment_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))

        ax.plot(indices, ydata, 
                alpha=0.5, color='b', 
                label='Text messages')

        ax.set_xlabel('Date')
        ax.set_ylabel('Sentiment')
        ax.set_title('Daily Sentiment')

        num_ticks = 8
        tick_spacing = round(len(indices) / num_ticks)
        ticks = [tick_spacing * i for i in range(num_ticks)]
        tick_labels = [xdata[tick] for tick in ticks]

        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

        ax.legend()

    # Call the graphing methods
    show_monthly_count_graph(ax_array[0][0], xdata_monthly, ydata_monthly, ydata_monthly_stickers)
    show_daily_average_graph(ax_array[1][0], xdata_day, ydata_day)
    show_hourly_average_graph(ax_array[2][0], xdata_hourly, ydata_hourly)
    show_daily_sentiment_graph(ax_array[0][1], xdata_sentiment, ydata_sentiment)

    # Display the plots
    fig.tight_layout()
    plt.show()

    print('Done.')


