import React from "react";
import ReactDOM from "react-dom/client";
import "antd/dist/reset.css";
import "./styles.css";

function App() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">ForgePulse</p>
        <h1>Industrial equipment telemetry platform</h1>
        <p>
          C++ edge gateway, Python data platform, React dashboard, and AI-assisted
          semiconductor yield analysis.
        </p>
      </section>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
