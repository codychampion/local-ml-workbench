"""
Style Constraints for Adversarial Patches
==========================================
Use CLIP to constrain adversarial patches to look like specific aesthetic styles.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Optional, Union
from pathlib import Path


class CLIPStyleConstraint:
    """CLIP-based style constraint for adversarial patches."""

    def __init__(
        self,
        style_prompts: Union[str, List[str]],
        model_name: str = "ViT-B/32",
        device: str = "cuda"
    ):
        """
        Initialize CLIP style constraint.

        Args:
            style_prompts: Text description(s) of desired style
            model_name: CLIP model variant
            device: Device to run on
        """
        self.device = device if torch.cuda.is_available() else "cpu"

        try:
            import clip
            self.clip_model, self.clip_preprocess = clip.load(model_name, device=device)
            self.clip_model.eval()
            self.clip = clip
        except ImportError:
            raise ImportError(
                "CLIP not installed. Install with: pip install git+https://github.com/openai/CLIP.git"
            )

        # Handle single or multiple prompts
        if isinstance(style_prompts, str):
            style_prompts = [style_prompts]
        self.style_prompts = style_prompts

        # Encode text features
        with torch.no_grad():
            text_tokens = self.clip.tokenize(style_prompts).to(device)
            self.text_features = self.clip_model.encode_text(text_tokens)
            self.text_features /= self.text_features.norm(dim=-1, keepdim=True)

    def compute_style_loss(self, images: torch.Tensor) -> torch.Tensor:
        """
        Compute style loss encouraging images to match text prompts.

        Args:
            images: Batch of images [B, 3, H, W] in [0, 1] range

        Returns:
            Style loss (lower = better match to style)
        """
        # CLIP expects specific normalization
        # Images should be in [-1, 1] range after CLIP preprocessing
        # We'll resize and normalize appropriately

        # Resize to CLIP input size (224x224)
        images_resized = F.interpolate(
            images,
            size=(224, 224),
            mode='bilinear',
            align_corners=False
        )

        # CLIP normalization
        mean = torch.tensor([0.48145466, 0.4578275, 0.40821073]).to(self.device)
        std = torch.tensor([0.26862954, 0.26130258, 0.27577711]).to(self.device)
        images_normalized = (images_resized - mean.view(1, 3, 1, 1)) / std.view(1, 3, 1, 1)

        # Encode image features
        image_features = self.clip_model.encode_image(images_normalized)
        image_features /= image_features.norm(dim=-1, keepdim=True)

        # Compute cosine similarity to style prompts
        # Higher similarity = better match = lower loss
        similarities = 100.0 * image_features @ self.text_features.T
        max_similarity = similarities.max(dim=-1)[0]  # Best match across prompts

        # Convert to loss (negative similarity)
        style_loss = -max_similarity.mean()

        return style_loss

    def get_similarity_score(self, images: torch.Tensor) -> float:
        """
        Get CLIP similarity score (for evaluation).

        Args:
            images: Batch of images

        Returns:
            Average similarity score in [0, 1] range
        """
        with torch.no_grad():
            loss = self.compute_style_loss(images)
            # Convert negative similarity back to positive score
            similarity = -loss.item() / 100.0
            # Normalize to [0, 1]
            similarity = (similarity + 1) / 2
            return max(0.0, min(1.0, similarity))


class TotalVariationLoss:
    """Total Variation loss for smooth patches."""

    def __init__(self, weight: float = 1.0):
        self.weight = weight

    def __call__(self, images: torch.Tensor) -> torch.Tensor:
        """
        Compute total variation loss.

        Args:
            images: Batch of images [B, 3, H, W]

        Returns:
            TV loss (lower = smoother)
        """
        # Compute differences in horizontal and vertical directions
        diff_h = torch.abs(images[:, :, :-1, :] - images[:, :, 1:, :])
        diff_w = torch.abs(images[:, :, :, :-1] - images[:, :, :, 1:])

        tv_loss = self.weight * (diff_h.mean() + diff_w.mean())
        return tv_loss


class PrintabilityLoss:
    """Encourage patches to use printable colors."""

    def __init__(self, weight: float = 1.0, num_colors: int = 8):
        """
        Initialize printability constraint.

        Args:
            weight: Loss weight
            num_colors: Number of discrete colors to encourage
        """
        self.weight = weight
        self.num_colors = num_colors

        # Define printable color palette (simple approach)
        # In practice, this could be CMYK gamut or screen printing colors
        colors = torch.linspace(0, 1, num_colors)
        self.palette = torch.stack(torch.meshgrid(colors, colors, colors, indexing='ij')).reshape(3, -1).T

    def __call__(self, images: torch.Tensor) -> torch.Tensor:
        """
        Compute printability loss.

        Args:
            images: Batch of images [B, 3, H, W] in [0, 1]

        Returns:
            Printability loss
        """
        # Flatten spatial dimensions
        B, C, H, W = images.shape
        images_flat = images.permute(0, 2, 3, 1).reshape(-1, 3)  # [B*H*W, 3]

        # Move palette to same device
        palette = self.palette.to(images.device)

        # Compute distance to nearest palette color
        # For efficiency, use L2 distance
        distances = torch.cdist(images_flat, palette, p=2)
        min_distances = distances.min(dim=1)[0]

        printability_loss = self.weight * min_distances.mean()
        return printability_loss


class StyleConstraintCombined:
    """Combined style constraints with multiple components."""

    def __init__(
        self,
        style_prompts: Union[str, List[str]],
        clip_weight: float = 1.0,
        tv_weight: float = 0.1,
        print_weight: float = 0.05,
        device: str = "cuda"
    ):
        """
        Initialize combined style constraints.

        Args:
            style_prompts: CLIP text prompts for style
            clip_weight: Weight for CLIP style loss
            tv_weight: Weight for total variation (smoothness)
            print_weight: Weight for printability
            device: Device to run on
        """
        self.clip_constraint = CLIPStyleConstraint(style_prompts, device=device)
        self.tv_loss = TotalVariationLoss(weight=tv_weight)
        self.print_loss = PrintabilityLoss(weight=print_weight)
        self.clip_weight = clip_weight

    def compute_loss(self, images: torch.Tensor) -> dict:
        """
        Compute all style constraint losses.

        Args:
            images: Batch of images

        Returns:
            Dictionary of losses
        """
        clip_loss = self.clip_constraint.compute_style_loss(images)
        tv_loss = self.tv_loss(images)
        print_loss = self.print_loss(images)

        total_loss = (
            self.clip_weight * clip_loss +
            tv_loss +
            print_loss
        )

        return {
            "style_total": total_loss,
            "style_clip": clip_loss,
            "style_tv": tv_loss,
            "style_print": print_loss,
        }

    def get_similarity_score(self, images: torch.Tensor) -> float:
        """Get CLIP similarity score for evaluation."""
        return self.clip_constraint.get_similarity_score(images)
