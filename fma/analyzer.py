import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from collections import namedtuple, defaultdict

import parser

def analyze(filename):

    # MESSAGE ANALYSIS
    messages = parser.get_messages(filename)

    message_counts = defaultdict(int)
    sticker_message_counts = defaultdict(int)
    for message in messages:
        truncated_date = message['date'].strftime('%Y-%m')
        message_counts[truncated_date] += 1
        if 'sticker' in message:
            sticker_message_counts[truncated_date] += 1

    print(message_counts)
    print(sticker_message_counts)
    
    xdata = sorted(list(message_counts.keys()))
    ydata = [message_counts[x] for x in xdata]
    ydata_stickers = [sticker_message_counts[x] for x in xdata]

    # DATA VISUALIZATION 
    
    fig, ax = plt.subplots()

    bar_indices = np.arange(len(xdata))
    bar_width = 0.4
    
    ax.bar(bar_indices, ydata, bar_width, 
            alpha=0.5, color='b',
            align='center',
            label='Monthly Message Count')

    ax.bar(bar_indices + bar_width, ydata_stickers, bar_width, 
            alpha=0.5, color='r',
            align='center',
            label='Monthly Sticker Count')

    ax.set_xlabel('Date')
    ax.set_ylabel('Count')
    ax.set_title('Message History')
    ax.set_xticks(bar_indices + bar_width / 2)
    ax.set_xticklabels(xdata)
    ax.legend()

    fig.tight_layout()
    plt.show()



