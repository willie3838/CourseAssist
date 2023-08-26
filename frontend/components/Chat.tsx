import { Button, TextField } from "@mui/material";
import { useState, useEffect, useRef } from "react";
import axios from "axios";
import ChatBox from "./Chatbox";

export default function Chat() {
  const [inputText, setInputText] = useState<string>("");
  const [conversation, setConversation] = useState<string[]>([]);

  const buttonRef = useRef<HTMLButtonElement | null>(null);
  const chatWindowRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const handleKeyPress = (event: any) => {
      if (
        buttonRef.current !== null &&
        event.key === "Enter" &&
        !event.shiftKey &&
        inputText != ""
      ) {
        buttonRef.current.click();
      }
    };

    document.addEventListener("keydown", handleKeyPress);
    return () => {
      document.removeEventListener("keydown", handleKeyPress);
    };
  }, [inputText]);

  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [conversation])

  const inputStyles = {
    color: "white", // Change to your desired text color
  };

  const handleSubmit = async () => {
    setConversation((prevConv) => [...prevConv, inputText]);
    setInputText("");
    await sendMessage();
  };

  const sendMessage = async () => {
    try {
      axios.defaults.baseURL = "http://127.0.0.1:5000";
      const resp = await axios.get(`/chat`, {
        params: {
          message: inputText,
        },
      });
      console.log("RESP: ", resp);
      setConversation((prevConv) => [...prevConv, resp.data]);
    } catch (err) {
      console.error("Error uploading file: ", err);
    }
  };

  const handleChange = (e: any) => {
    if (e.target.value !== "\n") {
      setInputText(e.target.value);
    }
  };

  return (
    <div className="flex flex-col h-full justify-center gap-2">
      <div ref={chatWindowRef} className="bg-blue-800 p-4 h-full rounded-md overflow-y-auto">
        {conversation.length === 0
          ? "Start your conversation by sending a message!"
          : conversation.map((msg, idx) => {
              return (
                <ChatBox key={idx} message={msg} isAlternate={idx % 2 == 0} />
              );
            })}
      </div>

      <div className="flex flex-col">
        <TextField
          className="bg-blue-400 rounded-md w-90"
          multiline
          placeholder={"Input your text here."}
          value={inputText}
          InputProps={{
            style: inputStyles,
          }}
          onChange={handleChange}
        />

        <Button
          ref={buttonRef}
          className="mt-2 bg-red-500"
          size="small"
          variant="contained"
          onClick={handleSubmit}
        >
          Send
        </Button>
      </div>
    </div>
  );
}
