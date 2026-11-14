// React chat panel for the NOC agent. Talks ONLY to your backend (/api/noc-agent/chat), never to Hermes directly.
// FOR THE LLM / DEVELOPER: adapt styling to the app; keep messages in state and send the full history each turn
// (chat completions are stateless; the backend also sends X-Hermes-Session-Id for continuity).
// Streams: `chat.completion.chunk` text deltas and `hermes.tool.progress` events (shown as a status line).
import { useRef, useState } from "react";

type Msg = { role: "user" | "assistant"; content: string };

export function NocAgentChat() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("");
  const conversationId = useRef(crypto.randomUUID());

  async function send() {
    const text = input.trim();
    if (!text) return;
    const history: Msg[] = [...messages, { role: "user", content: text }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");

    const res = await fetch("/api/noc-agent/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: conversationId.current, message_id: crypto.randomUUID(), messages: history }),
    });
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
      const lines = buf.split("\n");
      buf = lines.pop() ?? "";
      for (const line of lines) {
        if (line.startsWith("event: hermes.tool.progress")) { setStatus("running tools…"); continue; }
        if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
        try {
          const evt = JSON.parse(line.slice(6));
          if (evt.tool || evt.type === "hermes.tool.progress") { setStatus(`tool: ${evt.tool ?? evt.name ?? ""}`); continue; }
          const delta = evt.choices?.[0]?.delta?.content ?? "";
          if (delta) setMessages((m) => {
            const copy = [...m];
            copy[copy.length - 1] = { role: "assistant", content: copy[copy.length - 1].content + delta };
            return copy;
          });
        } catch { /* ignore non-JSON lines */ }
      }
    }
    setStatus("");
  }

  return (
    <div dir="auto" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {messages.map((m, i) => (
        <div key={i} style={{ whiteSpace: "pre-wrap", alignSelf: m.role === "user" ? "flex-end" : "flex-start" }}>{m.content}</div>
      ))}
      {status && <small>{status}</small>}
      <textarea value={input} onChange={(e) => setInput(e.target.value)} placeholder="שאל את סוכן ה-NOC…" />
      <button onClick={send}>שלח</button>
    </div>
  );
}
