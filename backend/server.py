from queue import Queue, Empty
from threading import Thread

from flask import Flask, Response, request
import PyPDF2
from flask_cors import CORS

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent

class StreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.q.put(token)
    
    def on_llm_end(self, *args, **kwargs) -> None:
        return self.q.empty()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
OPEN_API_KEY = "test"

q = Queue()
job_done = object()
embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
llm = ChatOpenAI(streaming=True, temperature=0, openai_api_key=OPEN_API_KEY, callbacks=[StreamingHandler(q)])
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
    def event_stream():
        while True:
            try:
                next_token = q.get()
                if next_token is job_done:
                    break
                yield next_token
            except Empty:
                continue
        
        while not q.empty():
            q.get()

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
    agent_executor({
        "input": template
    })

    return Response(event_stream(), mimetype="text/event-stream")


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
