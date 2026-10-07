"""Design system, color tokens, and styling constants for the Quiz Game UI."""
import customtkinter as ctk

# Color Palette (Dark Mode primary with dual-mode tuple support)
COLORS = {
    # Backgrounds
    "bg_dark": "#0F172A",          # Slate 900
    "bg_card": ("#F8FAFC", "#1E293B"),   # Light slate / Slate 800
    "bg_card_secondary": ("#EDE9FE", "#1E1E38"),
    "bg_input": ("#E2E8F0", "#334155"),
    
    # Primary & Secondary Accents
    "primary": "#6366F1",          # Indigo 500
    "primary_hover": "#4F46E5",    # Indigo 600
    "primary_light": "#818CF8",    # Indigo 400
    
    "secondary": "#06B6D4",        # Cyan 500
    "secondary_hover": "#0891B2",  # Cyan 600
    
    "accent_purple": "#8B5CF6",    # Violet 500
    "accent_pink": "#EC4899",      # Pink 500
    
    # Status Colors
    "success": "#10B981",          # Emerald 500
    "success_hover": "#059669",
    "success_bg": ("#D1FAE5", "#064E3B"),
    
    "warning": "#F59E0B",          # Amber 500
    "warning_hover": "#D97706",
    "warning_bg": ("#FEF3C7", "#78350F"),
    
    "danger": "#EF4444",           # Rose 500
    "danger_hover": "#DC2626",
    "danger_bg": ("#FEE2E2", "#7F1D1D"),
    
    # Text
    "text_primary": ("#0F172A", "#F8FAFC"),
    "text_secondary": ("#64748B", "#94A3B8"),
    "text_muted": ("#94A3B8", "#64748B"),
    "text_white": "#FFFFFF",
    
    # Border & Dividers
    "border": ("#CBD5E1", "#334155"),
    "border_highlight": ("#818CF8", "#6366F1"),
    
    # Lifeline Button Colors
    "lifeline_5050": ("#3B82F6", "#2563EB"),
    "lifeline_freeze": ("#06B6D4", "#0891B2"),
    "lifeline_hint": ("#F59E0B", "#D97706"),
}

# Typography
FONTS = {
    "display": ("Segoe UI", 28, "bold"),
    "title_large": ("Segoe UI", 22, "bold"),
    "title": ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 15, "bold"),
    "body_bold": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 13),
    "body_small": ("Segoe UI", 11),
    "code": ("Consolas", 12),
    "timer": ("Segoe UI", 24, "bold"),
    "score": ("Segoe UI", 32, "bold"),
    "badge": ("Segoe UI", 11, "bold"),
}

def apply_theme():
    """Initializes the CustomTkinter global theme appearance."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
