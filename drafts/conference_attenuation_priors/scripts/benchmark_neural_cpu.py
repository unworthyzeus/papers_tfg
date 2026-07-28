#!/usr/bin/env python3
"""Benchmark official dense radio-map networks on CPU and count conv MACs.

The script expects local checkouts of the official PMNet and RadioUNet
repositories. It does not load checkpoints because weights do not change the
architecture, parameter count, convolution MAC count, or dense forward path.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import statistics
import subprocess
import time
from pathlib import Path
from types import ModuleType
from typing import Any

import torch
from torch import nn


def load_module(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_revision(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def cpu_name() -> str:
    if os.name == "nt":
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-CimInstance Win32_Processor).Name",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return platform.processor() or "unknown"


def count_convolution_macs(model: nn.Module, sample: torch.Tensor) -> int:
    total = 0
    handles: list[Any] = []

    def hook(module: nn.Module, inputs: tuple[torch.Tensor, ...], output: torch.Tensor) -> None:
        nonlocal total
        if isinstance(module, nn.Conv2d):
            batch, out_channels, height, width = output.shape
            kernel_h, kernel_w = module.kernel_size
            total += (
                batch
                * out_channels
                * height
                * width
                * (module.in_channels // module.groups)
                * kernel_h
                * kernel_w
            )
        elif isinstance(module, nn.ConvTranspose2d):
            batch, in_channels, height, width = inputs[0].shape
            kernel_h, kernel_w = module.kernel_size
            total += (
                batch
                * in_channels
                * height
                * width
                * (module.out_channels // module.groups)
                * kernel_h
                * kernel_w
            )

    for module in model.modules():
        if isinstance(module, (nn.Conv2d, nn.ConvTranspose2d)):
            handles.append(module.register_forward_hook(hook))
    with torch.inference_mode():
        model(sample)
    for handle in handles:
        handle.remove()
    return total


def benchmark(
    model: nn.Module,
    sample: torch.Tensor,
    *,
    warmup: int,
    repeats: int,
) -> dict[str, Any]:
    model = model.cpu().eval()
    sample = sample.cpu()
    macs = count_convolution_macs(model, sample)
    with torch.inference_mode():
        for _ in range(warmup):
            model(sample)
    elapsed: list[float] = []
    with torch.inference_mode():
        for _ in range(repeats):
            start = time.perf_counter()
            model(sample)
            elapsed.append(time.perf_counter() - start)
    ordered = sorted(elapsed)
    p95_index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered)) - 1))
    return {
        "parameters": sum(parameter.numel() for parameter in model.parameters()),
        "convolution_macs": macs,
        "convolution_gmac": macs / 1e9,
        "cpu_time_s": {
            "median": statistics.median(elapsed),
            "mean": statistics.mean(elapsed),
            "p95": ordered[p95_index],
            "min": ordered[0],
            "max": ordered[-1],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pmnet-root", type=Path, required=True)
    parser.add_argument("--radiounet-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=6)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--repeats", type=int, default=50)
    args = parser.parse_args()

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.manual_seed(1234)

    pmnet_module = load_module(args.pmnet_root / "models" / "pmnet_v3.py", "official_pmnet_v3")
    pmnet = pmnet_module.PMNet(
        n_blocks=[3, 3, 27, 3],
        atrous_rates=[6, 12, 18],
        multi_grids=[1, 2, 4],
        output_stride=8,
    )
    radiounet_module = load_module(
        args.radiounet_root / "lib" / "modules.py", "official_radiounet_modules"
    )
    radiounet = radiounet_module.RadioWNet(inputs=2, phase="secondU")

    results = {
        "protocol": {
            "device": "cpu",
            "cpu": cpu_name(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torch_intraop_threads": torch.get_num_threads(),
            "torch_interop_threads": torch.get_num_interop_threads(),
            "mkldnn_enabled": torch.backends.mkldnn.enabled,
            "warmup_forward_passes": args.warmup,
            "timed_forward_passes": args.repeats,
            "batch_size": 1,
            "input": "fixed random float32 tensor",
            "weights": "random initialization; architecture-only benchmark",
            "timing_scope": "model forward only",
            "mac_scope": "Conv2d and ConvTranspose2d only; one MAC is one multiply-accumulate",
        },
        "models": {
            "PMNet_v3_output_stride_8": {
                "source": "https://github.com/abman23/PMNet",
                "source_commit": git_revision(args.pmnet_root),
                "input_shape": [1, 2, 256, 256],
                **benchmark(
                    pmnet,
                    torch.randn(1, 2, 256, 256, dtype=torch.float32),
                    warmup=args.warmup,
                    repeats=args.repeats,
                ),
            },
            "RadioUNet_RadioWNet": {
                "source": "https://github.com/RonLevie/RadioUNet",
                "source_commit": git_revision(args.radiounet_root),
                "input_shape": [1, 2, 256, 256],
                **benchmark(
                    radiounet,
                    torch.randn(1, 2, 256, 256, dtype=torch.float32),
                    warmup=args.warmup,
                    repeats=args.repeats,
                ),
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
