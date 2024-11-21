
from ollama_functions import Ollama
import argparse
from colors import PINK, CYAN, YELLOW, NEON_GREEN, RESET_COLOR
   
parser = argparse.ArgumentParser(description="Ollama Chat")
parser.add_argument("--model", default="llama3.2", help="Ollama model to use (default: llama3.2)")
args = parser.parse_args()

OllamaFunctions = Ollama(args.model)

while True:
    user_input = input(YELLOW + "Ask something about knitting (or type 'quit' to exit and add '--NORAG' to query without document information): " + RESET_COLOR)
    if user_input.lower() == 'quit':
        break
    print(CYAN + "Let me think about all this" + RESET_COLOR)
    
    if "--NORAG" in user_input:
        response = OllamaFunctions.ollama_no_rag_chat(user_input)
    else:
        response = OllamaFunctions.ollama_chat(user_input)
    print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
