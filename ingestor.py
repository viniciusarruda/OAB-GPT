import os
from tqdm import tqdm
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


def main():
    embeddings = OpenAIEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    splitted_documents = []
    pdf_folder = os.path.join("data", "pdf")
    for pdf_file_name in tqdm(os.listdir(pdf_folder), desc="Ingesting"):
        pdf_file_path = os.path.join(pdf_folder, pdf_file_name)

        loader = PyPDFLoader(pdf_file_path)
        documents = loader.load()
        splitted_documents += text_splitter.split_documents(documents)

    db = FAISS.from_documents(splitted_documents, embeddings)
    db.save_local(os.path.join("data", "faiss_index"))


if __name__ == "__main__":
    main()
