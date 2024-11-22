import torch
import os
import ollama
import json
from openai import OpenAI
from constants.colors import PINK, CYAN, YELLOW, NEON_GREEN, RESET_COLOR

class Ollama():
    def __init__(self, ollama_model, embeddings_file=None, vault_file=None, api_key="llama3"):
        self.model_url = "http://localhost:11434/v1"
        self.embeddings_file = embeddings_file or os.path.join("data", "vault_embeddings.pt")
        self.vault_file = vault_file or os.path.join("data", "vault.txt")
        self.ollama_model = ollama_model
        self.client = OpenAI(base_url=self.model_url, api_key=api_key)
        self.system_message = (
            """You are a helpful assistant that is an expert in knitting 
            by extracting the most useful tips from the given relevant context. 
            If you are given a relevant context in the query, please use as much 
            information as possible from that context in you answer."""
        )
        self.conversation_history = []
        self.vault_content = self._load_vault_content()
        
    def _save_embeddings(self, embeddings, filepath):
        torch.save(embeddings, filepath)
        
    def _load_embeddings(self, filepath):
        if os.path.exists(filepath):
            return torch.load(filepath, weights_only=True)
        return None
    
    def _load_vault_content(self):
        if os.path.exists(self.vault_file):
            with open(self.vault_file, "r", encoding="utf-8") as file:
                return file.readlines()
        return []
    
    def _generate_embeddings(self, content):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=content)
        return response["embedding"]
    
    def _get_vault_embeddings(self):
        embeddings = self._load_embeddings(self.embeddings_file)
        if embeddings is None:
            embeddings = [
                self._generate_embeddings(content) for content in self.vault_content
            ]
            embeddings_tensor = torch.tensor(embeddings)
            self._save_embeddings(embeddings_tensor)
            return embeddings_tensor
        return embeddings
    
    def _get_relevant_context(self, rewritten_input, top_k=3):
        vault_embeddings = self._get_vault_embeddings()
        if vault_embeddings.nelement() == 0:
            return []
        input_embedding = torch.tensor(
            self._generate_embeddings(rewritten_input)
        ).unsqueeze(0)
        cos_scores = torch.cosine_similarity(input_embedding, vault_embeddings)
        top_indices = torch.topk(cos_scores, k=min(top_k, len(cos_scores))).indices.tolist()
        return [self.vault_content[idx].strip() for idx in top_indices]
    
    
    def _rewrite_query(self, user_input_json):
        user_input = json.loads(user_input_json)["Query"]
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
            messages=[{"role": "assistant", "content": prompt}],
            max_tokens=500,
            n=1,
            temperature=0.1,
        )
        print("rewrittine queury ", response.choices[0].message.content.strip())
        return json.dumps({"Rewritten Query": response.choices[0].message.content.strip()})
    
    def _get_rewritten_query(self, user_input):
        if len(self.conversation_history) > 1:
            query_json = json.dumps({"Query": user_input, "Rewritten Query": ""})
            rewritten_query_json = self._rewrite_query(query_json)
            rewritten_query_data = json.loads(rewritten_query_json)
            return rewritten_query_data["Rewritten Query"]
        return user_input
        
    def _ask_ollama(self, temperature):
        messages = [
            {"role": "system", "content": self.system_message},
            *self.conversation_history,
        ]
        response = self.client.chat.completions.create(
            model=self.ollama_model, messages=messages, max_tokens=2000, temperature=temperature
        )
        assistant_message = response.choices[0].message.content.strip()
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        return assistant_message
    
    def ollama_chat(self, user_input, temperature):
        self.conversation_history.append({"role": "user", "content": user_input})
        rewritten_query = self._get_rewritten_query(user_input)
        relevant_context = self._get_relevant_context(rewritten_query)

        if relevant_context:
            context_str = "\n".join(relevant_context)
            print(CYAN + "Context: " + context_str + RESET_COLOR)
            rewritten_query += f"\n\nRelevant Context:\n{context_str}"
            

        self.conversation_history[-1]["content"] = rewritten_query
        return self._ask_ollama(temperature)
    
    def ollama_no_rag_chat(self, user_input, temperature):
        user_input = user_input.replace("--NORAG", "")
        self.conversation_history.append({"role": "user", "content": user_input})
        rewritten_query = self._get_rewritten_query(user_input)
        self.conversation_history[-1]["content"] = rewritten_query
        return self._ask_ollama(temperature)
