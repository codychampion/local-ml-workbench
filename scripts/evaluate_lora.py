#!/usr/bin/env python3
"""
LoRA Evaluation - Test Your Trained LoRAs
==========================================
Compare video generation with and without your custom LoRA

Usage:
    python evaluate_lora.py --lora ./outputs/lora/fallout/fallout_epoch5.safetensors
    python evaluate_lora.py --lora ./outputs/lora/newvegas/newvegas.safetensors --prompts prompts.txt
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def create_comparison_workflow(lora_path: str, test_prompts: list, output_dir: Path):
    """
    Create a ComfyUI workflow JSON that tests your LoRA

    This generates 2 videos per prompt:
    1. Without your LoRA (baseline)
    2. With your LoRA at different strengths
    """

    print("=" * 60)
    print("LoRA EVALUATION WORKFLOW")
    print("=" * 60)
    print(f"LoRA: {lora_path}")
    print(f"Test prompts: {len(test_prompts)}")
    print(f"Output: {output_dir}")
    print("=" * 60)

    # Create test configurations
    tests = []

    for prompt in test_prompts:
        # Test 1: No LoRA (baseline)
        tests.append({
            "name": f"baseline_{prompt[:30].replace(' ', '_')}",
            "prompt": prompt,
            "lora": None,
            "lora_strength": 0.0
        })

        # Test 2: Your LoRA at 0.5 strength
        tests.append({
            "name": f"lora_0.5_{prompt[:30].replace(' ', '_')}",
            "prompt": prompt,
            "lora": lora_path,
            "lora_strength": 0.5
        })

        # Test 3: Your LoRA at 0.8 strength
        tests.append({
            "name": f"lora_0.8_{prompt[:30].replace(' ', '_')}",
            "prompt": prompt,
            "lora": lora_path,
            "lora_strength": 0.8
        })

        # Test 4: Your LoRA at 1.0 strength
        tests.append({
            "name": f"lora_1.0_{prompt[:30].replace(' ', '_')}",
            "prompt": prompt,
            "lora": lora_path,
            "lora_strength": 1.0
        })

    # Save test config
    output_dir.mkdir(parents=True, exist_ok=True)
    config_file = output_dir / "evaluation_config.json"
    config_file.write_text(json.dumps({
        "lora_path": lora_path,
        "tests": tests,
        "created_at": datetime.now().isoformat()
    }, indent=2))

    print(f"\n✓ Created evaluation config: {config_file}")
    print(f"\n📝 Next steps:")
    print(f"1. Open ComfyUI: http://localhost:8188")
    print(f"2. Load your workflow")
    print(f"3. For each test prompt, run 2 generations:")
    print(f"   a) Without your LoRA (baseline)")
    print(f"   b) With your LoRA in node #83 at different strengths")
    print(f"4. Compare results side-by-side")

    return tests


def create_test_prompts(concept: str) -> list:
    """Generate test prompts for a concept"""

    prompts = {
        "fallout": [
            "A power-armored soldier walking through nuclear wasteland at sunset",
            "Vault dweller opening a rusty vault door, camera following",
            "Pip-Boy interface glowing in dark underground bunker",
            "Retro-futuristic robot patrolling ruined cityscape",
            "Nuka-Cola sign flickering in post-apocalyptic bar"
        ],
        "newvegas": [
            "NCR ranger overlooking Hoover Dam at golden hour",
            "Lucky 38 casino tower lit up at night in New Vegas",
            "Courier walking down the Strip past neon signs",
            "Desert landscape with distant Vegas skyline",
            "Sunset Sarsaparilla bottle in abandoned saloon"
        ],
        "default": [
            f"A cinematic scene featuring {concept} aesthetic",
            f"Detailed {concept} environment, camera moving slowly",
            f"Close-up of {concept} themed object with dramatic lighting"
        ]
    }

    return prompts.get(concept.lower(), prompts["default"])


def print_evaluation_metrics():
    """Print guide for evaluating LoRA quality"""

    print("\n" + "=" * 60)
    print("HOW TO EVALUATE YOUR LORA")
    print("=" * 60)

    print("\n✅ What to Look For (Good Signs):")
    print("  • Consistent theme/style across generations")
    print("  • Accurate representation of your concept")
    print("  • Better detail in concept-specific elements")
    print("  • Prompt adherence improved")
    print("  • Maintains video smoothness")

    print("\n❌ Warning Signs (Needs More Training):")
    print("  • Generic results (looks like baseline)")
    print("  • Overfitted (always same image/scene)")
    print("  • Broken/distorted outputs")
    print("  • Lost prompt following ability")
    print("  • Choppy or static video")

    print("\n📊 Comparison Checklist:")
    print("  1. Visual Quality: Is it better than baseline?")
    print("  2. Theme Accuracy: Does it capture your concept?")
    print("  3. Diversity: Different prompts give varied results?")
    print("  4. Prompt Control: Still responds to prompt changes?")
    print("  5. Optimal Strength: Which strength (0.5/0.8/1.0) works best?")

    print("\n💡 Tips:")
    print("  • Lower strength (0.5-0.7) = subtle theme, more flexible")
    print("  • Higher strength (0.8-1.0) = strong theme, less flexible")
    print("  • If too strong: retrain with fewer epochs")
    print("  • If too weak: retrain with more epochs or data")
    print("  • Stack with official 4-step LoRA for speed + theme")


def main():
    parser = argparse.ArgumentParser(description="Evaluate trained LoRA quality")

    parser.add_argument(
        "--lora",
        type=str,
        required=True,
        help="Path to your trained LoRA (.safetensors)"
    )
    parser.add_argument(
        "--concept",
        type=str,
        help="Concept name (for auto-generating test prompts)"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        help="Text file with test prompts (one per line)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("./outputs/evaluation"),
        help="Output directory for evaluation results"
    )

    args = parser.parse_args()

    # Load or generate test prompts
    if args.prompts:
        prompts = Path(args.prompts).read_text().strip().split('\n')
    elif args.concept:
        prompts = create_test_prompts(args.concept)
    else:
        # Try to infer concept from path
        concept = Path(args.lora).parent.name
        prompts = create_test_prompts(concept)

    # Create evaluation workflow
    tests = create_comparison_workflow(
        lora_path=args.lora,
        test_prompts=prompts,
        output_dir=args.output
    )

    # Print evaluation guide
    print_evaluation_metrics()

    print("\n" + "=" * 60)
    print(f"✓ Evaluation setup complete!")
    print(f"  Config saved to: {args.output}/evaluation_config.json")
    print(f"  Ready to test {len(tests)} configurations")
    print("=" * 60)


if __name__ == "__main__":
    main()
