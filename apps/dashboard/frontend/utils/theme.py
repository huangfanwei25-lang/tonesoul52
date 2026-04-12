"""
Theme helpers for the Streamlit frontend.
Blueprint + Crystalline aesthetic — aligned with site/style.css
"""

import streamlit as st


def apply_theme() -> None:
    """Inject ToneSoul theme styles."""
    st.markdown(
        """
        <style>
        :root {
          --ts-ink: #2c3e50;
          --ts-muted: #6b7c8d;
          --ts-accent: #3a6b9f;
          --ts-accent-2: #5a8ec0;
          --ts-sand: #eef1f5;
          --ts-card: rgba(255, 255, 255, 0.72);
          --ts-border: rgba(90, 142, 192, 0.2);
          --ts-shadow: 0 12px 30px rgba(44, 62, 80, 0.08);
          --ts-blue-light: #b8d4e8;
          --ts-blue-pale: #dce8f2;
        }

        .stApp {
          background-color: var(--ts-sand);
          background-image:
            linear-gradient(rgba(90, 142, 192, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(90, 142, 192, 0.06) 1px, transparent 1px);
          background-size: 40px 40px;
          color: var(--ts-ink);
          font-family: 'Segoe UI', system-ui, -apple-system, 'Noto Sans TC', sans-serif;
        }

        h1, h2, h3, h4 {
          color: var(--ts-ink);
          letter-spacing: 0.3px;
        }

        .ts-hero {
          padding: 20px 24px;
          border-radius: 18px;
          background: linear-gradient(120deg, rgba(58, 107, 159, 0.10), rgba(90, 142, 192, 0.08));
          border: 1px solid var(--ts-border);
          box-shadow: var(--ts-shadow);
          animation: tsFade 0.6s ease-out;
        }

        .ts-hero h1 {
          margin: 0;
          font-size: 32px;
          color: var(--ts-accent);
        }

        .ts-hero p {
          margin: 6px 0 0 0;
          color: var(--ts-muted);
          font-size: 15px;
        }

        .ts-card {
          background: var(--ts-card);
          backdrop-filter: blur(8px);
          border: 1px solid var(--ts-border);
          border-radius: 16px;
          padding: 16px;
          box-shadow: var(--ts-shadow);
          animation: tsFade 0.6s ease-out;
        }

        .ts-section-title {
          font-size: 18px;
          font-weight: 600;
          margin: 6px 0 10px 0;
          color: var(--ts-accent);
        }

        .ts-pill {
          display: inline-flex;
          gap: 6px;
          align-items: center;
          padding: 4px 10px;
          border-radius: 999px;
          background: rgba(58, 107, 159, 0.08);
          color: var(--ts-ink);
          font-size: 12px;
        }

        .ts-badge {
          display: inline-flex;
          align-items: center;
          padding: 2px 8px;
          border-radius: 8px;
          font-size: 12px;
          background: rgba(58, 107, 159, 0.10);
          color: var(--ts-accent);
          border: 1px solid var(--ts-border);
        }

        .stButton > button {
          border-radius: 999px;
          border: none;
          background: var(--ts-accent);
          color: #fff;
          padding: 0.45rem 1.1rem;
          font-weight: 600;
          letter-spacing: 0.2px;
        }

        .stButton > button:hover {
          background: #2d5a8a;
          color: #fff;
        }

        .stTextInput > div > div > input,
        .stTextArea textarea {
          border-radius: 12px;
          border: 1px solid var(--ts-border);
          background: rgba(255, 255, 255, 0.86);
        }

        div[data-testid="stChatMessage"],
        .stChatMessage {
          display: flex;
          gap: 12px;
          padding: 0.15rem 0;
        }

        div[data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"],
        .stChatMessage .stChatMessageAvatar {
          display: none;
        }

        div[data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
        .stChatMessage .stChatMessageContent {
          max-width: 78%;
          padding: 0.7rem 0.95rem;
          border-radius: 18px;
          background: rgba(255, 255, 255, 0.92);
          border: 1px solid var(--ts-border);
          box-shadow: 0 8px 20px rgba(44, 62, 80, 0.08);
          line-height: 1.6;
        }

        div[data-testid="stChatMessage"].stChatMessage--user,
        div[data-testid="stChatMessage"][data-author="user"] {
          justify-content: flex-end;
        }

        div[data-testid="stChatMessage"].stChatMessage--user [data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"][data-author="user"] [data-testid="stChatMessageContent"],
        .stChatMessage.stChatMessage--user .stChatMessageContent {
          background: rgba(58, 107, 159, 0.12);
          border-color: rgba(58, 107, 159, 0.25);
        }

        div[data-testid="stChatMessage"].stChatMessage--assistant [data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"][data-author="assistant"] [data-testid="stChatMessageContent"],
        .stChatMessage.stChatMessage--assistant .stChatMessageContent {
          background: rgba(255, 255, 255, 0.92);
        }

        .ts-muted {
          color: var(--ts-muted);
        }

        /* Gauge & visualization styles */
        .ts-gauge {
          text-align: center;
          padding: 12px;
        }

        .ts-timeline {
          border-left: 2px solid var(--ts-blue-light);
          padding-left: 20px;
          margin: 12px 0;
        }

        .ts-timeline-entry {
          position: relative;
          margin-bottom: 16px;
          padding: 10px 14px;
          background: var(--ts-card);
          border: 1px solid var(--ts-border);
          border-radius: 10px;
        }

        .ts-timeline-entry::before {
          content: '';
          position: absolute;
          left: -27px;
          top: 14px;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: var(--ts-accent);
          border: 2px solid var(--ts-sand);
        }

        .ts-journal-entry {
          background: var(--ts-card);
          backdrop-filter: blur(8px);
          border: 1px solid var(--ts-border);
          border-radius: 12px;
          padding: 14px 16px;
          margin-bottom: 12px;
        }

        .ts-vow-card {
          background: var(--ts-card);
          backdrop-filter: blur(8px);
          border: 1px solid var(--ts-border);
          border-left: 4px solid var(--ts-accent);
          border-radius: 0 10px 10px 0;
          padding: 12px 14px;
          margin-bottom: 8px;
        }

        .ts-demo-banner {
          background: rgba(58, 107, 159, 0.08);
          border: 1px solid var(--ts-border);
          border-radius: 8px;
          padding: 8px 16px;
          text-align: center;
          color: var(--ts-accent);
          font-size: 13px;
          letter-spacing: 0.05em;
          margin-bottom: 12px;
        }

        .ts-explainer {
          display: inline-block;
          width: 16px;
          height: 16px;
          line-height: 16px;
          text-align: center;
          border-radius: 50%;
          background: rgba(58, 107, 159, 0.10);
          color: var(--ts-accent);
          font-size: 11px;
          cursor: help;
          margin-left: 4px;
          vertical-align: middle;
        }

        @keyframes tsFade {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
          .ts-hero h1 { font-size: 26px; }
          .ts-card { padding: 14px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
