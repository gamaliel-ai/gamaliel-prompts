# Theological Guardrails Review System

This directory contains the automated theological review system for the Gamaliel Prompts repository. The system ensures that all changes to the repository comply with the mandatory core theological guardrails defined in `guardrails.md`.

## Overview

The theological review system automatically:
1. **Detects changes** to files in the `gamaliel-prompts` repository
2. **Analyzes content** using LLM-based review against theological guardrails
3. **Blocks violations** by preventing PRs from being merged if they contain heretical content
4. **Provides feedback** with detailed explanations of violations and suggestions for fixes

## How It Works

### 1. Trigger
The review runs automatically on:
- **Pull Requests**: When PRs are opened, updated, or reopened
- **Direct Pushes**: When code is pushed directly to the main branch

### 2. File Detection
The system identifies changed files in the `gamaliel-prompts` directory:
- Partner configurations (`partners/*.yml`)
- User profiles (`profiles/*.yml`)
- Theological perspectives (`theologies/*.yml`)
- Templates (`templates/**/*.j2`)
- Documentation (`*.md`)

### 3. LLM Analysis
Each changed file is analyzed using:
- **Primary**: OpenAI GPT-4 or Anthropic Claude (if API keys are available)
- **Fallback**: Basic keyword-based checking for obvious violations

### 4. Guardrails Enforcement
The system enforces the mandatory core theological guardrails:
- **Core Christian Doctrines** (Nicene Creed)
- **Authority of Scripture**
- **Guardrails Against Common Errors**

### 5. Results
- **Compliant**: PR can be merged
- **Violations**: PR is blocked with detailed feedback

## Setup Instructions

### 1. Repository Secrets
Add these secrets to your repository settings:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Note**: At least one API key is required for full LLM analysis. If neither is available, the system will use basic keyword checking.

### 2. File Structure
Ensure your repository has this structure:
```
gamaliel-prompts/
├── .github/
│   ├── workflows/
│   │   └── theological-review.yml
│   └── scripts/
│       └── theological_reviewer.py
├── guardrails.md
├── partners/
├── profiles/
├── theologies/
└── templates/
```

### 3. Permissions
The workflow requires these permissions:
- `contents: read` - To read repository files
- `pull-requests: write` - To comment on PRs
- `actions: read` - To run the workflow

## Configuration

### Workflow Configuration
The workflow can be customized in `.github/workflows/theological-review.yml`:

```yaml
# Review specific file types
- name: Get changed files
  run: |
    # Customize file filtering here
    grep "^gamaliel-prompts/" changed_files.txt > filtered_files.txt
```

### Review Script Configuration
The review script can be customized in `.github/scripts/theological_reviewer.py`:

```python
# Add custom file types
def _determine_file_type(self, file_path: str) -> str:
    if 'custom/' in file_path:
        return "Custom Configuration"
    # ... existing logic
```

## Example Workflow

### Successful Review
```
🚀 Starting Theological Guardrails Review
📋 Guardrails loaded from: guardrails.md
📁 Found 2 changed files to review:
  - gamaliel-prompts/partners/new-partner.yml
  - gamaliel-prompts/profiles/new-profile.yml
🔍 Reviewing: gamaliel-prompts/partners/new-partner.yml
✅ gamaliel-prompts/partners/new-partner.yml: Compliant
🔍 Reviewing: gamaliel-prompts/profiles/new-profile.yml
✅ gamaliel-prompts/profiles/new-profile.yml: Compliant

✅ All files comply with theological guardrails
```

### Failed Review
```
🚀 Starting Theological Guardrails Review
📋 Guardrails loaded from: guardrails.md
📁 Found 1 changed files to review:
  - gamaliel-prompts/partners/problematic-partner.yml
🔍 Reviewing: gamaliel-prompts/partners/problematic-partner.yml
❌ gamaliel-prompts/partners/problematic-partner.yml: 1 violations found

❌ Found 1 violations:
  - **gamaliel-prompts/partners/problematic-partner.yml**: Trinity Denial
```

## Violation Types

The system detects various types of theological violations:

### High Severity
- **Trinity Denial**: Rejecting the three persons of God
- **Christ's Divinity Denial**: Denying Jesus is fully God
- **Resurrection Denial**: Denying the physical resurrection
- **Scripture Authority Denial**: Rejecting biblical authority

### Medium Severity
- **Universalist Claims**: Suggesting all will be saved regardless of faith
- **Syncretism**: Mixing Christianity with other religions
- **Moral Relativism**: Denying objective moral truth

### Low Severity
- **Denominational Disputes**: Secondary theological differences
- **Style Issues**: Tone or presentation concerns

## Troubleshooting

### Common Issues

1. **"guardrails.md not found"**
   - Ensure `guardrails.md` exists in the repository root
   - Check file permissions and encoding

2. **"No API keys available"**
   - Add API keys to repository secrets
   - System will fall back to basic keyword checking

3. **"Analysis failed"**
   - Check API key validity and quotas
   - Review network connectivity
   - Check LLM service status

### Debug Mode
To enable debug output, add this to the workflow:
```yaml
- name: Review theological content
  run: |
    python .github/scripts/theological_reviewer.py
  env:
    DEBUG: "true"
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Contributing

### Adding New Violation Types
Edit `.github/scripts/theological_reviewer.py`:

```python
def _basic_keyword_check(self, content: str) -> Dict[str, Any]:
    # Add new keywords
    new_violation_keywords = ["new heretical phrase"]
    
    for keyword in new_violation_keywords:
        if keyword in content_lower:
            violations.append({
                "type": "New Violation Type",
                "description": f"Content contains: '{keyword}'",
                "severity": "high",
                "suggestion": "Remove or revise this content"
            })
```

### Customizing LLM Prompts
Modify the prompt in `_analyze_with_llm()`:

```python
prompt = f"""
# Add custom instructions here
{self.guardrails_content}
# ... rest of prompt
"""
```

## Security Considerations

1. **API Key Security**: Never commit API keys to the repository
2. **Content Privacy**: LLM providers may log content for analysis
3. **Rate Limiting**: Be aware of API rate limits and costs
4. **Fallback Security**: Basic keyword checking provides backup protection

## Support

For issues with the theological review system:
1. Check the workflow logs in GitHub Actions
2. Review the troubleshooting section above
3. Open an issue in the repository
4. Contact the maintainers for theological questions

---

*This system helps maintain the theological integrity of the Gamaliel AI system while enabling open collaboration.* 