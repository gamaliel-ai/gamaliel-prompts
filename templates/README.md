# Templates

This directory contains [Jinja2](https://jinja.palletsprojects.com/en/stable/) prompt templates that power all AI interactions in the Gamaliel system. These templates define the structure and content of prompts sent to the AI model, ensuring consistent, theologically sound responses.

## Directory Structure

- `chat_agent/` — Templates for the main Q&A chat interface
  - `instructions.j2` — Core system instructions and theological guardrails
  - `input.j2` — Template for formatting user questions and context
- `home/` — Templates for the home page and initial interactions
  - `instructions.j2` — Instructions for home page AI interactions
  - `input.j2` — Template for home page context and user input
- `suggestions/` — Templates for generating suggested questions
  - `instructions.j2` — Instructions for question suggestion generation
  - `input.j2` — Template for context used in generating suggestions

## Template System

Each template directory contains two main files:

- **`instructions.j2`** — Defines the AI's role, capabilities, and theological boundaries
- **`input.j2`** — Formats the user's input and context for the AI

## Key Features

- **Theological Consistency**: All templates include mandatory theological guardrails
- **Contextual Adaptation**: Templates adapt based on user profiles and theological perspectives
- **Transparency**: All prompt logic is open source and auditable
- **Modularity**: Templates can be customized for different use cases and partners

## Usage

Templates are processed by the Gamaliel system to generate prompts that include:

- User's question or context
- Selected user profile settings
- Chosen theological perspective
- Relevant biblical content and commentary
- System instructions and guardrails

## Customization

Templates can be customized for:

- Different AI models and capabilities
- Partner-specific requirements
- New interaction types
- Enhanced theological frameworks

See the individual template files for detailed examples and configuration options.
