
from ai.ollama_functions import Ollama
from ai.upload import PDFProcessor
from console.settings import AISettings
import argparse
from constants.colors import CYAN, YELLOW, PINK, NEON_GREEN, RESET_COLOR

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ollama Chat")
    parser.add_argument("--model", default="llama3.2", help="Ollama model to use (default: llama3.2)")
    args = parser.parse_args()
    
    ollama_class = Ollama(args.model)
    ai_settings = AISettings()
    processor = PDFProcessor()
    
    while True:
        ai_settings.ask_temperature()
        ai_settings.ask_document_settings()
        user_input = input(YELLOW + "Ask something about knitting (or type 'quit' to exit): " + RESET_COLOR)
        print(CYAN + "Let me think about all this..." + RESET_COLOR)
        if user_input.lower() == 'quit':
            break
        if ai_settings.file_id:
            processor.process_pdf(ai_settings.file_id)
            response = ollama_class.ollama_chat(user_input, ai_settings.temperature, ai_settings.file_id)
        else:
            print(CYAN + "Answering your question without using a RAG" + RESET_COLOR)
            response = ollama_class.ollama_no_rag_chat(user_input, ai_settings.temperature)
            
        print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
