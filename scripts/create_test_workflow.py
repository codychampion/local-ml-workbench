#!/usr/bin/env python3
"""
Create ComfyUI Test Workflow for Your Trained LoRA
===================================================
Automatically generates a ComfyUI workflow JSON configured with your custom LoRA

Usage:
    python scripts/create_test_workflow.py --lora outputs/lora/newvegas/newvegas_epoch5.safetensors
    python scripts/create_test_workflow.py --lora outputs/lora/fallout/fallout.safetensors --strength 0.7
"""

import argparse
import json
from pathlib import Path


def create_lora_test_workflow(lora_path: str, strength: float = 0.8, concept: str = None):
    """Create a ComfyUI workflow configured for testing a trained LoRA"""

    # Read the template
    template_path = Path("workflows/custom_lora_test.json")

    if not template_path.exists():
        print(f"Error: Template not found at {template_path}")
        return None

    workflow = json.loads(template_path.read_text())

    # Get LoRA filename (ComfyUI needs relative path from models/loras/)
    lora_file = Path(lora_path).name

    # Update node #2 (LoraLoaderModelOnly) with the LoRA path and strength
    for node in workflow["nodes"]:
        if node["id"] == 2:  # LoraLoaderModelOnly node
            node["widgets_values"] = [lora_file, strength]
            node["title"] = f"Custom LoRA: {lora_file} (strength: {strength})"
            break

    # If concept provided, update the prompt
    if concept:
        test_prompts = {
            "fallout": "Power-armored soldier walking through nuclear wasteland, Pip-Boy glowing, retro-futuristic aesthetic",
            "newvegas": "NCR ranger at Hoover Dam, Lucky 38 casino in distance, desert sunset",
            "default": f"Cinematic scene with {concept} aesthetic, detailed environment"
        }

        prompt = test_prompts.get(concept.lower(), test_prompts["default"])

        for node in workflow["nodes"]:
            if node["id"] == 5:  # Positive prompt node
                node["widgets_values"] = [prompt]
                break

    return workflow


def main():
    parser = argparse.ArgumentParser(description="Create ComfyUI test workflow for trained LoRA")

    parser.add_argument(
        "--lora",
        type=str,
        required=True,
        help="Path to your trained LoRA (.safetensors file)"
    )
    parser.add_argument(
        "--strength",
        type=float,
        default=0.8,
        help="LoRA strength (0.0-1.0, default: 0.8)"
    )
    parser.add_argument(
        "--concept",
        type=str,
        help="Concept name to generate test prompt"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="workflows/my_lora_test.json",
        help="Output workflow file (default: workflows/my_lora_test.json)"
    )

    args = parser.parse_args()

    # Check if LoRA exists
    lora_path = Path(args.lora)
    if not lora_path.exists():
        print(f"Error: LoRA file not found: {lora_path}")
        print(f"\nCheck available LoRAs:")
        print(f"  ls -la outputs/lora/*/")
        return

    # Infer concept from path if not provided
    concept = args.concept
    if not concept:
        # Try to get concept from parent directory name
        concept = lora_path.parent.name

    print("=" * 60)
    print("Creating ComfyUI Test Workflow")
    print("=" * 60)
    print(f"LoRA: {lora_path}")
    print(f"Strength: {args.strength}")
    print(f"Concept: {concept}")
    print("=" * 60)

    # Create workflow
    workflow = create_lora_test_workflow(
        lora_path=str(lora_path),
        strength=args.strength,
        concept=concept
    )

    if not workflow:
        return

    # Save workflow
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(workflow, indent=2))

    print(f"\n✓ Workflow created: {output_path}")
    print(f"\nNext steps:")
    print(f"1. Copy LoRA to ComfyUI location:")
    print(f"   cp {lora_path} models/loras/{lora_path.name}")
    print(f"")
    print(f"2. Open ComfyUI: http://localhost:8188")
    print(f"")
    print(f"3. Load workflow:")
    print(f"   - Click 'Load' button")
    print(f"   - Select: {output_path}")
    print(f"")
    print(f"4. Adjust if needed:")
    print(f"   - Node #2: Change LoRA strength")
    print(f"   - Node #5: Edit prompt")
    print(f"")
    print(f"5. Click 'Queue Prompt' to generate")
    print("=" * 60)


if __name__ == "__main__":
    main()
