# References and specification checks

These links are reference points for feasibility and study design. They do not establish that this proposed integrated system works.

## Official hardware and model documentation

1. Seeed Studio, reComputer RK3576 development kit, octa-core / 6 TOPS NPU: https://www.seeedstudio.com/reComputer-RK3576-Module-Dev-Kit-p-6952.html
2. Seeed Studio, ReSpeaker XVF3800 USB 4-Mic Array documentation: https://wiki.seeedstudio.com/respeaker_xvf3800_introduction/
3. Qwen team, Qwen3 repository / model information: https://github.com/QwenLM/Qwen3
4. Firefly product family / candidate board: check exact vendor SKU, carrier, RAM and published documentation *before purchase*. No vendor benchmark is claimed here.

## Relevant AI-agent safety evaluation

1. AgentDojo, ETH Zurich SPY Lab, indirect prompt injection benchmark: https://github.com/ethz-spylab/agentdojo
2. OWASP Top 10 for LLM Applications (2025), prompt injection and excessive agency: https://genai.owasp.org/llm-top-10/
3. Open Agent Security Benchmark (external example; independently examine licensing / applicability): https://github.com/opena2a-org/oasb

## Questions to verify during Week 1

- Does the exact RK3576 device variant support a deployable local Qwen3-0.6B checkpoint with the selected runtime and quantization?
- What is measured warm/cold decision latency and power draw for each safety path?
- Is the Firefly compact module + carrier substantially smaller or cheaper without losing required I/O?
- Does the microphone unit enumerate and record on the selected Linux image with the right USB firmware?
- Can the mock executor be configured such that the monitored agent *cannot* bypass the gateway?
