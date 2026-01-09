"""
Text-to-Video Generation using HuggingFace Diffusers

Supports multiple T2V models (lightly moderated/uncensored):
- Wan 2.2 (HunyuanVideo) - Tencent's latest T2V, Chinese model, less filtering
- CogVideoX (THUDM) - High quality 5B/2B params, Chinese, lightly moderated
- AnimateDiff - Community model, no filtering
- ModelScope T2V - Fast, good quality
- Zeroscope - Lightweight option

Usage:
    python -m pipelines.infer.generate_video \
        --prompt "A cat walking on the beach at sunset" \
        --model wan2.2 \
        --num-frames 81 \
        --output ./outputs/videos/cat_beach.mp4
"""

import argparse
import torch
from pathlib import Path
from diffusers import CogVideoXPipeline, DiffusionPipeline
from diffusers.utils import export_to_video
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_video_wan22(
    prompt: str,
    num_frames: int = 81,
    num_inference_steps: int = 30,
    guidance_scale: float = 6.0,
    device: str = "cuda",
):
    """Generate video using Wan 2.2 (HunyuanVideo) model from Tencent."""
    logger.info("Loading Wan 2.2 (HunyuanVideo) model...")

    try:
        from diffusers import HunyuanVideoPipeline
    except ImportError:
        logger.error("HunyuanVideo not available in this diffusers version")
        logger.info("Falling back to CogVideoX...")
        return generate_video_cogvideox(prompt, num_frames, num_inference_steps, guidance_scale, device)

    pipe = HunyuanVideoPipeline.from_pretrained(
        "tencent/HunyuanVideo",
        torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
    )

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        pipe.vae.enable_slicing()
        pipe.vae.enable_tiling()
    else:
        pipe = pipe.to(device)

    logger.info(f"Generating video with prompt: '{prompt}'")

    video = pipe(
        prompt=prompt,
        num_frames=num_frames,
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        generator=torch.Generator(device=device).manual_seed(42),
    ).frames[0]

    return video


def generate_video_cogvideox(
    prompt: str,
    num_frames: int = 49,
    num_inference_steps: int = 50,
    guidance_scale: float = 6.0,
    device: str = "cuda",
):
    """Generate video using CogVideoX model."""
    logger.info("Loading CogVideoX-2B model...")

    pipe = CogVideoXPipeline.from_pretrained(
        "THUDM/CogVideoX-2b",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    if device == "cuda":
        pipe.enable_model_cpu_offload()
        pipe.vae.enable_slicing()
        pipe.vae.enable_tiling()
    else:
        pipe = pipe.to(device)

    logger.info(f"Generating video with prompt: '{prompt}'")

    video = pipe(
        prompt=prompt,
        num_videos_per_prompt=1,
        num_inference_steps=num_inference_steps,
        num_frames=num_frames,
        guidance_scale=guidance_scale,
        generator=torch.Generator(device=device).manual_seed(42),
    ).frames[0]

    return video


def generate_video_modelscope(
    prompt: str,
    num_frames: int = 16,
    num_inference_steps: int = 25,
    device: str = "cuda",
):
    """Generate video using ModelScope T2V model."""
    logger.info("Loading ModelScope T2V model...")

    pipe = DiffusionPipeline.from_pretrained(
        "damo-vilab/text-to-video-ms-1.7b",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    if device == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)

    logger.info(f"Generating video with prompt: '{prompt}'")

    video_frames = pipe(
        prompt,
        num_inference_steps=num_inference_steps,
        num_frames=num_frames,
    ).frames[0]

    return video_frames


def generate_video_zeroscope(
    prompt: str,
    num_frames: int = 24,
    num_inference_steps: int = 40,
    device: str = "cuda",
):
    """Generate video using Zeroscope model (lightweight)."""
    logger.info("Loading Zeroscope XL model...")

    pipe = DiffusionPipeline.from_pretrained(
        "cerspense/zeroscope_v2_XL",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    if device == "cuda":
        pipe.enable_model_cpu_offload()
    else:
        pipe = pipe.to(device)

    logger.info(f"Generating video with prompt: '{prompt}'")

    video_frames = pipe(
        prompt,
        num_inference_steps=num_inference_steps,
        num_frames=num_frames,
        height=320,
        width=576,
    ).frames[0]

    return video_frames


def main():
    parser = argparse.ArgumentParser(description="Generate videos from text prompts")
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Text prompt describing the video to generate",
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["wan2.2", "cogvideox", "modelscope", "zeroscope"],
        default="wan2.2",
        help="Model to use for generation (default: wan2.2 - highest quality, lightly moderated)",
    )
    parser.add_argument(
        "--num-frames",
        type=int,
        default=None,
        help="Number of frames to generate (default varies by model)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of inference steps (default varies by model)",
    )
    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=6.0,
        help="Guidance scale for generation (higher = more prompt adherence)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./outputs/videos/generated.mp4",
        help="Output video path",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use (cuda/cpu)",
    )

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Set model-specific defaults
    if args.model == "wan2.2":
        num_frames = args.num_frames or 81
        num_steps = args.steps or 30
        video_frames = generate_video_wan22(
            prompt=args.prompt,
            num_frames=num_frames,
            num_inference_steps=num_steps,
            guidance_scale=args.guidance_scale,
            device=args.device,
        )
    elif args.model == "cogvideox":
        num_frames = args.num_frames or 49
        num_steps = args.steps or 50
        video_frames = generate_video_cogvideox(
            prompt=args.prompt,
            num_frames=num_frames,
            num_inference_steps=num_steps,
            guidance_scale=args.guidance_scale,
            device=args.device,
        )
    elif args.model == "modelscope":
        num_frames = args.num_frames or 16
        num_steps = args.steps or 25
        video_frames = generate_video_modelscope(
            prompt=args.prompt,
            num_frames=num_frames,
            num_inference_steps=num_steps,
            device=args.device,
        )
    elif args.model == "zeroscope":
        num_frames = args.num_frames or 24
        num_steps = args.steps or 40
        video_frames = generate_video_zeroscope(
            prompt=args.prompt,
            num_frames=num_frames,
            num_inference_steps=num_steps,
            device=args.device,
        )

    # Save video
    logger.info(f"Saving video to {output_path}")
    export_to_video(video_frames, str(output_path), fps=8)
    logger.info(f"✓ Video generation complete!")
    logger.info(f"  Frames: {num_frames}")
    logger.info(f"  Steps: {num_steps}")
    logger.info(f"  Output: {output_path}")


if __name__ == "__main__":
    main()
