# facebook-message-analysis

1. Download your Facebook messenger history from your Facebook settings. 
[More here.](https://webapps.stackexchange.com/questions/27640/how-can-i-download-all-messages-from-facebook)
2. Unzip your data into the directory of your choice.
3. Identify a person whose chat history you want to analyze.
4. Find the JSON file listing all of their messages with you (named after their username).
    1. We will refer to this file's path as **${FILE}**.
5. Clone this repository and change directory into it.
```
git clone https://github.com/dmhacker/facebook-message-analysis && cd facebook-message-analysis
```
6. Install any dependencies.
```
pip install -r requirements.txt
```
7. If you get an NTLK download error, use this command to resolve the issue. 
It will tell NTLK to download the appropriate stopwords file.
```
python
>>> import nltk
>>> nltk.download('stopwords')
>>> quit()
```
8. Run the analyzer.
```
python fbmessages ${FILE}
```

In a few seconds, you should get some nice visualizations. Have fun!
