import os

# import requests
from tqdm import tqdm
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


import gdown


def get_db():
    index_folder = os.path.join("data", "faiss_index")
    embeddings = OpenAIEmbeddings()

    if not os.path.exists(index_folder):
        # https://drive.google.com/drive/folders/1v3o7i-ONbVY2F6Wh-2_-ucYCLRAUMBxq?usp=share_link
        gdown.download_folder(output=index_folder, quiet=False, id="1v3o7i-ONbVY2F6Wh-2_-ucYCLRAUMBxq")

    return FAISS.load_local(index_folder, embeddings)


def main():
    # Shared Google Drive links
    # pdf_links = [
    #     "https://drive.google.com/file/d/1Lo2iuTBN5SWMcUnHfGA_O0bO6bBTzApF/view?usp=share_link",
    #     "https://drive.google.com/file/d/1-ZTP4g6LKMXdnp80QV79wZuP_dmZtgiw/view?usp=share_link",
    # ]

    # Get the ID of each file from the above links
    pdf_ids = [
        "1Lo2iuTBN5SWMcUnHfGA_O0bO6bBTzApF",
        "1-ZTP4g6LKMXdnp80QV79wZuP_dmZtgiw",
    ]

    pdf_folder = os.path.join("data", "pdf")
    index_folder = os.path.join("data", "faiss_index")
    os.makedirs(pdf_folder)
    os.makedirs(index_folder)

    for i, pdf_id in tqdm(enumerate(pdf_ids), desc="Downloading PDFs"):
        gdown.download(output=os.path.join(pdf_folder, f"{i}.pdf"), quiet=False, id=pdf_id)

        # If you want to download for a website other than gdrive
        #     response = requests.get(pdf_link, stream=True)
        #     assert response.status_code == 200
        #     with open(os.path.join(pdf_folder, f"{i}.pdf"), "wb") as f:
        #         for chunk in response.iter_content(512):
        #             f.write(chunk)

    embeddings = OpenAIEmbeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    splitted_documents = []
    for pdf_file_name in tqdm(os.listdir(pdf_folder), desc="Ingesting"):
        pdf_file_path = os.path.join(pdf_folder, pdf_file_name)

        loader = PyPDFLoader(pdf_file_path)
        documents = loader.load()
        splitted_documents += text_splitter.split_documents(documents)

    print("Creating embeddings...", end="")
    db = FAISS.from_documents(splitted_documents, embeddings)
    print(" Done!")

    print("Saving embeddings...", end="")
    db.save_local(index_folder)
    print(" Done!")


if __name__ == "__main__":
    main()
