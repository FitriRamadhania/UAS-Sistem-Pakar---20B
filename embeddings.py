from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Memuat variabel lingkungan
load_dotenv()

# Langkah 1: Memuat dokumen PDF
loader = PyPDFLoader("DATASET TBC.pdf")
data = loader.load()
print("Jumlah dokumen dalam PDF: ", len(data))

# Langkah 2: Memecah dokumen menjadi bagian kecil
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)
print("Jumlah dokumen setelah dipecah: ", len(docs))
print("Contoh isi dokumen ke-7:\n", docs[7].page_content)

# Langkah 3: Membuat embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector = embeddings.embed_query("diagnosa tuberkulosis")
print("Contoh vektor embedding:\n", vector[:5])

# Langkah 4: Membuat dan menyimpan vectorstore ke folder khusus
save_folder = "data"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
vectorstore.persist(save_folder)  # Menyimpan vectorstore ke folder khusus
print(f"Vectorstore berhasil disimpan di folder: {save_folder}")

# Langkah 5: Memuat kembali vectorstore dari folder khusus
vectorstore = Chroma.load(save_folder, embedding=embeddings)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
print("Vectorstore berhasil dimuat kembali.")

# Langkah 6: Mengambil dokumen relevan untuk diagnosa TBC
retrieved_docs = retriever.invoke("Bagaimana cara mendiagnosis TBC aktif?")
print("Jumlah dokumen yang diambil: ", len(retrieved_docs))
print("Contoh isi dokumen yang relevan:\n", retrieved_docs[5].page_content)

# Langkah 7: Mengatur model LLM dan prompt
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3, max_tokens=500)
system_prompt = (
            "Anda adalah asisten tentang penyakit TBC dengan nama TBCheck. "
            "Anda hanya memproses jawaban menggunakan data dari dataset yang telah dilatih"
            "Data yang Anda peroleh berasal dari seorang pakar dr. Syarifuddin Sp. PD, "
            "dokter spesialis penyakit dalam yang praktik di RS Mutiara dan RS Sele Be Solu Kota Sorong."
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Langkah 8: Membuat chain untuk tanya jawab
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Langkah 9: Menjawab pertanyaan tentang diagnosis TBC
response = rag_chain.invoke({"input": "Apa itu IGRA (Interferon-Gamma Release Assays)?"})
print("Jawaban:\n", response["answer"])
