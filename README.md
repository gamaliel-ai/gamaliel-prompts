# Gamaliel Prompts & Transparency

**Your Questions. Biblical Answers. Open Source.**

Gamaliel Prompts is the open-source heart of the [Gamaliel.ai](https://gamaliel.ai) project—a next-generation, AI-powered Bible study companion. This repository contains all the prompt templates, user profiles, and theological guardrails that power the biblical reasoning and transparency of the Gamaliel system.

## Vision & Mission

Gamaliel exists to make deep, trustworthy Bible study accessible to everyone—whether you're a curious seeker, a lifelong believer, or anywhere in between. Inspired by the mentorship of the biblical Gamaliel to the Apostle Paul, our goal is to provide clear, scripturally-rooted answers to your questions, with complete transparency about how those answers are generated.

## Theological Foundation

Gamaliel operates within clear theological guardrails rooted in historic Christian orthodoxy. Our system is built on two foundational principles:

### Core Christian Doctrines (Nicene Creed)
All responses must affirm the essential beliefs shared by Nicene-affirming Christian traditions:
- **The Trinity**: One God in three persons—Father, Son, and Holy Spirit
- **The Incarnation**: Jesus Christ as fully God and fully man
- **The Gospel**: Christ's death, resurrection, and ascension for our salvation
- **The Church**: One holy, catholic (universal), and apostolic Church
- **The Future**: Resurrection of the dead and life everlasting

### Authority of Scripture
- **Divine Inspiration**: The Bible is the inspired, authoritative, and trustworthy word of God
- **Scriptural Sufficiency**: All doctrine and teaching must be consistent with Scripture
- **Historical Context**: Scripture is interpreted in light of the historic Christian faith

These guardrails ensure that Gamaliel provides biblically faithful responses while respecting the diversity of Christian traditions. See our [theological guardrails](theologies/) for specific denominational perspectives.

**📋 Complete Theological Guardrails**: See [guardrails.md](guardrails.md) for the complete, authoritative list of mandatory core theological guardrails that all responses must follow.

## Why Transparency?

Just as open source builds trust in software, we believe open prompts and theological guardrails build trust in AI-powered biblical study. All system instructions, prompt templates, and theological perspectives are public, so that scholars, theologians, and the community can audit, improve, and verify the system's biblical fidelity and theological soundness. See our [AI Transparency Strategy](../docs/ai-transparency-strategy.md) for more details.

## Repository Structure

- `templates/` — Jinja2 prompt templates for all system interactions (Q&A, suggestions, translation, etc.)
- `profiles/` — User profile YAMLs that shape the AI's tone, depth, and approach for different audiences
- `theologies/` — Theological guardrails (YAML) for denominational and doctrinal perspectives

## What Makes Gamaliel Different?
- **Completely Anonymous**: No login, no signup, no tracking—just open and ask.
- **100% Bible-Based**: Every answer is rooted in Scripture, with clear theological boundaries.
- **Tailored to You**: Profiles adapt responses to your spiritual background and needs.
- **Free & Open Source**: No paywalls, no hidden fees. All prompt logic is open for review and improvement.
- **Radical Transparency**: Every AI response is auditable, with full prompt and context disclosure.

## Contributing

We welcome contributions from biblical scholars, theologians, AI researchers, and anyone passionate about trustworthy, transparent Bible study. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to:
- Improve or add prompt templates
- Expand user profiles for new audiences
- Refine or add theological guardrails
- Suggest new features or documentation

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Learn More
- [About Gamaliel](../client/src/components/About.jsx)
- [AI Transparency Strategy](../docs/ai-transparency-strategy.md)
- [Gamaliel.ai Website](https://gamaliel.ai)

---

*Gamaliel: Helping you discover, understand, and grow in faith—openly, honestly, and together.*
