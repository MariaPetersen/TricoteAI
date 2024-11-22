from rich.console import Console
from rich.prompt import Prompt
from constants.colors import PINK, RESET_COLOR

        

        



class AISettings():
    def __init__(self):
        self.temperature = 0.3
        self.file_id = None
        self.console = Console()
        
    def _set_temperature(self, temperature):
        self.temperature = temperature
        print(PINK + f"Temperature set to: {temperature}" + RESET_COLOR)
    
    def _set_file_id(self, file_id, file_name):
        self.file_id = file_id
        if not self.file_id:
            print(PINK + f"I will answer you question without using a document" + RESET_COLOR)
        else:
            print(PINK + f"I will answer you question using the document: {file_name}" + RESET_COLOR)
    
    def ask_temperature(self):
        self.console.print("[bold]Choose the creativity of your answer :[/bold]")
        self.console.print("[1] Low")
        self.console.print("[2] Medium")
        self.console.print("[3] High")
        choice = Prompt.ask("Enter the number of your choice", choices=["1", "2", "3"])
        if choice == "1":
            self._set_temperature(0.1)
        elif choice == "2":
            self._set_temperature(0.6)
        elif choice == "3":
            self._set_temperature(1.5)
            
    def ask_document_settings(self):
        self.console.print("[bold]Would you like to base the answer on a document :[/bold]")
        self.console.print("[1] Bergere France - Knitting basics")
        self.console.print("[2] University of Kentucky - Beginning knitting")
        self.console.print("[3] No")
        choice = Prompt.ask("Enter the number of your choice", choices=["1", "2"])
        if choice == "1":
            self._set_file_id("188r6xcoIUYk9W6wJiHyfVRCGyJPFQiLu", "Bergere France - Knitting basics")
        if choice == "2":
            self._set_file_id("1uvwhgZOApTXtpt_2i5046leEqX1p3g8c", "University of Kentucky - Beginning knitting")
        elif choice == "3":
            self._set_file_id(None, None)
        