from ai_presenter.reader import Reader
from ai_presenter.text_ai.chatgpt import ScriptChatGPT
import logging
import sys
import argparse


USAGE = '''
Examples:

    python3 make_script.py --plot="a plot with 10 scenes about a space war around Europa" --out=myscript.yml

'''
parser = argparse.ArgumentParser(description='AI Presenter YAML Creator')
parser.add_argument(
    '--plot', dest='plot', required=True,
    default='', help='Plot to send to ChatGPT to create scenes',
)
parser.add_argument(
    '--out', dest='out', required=True,
    default='', help='Path to the YAML script to write',
)
args = parser.parse_args()

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("Program starting")
    gpt = ScriptChatGPT()
    with open(args.out, 'w') as file:
        file.write(gpt.generate(args.plot) + '\n')
    logging.info("Done")
    

if __name__ == '__main__':
    main()