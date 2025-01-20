from flask import Flask, request, render_template, jsonify
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load and process PDF document
loader = PyPDFLoader("DATASET TBC.pdf")
data = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)

# Create vector store and retriever
vectorstore = Chroma.from_documents(documents=docs, embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0, max_tokens=None, timeout=None)

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    query = request.json.get('query', '')
    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": query})
    return jsonify({"answer": response["answer"]})

if __name__ == '__main__':
    app.run(debug=True)
