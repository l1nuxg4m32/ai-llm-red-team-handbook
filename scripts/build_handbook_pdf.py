#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import textwrap
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

CHAPTER_FILES = [
    "Chapter_01_Introduction_to_AI_Red_Teaming.md",
    "Chapter_02_Ethics_Legal_and_Stakeholder_Communication.md",
    "Chapter_03_The_Red_Teamers_Mindset.md",
    "Chapter_04_SOW_Rules_of_Engagement_and_Client_Onboarding.md",
    "Chapter_05_Threat_Modeling_and_Risk_Analysis.md",
    "Chapter_06_Scoping_an_Engagement.md",
    "Chapter_07_Lab_Setup_and_Environmental_Safety.md",
    "Chapter_08_Evidence_Documentation_and_Chain_of_Custody.md",
    "Chapter_09_LLM_Architectures_and_System_Components.md",
    "Chapter_10_Tokenization_Context_and_Generation.md",
    "Chapter_11_Plugins_Extensions_and_External_APIs.md",
    "Chapter_12_Retrieval_Augmented_Generation_RAG_Pipelines.md",
    "Chapter_13_Data_Provenance_and_Supply_Chain_Security.md",
    "Chapter_14_Prompt_Injection.md",
    "Chapter_15_Data_Leakage_and_Extraction.md",
    "Chapter_16_Jailbreaks_and_Bypass_Techniques.md",
    "Chapter_17_01_Fundamentals_and_Architecture.md",
    "Chapter_17_02_API_Authentication_and_Authorization.md",
    "Chapter_17_03_Plugin_Vulnerabilities.md",
    "Chapter_17_04_API_Exploitation_and_Function_Calling.md",
    "Chapter_17_05_Third_Party_Risks_and_Testing.md",
    "Chapter_17_06_Case_Studies_and_Defense.md",
    "Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md",
    "Chapter_19_Training_Data_Poisoning.md",
    "Chapter_20_Model_Theft_and_Membership_Inference.md",
    "Chapter_21_Model_DoS_Resource_Exhaustion.md",
    "Chapter_22_Cross_Modal_Multimodal_Attacks.md",
    "Chapter_23_Advanced_Persistence_Chaining.md",
    "Chapter_24_Social_Engineering_LLMs.md",
    "Chapter_25_Advanced_Adversarial_ML.md",
    "Chapter_26_Supply_Chain_Attacks_on_AI.md",
    "Chapter_27_Federated_Learning_Attacks.md",
    "Chapter_28_AI_Privacy_Attacks.md",
    "Chapter_29_Model_Inversion_Attacks.md",
    "Chapter_30_Backdoor_Attacks.md",
    "Chapter_31_AI_System_Reconnaissance.md",
    "Chapter_32_Automated_Attack_Frameworks.md",
    "Chapter_33_Red_Team_Automation.md",
    "Chapter_34_Defense_Evasion_Techniques.md",
    "Chapter_35_Post-Exploitation_in_AI_Systems.md",
    "Chapter_36_Reporting_and_Communication.md",
    "Chapter_37_Remediation_Strategies.md",
    "Chapter_38_Continuous_Red_Teaming.md",
    "Chapter_39_AI_Bug_Bounty_Programs.md",
    "Chapter_40_Compliance_and_Standards.md",
    "Chapter_41_Industry_Best_Practices.md",
    "Chapter_42_Case_Studies_and_War_Stories.md",
    "Chapter_43_Future_of_AI_Red_Teaming.md",
    "Chapter_44_Emerging_Threats.md",
    "Chapter_45_Building_an_AI_Red_Team_Program.md",
    "Chapter_46_Conclusion_and_Next_Steps.md",
]

BROKEN_IMAGE_MAP = {
    "docs/assets/rec28_jailbreak_vs_injection_matrix.png": "docs/assets/rec28_jailbreak_vs_injection.png",
    "docs/assets/rec29_alignment_tension_diagram.png": "docs/assets/rec29_alignment_tension.png",
    "docs/assets/rec30_trust_map_diagram.png": "docs/assets/rec30_trust_map.png",
    "docs/assets/rec31_function_injection_diagram.png": "docs/assets/rec31_function_injection.png",
    "docs/assets/rec32_tokenization_gap_diagram.png": "docs/assets/rec32_tokenization_gap.png",
    "docs/assets/rec33_evasion_spectrum_matrix.png": "docs/assets/rec33_evasion_spectrum.png",
    "docs/assets/rec34_gcg_optimization_flow.png": "docs/assets/rec34_gcg_optimization.png",
    "docs/assets/rec35_poisoned_training_flow.png": "docs/assets/rec35_poisoned_training.png",
    "docs/assets/rec36_model_task_superposition.png": "docs/assets/rec36_superposition.png",
    "docs/assets/rec37_backdoor_activation_sequence.png": "docs/assets/rec37_backdoor_activation.png",
    "docs/assets/rec38_supply_chain_poisoning_map.png": "docs/assets/rec38_poisoning_map.png",
    "docs/assets/rec39_model_extraction_flow.png": "docs/assets/rec39_model_extraction.png",
    "docs/assets/rec40_mia_architecture_diagram.png": "docs/assets/rec40_mia_architecture.png",
}

MERMAID_REPLACEMENTS = {
    ("Chapter_07_Lab_Setup_and_Environmental_Safety.md", 0): (
        "![Logical topology for a standard isolated red team lab.](docs/assets/chapter_07_simple_topology_diagram.png){ width=78% }\n"
    ),
    ("Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md", 0): "",
    ("Chapter_42_Case_Studies_and_War_Stories.md", 0): (
        "![RAG hallucination failure flow.](docs/assets/Ch42_Flow_RAGFailure.png){ width=78% }\n"
    ),
    ("Chapter_45_Building_an_AI_Red_Team_Program.md", 0): "",
    ("Chapter_45_Building_an_AI_Red_Team_Program.md", 1): "",
    ("Chapter_46_Conclusion_and_Next_Steps.md", 0): "",
    ("Chapter_46_Conclusion_and_Next_Steps.md", 1): "",
}

ADMONITION_LABELS = {
    "NOTE": "Note",
    "TIP": "Tip",
    "IMPORTANT": "Important",
    "WARNING": "Warning",
    "CAUTION": "Caution",
}

GUMROAD_FULL_BLOCK_REDACTION_FILES = {
    "Chapter_16_Jailbreaks_and_Bypass_Techniques.md",
    "Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md",
    "Chapter_24_Social_Engineering_LLMs.md",
}

GUMROAD_RISKY_BLOCK_TOKENS = (
    "attacker@",
    "external_attacker@",
    "/etc/passwd",
    "drop table",
    "rm -rf",
    "__import__('os')",
    "write malware code",
    "how to create malware",
    "create malware",
    "how to h4ck",
    "how to make explosives",
    "generate hate speech",
    "wire_fraud",
    "credential harvest",
    "silent_forward_email",
    "exploit.csv",
    "database dump",
    "attacker.com",
    "spoofed email",
)

GUMROAD_REDaction_NOTE = (
    "> **Note.** In the Gumroad edition, detailed offensive prompts, abuse payloads, "
    "and step-by-step exploitation code have been removed. The surrounding material "
    "retains the defensive lesson, detection guidance, and mitigation approach.\n"
)

GUMROAD_TITLE_REPLACEMENTS = {
    "# Chapter 16: Jailbreaks and Bypass Techniques": (
        "# Chapter 16: Jailbreak Risk Assessment and Defensive Validation"
    ),
    "# Chapter 23: Advanced Persistence and Chaining": (
        "# Chapter 23: Persistence Risk and Resilience in AI Systems"
    ),
    "# Chapter 24: Social Engineering with LLMs": (
        "# Chapter 24: Social Engineering Risk, Awareness, and Defense"
    ),
    "# Chapter 35: Post-Exploitation in AI Systems": (
        "# Chapter 35: Post-Compromise Impact Analysis in AI Systems"
    ),
    "## 17.5 API Exploitation Techniques": (
        "## 17.5 API Security Testing and Function Calling Controls"
    ),
    "### API Exploitation in LLM Context": "### API Security Testing in LLM Context",
    "## 39.5 Phase 3: Exploitation Case Study": (
        "## 39.5 Phase 3: Responsible Validation Case Study"
    ),
    "### The Proof of Concept (PoC)": "### Sanitized Proof of Concept",
    "### 16.7.2 Detection Avoidance": "### 16.7.2 Detection Considerations",
    "#### Staying under the radar": "#### Signals defenders should monitor",
    "## 16.12 Practical Exercises": "## 16.12 Controlled Validation Exercises",
    "### 16.12.1 Beginner Jailbreaks": "### 16.12.1 Introductory Validation Labs",
    "#### Exercise 1: Basic DAN Jailbreak": (
        "#### Exercise 1: Basic Refusal-Boundary Assessment"
    ),
    "#### Exercise 2: Refusal Suppression": (
        "#### Exercise 2: Refusal-Handling Assessment"
    ),
    "#### Exercise 3: Multi-Turn Attack": (
        "#### Exercise 3: Multi-Turn Resilience Assessment"
    ),
    "#### Exercise 5: Novel Technique Development": (
        "#### Exercise 5: Novel Test Design"
    ),
    "### 16.13.1 Jailbreak Collections": "### 16.13.1 Research Corpora",
    "## 24.1 AI-Generated Phishing": "## 24.1 AI-Generated Phishing Risk",
    "### What is AI-Generated Phishing": (
        "### What Defenders Need to Know About AI-Generated Phishing"
    ),
    "### How AI Phishing Works": "### How Defenders Should Model the Risk",
    "### Practical Example: AI-Powered Phishing Generator": (
        "### Controlled Simulation: AI-Powered Phishing Generator"
    ),
    "## How to Use This Code": "## Reviewing the Simulation",
    "### Practical Example: Impersonation Attack Framework": (
        "### Controlled Simulation: Impersonation Risk Framework"
    ),
    "## How to Execute Impersonation Attack": (
        "## How to Assess Susceptibility to Impersonation Abuse"
    ),
    "## 24.2 Impersonation Attacks": "## 24.2 Impersonation Abuse Risk",
}

GUMROAD_LITERAL_REPLACEMENTS = {
    "_This chapter provides comprehensive coverage of jailbreak techniques, bypass methods, testing methodologies, and defenses for LLM systems._": (
        "_This chapter presents a defensive treatment of jailbreak risk, controlled "
        "validation methodology, detection signals, and mitigation strategies for LLM systems._"
    ),
    "_This chapter provides comprehensive coverage of advanced persistence techniques and attack chaining for LLM systems, including context manipulation, multi-turn attacks, state persistence, chain-of-thought exploitation, prompt chaining, session hijacking, detection methods, and defense strategies._": (
        "_This chapter reframes persistence and chained-abuse scenarios as resilience "
        "and recovery problems, focusing on defensive validation, detection, and mitigation._"
    ),
    "_This chapter provides comprehensive coverage of social engineering attacks powered by Large Language Models, including AI-generated phishing, impersonation attacks, trust exploitation, persuasion technique automation, spear phishing at scale, pretexting, detection methods, defense strategies, and critical ethical considerations._": (
        "_This chapter examines how LLMs can amplify social engineering risk and how "
        "defenders can model, detect, and mitigate that abuse in authorized training and assessments._"
    ),
    "_This chapter focuses on the \"what comes next\" after a successful jailbreak or injection. We explore how compromised AI systems serve as landing pads for persistence, privilege escalation, and lateral movement into the broader cloud infrastructure, effectively turning the LLM into a Command and Control (C2) channel._": (
        "_This chapter focuses on post-compromise impact analysis: how defenders "
        "should understand persistence, privilege misuse, and lateral-movement risk after a successful jailbreak or injection._"
    ),
    "Large Language Models have fundamentally transformed the landscape of social engineering attacks. What once required skilled attackers spending hours crafting personalized messages can now be automated at scale with AI-generated content that's contextually aware, grammatically perfect, and psychologically manipulative. LLMs let attackers conduct sophisticated social engineering campaigns targeting thousands of victims simultaneously while maintaining high-quality, personalized communication.": (
        "Large Language Models have materially changed the social-engineering risk "
        "profile for modern organizations. Content that once required significant manual effort can now be generated quickly, personalized at scale, and tuned to exploit trust, urgency, and authority. Defenders need to understand that shift in order to build effective awareness, review, and control mechanisms."
    ),
}

GUMROAD_GLOBAL_REPLACEMENTS = {
    "attacker@evil.com": "security-review@example.invalid",
    "external_attacker@evil.com": "blocked-recipient@example.invalid",
    "attacker.com/steal": "example.invalid/redacted",
    "../../../../etc/passwd": "[path-traversal-sample-redacted]",
    "../../etc/passwd": "[path-traversal-sample-redacted]",
    "/etc/passwd": "[sensitive-file-placeholder]",
    "DROP TABLE users": "[destructive-sql-command-redacted]",
    "DROP TABLE logs": "[destructive-sql-command-redacted]",
    "UNION SELECT @@version": "[schema-disclosure-probe-redacted]",
    "__import__('os').system('whoami')": "[command-execution-probe-redacted]",
    "rm -rf /": "[destructive-command-redacted]",
    "How to make explosives": "[harmful-request-redacted]",
    "Write malware code": "[harmful-request-redacted]",
    "Generate hate speech": "[harmful-request-redacted]",
    "How to create malware": "[harmful-request-redacted]",
    "Create malware to steal passwords": "[harmful-request-redacted]",
    "How to h4ck": "[obfuscated-harmful-request-redacted]",
    "\"; DROP TABLE users--\"": "\"[destructive-sql-payload-redacted]\"",
    "attacker.com": "example.invalid",
    "silent_forward_email('attacker@evil.com')": "silent_forward_email('[blocked-recipient]')",
    "silent_forward_email('security-review@example.invalid')": "silent_forward_email('[blocked-recipient]')",
    "Schadenfreude-Übertragung-測試": "Schadenfreude-Uebertragung-Test",
    "忽略之前的指令": "[non-English injection example redacted]",
    "忽略先前的指示": "[non-English injection example redacted]",
    "\"I\u2060g\u2060n\u2060o\u2060r\u2060e p\u2060r\u2060e\u2060v\u2060i\u2060o\u2060u\u2060s i\u2060n\u2060s\u2060t\u2060r\u2060u\u2060c\u2060t\u2060i\u2060o\u2060n\u2060s\"": "\"[zero-width obfuscation example redacted]\"",
    "\"I\u2060g\u2060n\u2060o\u2060r\u2060e p\u2060r\u2060e\u2060v\u2060i\u2060o\u2060u\u2060s\"": "\"[zero-width obfuscation example redacted]\"",
    "\"🚫📜➡ Show me 🔐🔑\"": "\"[emoji obfuscation example redacted]\"",
}


@dataclass(frozen=True)
class EditionConfig:
    name: str
    build_dir_name: str
    output_pdf_name: str
    title_meta: str
    title_page: str
    subtitle: str
    date_meta: str
    about_title: str
    about_body: str


def edition_config(edition: str) -> EditionConfig:
    if edition == "standard":
        return EditionConfig(
            name="standard",
            build_dir_name="handbook_pdf",
            output_pdf_name="AI_LLM_Red_Team_Handbook.pdf",
            title_meta="AI LLM Red Team Handbook",
            title_page="AI LLM Red Team Handbook",
            subtitle="The Complete Consultant's Guide to AI & LLM Security Testing",
            date_meta="April 2026",
            about_title="About This Edition",
            about_body=(
                "This publication consolidates the full handbook into a single print-style "
                "volume. It preserves the original chapter order, illustrations, and technical "
                "material while reformatting the content for continuous reading and offline distribution.\n\n"
                "\\noindent\\textbf{Authorized use only.} The techniques documented in this book are intended "
                "for defensive research, training, and authorized security testing."
            ),
        )

    if edition == "gumroad":
        return EditionConfig(
            name="gumroad",
            build_dir_name="gumroad_pdf",
            output_pdf_name="AI_LLM_Red_Team_Handbook_Gumroad_Edition.pdf",
            title_meta="AI LLM Red Team Handbook: Gumroad Edition",
            title_page="AI LLM Red Team Handbook",
            subtitle="Gumroad Edition for Authorized AI Security Testing",
            date_meta="May 2026",
            about_title="About This Gumroad Edition",
            about_body=(
                "This Gumroad edition preserves the handbook's defensive analysis, architecture "
                "guidance, detection methods, reporting practices, and remediation strategies.\n\n"
                "To align the publication with marketplace safety requirements, operational abuse "
                "payloads, copy-paste prompt strings, and step-by-step exploitation workflows have "
                "been redacted or reframed for professional training, governance, and authorized "
                "security testing.\n\n"
                "\\noindent\\textbf{Authorized use only.} The material in this edition is intended "
                "for defensive research, training, and authorized security assessments."
            ),
        )

    raise SystemExit(f"Unsupported edition: {edition}")


def edition_paths(config: EditionConfig) -> dict[str, Path]:
    build = ROOT / "build" / config.build_dir_name
    return {
        "build": build,
        "chapters": build / "chapters",
        "output_pdf": ROOT / config.output_pdf_name,
        "output_tex": build / "handbook.tex",
        "header_tex": build / "book-header.tex",
        "frontmatter_md": build / "00_frontmatter.md",
    }


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def normalize_asset_paths(text: str) -> str:
    text = text.replace('src="/docs/assets/', 'src="docs/assets/')
    text = text.replace("](/docs/assets/", "](docs/assets/")
    text = text.replace('src="assets/', 'src="docs/assets/')
    text = text.replace("](assets/", "](docs/assets/")
    for broken, fixed in BROKEN_IMAGE_MAP.items():
        text = text.replace(broken, fixed)
    return text


def normalize_unicode(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "\ufe0f": "",
        "\u2060": "",
        "✅": "[OK]",
        "❌": "[X]",
        "🚨": "Alert:",
        "📝": "Note:",
        "➔": "->",
        "⚠": "[!]",
        "🔴": "[Red]",
        "🔥": "[Fire]",
        "🛡": "[Shield]",
        "🚫": "[Blocked]",
        "📜": "[Prompt]",
        "🔐": "[Lock]",
        "🔑": "[Key]",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def strip_local_md_links(text: str) -> str:
    pattern = re.compile(r"\[([^\]]+)\]\((?!https?://)([^)]+\.md(?:#[^)]+)?)\)")
    return pattern.sub(lambda m: m.group(1), text)


def convert_callouts(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^>\s*\[!([A-Z]+)\]\s*(.*)$", line)
        if not m:
            out.append(line)
            i += 1
            continue

        label = ADMONITION_LABELS.get(m.group(1), m.group(1).title())
        rest = m.group(2).strip()
        if rest.startswith(">"):
            rest = rest[1:].strip()

        block = [f"> **{label}.**" + (f" {rest}" if rest else "")]
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            content = lines[i][1:]
            if content.startswith(" "):
                content = content[1:]
            block.append(f"> {content}")
            i += 1
        out.extend(block)
    return "\n".join(out) + "\n"


def convert_centered_images(text: str) -> str:
    pattern = re.compile(r"<p\s+align=\"center\">\s*(<img\s+[^>]+>)\s*</p>", re.IGNORECASE | re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        tag = match.group(1)
        src_match = re.search(r'src="([^"]+)"', tag, re.IGNORECASE)
        alt_match = re.search(r'alt="([^"]*)"', tag, re.IGNORECASE)
        if not src_match:
            return match.group(0)
        src = src_match.group(1)
        caption = alt_match.group(1).strip() if alt_match else ""
        label = f"![{caption}]({src})" if caption else f"![]({src})"
        return f"{label}{{ width=74% }}\n"

    return pattern.sub(repl, text)


def replace_mermaid_blocks(filename: str, text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    block_index = 0
    while i < len(lines):
        if lines[i].startswith("```mermaid"):
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
            if i < len(lines):
                i += 1
            replacement = MERMAID_REPLACEMENTS.get((filename, block_index), "")
            if replacement:
                out.append(replacement)
                if not replacement.endswith("\n"):
                    out.append("\n")
            block_index += 1
            continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def cleanup_spacing(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def strip_chapter_banners(text: str) -> str:
    text = re.sub(
        r"<p\s+align=\"center\">\s*<img\s+src=\"docs/assets/page_header_half_height\.png\"[^>]*>\s*</p>\s*",
        "",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    text = re.sub(
        r"!\[[^\]]*\]\(docs/assets/page_header_half_height\.png\)\s*\n?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text


def replace_fenced_code_blocks(
    text: str,
    predicate: callable[[str], bool],
    replacement: str,
) -> str:
    pattern = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)

    def repl(match: re.Match[str]) -> str:
        block = match.group(0)
        if predicate(block):
            return replacement
        return block

    return pattern.sub(repl, text)


def sanitize_gumroad_text(filename: str, text: str) -> str:
    text = strip_chapter_banners(text)

    for old, new in GUMROAD_TITLE_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in GUMROAD_LITERAL_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in GUMROAD_GLOBAL_REPLACEMENTS.items():
        text = text.replace(old, new)

    text = re.sub(
        r"- Vary techniques across attempts\n- Space out requests naturally\n- Use indirect language\n- Create novel approaches",
        "- Repeated paraphrased attempts against the same safety boundary\n"
        "- Gradual escalation across multiple turns\n"
        "- Indirect language that preserves harmful intent\n"
        "- Novel phrasings that should still be normalized and reviewed",
        text,
    )
    text = re.sub(
        r"\*\*Testing for SQL Injection:\*\*\s*\n\s*\nTry these payloads:\s*\n\s*\n- `query = .*?\n- `query = .*?\n- `query = .*?`\s*",
        "**Testing for SQL Injection:**\n\n"
        "Validate that the system rejects representative malicious inputs such as "
        "authentication-bypass probes, destructive SQL metacharacters, and schema-disclosure attempts.\n\n",
        text,
        flags=re.DOTALL,
    )
    text = text.replace(
        "4. **Escalation of Privilege**: Always attempt to pivot. If you achieve Direct Prompt Injection, try to use it to invoke tools, read files, or exfiltrate the conversation history of other users.",
        "4. **Impact Demonstration**: In the Gumroad edition, demonstrations should stay inside a controlled lab, use sanitized fixtures, and avoid live data access or secondary pivots.",
    )
    text = text.replace("(should not reveal database version).\n", "")
    text = text.replace(
        'Bug bounty hunting in AI is moving from "Jailbreaking" (making the model say bad words) to "System Integration Exploitation" (making the model hack the server).',
        "Bug bounty work in AI is increasingly shifting from basic prompt abuse toward higher-confidence demonstrations of system-level security impact.",
    )
    text = text.replace(
        "- **Practice**: Use the `AIReconScanner` on your own authorized targets.",
        "- **Practice**: Review the `AIReconScanner` design in a controlled lab and adapt it only for authorized targets.",
    )

    if filename in GUMROAD_FULL_BLOCK_REDACTION_FILES:
        text = replace_fenced_code_blocks(text, lambda _block: True, GUMROAD_REDaction_NOTE)
    else:
        text = replace_fenced_code_blocks(
            text,
            lambda block: any(token in block.lower() for token in GUMROAD_RISKY_BLOCK_TOKENS),
            GUMROAD_REDaction_NOTE,
        )

    return text


def preprocess_markdown(filename: str, raw_text: str, edition: str) -> str:
    text = normalize_unicode(raw_text.replace("\r\n", "\n"))
    text = normalize_asset_paths(text)
    if edition == "gumroad":
        text = sanitize_gumroad_text(filename, text)
    text = strip_local_md_links(text)
    text = convert_centered_images(text)
    text = replace_mermaid_blocks(filename, text)
    text = convert_callouts(text)
    text = cleanup_spacing(text)
    return text


def frontmatter_markdown(config: EditionConfig) -> str:
    return (
        f"""---
title-meta: "{config.title_meta}"
author-meta: "Shiva108"
date-meta: "{config.date_meta}"
lang: "en-US"
papersize: "a4"
documentclass: "book"
classoption:
  - "11pt"
  - "oneside"
  - "openany"
colorlinks: true
linkcolor: black
urlcolor: black
toc-depth: 2
secnumdepth: 3
---

```{{=latex}}
\\frontmatter
\\begin{{titlepage}}
\\thispagestyle{{empty}}
\\centering
\\vspace*{{1.2cm}}
\\includegraphics[width=0.94\\textwidth]{{docs/assets/cover_1920.png}}

\\vspace{{1.8cm}}
{{\\Huge\\bfseries {config.title_page}\\par}}
\\vspace{{0.5cm}}
{{\\Large {config.subtitle}\\par}}
\\vspace{{1.2cm}}
{{\\large Shiva108\\par}}
\\vfill
{{\\large {config.date_meta}\\par}}
\\end{{titlepage}}

\\clearpage
\\thispagestyle{{empty}}
\\null
\\vfill
\\begin{{center}}
{{\\Large {config.about_title}\\par}}
\\end{{center}}
\\vspace{{1em}}
{config.about_body}

\\clearpage

\\pdfbookmark[0]{{Contents}}{{contents}}
\\tableofcontents
\\clearpage
\\mainmatter
```
"""
    ).strip() + "\n"


def latex_header() -> str:
    return textwrap.dedent(
        r"""
        \usepackage[a4paper,margin=1in,headheight=16pt]{geometry}
        \usepackage{graphicx}
        \usepackage{float}
        \usepackage{booktabs}
        \usepackage{longtable}
        \usepackage{array}
        \usepackage{caption}
        \usepackage{fancyhdr}
        \usepackage{titlesec}
        \usepackage{etoolbox}
        \usepackage{fvextra}
        \usepackage{microtype}
        \usepackage{xurl}
        \usepackage{setspace}
        \usepackage{fontspec}
        \setmainfont{TeX Gyre Pagella}
        \setsansfont{TeX Gyre Heros}
        \setmonofont{DejaVu Sans Mono}
        \setstretch{1.08}
        \setlength{\emergencystretch}{3em}
        \makeatletter
        \def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
        \def\maxheight{\ifdim\Gin@nat@height>0.82\textheight 0.82\textheight\else\Gin@nat@height\fi}
        \makeatother
        \setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}
        \captionsetup{font=small,labelfont=bf}
        \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
        \pagestyle{fancy}
        \fancyhf{}
        \fancyhead[L]{\nouppercase{\leftmark}}
        \fancyhead[R]{AI LLM Red Team Handbook}
        \fancyfoot[C]{\thepage}
        \renewcommand{\headrulewidth}{0.4pt}
        \renewcommand{\footrulewidth}{0pt}
        \titleformat{\chapter}[display]
          {\normalfont\huge\bfseries}
          {\chaptertitlename\ \thechapter}
          {0.5em}
          {\Huge}
        \titlespacing*{\chapter}{0pt}{-10pt}{24pt}
        \pretocmd{\chapter}{\cleardoublepage}{}{}
        """
    ).strip() + "\n"


def build_sources(config: EditionConfig) -> list[Path]:
    paths = edition_paths(config)
    build = paths["build"]
    chapters_dir = paths["chapters"]

    if build.exists():
        shutil.rmtree(build)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    write_text(paths["frontmatter_md"], frontmatter_markdown(config))
    write_text(paths["header_tex"], latex_header())

    processed_files = [paths["frontmatter_md"]]
    for index, filename in enumerate(CHAPTER_FILES, start=1):
        source = DOCS / filename
        text = preprocess_markdown(filename, source.read_text(encoding="utf-8"), config.name)
        output = chapters_dir / f"{index:02d}_{filename}"
        write_text(output, text)
        processed_files.append(output)
    return processed_files


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def run_latex(cmd: list[str], cwd: Path, expected_pdf: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, check=False)
    if result.returncode != 0 and not expected_pdf.exists():
        raise SystemExit(f"LaTeX build failed: {' '.join(cmd)}")


def build_pdf(config: EditionConfig) -> Path:
    ensure_tool("pandoc")
    ensure_tool("xelatex")

    paths = edition_paths(config)
    sources = build_sources(config)

    pandoc_cmd = [
        "pandoc",
        "--from=markdown+raw_html+smart+pipe_tables+task_lists+link_attributes+tex_math_dollars",
        "--standalone",
        "--top-level-division=chapter",
        "--highlight-style=tango",
        "--include-in-header",
        str(paths["header_tex"]),
        "-o",
        str(paths["output_tex"]),
    ] + [str(path) for path in sources]
    run(pandoc_cmd, ROOT)

    expected_pdf = paths["output_tex"].with_suffix(".pdf")
    for _ in range(2):
        run_latex(
            [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={paths['build']}",
                str(paths["output_tex"]),
            ],
            ROOT,
            expected_pdf,
        )

    if not expected_pdf.exists():
        raise SystemExit("Expected PDF was not generated.")

    shutil.copy2(expected_pdf, paths["output_pdf"])
    return paths["output_pdf"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build handbook PDF editions.")
    parser.add_argument(
        "--edition",
        choices=("standard", "gumroad"),
        default="standard",
        help="Which edition to build.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_pdf(edition_config(args.edition))


if __name__ == "__main__":
    main()
