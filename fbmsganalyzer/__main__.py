import argparse
import analyzer

parser = argparse.ArgumentParser(description='Tool to analyze your Facebook Messenger history')
parser.add_argument('file', help='Facebook chat messages in JSON format') 

args = parser.parse_args()
analyzer.analyze(args.file)
