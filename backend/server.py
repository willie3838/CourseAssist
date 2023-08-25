from flask import Flask, request
import PyPDF2
from flask_cors import CORS

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryMemory

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

OPEN_API_KEY = "test"
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
llm = ChatOpenAI(openai_api_key=OPEN_API_KEY)
vectorstore = Chroma("course-assist-store", embeddings)


@app.route("/pdf-to-text", methods=["POST"])
def convertText():
    pdfFile = request.files["file"]
    text = extractTextFromPDF(pdfFile)
    storeText(text)
    return "", 201


@app.route("/chat", methods=["GET"])
def chat():
    message = request.args["message"]
    memory = ConversationSummaryMemory(
        llm=llm, memory_key="chat_history", return_messages=True
    )
    retriever = vectorstore.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    res = qa(message)
    print("Res: ", res)
    return res["answer"], 201


def storeText(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=60)
    all_splits = text_splitter.split_text(text)
    vectorstore.add_texts(texts=all_splits)
    print("Successfully embedded file")

    # llm = ChatOpenAI(openai_api_key=OPEN_API_KEY)
    # memory = ConversationSummaryMemory(
    #     llm=llm, memory_key="chat_history", return_messages=True
    # )

    # retriever = vectorstore.as_retriever()
    # qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    # res = qa("What did I do at Scale AI?")
    # print("Res: ", res)


def extractTextFromPDF(pdfFile):
    pdfFile = request.files["file"]
    pdfReader = PyPDF2.PdfReader(pdfFile)
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()
    return text


if __name__ == "__main__":
    app.run(debug=True)
