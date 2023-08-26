import Chat from "@/components/Chat";
import Upload from "@/components/Upload";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
  },
});

export default function Home() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <div className="flex flex-col h-screen justify-center gap-2 py-8 px-7">
        <Upload />
        <Chat />
      </div>
    </ThemeProvider>
  );
}
