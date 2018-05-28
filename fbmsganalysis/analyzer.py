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
import json
import copy

english_stopwords = set(stopwords.words('english'))
sentiment_analyzer = SentimentIntensityAnalyzer()
cache = {}

def _load_messages(filename):
    if filename in cache:
        return cache[filename]
    else:
        with open(filename) as jsonfile:
            data = json.load(jsonfile)
            cache[filename] = data
            return data
        
def get_messages(filename, copy_from_cache=True):
    data = _load_messages(filename)

    # Copy the stored messages we have
    copied_messages = data['messages']
    if copy_from_cache:
        copied_messages = copy.deepcopy(data['messages'])

    # Return a sorted list of messages by time
    return sorted(copied_messages, key=lambda message : message['timestamp'])

def analyze(filename):
    '''
    MESSAGE ANALYSIS
    '''

    # Load messages
    print('Reading file {0} ...'.format(filename))
    timestamp = time.clock()
    messages = get_messages(filename, copy_from_cache=False)
    print('Loaded {0} messages in {1:.2f} seconds.'.format(len(messages), time.clock() - timestamp))

    print('Aggregating data ...')
    timestamp = time.clock()

    # Data structures to hold information about the messages 
    daily_counts = defaultdict(int)
    daily_sticker_counts = defaultdict(int)
    daily_sentiments = defaultdict(float)
    monthly_counts = defaultdict(int)
    monthly_sticker_counts = defaultdict(int)
    hourly_counts = defaultdict(int)
    day_name_counts = defaultdict(int)
    word_frequencies = defaultdict(int)
    first_date = None 
    last_date = None 

    # Extract information from the messages 
    for message in messages:
        # Convert message's Unix timestamp to local datetime
        date = datetime.datetime.fromtimestamp(message['timestamp'])
        month = date.strftime('%Y-%m')
        day = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A')
        hour = date.time().hour

        # Get content in message if it has any
        if 'content' in message:
            content = unidecode(message['content'])

        # Increment message counts
        hourly_counts[hour] += 1 
        day_name_counts[day_name] += 1 
        daily_counts[day] += 1
        monthly_counts[month] += 1
        if 'sticker' in message:
            daily_sticker_counts[day] += 1
            monthly_sticker_counts[month] += 1

        # Rudimentary sentiment analysis using VADER
        sentiments = sentiment_analyzer.polarity_scores(content)
        daily_sentiments[day] += sentiments['pos'] - sentiments['neg']

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
    for day, message_count in daily_counts.items():
        daily_sentiments[day] /= message_count

    # Get the number of days the messages span over
    num_days = (last_date - first_date).days

    # Get most common words
    top_words = heapq.nlargest(42, word_frequencies.items(), key=itemgetter(1)) 

    print('Processed data in {0:.2f} seconds.'.format(time.clock() - timestamp))

    print('Preparing data for display ...')

    # Format data for graphing
    xdata_daily = sorted(list(daily_counts.keys()))
    ydata_daily = [daily_counts[x] for x in xdata_daily]
    ydata_daily_stickers = [daily_sticker_counts[x] for x in xdata_daily]
    xdata_monthly = sorted(list(monthly_counts.keys()))
    ydata_monthly = [monthly_counts[x] for x in xdata_monthly]
    ydata_monthly_stickers = [monthly_sticker_counts[x] for x in xdata_monthly]
    xdata_day_name = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    ydata_day_name = [float(day_name_counts[x]) / num_days * 7 for x in xdata_day_name]
    xdata_hourly = ['{0}:00'.format(i) for i in range(24)]
    ydata_hourly = [float(hourly_counts[x]) / num_days for x in range(24)]
    xdata_sentiment = sorted(list(daily_sentiments.keys()))
    ydata_sentiment = [daily_sentiments[x] for x in xdata_sentiment]
    xdata_top_words, ydata_top_words = zip(*top_words) 

    '''
    DATA VISUALIZATION 
    '''

    print('Displaying ...')

    # Generate subplots
    fig, ax_array = plt.subplots(2, 3)

    def show_daily_total_graph(ax, xdata, ydata, ydata_stickers):
        indices = np.arange(len(xdata))

        ax.plot(indices, ydata, 
                alpha=1.0, color='dodgerblue', 
                label='All messages')

        ax.plot(indices, ydata_stickers, 
                alpha=1.0, color='orange', 
                label='Facebook stickers')

        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title('Number of messages exchanged every day')

        num_ticks = 16 if len(indices) >= 16 else len(indices)
        tick_spacing = round(len(indices) / num_ticks)
        ticks = [tick_spacing * i for i in range(num_ticks) if tick_spacing * i < len(xdata)]
        tick_labels = [xdata[tick] for tick in ticks]

        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

        ax.legend()

    def show_monthly_total_graph(ax, xdata, ydata, ydata_stickers):
        indices = np.arange(len(xdata))

        ax.bar(indices, ydata, 
                alpha=1.0, color='dodgerblue', 
                label='All messages')

        ax.bar(indices, ydata_stickers, 
                alpha=1.0, color='orange', 
                label='Facebook stickers')

        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title('Number of messages exchanged every month')

        ax.set_xticks(indices)
        ax.set_xticklabels(xdata)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

        ax.legend()
   
    def show_day_name_average_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))
        bar_width = 0.6
        
        ax.bar(indices, ydata, bar_width, 
                alpha=1.0, color='dodgerblue',
                align='center',
                label='All messages')

        ax.set_xlabel('Day of the Week')
        ax.set_ylabel('Count')
        ax.set_title('Average number of messages every day of the week')

        ax.set_xticks(indices)
        ax.set_xticklabels(xdata)

    def show_hourly_average_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))
        bar_width = 0.8
        
        ax.bar(indices, ydata, bar_width, 
                alpha=1.0, color='dodgerblue',
                align='center',
                label='All messages')

        ax.set_xlabel('Hour')
        ax.set_ylabel('Count')
        ax.set_title('Average number of messages every hour of the day')

        ax.set_xticks(indices)
        ax.set_xticklabels(xdata)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)

    def show_daily_sentiment_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))

        ax.plot(indices, ydata, 
                alpha=1.0, color='darkseagreen', 
                label='VADER sentiment')

        ax.set_xlabel('Date')
        ax.set_ylabel('Sentiment')
        ax.set_title('Average sentiment over time')

        num_ticks = 16 if len(indices) >= 16 else len(indices)
        tick_spacing = round(len(indices) / num_ticks)
        ticks = [tick_spacing * i for i in range(num_ticks) if tick_spacing * i < len(xdata)]
        tick_labels = [xdata[tick] for tick in ticks]

        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)
        for tick in ax.get_xticklabels():
            tick.set_rotation(30)
        ax.set_ylim([-1.0, 1.0])

        ax.legend()

    def show_top_words_graph(ax, xdata, ydata):
        indices = np.arange(len(xdata))
        bar_width = 0.8
        
        ax.barh(indices, ydata, bar_width, 
                alpha=1.0, color='orchid',
                align='center',
                label='All messages')

        ax.set_ylabel('Word')
        ax.set_xlabel('Uses')
        ax.set_title('Our {0} most used words'.format(len(xdata)))

        ax.set_yticks(indices)
        ax.set_yticklabels(xdata)

    # Call the graphing methods
    show_daily_total_graph(ax_array[0][0], xdata_daily, ydata_daily, ydata_daily_stickers)
    show_monthly_total_graph(ax_array[0][1], xdata_monthly, ydata_monthly, ydata_monthly_stickers)
    show_daily_sentiment_graph(ax_array[0][2], xdata_sentiment, ydata_sentiment)
    show_day_name_average_graph(ax_array[1][0], xdata_day_name, ydata_day_name)
    show_hourly_average_graph(ax_array[1][1], xdata_hourly, ydata_hourly)
    show_top_words_graph(ax_array[1][2], xdata_top_words[::-1], ydata_top_words[::-1])

    # Display the plots
    plt.show()

    print('Done.')


