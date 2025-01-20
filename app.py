from flask import Flask, render_template, request, jsonify, session
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain  # Gunakan LLMChain jika tidak ada RunnableSequence
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan
load_dotenv()

app = Flask(__name__)

# Set secret key untuk manajemen sesi               
app.secret_key = os.urandom(24)

# Memuat vectorstore yang sudah ada dari direktori "data"
try:
    vectorstore = Chroma(
        persist_directory="data",
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/bert-base-nli-max-tokens")
    )
    print("Vectorstore berhasil dimuat.")
except Exception as e:
    print(f"Kesalahan saat memuat vectorstore: {e}")

# Menyiapkan retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Menyiapkan model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, max_tokens=None, timeout=None)

# Membuat memori
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Membuat prompt dengan memori
prompt = ChatPromptTemplate(
    messages=[
        SystemMessagePromptTemplate.from_template(
            "Anda adalah asisten tentang penyakit TBC dengan nama TBCheck. "
            "Anda hanya memproses jawaban menggunakan data dari dataset yang telah dilatih"
            "Berikan jawaban yang lengkap dan ringkas"
            "Data yang Anda peroleh berasal dari seorang pakar dr. Syarifuddin Sp. PD, "
            "dokter spesialis penyakit dalam yang praktik di RS Mutiara dan RS Sele Be Solu Kota Sorong."
            "SIstem ini dirancang oleh Fitri Ramadhania dan Chenitia P Suardi. "
            "mahasiswa Universitas Muhammadiyah Sorong "
        ),
        MessagesPlaceholder(variable_name="chat_history"),  # Memori akan otomatis disisipkan di sini
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)

# Membuat chain dengan LLMChain
conversation_chain = LLMChain(
    llm=llm,
    prompt=prompt,  # Pastikan memberikan prompt
    memory=memory,
    verbose=True
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/coba')
def kidzicare():
    return render_template('coba.html')

@app.route('/about')
def abouti():
    return render_template('about.html')

@app.route('/get', methods=['GET'])
def get_response():
    user_message = request.args.get('msg')  # Ambil pesan dari user
    
    # Ambil riwayat percakapan dari sesi Flask
    if "chat_history" not in session:
        session["chat_history"] = []

    # Gabungkan semua pesan sebelumnya dalam chat history sebagai konteks
    conversation_history = session["chat_history"]
    
    # Proses input dengan chain yang sudah terintegrasi dengan memori
    result = conversation_chain.run({"question": user_message})  # Memori otomatis diperbarui
    
    # Simpan pesan pengguna dan respons bot ke dalam riwayat percakapan
    conversation_history.append({"sender": "user", "message": user_message})
    conversation_history.append({"sender": "bot", "message": result})

    # Simpan kembali riwayat percakapan dalam sesi Flask
    session["chat_history"] = conversation_history

    return jsonify(result)  # Kembalikan respons ke front-end

@app.route('/load_history', methods=['GET'])
def load_history():
    # Mengembalikan riwayat percakapan yang ada dalam sesi
    conversation_history = session.get("chat_history", [])
    return jsonify(conversation_history)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Menghapus riwayat percakapan dari sesi
    session.pop("chat_history", None)
    memory.clear() 
    return jsonify({"status": "success", "message": "Riwayat percakapan telah dihapus"})

# Perbaikan penulisan __main__
if __name__ == '__main__':
    app.run(debug=True)
