from langchain_community.document_loaders import PyPDFLoader

# Memuat file PDF
loader = PyPDFLoader("DATASET.pdf")
data = loader.load()  # Seluruh PDF dimuat sebagai satu Dokumen
#data
len(data)

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Membagi data menjadi beberapa bagian
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_documents(data)

print("Total jumlah dokumen: ", len(docs))
docs[7]

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

# Mendapatkan API key:
# Buka https://ai.google.dev/gemini-api/docs/api-key untuk menghasilkan Google AI API key dan tempelkan di file .env

# Model embedding: https://python.langchain.com/v0.1/docs/integrations/text_embedding/

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector = embeddings.embed_query("halo, dunia!")
vector[:5]
#vector
vectorstore = Chroma.from_documents(documents=docs, embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Melakukan pencarian terhadap dokumen terkait pertanyaan
retrieved_docs = retriever.invoke("apa saja penyakit pada jagung?")
len(retrieved_docs)
print(retrieved_docs[5].page_content)

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_tokens=500)
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Prompt untuk asisten menjawab pertanyaan terkait penyakit jagung
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

# Membuat rantai tanya jawab
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Mengajukan pertanyaan terkait penyakit jagung
response = rag_chain.invoke({"input": "Apa saja penyakit umum yang menyerang tanaman jagung?"})
print(response["answer"])
