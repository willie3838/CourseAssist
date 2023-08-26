from flask import Flask, request
import PyPDF2
from flask_cors import CORS

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI

from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

OPEN_API_KEY = "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"
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
llm = ChatOpenAI(temperature=0, openai_api_key=OPEN_API_KEY)
vectorstore = Chroma("course-assist-store", embeddings, persist_directory="./chroma_db")
tools = []

@app.route("/pdf-to-text", methods=["POST"])
def convertText():
    pdfFile = request.files["file"]
    text = extractTextFromPDF(pdfFile)
    storeText(text)
    return "", 201


@app.route("/chat", methods=["GET"])
def chat():
    message = request.args["message"]
    template = f'''
    Context:
    You're a chatbot having a conversation with a student. Your
    goal is to provide them information about the course they're inquiring about since
    you have access to the course syllabus. If a student talks about assessments, they're referring to quizzes, assignments,
    midterms, and finals.

    Student's question:
    {message}

    Your response:
    '''
    
    retriever = vectorstore.as_retriever()
    tool = create_retriever_tool(
        retriever, 
        "search_course_info",
        "Searches and returns documents regarding course information."
    )
    tools = [tool]
    agent_executor = create_conversational_retrieval_agent(llm, tools, verbose=True)
    result = agent_executor({
        "input": template
    })
   
    return result["output"], 201


def storeText(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=60)
    all_splits = text_splitter.split_text(text)
    vectorstore.add_texts(texts=all_splits)
    print("Successfully embedded file")

def extractTextFromPDF(pdfFile):
    pdfFile = request.files["file"]
    pdfReader = PyPDF2.PdfReader(pdfFile)
    text = ""
    for page in pdfReader.pages:
        text += page.extract_text()
    return text


if __name__ == "__main__":
    app.run(debug=True)
