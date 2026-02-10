import argparse
import os
from typing import Dict

from ..ystm.demo import DEFAULT_SEGMENTS, DemoConfig, write_demo_outputs
from ..ystm.energy import EnergyConfig
from ..ystm.ingest import load_segments
from ..ystm.representation import EmbeddingConfig
from ..ystm.terrain import TerrainConfig


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate YSTM v0.1 minimal demo outputs.")
    parser.add_argument(
        "--output-dir",
        default=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "reports", "ystm_demo")
        ),
        help="Directory to write nodes.json, audit_log.json, terrain.html, terrain.json, terrain_p2.*.",
    )
    parser.add_argument(
        "--input",
        help="Optional JSON file containing segments list or {segments: [...]} wrapper.",
    )
    parser.add_argument("--grid-width", type=int, default=80)
    parser.add_argument("--grid-height", type=int, default=60)
    parser.add_argument("--sigma", type=float, default=0.75)
    parser.add_argument("--levels", type=int, default=5)
    parser.add_argument("--embedding-dims", type=int, default=12)
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--beta", type=float, default=0.0)
    parser.add_argument("--gamma", type=float, default=0.0)
    parser.add_argument("--no-normalize-energy", action="store_true")
    parser.add_argument(
        "--export-png", action="store_true", help="Export PNG if cairosvg is available."
    )
    parser.add_argument("--png-scale", type=float, default=2.0, help="Scale factor for PNG export.")
    return parser


def main() -> Dict[str, str]:
    parser = build_arg_parser()
    args = parser.parse_args()
    segments = DEFAULT_SEGMENTS
    if args.input:
        segments = load_segments(args.input)
    config = DemoConfig(
        embedding=EmbeddingConfig(dims=args.embedding_dims),
        energy=EnergyConfig(
            alpha=args.alpha,
            beta=args.beta,
            gamma=args.gamma,
            normalize=not args.no_normalize_energy,
        ),
        terrain=TerrainConfig(
            grid_width=args.grid_width,
            grid_height=args.grid_height,
            sigma=args.sigma,
            contour_levels=args.levels,
        ),
    )
    outputs = write_demo_outputs(
        output_dir=args.output_dir,
        segments=segments,
        config=config,
        export_png=args.export_png,
        png_scale=args.png_scale,
    )
    outputs["export_png"] = args.export_png
    return outputs


if __name__ == "__main__":
    paths = main()
    print(f"nodes.json: {paths['nodes']}")
    print(f"audit_log.json: {paths['audit']}")
    print(f"terrain.html: {paths['terrain']}")
    print(f"terrain.svg: {paths['terrain_svg']}")
    if paths.get("terrain_png"):
        print(f"terrain.png: {paths['terrain_png']}")
    elif paths.get("export_png"):
        print("terrain.png: not generated (missing cairosvg/cairo)")
    print(f"terrain.json: {paths['terrain_json']}")
    print(f"terrain_p2.html: {paths['terrain_p2']}")
    print(f"terrain_p2.svg: {paths['terrain_p2_svg']}")
    if paths.get("terrain_p2_png"):
        print(f"terrain_p2.png: {paths['terrain_p2_png']}")
    elif paths.get("export_png"):
        print("terrain_p2.png: not generated (missing cairosvg/cairo)")
    print(f"terrain_p2.json: {paths['terrain_p2_json']}")
