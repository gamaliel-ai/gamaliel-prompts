# Gamaliel Prompts & Transparency

**Your Questions. Biblical Answers. Open Source.**

Gamaliel Prompts is the open-source heart of the [Gamaliel.ai](https://gamaliel.ai) project—a free, Open, AI-powered Bible study companion. This repository contains all the prompt templates, user profiles, and theological guidelines that power the biblical reasoning and transparency of the Gamaliel system.

> **⚠️ Note: We are in Early Development**
>
> This project is currently under early development. We expect many changes as we refine our approach, prompt engineering, and theological frameworks. We will begin actively engaging with contributors, accepting PRs, and expanding community involvement once the project matures and stabilizes. Thank you for your patience and understanding during this research phase.

## Vision & Mission

Gamaliel exists to make deep, trustworthy Bible study accessible to everyone—whether you're a curious seeker, a lifelong believer, or anywhere in between. Inspired by the mentorship of the biblical Gamaliel to the Apostle Paul, our goal is to provide clear, scripturally-rooted answers to your questions, with complete transparency about how those answers are generated.

## What Makes Gamaliel Different?

- **Completely Anonymous**: No login, no signup, no tracking—just open and ask.
- **100% Bible-Based**: Every answer is rooted in Scripture, with clear theological boundaries.
- **Tailored to You**: Profiles adapt responses to your spiritual background and needs.
- **Free & Open Source**: No paywalls, no hidden fees. All prompt logic is open for review and improvement.
- **Radical Transparency**: Every AI response is auditable, with full prompt and context disclosure.

## Theological Foundation

Gamaliel operates within clear theological guidelines rooted in historic Christian orthodoxy. Our system is built on the authority of Scripture and core Christian doctrines shared by Nicene-affirming traditions.

These guidelines ensure that Gamaliel provides biblically faithful responses while respecting the diversity of Christian traditions. See our [theological guidelines](theologies/) for specific denominational perspectives and [guardrails.md](guardrails.md) for the complete list of mandatory core doctrines.

## Why Transparency?

Just as open source builds trust in software, we believe open prompts and theological guidelines build trust in AI-powered biblical study. All system instructions, prompt templates, and theological perspectives are public, so that scholars, theologians, and the community can audit, improve, and verify the system's biblical fidelity and theological soundness. In addition, users will be able to audit any question they ask in Gamaliel to see the precise input, tool results, output, and model used to generate their answer.

## Repository Structure

Gamaliel prompts are customized and composed from various sources, all
of which are provided in this open source repository:

- `templates/` — [Jinja](https://jinja.palletsprojects.com/en/stable/) prompt templates that are used to generate instructions (system prompts) and input (user prompts) for the the Gamaliel agents that power the system. See [templates/README.md](templates/README.md) for details.
- `profiles/` — User profile YAMLs that shape the AI's tone, depth, and approach for different audiences. See [profiles/README.md](profiles/README.md) for details.
- `theologies/` — Theological guidelines (YAML) for denominational and doctrinal perspectives. See [theologies/README.md](theologies/README.md) for details.
- `cli/` — Command-line interface tool for testing and validating prompt templates, profiles, and theologies locally. This tool provides a simplified reference implementation that mimics the production system's behavior, allowing developers to test changes submitting a PR. See [cli/README.md](cli/README.md) for detailed usage instructions.

## Contributing

As the project matures, we will welcome contributions from biblical scholars, theologians, AI researchers, and anyone passionate about trustworthy, transparent Bible study. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to:

- Improve or add prompt templates
- Expand user profiles for new audiences
- Refine or add theological guidelines
- Suggest new features or documentation

## License

These prompts and configuation files are licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Bible Copyright Notices

We are in discussions with license holders of several popular Bible
translations and intend to include them in a later release. We also intend to support other languages in the future. For now, we are using the World English Bible (WEB) and the King James Version (KJV) as both are in the public domain.

### World English Bible (WEB)

https://ebible.org/eng-web/webfaq.htm

### King James Version (KJV)

https://www.cambridge.org/gb/bibles/about/rights-and-permissions/rights-and-permissions-kjv

> Scripture quotations from The Authorized (King James) Version. Rights in the Authorized Version in the United Kingdom are vested in the Crown. Reproduced by permission of the Crown’s patentee, Cambridge University Press

## Learn More

- [About Gamaliel](https://gamaliel.ai/about)
- [Why Gameliel?](https://gamaliel.ai/read/ISA/40?verse=8)

---
