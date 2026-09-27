"""
AetherMind Multimodal AI - UI Component Registry Specifications
Defines metadata, HTML structure, and prop schemas for all reusable UI components.
"""

from typing import Dict, Any, List

class UIComponentRegistry:
    """Registry of reusable enterprise UI components"""

    @staticmethod
    def get_components() -> List[str]:
        return [
            "Button",
            "Card",
            "DialogModal",
            "Dropdown",
            "Tooltip",
            "AttachmentPreview",
            "MessageBubble",
            "CodeBlock",
            "AudioWaveform",
            "ImageViewer",
            "SettingsTabs",
            "ToastNotification",
        ]
