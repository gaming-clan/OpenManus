<p align="center">
  <img src="assets/logo.jpg" width="200"/>
</p>

English | [中文](README_zh.md) | [한국어](README_ko.md) | [日本語](README_ja.md)

[![GitHub stars](https://img.shields.io/github/stars/FoundationAgents/OpenManus?style=social)](https://github.com/FoundationAgents/OpenManus/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) &ensp;
[![Discord Follow](https://dcbadge.vercel.app/api/server/DYn29wFk9z?style=flat)](https://discord.gg/DYn29wFk9z)
[![Demo](https://img.shields.io/badge/Demo-Hugging%20Face-yellow)](https://huggingface.co/spaces/lyh-917/OpenManusDemo)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15186407.svg)](https://doi.org/10.5281/zenodo.15186407)

# 👋 OpenManus

Manus is incredible, but OpenManus can achieve any idea without an *Invite Code* 🛫!

Our team members [@Xinbin Liang](https://github.com/mannaandpoem) and [@Jinyu Xiang](https://github.com/XiangJinyu) (core authors), along with [@Zhaoyang Yu](https://github.com/MoshiQAQ), [@Jiayi Zhang](https://github.com/didiforgithub), and [@Sirui Hong](https://github.com/stellaHSR), we are from [@MetaGPT](https://github.com/geekan/MetaGPT). The prototype is launched within 3 hours and we are keeping building!

It's a simple implementation, so we welcome any suggestions, contributions, and feedback!

Enjoy your own agent with OpenManus!

We're also excited to introduce [OpenManus-RL](https://github.com/OpenManus/OpenManus-RL), an open-source project dedicated to reinforcement learning (RL)- based (such as GRPO) tuning methods for LLM agents, developed collaboratively by researchers from UIUC and OpenManus.

---

## 🚀 What’s New

### WSL Sandbox Support & Native Usage

- **No Docker needed!** Run OpenManus completely natively inside [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/)—no Docker required.
- Provided `scripts/setup_wsl.sh` for auto-setup on WSL.
- WSL-specific instructions under [Installation](#installation).
- Project tested and compatible with WSL2 (Ubuntu recommended).

### Modern Web GUI

- Clean, minimal, responsive Web GUI built with vanilla HTML, CSS, and JavaScript.
- Launchable via `python main.py --web` (see [Quick Start](#quick-start)).
- Web GUI runs on `http://localhost:7860` by default.
- Easily extensible for custom workflows.

### API Key Management (keys.txt)

- We provide a sample `keys.example.txt` in the project root. Copy it to `keys.txt` and fill in your provider keys:

```bash
cp keys.example.txt keys.txt
```

- Format: Each line as `PROVIDER=your_key`, e.g.:
    ```
    ANTHROPIC_KEY=sk-...
    OPENAI_KEY=sk-...
    AZURE_OPENAI_KEY=...
    GEMINI_KEY=...
    DEEPSEEK_KEY=...
    ```
- The configuration loader prefers a project-level `keys.txt` (project root) and will fall back to `~/keys.txt` if present.
- No hardcoding—edit `keys.txt` and restart.

### Modular, Documented, Production-Ready

- All new features are modular and well-documented.
- Compatible with both CLI and Web GUI.
- Production-ready: error handling, extensible structure, security best practices.
---

## Project Demo

<video src="https://private-user-images.githubusercontent.com/61239030/420168772-6dcfd0d2-9142-45d9-b74e-d10aa75073c6.mp4" controls="controls" muted="muted" class="d-block rounded-bottom-2 border-top width-fit" style="max-height:640px; min-height: 200px"></video>

---

## Installation

### Method 1: WSL (Recommended for Windows)

1. **Open WSL terminal** (ensure Ubuntu 20.04+).
2. **Run the setup script:**
    ```bash
    bash scripts/setup_wsl.sh
    ```
    This installs Python, dependencies, and sets up the virtual environment.
3. **Activate environment:**
    ```bash
    source .venv/bin/activate
    ```
4. **Continue with [API Key setup](#api-key-management).**

### Method 2: Using uv

1. Install uv (A fast Python package installer and resolver):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Clone the repository:
    ```bash
    git clone https://github.com/FoundationAgents/OpenManus.git
    cd OpenManus
    ```

3. Create and activate environment:
    ```bash
    uv venv --python 3.12
    source .venv/bin/activate
    ```
4. Install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```

### Method 3: Using conda

1. Create a new conda environment:
    ```bash
    conda create -n open_manus python=3.12
    conda activate open_manus
    ```

2. Clone and install as above.

### Browser Automation Tool (Optional)
```bash
playwright install
```

---

## API Key Management

- Create a file named `keys.txt` in your project root.
- Add your keys as:
  ```
  ANTHROPIC_KEY=sk-...
  OPENAI_KEY=sk-...
  AZURE_OPENAI_KEY=...
  GEMINI_KEY=...
  DEEPSEEK_KEY=...
  ```
- The application auto-loads and injects these keys at runtime.

---

## Configuration

OpenManus requires configuration for the LLM APIs it uses.

- Copy the config template:
    ```bash
    cp config/config.example.toml config/config.toml
    ```
- Edit `config/config.toml` *or* use `keys.txt` for API key management.

---

## Quick Start

**CLI Mode:**
```bash
python main.py
```

**Web GUI Mode (Modern, Minimal UI):**
```bash
python main.py --web
```
Then open [http://localhost:7860](http://localhost:7860) in your browser.

**MCP Tool Version:**
```bash
python run_mcp.py
```

**Unstable Multi-Agent Version:**
```bash
python run_flow.py
```

---

## Custom Agents and Extensibility

You can add custom agents (e.g. DataAnalysis Agent) via `run_flow` in `config.toml`.

```toml
[runflow]
use_data_analysis_agent = true
```
See [detailed guide](app/tool/chart_visualization/README.md##Installation).

---

## How to contribute

We welcome any friendly suggestions and helpful contributions! Just create issues or submit pull requests.

Or contact @mannaandpoem via 📧email: mannaandpoem@gmail.com

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.

---

## Community Group
Join our networking group on Feishu and share your experience with other developers!

<div align="center" style="display: flex; gap: 20px;">
    <img src="assets/community_group.jpg" alt="OpenManus 交流群" width="300" />
</div>

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=FoundationAgents/OpenManus&type=Date)](https://star-history.com/#FoundationAgents/OpenManus&Date)

---

## Sponsors
Thanks to [PPIO](https://ppinfra.com/user/register?invited_by=OCPKCN&utm_source=github_openmanus&utm_medium=github_readme&utm_campaign=link) for computing source support.
> PPIO: The most affordable and easily-integrated MaaS and GPU cloud solution.

---

## Acknowledgement

Thanks to [anthropic-computer-use](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo), [browser-use](https://github.com/browser-use/browser-use) and [crawl4ai](https://github.com/unclecode/crawl4ai) for providing basic support for this project!

Additionally, we are grateful to [AAAJ](https://github.com/metauto-ai/agent-as-a-judge), [MetaGPT](https://github.com/geekan/MetaGPT), [OpenHands](https://github.com/All-Hands-AI/OpenHands) and [SWE-agent](https://github.com/SWE-agent/SWE-agent).

We also thank stepfun(阶跃星辰) for supporting our Hugging Face demo space.

OpenManus is built by contributors from MetaGPT. Huge thanks to this agent community!

---

## Cite

```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong and Sheng Fan and Xiao Tang},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15186407},
  url = {https://doi.org/10.5281/zenodo.15186407},
}
```
