"""
Theme helpers for the Streamlit frontend.
"""

import streamlit as st


def apply_theme() -> None:
    """Inject ToneSoul theme styles."""
    st.markdown(
        """
        <style>
        :root {
          --ts-ink: #1f1c16;
          --ts-muted: #6b5d4d;
          --ts-accent: #e76f51;
          --ts-accent-2: #2a9d8f;
          --ts-sand: #fdf6ed;
          --ts-card: rgba(255, 255, 255, 0.72);
          --ts-border: rgba(31, 28, 22, 0.08);
          --ts-shadow: 0 12px 30px rgba(31, 28, 22, 0.08);
        }

        .stApp {
          background:
            radial-gradient(1000px 520px at 8% -10%, rgba(231, 111, 81, 0.18), transparent 60%),
            radial-gradient(900px 520px at 95% 10%, rgba(42, 157, 143, 0.14), transparent 65%),
            linear-gradient(180deg, #f6efe4 0%, #fdfaf5 100%);
          color: var(--ts-ink);
          font-family: "Noto Serif TC", "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", serif;
        }

        h1, h2, h3, h4 {
          color: var(--ts-ink);
          letter-spacing: 0.3px;
        }

        .ts-hero {
          padding: 20px 24px;
          border-radius: 18px;
          background: linear-gradient(120deg, rgba(231, 111, 81, 0.14), rgba(42, 157, 143, 0.12));
          border: 1px solid var(--ts-border);
          box-shadow: var(--ts-shadow);
          animation: tsFade 0.6s ease-out;
        }

        .ts-hero h1 {
          margin: 0;
          font-size: 32px;
        }

        .ts-hero p {
          margin: 6px 0 0 0;
          color: var(--ts-muted);
          font-size: 15px;
        }

        .ts-card {
          background: var(--ts-card);
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
        }

        .ts-pill {
          display: inline-flex;
          gap: 6px;
          align-items: center;
          padding: 4px 10px;
          border-radius: 999px;
          background: rgba(31, 28, 22, 0.08);
          color: var(--ts-ink);
          font-size: 12px;
        }

        .ts-badge {
          display: inline-flex;
          align-items: center;
          padding: 2px 8px;
          border-radius: 8px;
          font-size: 12px;
          background: rgba(231, 111, 81, 0.12);
          color: var(--ts-ink);
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
          background: #e05a3f;
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
          box-shadow: 0 8px 20px rgba(31, 28, 22, 0.08);
          line-height: 1.6;
        }

        div[data-testid="stChatMessage"].stChatMessage--user,
        div[data-testid="stChatMessage"][data-author="user"] {
          justify-content: flex-end;
        }

        div[data-testid="stChatMessage"].stChatMessage--user [data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"][data-author="user"] [data-testid="stChatMessageContent"],
        .stChatMessage.stChatMessage--user .stChatMessageContent {
          background: rgba(231, 111, 81, 0.18);
          border-color: rgba(231, 111, 81, 0.35);
        }

        div[data-testid="stChatMessage"].stChatMessage--assistant [data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"][data-author="assistant"] [data-testid="stChatMessageContent"],
        .stChatMessage.stChatMessage--assistant .stChatMessageContent {
          background: rgba(255, 255, 255, 0.92);
        }

        .ts-muted {
          color: var(--ts-muted);
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
