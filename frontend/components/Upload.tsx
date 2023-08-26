import { useState } from "react";
import axios from "axios";
import Button from "@mui/material/Button";

export default function Upload() {
  const [selectedFile, setSelectedFile] = useState<any>();
  const [loading, setIsLoading] = useState<boolean>(false);

  const changeHandler = (event: any) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append("file", selectedFile);
    console.log("Form data: ", formData);
    try {
      setIsLoading(true);
      axios.defaults.baseURL = "http://127.0.0.1:5000";
      const config = {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      };

      await axios.post(
        `/pdf-to-text`,
        {
          file: selectedFile,
        },
        config
      );
    } catch (err) {
      console.error("Error uploading file: ", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div>
        <input className="inline-block" type="file" onChange={changeHandler} />
      </div>
      <div>
        <Button
          className="mt-2 bg-blue-500 px"
          size="small"
          variant="contained"
          onClick={handleUpload}
        >
          {loading ? "Loading..." : "Upload"}
        </Button>
      </div>
    </div>
  );
}
