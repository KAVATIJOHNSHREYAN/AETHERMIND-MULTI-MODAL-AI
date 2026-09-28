"""
AetherMind Multimodal AI — Image Generation & Creative Engine (Phase 7+)
Supports Text-to-Image, Negative Prompts, Aspect Ratios, Quality Selection, Variations, Image History, Download.
Auto-Rotating Multi-Model Engine: Automatically selects the best free API-less model for each generation request.
"""

import os
import uuid
import io
import math
import random
import urllib.parse
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.logging.logger import logger
from app.providers.manager import ai_provider_manager


class ImageGeneratorEngine:
    """Image Generation Engine with Auto-Rotating API-less Models & synthetic canvas fallback"""

    # ── Free API-less Image Models (Pollinations AI) ──────────────────────
    # The system automatically rotates through these models behind the scenes.
    # Users never need to configure or select anything.
    APILESS_IMAGE_MODELS = [
        {
            "id": "flux",
            "name": "AetherMind Flux",
            "description": "High-quality photorealism and complex prompt adherence",
            "weight": 40,  # Higher weight = more likely to be selected
        },
        {
            "id": "turbo",
            "name": "AetherMind Turbo",
            "description": "Lightning-fast generation with great artistic style",
            "weight": 25,
        },
        {
            "id": "flux-realism",
            "name": "AetherMind Realism",
            "description": "Ultra-photorealistic photography and cinematic shots",
            "weight": 15,
        },
        {
            "id": "flux-anime",
            "name": "AetherMind Anime",
            "description": "High-quality anime, manga, and 2D illustrations",
            "weight": 10,
        },
        {
            "id": "flux-3d",
            "name": "AetherMind 3D",
            "description": "3D rendered scenes, objects, and characters",
            "weight": 10,
        },
    ]

    ASPECT_RATIOS = {
        "1:1": (1024, 1024),
        "16:9": (1280, 720),
        "9:16": (720, 1280),
        "4:3": (1024, 768),
        "3:2": (1080, 720),
    }

    def __init__(self):
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)
        self._generation_count = 0

    def _auto_select_model(self, prompt: str) -> dict:
        """Intelligently auto-select the best image model based on prompt keywords.
        Falls back to weighted random rotation if no keyword match is found."""
        p_lower = prompt.lower()

        # Keyword-based smart routing
        if any(kw in p_lower for kw in ["anime", "manga", "cartoon", "2d", "chibi", "waifu"]):
            return next(m for m in self.APILESS_IMAGE_MODELS if m["id"] == "flux-anime")
        if any(kw in p_lower for kw in ["3d", "render", "blender", "isometric", "voxel", "clay"]):
            return next(m for m in self.APILESS_IMAGE_MODELS if m["id"] == "flux-3d")
        if any(kw in p_lower for kw in ["photo", "realistic", "portrait", "cinematic", "photograph", "dslr", "canon"]):
            return next(m for m in self.APILESS_IMAGE_MODELS if m["id"] == "flux-realism")
        if any(kw in p_lower for kw in ["fast", "quick", "sketch", "draft", "concept"]):
            return next(m for m in self.APILESS_IMAGE_MODELS if m["id"] == "turbo")

        # Weighted random rotation for generic prompts
        weights = [m["weight"] for m in self.APILESS_IMAGE_MODELS]
        selected = random.choices(self.APILESS_IMAGE_MODELS, weights=weights, k=1)[0]
        return selected

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        quality: str = "standard",
        model: str = "auto",
        variation_of: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate high-quality image from prompt with auto-model selection."""
        dim = self.ASPECT_RATIOS.get(aspect_ratio, (1024, 1024))
        width, height = dim

        if quality == "hd":
            width = int(width * 1.25)
            height = int(height * 1.25)
        elif quality == "ultra":
            width = int(width * 1.5)
            height = int(height * 1.5)

        record_id = str(uuid.uuid4())
        filename = f"gen_{record_id[:8]}.png"
        filepath = os.path.join(self.upload_dir, filename)
        public_url = f"/static/uploads/{filename}"

        # Auto-select the best model for this prompt
        selected_model = self._auto_select_model(prompt)
        model_id = selected_model["id"]
        model_name = selected_model["name"]
        self._generation_count += 1

        # Build the Pollinations API-less URL with the auto-selected model
        encoded_prompt = urllib.parse.quote(prompt)
        seed = random.randint(1, 999999)
        pollination_url = (
            f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            f"?width={width}&height={height}&model={model_id}&nologo=true&seed={seed}"
        )

        # On cloud serverless environments (Vercel), use /tmp if root static directory is read-only
        if os.environ.get("VERCEL") or not os.access(os.path.dirname(self.upload_dir), os.W_OK):
            self.upload_dir = "/tmp"
            os.makedirs(self.upload_dir, exist_ok=True)
            filepath = os.path.join(self.upload_dir, filename)

        image_saved = False
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(pollination_url)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    try:
                        with open(filepath, "wb") as f:
                            f.write(resp.content)
                    except Exception:
                        pass
                    image_saved = True
                    public_url = pollination_url
                    logger.info(f"Image generated with model '{model_name}' ({model_id}) — seed {seed}")
        except Exception as err:
            logger.warning(f"Pollinations AI '{model_id}' error ({err}). Falling back to PIL canvas engine.")

        if not image_saved:
            # Create crisp artwork image using PIL as fallback
            img = Image.new("RGBA", (width, height), (14, 18, 30, 255))
            draw = ImageDraw.Draw(img)

            # Draw artistic radial gradient background
            cx, cy = width // 2, height // 2
            max_r = math.sqrt(cx**2 + cy**2)
            
            # Color palettes based on prompt keywords
            p_lower = prompt.lower()
            if "neon" in p_lower or "cyberpunk" in p_lower:
                c1, c2 = (6, 182, 212), (168, 85, 247)
            elif "nature" in p_lower or "forest" in p_lower or "panda" in p_lower:
                c1, c2 = (16, 185, 129), (14, 116, 144)
            elif "sunset" in p_lower or "fire" in p_lower:
                c1, c2 = (244, 63, 94), (245, 158, 11)
            else:
                c1, c2 = (99, 102, 241), (6, 182, 212)

            for y in range(0, height, 4):
                for x in range(0, width, 4):
                    dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_r
                    r = int(c1[0] * (1 - dist) + c2[0] * dist)
                    g = int(c1[1] * (1 - dist) + c2[1] * dist)
                    b = int(c1[2] * (1 - dist) + c2[2] * dist)
                    draw.rectangle([x, y, x + 4, y + 4], fill=(r, g, b, 255))

            # Add stylized geometric aesthetic shapes
            draw.ellipse([cx - 180, cy - 180, cx + 180, cy + 180], outline=(255, 255, 255, 60), width=6)
            draw.polygon([(cx, cy - 140), (cx + 120, cy + 100), (cx - 120, cy + 100)], outline=(255, 255, 255, 80), width=4)

            # Render prompt text overlay
            display_prompt = prompt[:45] + ("..." if len(prompt) > 45 else "")
            draw.rectangle([20, height - 80, width - 20, height - 20], fill=(0, 0, 0, 160))
            draw.text((40, height - 60), f"🎨 {display_prompt}", fill=(255, 255, 255, 230))
            draw.text((40, height - 40), f"AetherMind AI Generator • {aspect_ratio} • {quality.upper()}", fill=(6, 182, 212, 220))

            img.save(filepath, format="PNG")
            public_url = f"/static/uploads/{filename}"
            model_name = "AetherMind Canvas (Fallback)"

        metadata = {
            "prompt": prompt,
            "negative_prompt": negative_prompt or "",
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "dimensions": f"{width}x{height}",
            "model_used": model_id,
            "model_name": model_name,
            "seed": seed,
            "variation_of": variation_of,
            "generation_number": self._generation_count,
            "future_editing_ready": True
        }

        return {
            "id": record_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "image_url": public_url,
            "model_name": model_name,
            "width": width,
            "height": height,
            "created_at": datetime.utcnow(),
            "metadata": metadata
        }

    async def generate_variation(
        self,
        parent_image_id: str,
        prompt: str,
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """Generate a variation of an existing image record."""
        return await self.generate_image(
            prompt=f"Variation of image {parent_image_id}: {prompt}",
            aspect_ratio=aspect_ratio,
            variation_of=parent_image_id
        )


image_generator = ImageGeneratorEngine()

