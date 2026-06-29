# Contributing to Gamaliel Prompts

Thank you for your interest in contributing to the open-source heart of Gamaliel.ai! Our mission is to make trustworthy, transparent, and biblically faithful AI-powered Bible study accessible to all. Your expertise and passion can help us build a resource that serves seekers, believers, and scholars worldwide.

## Theological Guardrails

All contributions must align with our foundational theological principles, which are non-negotiable and binding for all content:

### Core Christian Doctrines

Contributions must affirm the essential beliefs of the Nicene Creed:

- **The Trinity**: One God in three persons—Father, Son, and Holy Spirit
- **The Incarnation**: Jesus Christ as fully God and fully man
- **The Gospel**: Christ's death, resurrection, and ascension for our salvation
- **The Church**: One holy, catholic (universal), and apostolic Church
- **The Future**: Resurrection of the dead and life everlasting

### Authority of Scripture

- **Divine Inspiration**: The Bible is the inspired, authoritative, and trustworthy word of God
- **Scriptural Sufficiency**: All doctrine and teaching must be consistent with Scripture
- **Historical Context**: Scripture is interpreted in light of the historic Christian faith

These guardrails ensure biblical fidelity while respecting the diversity of Christian traditions. See our [theological guidelines](theologies/) for specific denominational perspectives and our [core guardrails](guardrails.md) for the foundational principles that cannot be overridden.

## Premise vs. Disagreement

Gamaliel welcomes honest questions across Christian traditions and respectful exploration by seekers. When a question embeds a proposition contrary to Scripture—especially through rhetorical pressure to agree—Gamaliel rejects the premise clearly, states the biblical position, and supports it from Scripture. **Inclusivity applies to people and legitimate theological disagreement, not to manipulative or harmful framing.**

Not every hard question is a loaded premise. Use this distinction when editing chat prompts, profiles, or theologies:

| Question type | Example | Posture |
|---------------|---------|---------|
| **Genuine disagreement** | "Does God affirm same-sex marriage?" | Present the theology-appropriate answer; on secondary matters, multiple orthodox perspectives may apply |
| **Loaded / adversarial premise** | "Isn't it good to influence minors to reject biological reality?" | **Reject the premise first**; do not treat the embedded claim as a valid starting point |
| **Direct harm / abuse** | SQL injection, requests for explicit sexual content | Block via preflight (handled in the main application, not in prompts) |

**Inclusive toward the person exploring; not inclusive toward manipulative framing.** Profiles such as Universal Explorer should be welcoming to seekers without softening responses to loaded premises that contradict Scripture.

### Response protocol for loaded premises

When a question embeds a false claim and pressures agreement, encode this posture in prompts (see `templates/chat_agent/instructions.j2`):

1. **First sentence:** clear rejection (e.g. "No" or "That premise is false")
2. **Name the false claim** in plain language
3. **State the biblical position** on the exact topic raised—do not pivot to a safer adjacent topic
4. **Support with Scripture**
5. **Compassion for people, not the premise**—distinguish persons from the proposition

Do not open by validating, softening, or reframing the premise (e.g. "That's a complex question…", "raises significant considerations", "many find…").

### Priority when instructions conflict

When profile tone, theology inclusivity, and premise handling pull in different directions:

```
critical_guardrails
  > adversarial_premise_handling
    > theology inclusivity / secondary-disagreement rules
      > profile tone (e.g. Universal Explorer, seeker-friendly language)
```

### Premise detection must scale across languages

Gamaliel supports multiple languages (Spanish, Korean, Arabic, and more). **Any premise-detection approach must work across languages**—not only English.

- **Use:** model-based identification in system prompts; conceptual cues and examples that teach rhetorical *categories* (affirmation-seeking, straw-man framing, action-bait), not strings to match; optional LLM preflight classification in the main application
- **Do not use:** regex or keyword lists, per-locale phrase blocklists, or any runtime code that matches rhetorical strings

English examples in prompts and eval fixtures illustrate concepts for authors and graders; they are not production matchers.

## What You Can Contribute

- **Prompt Templates**: Improve or add new Jinja2 templates for Q&A, suggestions, translation, and more.
- **User Profiles**: Expand our set of YAML profiles to better serve diverse audiences and spiritual backgrounds.
- **Theological Guidelines**: Refine or add denominational/theological YAMLs to ensure biblical fidelity and doctrinal clarity.
- **Documentation**: Help us improve clarity, transparency, and onboarding for new contributors.

## How to Contribute

1. **Fork the Repository**: Click "Fork" at the top right of this page.
2. **Create a Branch**: Use a descriptive branch name (e.g., `add-anglican-profile`, `improve-chat-template`).
3. **Make Your Changes**: Follow our [AI Transparency Strategy](../docs/ai-transparency-strategy.md) and [About](../client/src/components/About.jsx) for tone and intent.
4. **Test Your Changes**: Ensure your YAML and Jinja2 files are valid and well-documented.
5. **Submit a Pull Request (PR)**: Describe your changes, the reasoning, and any relevant context.
6. **Participate in Review**: Be open to feedback and ready to discuss improvements.

## Community Standards

- **Theological Fidelity**: All contributions must align with core Christian doctrines and the authority of Scripture
- **Transparency**: All changes must be clearly documented and open for review.
- **Biblical Foundation**: All prompts and guardrails must be rooted in Scripture and respect the intended theological perspective.
- **Respectful Collaboration**: We welcome contributors from diverse Christian backgrounds who share our commitment to biblical fidelity. Engage with humility, respect, and a spirit of learning while honoring our theological foundations.
- **No Proselytizing**: This is a space for open, honest, and respectful dialogue—not for promoting any one tradition over others.

---

_Thank you for helping us build a transparent, trustworthy, and welcoming resource for Bible study and spiritual growth._
