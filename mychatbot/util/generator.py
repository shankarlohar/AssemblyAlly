import os
import warnings

from PyPDF2 import PdfReader
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
import os
from PIL import Image
import google.generativeai as genai

from mychatbot.settings import BASE_DIR


def ready():
    warnings.filterwarnings("ignore")
    os.environ["OPENAI_API_KEY"] = "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"
    doc_reader = PdfReader('./data/guide_1.pdf')

    # Read data from the PDF and split it into chunks
    raw_text = ''
    for i, page in enumerate(doc_reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text

    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    texts = text_splitter.split_text(raw_text)

    # Create embeddings and a vector store for similarity search
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)

    # Load the question-answering chain
    return load_qa_chain(OpenAI(), chain_type="stuff"), docsearch


def give_output(chain, docsearch, query):
    # Perform similarity search and run the chain
    docs = docsearch.similarity_search(query)

    text = chain.run(input_documents=docs, question=query)

    images = find_and_return_image(text)

    return text, images


def find_and_return_image(target_name):
    genai.configure(api_key='AIzaSyA8Jn6cFDCoaH6TNLyvOQvKck7fXxJkrNg')
    model = genai.GenerativeModel('gemini-pro')

    images = []

    for filename in os.listdir('./util/dataimage'):

        response = model.generate_content(
            "if " + filename + " matches to the description: " + target_name + " just say 'Yes' else say 'No"
        )
        if 'yes' in response.text.lower():  # Case-insensitive comparison
            image_path = os.path.join(BASE_DIR, filename)
            images.append(image_path.split('/')[-1])

    # If not found, return the dummy image
    if len(images) == 0:
        images.append('Image_not_available.png')
    return images
