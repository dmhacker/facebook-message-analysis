import argparse
import analyzer

parser = argparse.ArgumentParser(description='Analyze your Facebook Messenger history')
parser.add_argument('file', metavar='F', help='Facebook chat messages in JSON format')

args = parser.parse_args()
analyzer.analyze(args.file)
