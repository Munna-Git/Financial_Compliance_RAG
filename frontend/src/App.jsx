import { useState } from "react";
import axios from "axios";
import toast, { Toaster } from "react-hot-toast";

export default function App() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [citations, setCitations] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const API_BASE = "http://127.0.0.1:8000";

  const handleQuery = async () => {
    if (!query.trim()) return toast.error("Enter a question");
    try {
      setLoading(true);
      setResponse("");
      setCitations([]);
      toast.loading("Processing query...");
      const res = await axios.post(`${API_BASE}/api/query`, { query });
      setResponse(res.data.response);
      setCitations(res.data.citations || []);
      toast.dismiss();
      toast.success("Response ready!");
    } catch (e) {
      toast.dismiss();
      toast.error("Query failed");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!file) return toast.error("Choose a PDF file");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("multimodal", true);
    try {
      setUploading(true);
      toast.loading("Uploading document...");
      const res = await axios.post(`${API_BASE}/api/ingest`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.dismiss();
      toast.success("Upload and ingestion started!");
    } catch (e) {
      toast.dismiss();
      toast.error("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      minWidth: "100vw",
      background: "linear-gradient(to right,#e0e7ff 40%, #f8fafc 100%)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "flex-start",
      overflowX: "hidden"
    }}>
      <Toaster position="top-right" />
      <div style={{
        background: "#fff",
        borderRadius: "1.1rem",
        boxShadow: "0 10px 32px 0 rgba(0,0,0,0.10)",
        padding: "2.8rem 2rem",
        width: "95vw",
        maxWidth: "1100px",
        margin: "2.5rem auto 1.2rem",
      }}>
        <h2 style={{
          textAlign: "center",
          color: "#334155",
          fontSize: "2.4rem",
          fontWeight: 700,
          marginBottom: "1.7rem"
        }}>
          <span style={{color: "#6366F1"}}>Financial Compliance</span> <span style={{fontWeight:400}}>RAG Assistant</span>
        </h2>
        <div style={{display:"flex", flexDirection:"column", gap:"1rem"}}>
          <label style={{fontWeight: 600, color: "#475569"}}>
            Ask a Financial Compliance Question
          </label>
          <textarea
            style={{
              width: "100%",
              fontSize: "1.08rem",
              border: "1.5px solid #b6bff7",
              borderRadius: "0.75rem",
              padding: "1rem",
              outline: "none",
              marginBottom: "0",
              marginTop: "2px",
              resize: "vertical",
              minHeight: "75px",
              transition: "border 0.2s"
            }}
            placeholder="What are Basel III liquidity guidelines?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button
            onClick={handleQuery}
            disabled={loading}
            style={{
              background: "linear-gradient(90deg,#6366F1 70%, #818cf8 100%)",
              color: "#fff",
              fontWeight: 600,
              padding: "12px 38px",
              border: "none",
              borderRadius: "30px",
              fontSize: "1.18rem",
              cursor: loading ? "not-allowed" : "pointer",
              margin: "0 0 18px 0",
              alignSelf: "flex-start",
              boxShadow: "0 4px 14px rgba(99,102,241,.07)"
            }}
          >
            {loading ? "Processing..." : "Ask"}
          </button>
        </div>

        <hr style={{margin: "1.6rem 0 1.6rem"}} />

        <div>
          <span style={{
            fontWeight: 700, fontSize: "1.07rem",
            color: "#6366F1"
          }}>
            Upload New Compliance Document
          </span>
        </div>
        <div style={{display: "flex", gap: 10, alignItems: "center", marginBottom: "2.5rem"}}>
          <input
            type="file"
            accept="application/pdf"
            disabled={uploading}
            style={{
              border: "none",
              background: "#f1f5f9",
              borderRadius: "0.5rem",
              padding: 3,
            }}
            onChange={e => setFile(e.target.files[0])}
          />
          <button
            style={{
              background: "#fff",
              border: "2.5px solid #6366F1",
              color: "#6366F1",
              fontWeight: 600,
              fontSize: "1.01rem",
              borderRadius: "25px",
              padding: "8px 26px",
              cursor: uploading ? "not-allowed" : "pointer"
            }}
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? "Uploading..." : "Ingest PDF"}
          </button>
        </div>

        <div style={{
          padding: "1.3rem",
          border: "1.6px solid #e5e7eb",
          background: "#f7fafc",
          minHeight: 85,
          borderRadius: "1.0rem",
          whiteSpace: "pre-wrap",
          fontSize: "1.13rem",
          color: "#262626",
          marginBottom: "1.3rem",
        }}>
          {!loading && !response && <span style={{color:"#bdbdbd"}}>Your answer will appear here.</span>}
          {!loading && response}
          {loading && <span style={{color:"#b1b1b1"}}>Waiting for server response...</span>}
        </div>
        {citations && citations.length > 0 &&
          <div style={{
            marginTop: "0.9rem",
            marginBottom:"0.6rem",
            border: "1.3px solid #c7d2fe",
            background: "#f1f5fa",
            padding: "1.12rem",
            borderRadius: "0.9rem"
          }}>
            <div style={{fontWeight:700,marginBottom:7, color:"#6366F1", letterSpacing:"0.03em"}}>Citations</div>
            {citations.map((c, idx) => (
              <div key={idx} style={{marginBottom:6, fontSize:'1.01rem'}}>
                <span style={{fontWeight:600}}>[Document {c.index}]</span>
                {" "}File: <span style={{fontFamily:"monospace"}}>{c.filename}</span>,
                chunk: <span style={{fontFamily:"monospace"}}>{c.chunk_index}</span>
                {c.compliance_categories && c.compliance_categories.length > 0 &&
                  <> | Categories: {c.compliance_categories.join(", ")}</>
                }
              </div>
            ))}
          </div>
        }
      </div>
      <footer style={{
        marginTop: "2.7rem", color:"#6d6b6b", fontSize:"0.99rem",
        letterSpacing:"0.011em", paddingBottom:"1.2rem"
      }}>
        Financial Compliance RAG &bull; <span style={{color:"#6366F1"}}>2025</span>
      </footer>
    </div>
  );
}
