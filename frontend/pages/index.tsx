import Chat from "@/components/Chat";
import Upload from "@/components/Upload";

export default function Home() {
  return (
    <div className="flex flex-col h-screen justify-center gap-2 py-8 px-7">
      <Upload />
      <Chat />
    </div>
  );
}
