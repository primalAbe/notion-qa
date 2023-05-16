import json
from bs4 import BeautifulSoup

# Read the HTML file from current directory using os

path = 'C:/repos/notion-qa/bookmarker/bookmarks.html'

with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

# Parse the HTML
soup = BeautifulSoup(html, 'html.parser')

# Find all anchor tags
anchors = soup.find_all('a')

# Create a dictionary to store the anchor text and href
result = {}
for anchor in anchors:
    text = anchor.text
    href = anchor['href']
    result[text] = href

# Convert the dictionary to JSON
json_data = json.dumps(result, indent=4)

# write the JSON data
with open('./bookmarks.json', 'w') as f:
        f.write(json_data)

#  remove all data.values that don't start with http or https
data = {key:val for key, val in result.items() if val.startswith('http')}

import os
os.environ["OPENAI_API_KEY"] = '[OPENAI_API_KEY]'

from langchain.document_loaders import PlaywrightURLLoader
urls = list(data.values())
loader = PlaywrightURLLoader(urls=urls[:5], remove_selectors=["header", "footer"])
documents = loader.load()

# Convert the dictionary to JSON
json_data = json.dumps(documents, indent=4)

# write the JSON data
with open('./documents.json', 'w') as f:
        f.write(json_data)


# from langchain.text_splitter import CharacterTextSplitter
# text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=100, chunk_overlap=0)
# documents = text_splitter.split_documents(documents)

# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma.from_documents(documents, embeddings)

# from langchain.memory import ConversationBufferMemory
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# from langchain.chains import ConversationalRetrievalChain
# from langchain.llms import OpenAI
# qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0), vectorstore.as_retriever(), memory=memory)




