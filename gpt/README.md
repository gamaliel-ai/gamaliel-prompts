# Gamaliel GPT System Instructions

This directory contains the system instructions for building a custom OpenAI GPT that integrates with Gamaliel's scripture search API.

## Purpose

These instructions enable developers to create a ChatGPT-powered biblical assistant that:
- Uses Gamaliel's public scripture search API to find relevant Bible chapters
- Provides biblically-grounded answers with proper theological guardrails
- Maintains consistency with Gamaliel's core theological principles

## What's Included

- **`system_instructions.md`** — Complete system prompt for configuring a custom GPT in OpenAI's GPT builder

## Usage

1. Copy the contents of `system_instructions.md`
2. In OpenAI's GPT builder, go to **Configure → Instructions**
3. Paste the system instructions
4. Configure the `searchScripture` action using the OpenAPI spec (see the main documentation)

## Key Features

- **Mandatory theological guardrails** — Ensures responses align with core Christian doctrines
- **Scripture search integration** — Uses Gamaliel's semantic search to find the 5 most relevant chapters
- **Response guidelines** — Structured approach to citing Scripture and providing answers
- **Query optimization** — Guidance on transforming user questions into effective search queries

## Transparency

Like all Gamaliel prompts, these instructions are published openly for transparency and auditability. Anyone can review, verify, and understand exactly how the GPT is configured to provide biblical answers.

## Related Documentation

For complete setup instructions, including the OpenAPI action configuration, see:
- [`docs/openai-gpt-scripture-search.md`](../../docs/openai-gpt-scripture-search.md) in the main repository

## License

These instructions are part of the Gamaliel Prompts project and are licensed under the MIT License.
