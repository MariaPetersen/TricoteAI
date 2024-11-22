# TricoteAI: A Versatile Question-Answering Platform About Knitting

TricoteAI is an interactive and flexible project that enables users to ask questions based on various documents while controlling the creativity of the generated answers. With a straightforward setup process, TricoteAI is designed to be user-friendly and adaptable for different operating systems.

---

## Features
- Creative Control: Adjust the creativity level of the AI's answers to suit your needs—ranging from precise factual responses to imaginative interpretations.
- Document-Based Q&A: Ask questions that derive insights directly from the document you chose.

---

## Prerequisites

Before getting started, ensure your local machine meets the following requirements:

1. Python: Install the latest version of Python (>=3.8) from Python.org.
2. Ollama: Download and install Ollama, which is used to manage language models. Visit Ollama's website for installation instructions.

---

## Setup Instructions

1. Clone the repository
Clone the TricoteAI project repository to your local machine:
```bash
git clone https://github.com/MariaPetersen/TricoteAI
cd tricoteai
```
2. Install Dependencies
Install the required Python dependencies:
```bash
pip install -r requirements.txt
```
3. Download Required Models
- Llama 3.2:
```bash
ollama pull llama3.2
```
- mxbai-embed-large:
```bash
ollama pull mxbai-embed-large
```
4. Launch the Project
Run the project from the project folder using main.py with the following commands:
- On Windows:
```bash
python main.py
```
- On macOS/Linux:
```bash
python3 main.py
```
5. Interact with TricoteAI
Once launched, follow the on-screen prompts to load your documents, adjust creativity settings, and start asking questions.
