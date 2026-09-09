# vfWorks

**A Python framework for the valid use and reuse of AI models.**

vfWorks provides tools for working with **Validity Frame (VF) enabled AI models**, supporting the validation and reuse of AI models within their intended context.

## Installation

```bash
uv sync
uv sync --extra ml
uv sync --extra api
uv sync --group screw-detection
uv sync --all-groups --all-extras
```

## License

vfWorks is licensed under the [Apache License 2.0](LICENSE).

## Citation

If you use vfWorks in academic work, please cite:

```bibtex
@software{vfworks,
  title  = {vfWorks: A Python Framework for the Valid Use and Reuse of AI Models},
  author = {Gladiné, Jan and Van Acker, Bert and Ryś, Arkadiusz Michał},
  year   = {2026},
  url    = {https://github.com/BertVanAcker/vfWorks}
}
```