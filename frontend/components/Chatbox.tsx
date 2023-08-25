import { Button, TextField } from "@mui/material";
import { useState } from "react";

interface ChatBoxProps {
  message: string;
  isAlternate: boolean;
}

export default function ChatBox({ message, isAlternate }: ChatBoxProps) {
  return (
    <div
      className={`mt-2 rounded-md p-6 
      ${
        isAlternate ? "bg-white" : "bg-slate-300"
      } text-black transition-opacity ease-in duration-1000 opacity-100`
    }
    >
      {message}
    </div>
  );
}
