// 1. Added 'useEffect' and 'Loader2' icon
import { useState, useMemo } from "react";
import { Send, Copy, Check, Paperclip, Trash2, ThumbsUp, ThumbsDown, Loader2 } from "lucide-react";

// Fallback API URL if env var is missing
const API_URL = "https://qx8ntbgft7.execute-api.ap-south-1.amazonaws.com/Prod";

export default function App() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // New State for Feedback (null = none, 1 = like, -1 = dislike)
  const [feedbackStatus, setFeedbackStatus] = useState<number | null>(null);
  // New State for Status Message (e.g. "Drafting...", "Refining...")
  const [statusMsg, setStatusMsg] = useState("");

  // 2. Added type ': string' here
  const wordCount = (text: string) => {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
  };

  const inWords = useMemo(() => wordCount(input), [input]);
  const outWords = useMemo(() => wordCount(output), [output]);

  // 👇 THE NEW POLLING LOGIC (The "Are you done yet?" loop)
  const pollJobStatus = async (jobId: string) => {
    const maxRetries = 30; // 30 * 2s = 60 seconds max wait (enough for now)
    let attempts = 0;

    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/jobs/${jobId}`);
        const data = await res.json();

        if (data.status === "COMPLETED") {
          setOutput(data.result);
          setStatusMsg("");
          setLoading(false);
          return;
        } 
        
        if (data.status === "FAILED") {
          setOutput(`❌ Error: ${data.error || "Job failed"}`);
          setLoading(false);
          return;
        }

        // Still processing? Update status and try again.
        setStatusMsg("AI is thinking... (Drafting & Critiquing)");
        attempts++;
        
        if (attempts < maxRetries) {
          setTimeout(checkStatus, 2000); // Check again in 2 seconds
        } else {
          setOutput("⚠️ Request timed out. The AI took too long.");
          setLoading(false);
        }
      } catch (err) {
        console.error("Polling error:", err);
        setLoading(false);
      }
    };

    // Start the first check
    checkStatus();
  };

  // Handle the API call
  const handleHumanize = async () => {
    if (!input) return;
    setLoading(true);
    setOutput("");
    setFeedbackStatus(null); 
    setStatusMsg("Starting job...");

    try {
      // 1. Request the Ticket
      const response = await fetch(`${API_URL}/rewrite`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // 2. If we get a Ticket (job_id), start waiting
      if (data.job_id) {
        pollJobStatus(data.job_id);
      } else {
        // Fallback for synchronous responses (just in case)
        setOutput(data.rewritten_text || "Result format error.");
        setLoading(false);
      }

    } catch (err) {
      console.error(err);
      setOutput("⚠️ Note: The API request failed. Please check your internet or API URL.");
      setLoading(false);
    }
  };

  // 3. Added type ': number' here
  const handleFeedback = async (score: number) => {
    if (!output) return;
    
    setFeedbackStatus(score);

    try {
      await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_text: input,
          rewritten_text: output,
          score: score
        }),
      });
      console.log("Feedback saved successfully!");
    } catch (err) {
      console.error("Failed to save feedback:", err);
      setFeedbackStatus(null);
    }
  };

  const handlePaste = async () => {
    try {
      const txt = await navigator.clipboard.readText();
      setInput(txt);
    } catch (err) {
      console.error("Failed to read clipboard", err);
    }
  };

  const handleCopyResult = () => {
    if (!output) return;
    try {
      navigator.clipboard.writeText(output);
      setCopied(true);
    } catch (e) {
      const textArea = document.createElement("textarea");
      textArea.value = output;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      setCopied(true);
    }
    setTimeout(() => setCopied(false), 1600);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        :root {
          --card-bg: rgba(7, 13, 23, 0.55);
          --card-border: rgba(255, 255, 255, 0.05);
          --muted: #94a3b8;
        }

        body {
          font-family: 'Inter', sans-serif;
          background-color: #020617;
          color: #e2e8f0;
        }

        textarea::-webkit-scrollbar { width: 8px; }
        textarea::-webkit-scrollbar-track { background: transparent; }
        textarea::-webkit-scrollbar-thumb { background-color: rgba(255, 255, 255, 0.1); border-radius: 4px; }
        textarea::-webkit-scrollbar-thumb:hover { background-color: rgba(255, 255, 255, 0.2); }

        .app-bg {
          background: 
            radial-gradient(circle at 50% 0%, rgba(29, 78, 216, 0.15), transparent 50%),
            radial-gradient(circle at 0% 50%, rgba(56, 189, 248, 0.05), transparent 40%),
            #020617;
          min-height: 100vh;
          width: 100%;
        }

        .card {
          background: linear-gradient(180deg, rgba(15, 23, 42, 0.6) 0%, rgba(15, 23, 42, 0.4) 100%);
          backdrop-filter: blur(12px);
          border: 1px solid var(--card-border);
          border-radius: 16px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }
        
        .card-head {
          display: flex; align-items: center; justify-content: space-between;
          padding: 14px 20px; background: rgba(2, 6, 23, 0.3);
          border-bottom: 1px solid var(--card-border);
          font-size: 0.75rem; font-weight: 700; letter-spacing: 0.05em;
          text-transform: uppercase; color: #94a3b8;
        }

        .card-body { flex: 1; padding: 0; display: flex; flex-direction: column; }
        .textarea-wrapper { flex: 1; position: relative; min-height: 380px; }
        
        textarea {
          width: 100%; height: 100%; background: transparent; border: none; resize: none;
          padding: 20px; font-size: 1rem; line-height: 1.6; color: #cbd5e1;
          font-family: 'Inter', sans-serif;
        }
        textarea:focus { outline: none; }

        .card-footer {
          padding: 14px 20px; background: rgba(2, 6, 23, 0.3);
          border-top: 1px solid var(--card-border);
          display: flex; align-items: center; justify-content: space-between;
        }

        .btn-primary {
          background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
          color: white; padding: 8px 16px; border-radius: 8px;
          font-weight: 600; font-size: 0.875rem; display: flex; align-items: center; gap: 8px;
          transition: all 0.2s; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        }
        .btn-primary:hover:not(:disabled) {
          transform: translateY(-1px);
          background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
        }
        .btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

        .btn-ghost {
          color: #64748b; padding: 8px 12px; border-radius: 8px;
          font-size: 0.875rem; font-weight: 600; display: flex; align-items: center; gap: 6px;
          transition: all 0.2s;
        }
        .btn-ghost:hover { color: #94a3b8; background: rgba(255, 255, 255, 0.03); }

        .btn-icon {
           padding: 8px; border-radius: 8px; transition: all 0.2s; color: #64748b;
        }
        .btn-icon:hover { background: rgba(255, 255, 255, 0.05); color: #e2e8f0; }
        .btn-icon.active-up { color: #10b981; background: rgba(16, 185, 129, 0.1); }
        .btn-icon.active-down { color: #ef4444; background: rgba(239, 68, 68, 0.1); }

        .word-badge {
          background: rgba(255, 255, 255, 0.05); padding: 2px 8px;
          border-radius: 4px; font-variant-numeric: tabular-nums;
        }
      `}</style>

      <div className="app-bg flex flex-col items-center">
        <div className="w-full max-w-5xl text-center pt-16 pb-10 px-4">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/50 border border-slate-800 text-slate-400 text-[10px] font-bold tracking-wider mb-6">
            <span className="text-indigo-400">✨ AI POWERED</span>
            <span className="w-px h-3 bg-slate-700"></span>
            <span>v2.0 Async</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight tracking-tight mb-4">
            The Evolving <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">Humanizer</span>
          </h1>
        </div>

        <div className="w-full max-w-[1200px] px-4 grid grid-cols-1 lg:grid-cols-2 gap-6 mb-20">
          <div className="card">
            <div className="card-head">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></div>
                <span>Robotic Input</span>
              </div>
              <div className="word-badge">{inWords} words</div>
            </div>

            <div className="card-body">
              <div className="textarea-wrapper">
                <textarea
                  placeholder="Paste your AI-generated text here (ChatGPT, Claude, Jasper)..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  spellCheck="false"
                />
              </div>
              
              <div className="card-footer">
                <div className="flex items-center gap-2">
                  <button className="btn-ghost" onClick={() => setInput("")} title="Clear input">
                    <Trash2 className="w-4 h-4" />
                  </button>
                  <button className="btn-ghost" onClick={handlePaste} title="Paste from clipboard">
                    <Paperclip className="w-4 h-4" /> 
                    <span className="hidden sm:inline">Paste</span>
                  </button>
                </div>

                <button className="btn-primary" onClick={handleHumanize} disabled={loading || !input}>
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  <span>{loading ? "Processing..." : "Humanize Text"}</span>
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-head">
              <div className="flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
                <span>Humanized Output</span>
              </div>
              <div className="word-badge">{outWords} words</div>
            </div>

            <div className="card-body">
               <div className="textarea-wrapper relative">
                {/* Status Message Overlay */}
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm z-10 rounded-xl">
                    <span className="text-indigo-300 font-medium animate-pulse">{statusMsg || "Initializing..."}</span>
                  </div>
                )}
                <textarea
                  readOnly
                  placeholder="The humanized result will appear here..."
                  value={output}
                  className="text-slate-300"
                />
              </div>

              <div className="card-footer justify-between">
                <div className="flex items-center gap-2">
                   <button 
                      className={`btn-icon ${feedbackStatus === 1 ? 'active-up' : ''}`} 
                      onClick={() => handleFeedback(1)}
                      disabled={!output}
                      title="Good Result"
                   >
                      <ThumbsUp className="w-4 h-4" />
                   </button>
                   <button 
                      className={`btn-icon ${feedbackStatus === -1 ? 'active-down' : ''}`} 
                      onClick={() => handleFeedback(-1)}
                      disabled={!output}
                      title="Bad Result"
                   >
                      <ThumbsDown className="w-4 h-4" />
                   </button>
                </div>
                
                <button 
                  className="btn-primary" 
                  style={{
                    background: copied 
                      ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' 
                      : 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)',
                    boxShadow: copied ? '0 4px 12px rgba(16,185,129,0.2)' : undefined
                  }}
                  onClick={handleCopyResult}
                  disabled={!output}
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? "Copied!" : "Copy Result"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <footer className="w-full text-center pb-8 text-slate-600 text-sm font-medium">
          <p>© 2025 The Evolving Humanizer. Built for creators.</p>
        </footer>
      </div>
    </>
  );
}