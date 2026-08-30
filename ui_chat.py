[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, #ff0040, #cc0033) !important;
    border: 1px solid rgba(255, 0, 64, 0.7) !important;
    box-shadow:
        0 0 25px rgba(255, 0, 64, 0.6),
        inset 0 0 15px rgba(255, 255, 255, 0.15) !important;
    border-radius: 18px !important;
    padding: 10px 16px !important;
    margin-bottom: 14px !important;
    transition: all 0.25s ease !important;
}

[data-testid="stChatMessage"]:hover {
    box-shadow:
        0 0 40px rgba(255, 0, 64, 0.9),
        inset 0 0 20px rgba(255, 255, 255, 0.25) !important;
    transform: scale(1.01);
}
