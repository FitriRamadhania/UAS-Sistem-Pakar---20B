from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

file_path = "DATASET.pdf"

def process_pdf():
    loader = PyPDFLoader(file_path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
    docs = text_splitter.split_documents(data)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory="./chroma_storage"
    )
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
    return retriever

retriever = process_pdf()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()  # Mendapatkan data JSON dari permintaan POST
    query = data.get("query", "")

    # Buat chain untuk tanya jawab
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_tokens=500)
    system_prompt = (
        "Anda adalah asisten untuk tugas tanya jawab. "
        "Gunakan potongan konteks yang ditemukan untuk menjawab "
        "pertanyaan berikut. Jika Anda tidak tahu jawabannya, katakan bahwa Anda "
        "tidak tahu. Gunakan maksimal tiga kalimat dan buat jawaban yang singkat."
        "\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    response = rag_chain.invoke({"input": query})  # Mendapatkan jawaban dari chain
    return jsonify({"answer": response["answer"]})

if __name__ == "__main__":
    app.run(debug=True)
