# Environment Troubleshooting

| Symptom | Fix |
|---|---|
| command not found | activate the intended environment and verify installation |
| `ModuleNotFoundError` | install the named public package with `python -m pip` |
| public-data download fails | check network, provider status, and loader version |
| empty artifact | verify season coverage, filters, and completion status |
| helper import error | verify the helper's documented public dependencies |
| optional loader missing | install only the named loader and rerun its probe |
| `libxgboost` cannot load `libomp.dylib` on macOS | run `brew install libomp`, then retry the optional `sportsdataverse` import |
