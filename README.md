# facebook-message-analysis

1. Download your Facebook messenger history from your Facebook settings. [More here.](https://webapps.stackexchange.com/questions/27640/how-can-i-download-all-messages-from-facebook)
2. Unzip your data into the directory of your choice.
3. Identify a person whose chat history you want to analyze.
4. Find the JSON file listing all of their messages with you (it's going to named after their username).
5. Now, run:

```
git clone https://github.com/dmhacker/facebook-message-analysis && cd facebook-message-analysis
python fbmsganalysis FILE
```
<sup><sub>Replace FILE with the JSON file you identified earlier.</sub><sup>

In a few seconds, you should have some nice & pretty graphs that might reveal some interesting insights into your messages
with whomever you choose earlier.

## Troubleshooting

If you get an import error, it means that the dependencies that `facebook-message-analysis` needs are not installed.
Use this command inside the project directory to install them:

```
pip install -r requirements.txt
```

If you get an NLTK download error, it means that NLTK hasn't downloaded the stopwords file that `facebook-message-analysis` uses.
Use this command inside the project directory to resolve this:

```
python
>>> import nltk
>>> nltk.download('stopwords')
>>> quit()
```
