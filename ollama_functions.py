import torch
import os
import ollama
import json
from openai import OpenAI
from colors import PINK, CYAN, YELLOW, NEON_GREEN, RESET_COLOR

class Ollama():
    def __init__(self, ollama_model):
        self.model_url = 'http://localhost:11434/v1'
        self.embeddings_file = "vault_embeddings.pt"
        self.vault_content = self.get_vault_content()
        self.client = OpenAI(
                base_url=self.model_url,
                api_key='llama3'
            )
        self.conversation_history = []
        self.system_message = "You are a helpful assistant that is an expert in knitting by extracting the most useful tips from the given document."
        self.ollama_model = ollama_model
        
    def save_embeddings(self, embeddings, filepath):
        torch.save(embeddings, filepath)
        
    def load_embeddings(self, filepath):
        if os.path.exists(filepath):
            return torch.load(filepath, weights_only=False)
        return None
    
    def get_vault_content(self):
        vault_content = []
        if os.path.exists("vault.txt"):
            with open("vault.txt", "r", encoding='utf-8') as vault_file:
                vault_content = vault_file.readlines()
        return vault_content
    
    def get_relevant_context(self, rewritten_input, top_k=3):
        vault_embeddings = self.get_vault_embeddings_tenor()
        if vault_embeddings.nelement() == 0:
            return []
        input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
        cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
        top_k = min(top_k, len(cos_scores))
        top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
        relevant_context = [self.vault_content[idx].strip() for idx in top_indices]
        return relevant_context
    
    def get_vault_embeddings_tenor(self):
        vault_embeddings_tensor = self.load_embeddings(self.embeddings_file)

        if vault_embeddings_tensor is None:
            vault_embeddings = []
            for content in self.vault_content:
                response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
                vault_embeddings.append(response["embedding"])
            vault_embeddings_tensor = torch.tensor(vault_embeddings) 
            self.save_embeddings(vault_embeddings_tensor, self.embeddings_file)
        return vault_embeddings_tensor
    
    def rewrite_query(self, user_input_json):
        user_input = json.loads(user_input_json)["Query"]
        user_input.replace("--NORAG", "")
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-2:]])
        prompt = f"""Rewrite the following query by incorporating relevant context from the conversation history.
        The rewritten query should:
        
        - Preserve the core intent and meaning of the original query
        - Expand and clarify the query to make it more specific and informative for retrieving relevant context
        - Avoid introducing new topics or queries that deviate from the original query
        - DONT EVER ANSWER the Original query, but instead focus on rephrasing and expanding it into a new query
        
        Return ONLY the rewritten query text, without any additional formatting or explanations.
        
        Conversation History:
        {context}
        
        Original query: [{user_input}]
        
        Rewritten query: 
        """
        response = self.client.chat.completions.create(
            model=self.ollama_model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=200,
            n=1,
            temperature=0.1,
        )
        rewritten_query = response.choices[0].message.content.strip()
        return json.dumps({"Rewritten Query": rewritten_query})
    
    
    def get_rewritten_query(self, user_input):
        if len(self.conversation_history) > 1:
            query_json = {
                "Query": user_input,
                "Rewritten Query": ""
            }
            rewritten_query_json = self.rewrite_query(json.dumps(query_json))
            rewritten_query_data = json.loads(rewritten_query_json)
            rewritten_query = rewritten_query_data["Rewritten Query"]
        else:
            rewritten_query = user_input
        return rewritten_query
    
    def ask_ollama(self):
        messages = [
            {"role": "system", "content": self.system_message},
            *self.conversation_history
        ]
        
        response = self.client.chat.completions.create(
            model=self.ollama_model,
            messages=messages,
            max_tokens=2000,
        )
        
        self.conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
        
        return response.choices[0].message.content
        
    def ollama_chat(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        rewritten_query = self.get_rewritten_query(user_input)
        relevant_context = self.get_relevant_context(rewritten_query)
        if relevant_context:
            context_str = "\n".join(relevant_context)
        
        user_input_with_context = user_input
        if relevant_context:
            user_input_with_context = user_input + "\n\nRelevant Context:\n" + context_str
        
        self.conversation_history[-1]["content"] = user_input_with_context
        
        return self.ask_ollama()
    
    def ollama_no_rag_chat(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        rewritten_query = self.get_rewritten_query(user_input)
        self.conversation_history[-1]["content"] = rewritten_query
        
        return self.ask_ollama()
