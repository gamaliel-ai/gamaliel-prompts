# Theological Guidelines

This directory contains theological perspective files that shape how Gamaliel interprets Scripture and responds to user questions. Each theology represents a specific Christian tradition or denominational perspective while operating within mandatory core guidelines.

## What is a Theology?

A theology file is a YAML configuration that defines:

- **Doctrinal distinctives** of a specific Christian tradition
- **Interpretive principles** for understanding Scripture
- **Response guidelines** for addressing theological questions
- **Unique emphases** that differentiate one tradition from others

Theologies work alongside the mandatory core guidelines to provide nuanced, tradition-specific biblical interpretation while maintaining essential Christian orthodoxy.

## How Theologies Work

### Hierarchy of Guidelines

1. **Mandatory Core Guidelines** (always in effect)

   - Core Christian Doctrines (Nicene Creed)
   - Authority of Scripture
   - Guidelines Against Common Errors
   - See [guidelines.md](../guidelines.md) for the definitive list of mandatory core guidelines. This text is copied verbatim into the system instructions.

2. **Specific Theology Guidelines** (user-selectable)
   - Denominational distinctives
   - Tradition-specific interpretations
   - Unique doctrinal emphases
   - The default theology is defined in [default.yml](default.yml), but users can select a different theology from the list of available theologies.

### Integration with the System

- **Instructions Template**: Theologies are injected into [templates/chat_agent/instructions.j2](../templates/chat_agent/instructions.j2).
- **User Selection**: Users who self-identify as Christian can choose a theology that matches their tradition. Non-Christian users are assigned the [default](./default.yml) (ecumenical) theology.
- **Core Protection**: No theology can override or conflict with the mandatory core [guidelines](../guidelines.md).

## Creating a New Theology

### File Structure

```yaml
name: 'Theology Name'
description: 'Brief description of the theological perspective'
instructions: |
  Detailed theological instructions that include:

  1. Core Distinctives
     - Key doctrinal beliefs unique to this tradition
     - Interpretive principles
     - Theological emphases

  2. Response Guidelines
     - How to approach Scripture from this perspective
     - Language and terminology preferences
     - Areas of emphasis or caution

  3. Additional Doctrines
     - Secondary beliefs that define this tradition
     - Practical applications
     - Worship and practice considerations
```

### Ground Rules for New Theologies

#### ✅ What to Include

1. **Denominational Distinctives**

   - Unique doctrinal beliefs that define the tradition
   - Interpretive approaches specific to the tradition
   - Theological emphases and priorities

2. **Response Guidelines**

   - How to present biblical truth from this perspective
   - Language preferences and terminology
   - Areas of emphasis or special focus

3. **Practical Applications**
   - How doctrine applies to daily life
   - Worship and practice considerations
   - Community and church life

#### Not necessary for inclusion

1. **Core Christian Doctrines** (already covered by mandatory guidelines)

   - Trinity, Incarnation, Gospel, Church, Future
   - Authority of Scripture
   - Basic Nicene Creed content

2. **Common Errors** (already covered by mandatory guidelines)

   - Denial of Trinity, Christ's divinity, etc.
   - Heresies and false teachings

3. **Contradictory Content**
   - Anything that conflicts with mandatory core guidelines
   - Denial of essential Christian doctrines

### Quality Standards

1. **Theological Accuracy**

   - Faithfully represent the tradition's actual beliefs
   - Use accurate terminology and concepts
   - Avoid caricatures or misrepresentations

2. **Clarity and Precision**
   - Clear, specific instructions
   - Well-organized structure
   - Accessible language

## Editing Existing Theologies

### Guidelines for Changes

1. **Maintain Tradition Fidelity**

   - Changes should reflect actual denominational teaching
   - Consult official denominational documents
   - Preserve the tradition's unique voice

2. **Avoid Redundancy**

   - Don't repeat content covered by mandatory guidelines
   - Focus on distinctive elements
   - Keep content concise and focused

3. **Test for Conflicts**
   - Ensure changes don't conflict with core guidelines
   - Maintain compatibility with the system
   - Verify theological consistency

### Review Process

1. **Theological Review**

   - Verify accuracy with denominational sources
   - Check for theological consistency
   - Ensure respectful representation

2. **Technical Review**

   - Validate YAML syntax
   - Test integration with the system
   - Verify no conflicts with core guidelines

3. **Community Review**
   - Open for community feedback
   - Address concerns respectfully
   - Iterate based on input

## Mandatory Core Guidelines

All theologies must operate within the mandatory core guidelines. **For the complete, authoritative list, see [../guidelines.md](../guidelines.md).**

These guidelines include:

- Core Christian Doctrines (Nicene Creed)
- Authority of Scripture
- Guidelines Against Common Errors

No theology can override these essential boundaries.

## Contributing

As the project matures, we will welcome contributions to improve theological perspectives. See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.

---

_The goal is to provide accurate, respectful representation of Christian traditions while maintaining the essential unity of the faith._
