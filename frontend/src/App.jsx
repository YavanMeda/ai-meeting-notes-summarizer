import { useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function App() {
  const [transcript, setTranscript] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const canSubmit = useMemo(
    () => transcript.trim().length > 0 && !loading,
    [transcript, loading]
  );

  async function handleSummarize() {
    setError("");
    setResult(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript }),
      });

      if (!res.ok) {
        const payload = await res.json().catch(() => null);
        let msg = `Request failed (${res.status})`;

        if (payload?.detail) {
          if (typeof payload.detail === "string") {
            msg = payload.detail;
          } else if (Array.isArray(payload.detail)) {
            msg = payload.detail
              .map((d) => `${d.loc?.join(".")}: ${d.msg}`)
              .join(" | ");
          }
        }
        throw new Error(msg);
      }

      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={page}>
      <h1>AI Meeting Notes Summarizer</h1>

      <label style={{ fontWeight: 600 }}>Paste transcript</label>
      <textarea
        rows={10}
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        placeholder='Example: "Alice: We should ship next week. Bob: I will send notes."'
        style={textarea}
      />

      <button
        onClick={handleSummarize}
        disabled={!canSubmit}
        style={{
          ...button,
          opacity: canSubmit ? 1 : 0.6,
          cursor: canSubmit ? "pointer" : "not-allowed",
        }}
      >
        {loading ? "Summarizing..." : "Summarize"}
      </button>

      {error && <div style={errorBox}>Error: {error}</div>}

      {result && (
        <div style={{ marginTop: 24 }}>
          <Section title="Meeting Title">
            {result.meeting_title}
          </Section>

          <Section title="Summary">
            <Bullets items={result.summary_bullets} />
          </Section>

          <Section title="Decisions">
            <Bullets items={result.decisions} />
          </Section>

          <Section title="Action Items">
            <table style={table}>
              <thead>
                <tr>
                  <th style={th}>Task</th>
                  <th style={th}>Owner</th>
                  <th style={th}>Due</th>
                  <th style={th}>Priority</th>
                </tr>
              </thead>
              <tbody>
                {result.action_items.map((ai, i) => (
                  <tr key={i}>
                    <td style={td}>{ai.task}</td>
                    <td style={td}>{ai.owner ?? "Unassigned"}</td>
                    <td style={td}>{ai.due_date ?? "None"}</td>
                    <td style={td}>{ai.priority}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Section>

          <Section title="Risks / Blockers">
            <Bullets items={result.risks_blockers} />
          </Section>

          <Section title="Open Questions">
            <Bullets items={result.open_questions} />
          </Section>

          <Section title="Raw JSON">
            <pre style={pre}>{JSON.stringify(result, null, 2)}</pre>
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div style={card}>
      <h2>{title}</h2>
      {children}
    </div>
  );
}

function Bullets({ items }) {
  if (!items || items.length === 0) {
    return <div style={{ color: "#666" }}>None</div>;
  }
  return (
    <ul>
      {items.map((x, i) => (
        <li key={i}>{x}</li>
      ))}
    </ul>
  );
}

const page = {
  maxWidth: 900,
  margin: "40px auto",
  fontFamily: "system-ui, Arial",
};

const textarea = {
  width: "100%",
  marginTop: 8,
  marginBottom: 12,
  padding: 10,
};

const button = {
  padding: "10px 14px",
  fontWeight: 600,
  marginTop: 8,
};

const errorBox = {
  marginTop: 12,
  padding: 10,
  border: "1px solid red",
  color: "red",
};

const card = {
  marginTop: 16,
  padding: 14,
  border: "1px solid #ddd",
  borderRadius: 6,
};

const table = {
  width: "100%",
  borderCollapse: "collapse",
};

const th = {
  textAlign: "left",
  borderBottom: "1px solid #ccc",
  padding: 6,
};

const td = {
  borderBottom: "1px solid #eee",
  padding: 6,
};

const pre = {
  background: "#f5f5f5",
  padding: 10,
  overflowX: "auto",
};

