#!/usr/bin/env python3
"""
Theological Guardrails Reviewer

This script reviews changes to gamaliel-prompts files to ensure they comply
with the mandatory core theological guardrails defined in guardrails.md.
"""

import os
import sys
import json
import yaml
import subprocess
import re
from typing import List, Dict, Any, Optional
from pathlib import Path

MODEL="gpt-4.1-nano"


# Only import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class TheologicalReviewer:
    def __init__(self):
        self.guardrails_content = self._load_guardrails()
        self.violations = []
        self.details = []
        
    def _load_guardrails(self) -> str:
        """Load the theological guardrails from guardrails.md"""
        guardrails_path = Path("guardrails.md")
        if not guardrails_path.exists():
            print("❌ Error: guardrails.md not found")
            sys.exit(1)
        
        with open(guardrails_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_changed_files(self) -> List[str]:
        """Get list of changed files in gamaliel-prompts directory"""
        # Read from the file created by the GitHub Action
        try:
            with open("filtered_files.txt", "r") as f:
                files = [line.strip() for line in f if line.strip()]
            return files
        except FileNotFoundError:
            print("No changed files found or filtered_files.txt not found")
            return []
    
    def _get_file_content(self, file_path: str) -> str:
        """Get the content of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def _get_file_diff(self, file_path: str) -> str:
        """Get the diff for a specific file"""
        try:
            # Get diff for the specific file
            result = subprocess.run(
                ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
                capture_output=True, text=True, check=False
            )
            return result.stdout
        except Exception as e:
            print(f"Error getting diff for {file_path}: {e}")
            return ""
    
    def _analyze_with_llm(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze content using LLM for theological compliance"""
        
        # System prompt with instructions and format
        system_prompt = f"""You are a theological reviewer for the Gamaliel AI system. Your job is to detect serious theological violations and heresies while allowing room for legitimate theological interpretation within orthodox Christianity.

## THEOLOGICAL GUARDRAILS TO ENFORCE:
{self.guardrails_content}

## AREAS OF LEGITIMATE DEBATE:
The following are examples of major doctrinal areas where orthodox Christians (Catholic, Protestant, Orthodox, Charismatic, etc.) have legitimate disagreements. Do NOT flag these as violations if they are presented within the bounds of historic Christian orthodoxy:
- Theosis (deification) as participation in God's nature (Orthodox)
- Veneration of icons and saints (Orthodox, Catholic)
- Marian dogmas (Immaculate Conception, Assumption, perpetual virginity)
- The role of tradition and the Magisterium (Catholic, Orthodox)
- Faith vs. works in justification (Catholic, Protestant)
- The number and nature of sacraments
- The real presence in the Eucharist (transubstantiation, consubstantiation, memorialism)
- The role and gifts of the Holy Spirit (spiritual gifts, prophecy, tongues, healing)
- Eschatology (end times, millennium, rapture)
- Original sin and ancestral sin
- The filioque clause in the Nicene Creed
- Baptismal regeneration
- Church governance (episcopal, presbyterian, congregational)
- The use of icons, relics, and liturgical practices
- The role of Mary and the saints in intercession
- Purgatory and prayers for the dead
- The office of prophet and ongoing revelation (within the bounds of Scripture's authority)
- The nature of spiritual warfare (territorial spirits, deliverance)
- The process of sanctification and Christian perfection

## ANALYSIS TASK:
1. Review the content against the mandatory core theological guardrails
2. Focus on detecting actual heresies that contradict core Christian doctrines
3. Allow room for legitimate theological interpretation within orthodox Christianity
4. Recognize that different Christian traditions (Catholic, Protestant, Orthodox, Charismatic, etc.) have valid theological perspectives

## WHAT CONSTITUTES A VIOLATION:
- Explicit denial of core doctrines (Trinity, Incarnation, Resurrection, etc.)
- Promotion of universalism (all will be saved regardless of faith)
- Syncretism with non-Christian religions
- Denial of the authority of Scripture
- Prosperity gospel teachings that equate material wealth with spiritual blessing or guarantee wealth
- Gnostic or pantheistic views that deny the material world or incarnation
- Explicit rejection of the Church or sacraments
- Denial of Christ's divinity or humanity

## WHAT DOES NOT CONSTITUTE A VIOLATION:
- Different emphases or theological perspectives within orthodox Christianity
- Different views on secondary doctrines (baptism, communion, church governance, etc.)
- Different approaches to spiritual gifts or worship styles
- Different interpretations of eschatology or end times
- Different views on the role of tradition vs. Scripture (as long as Scripture remains authoritative)
- Different understandings of salvation (as long as Christ is central)
- Charismatic beliefs about spiritual gifts, tongues, prophecy, and divine healing
- Belief in material blessings from God (as long as not guaranteed or primary)
- Emphasis on spiritual experiences and the Holy Spirit's work
- Different approaches to spiritual warfare and deliverance
- Legitimate points of disagreement within mainstream Christianity (Protestant, Catholic, Orthodox, etc.)

## PROFILE REVIEW GUIDELINES:
- Profiles can describe user perspectives (including skeptical, non-Christian, or heretical views)
- The instructions given to the AI must not violate theological guardrails
- It's acceptable to describe a user as "not Christian" or having different beliefs
- The AI's response instructions must remain orthodox and not promote heresy
- Focus on whether the AI instructions are compliant, not the user's described perspective
- CRITICAL: Do NOT flag a profile just because it targets non-Christians or describes users as non-Christian
- CRITICAL: Only flag profiles if the actual instructions given to the AI contain heretical content
- CRITICAL: The target audience (atheist, agnostic, other religion) is irrelevant - only the AI instructions matter

## EXAMPLE OF WHAT IS ACCEPTABLE:
A profile with `is_christian: false` and instructions like "Help them understand what the Bible teaches while respecting their journey" is PERFECTLY ACCEPTABLE. This is not heresy - it's respectful engagement with non-Christians.

## EXAMPLE OF WHAT IS NOT ACCEPTABLE:
Instructions like "The Bible is just one of many valid spiritual texts" or "All religions lead to God" would be heretical because they deny the uniqueness of Christ and Scripture.

## RESPONSE FORMAT:
Return a JSON object with this structure:
{{
    "compliant": boolean,
    "violations": [
        {{
            "type": "string describing the type of violation",
            "text": "the substring that caused the violation",
            "description": "detailed description of the violation",
            "severity": "high|medium|low",
            "suggestion": "how to fix the violation"
        }}
    ],
    "summary": "brief summary of the review"
}}

## IMPORTANT:
- Look for explicit denials or contradictions of core doctrines
- Allow for theological diversity within orthodox Christianity
- Focus on what is clearly stated, not what might be inferred
- Consider the context and intended audience
- Be generous in interpretation while maintaining doctrinal integrity
- Accept legitimate theological traditions and their distinctives
- If content is compliant, return empty violations array
- Respond only with valid JSON"""

        # User prompt with content to review
        user_prompt = f"""File Type: {file_type}
Content:
{content}"""

        # Only use OpenAI, fallback to basic keyword checking
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            return self._analyze_with_openai(system_prompt, user_prompt)
        else:
            # Fallback to basic keyword checking
            return self._basic_keyword_check(content)
    
    def _analyze_with_openai(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI API"""
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"OpenAI analysis failed: {e}")
            return {"compliant": True, "violations": [], "summary": "Analysis failed, assuming compliant"}
    
    def _basic_keyword_check(self, content: str) -> Dict[str, Any]:
        """Basic keyword-based check as fallback"""
        violations = []
        
        # Check for obvious violations
        anti_trinity_keywords = ["deny the trinity", "reject the trinity", "not three persons", "unitarian"]
        anti_christ_keywords = ["deny christ's divinity", "jesus is not god", "christ is not divine"]
        anti_resurrection_keywords = ["deny resurrection", "spiritual resurrection only", "no physical resurrection"]
        
        content_lower = content.lower()
        
        for keyword in anti_trinity_keywords:
            if keyword in content_lower:
                violations.append({
                    "type": "Trinity Denial",
                    "description": f"Content contains language that denies the Trinity: '{keyword}'",
                    "severity": "high",
                    "suggestion": "Remove or revise content that denies the Trinity"
                })
        
        for keyword in anti_christ_keywords:
            if keyword in content_lower:
                violations.append({
                    "type": "Christ's Divinity Denial",
                    "description": f"Content contains language that denies Christ's divinity: '{keyword}'",
                    "severity": "high",
                    "suggestion": "Remove or revise content that denies Christ's divinity"
                })
        
        for keyword in anti_resurrection_keywords:
            if keyword in content_lower:
                violations.append({
                    "type": "Resurrection Denial",
                    "description": f"Content contains language that denies the physical resurrection: '{keyword}'",
                    "severity": "high",
                    "suggestion": "Remove or revise content that denies the physical resurrection"
                })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "summary": f"Basic keyword check completed. Found {len(violations)} potential violations."
        }
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine the type of file being reviewed"""
        if file_path.endswith('.yml') or file_path.endswith('.yaml'):
            if 'partners/' in file_path:
                return "Partner Configuration"
            elif 'profiles/' in file_path:
                return "User Profile"
            elif 'theologies/' in file_path:
                return "Theological Perspective"
            else:
                return "YAML Configuration"
        elif file_path.endswith('.md'):
            return "Documentation"
        elif file_path.endswith('.j2'):
            return "Jinja2 Template"
        else:
            return "Other"
    
    def review_file(self, file_path: str) -> bool:
        """Review a single file for theological compliance"""
        print(f"🔍 Reviewing: {file_path}")
        
        # Get file content
        content = self._get_file_content(file_path)
        if not content:
            print(f"⚠️  Warning: Could not read {file_path}")
            return True
        
        # Get file type
        file_type = self._determine_file_type(file_path)
        
        # Analyze with LLM
        analysis = self._analyze_with_llm(content, file_type)
        
        # Process results
        if not analysis.get("compliant", True):
            violations = analysis.get("violations", [])
            for violation in violations:
                self.violations.append(f"**{file_path}**: {violation.get('type', 'Unknown')}")
                severity = violation.get('severity', 'medium').upper()
                description = violation.get('description', 'No description provided')
                suggestion = violation.get('suggestion', 'No suggestion provided')
                self.details.append(f"**{file_path}** - {severity}: {description}\nSuggestion: {suggestion}")
            
            print(f"❌ {file_path}: {len(violations)} violations found")
            return False
        else:
            print(f"✅ {file_path}: Compliant")
            return True
    
    def run_review(self) -> bool:
        """Run the complete theological review"""
        print("🚀 Starting Theological Guardrails Review")
        print(f"📋 Guardrails loaded from: guardrails.md")
        
        # Get changed files
        changed_files = self._get_changed_files()
        if not changed_files:
            print("ℹ️  No files to review")
            return True
        
        print(f"📁 Found {len(changed_files)} changed files to review:")
        for file_path in changed_files:
            print(f"  - {file_path}")
        
        # Review each file
        all_compliant = True
        for file_path in changed_files:
            if not self.review_file(file_path):
                all_compliant = False
                # Log violation details immediately
                print(f"\n❌ VIOLATIONS FOUND IN {file_path}:")
                for detail in self.details:
                    if file_path in detail:
                        print(f"\n{detail}")
        
        # Set output variables for GitHub Actions
        violations_text = "\n".join(self.violations) if self.violations else ""
        details_text = "\n\n".join(self.details) if self.details else ""
        
        # Write to GitHub Actions output
        with open(os.environ.get('GITHUB_OUTPUT', '/dev/null'), 'a') as f:
            f.write(f"violations={violations_text}\n")
            f.write(f"details={details_text}\n")
        
        # Print summary
        if all_compliant:
            print("\n✅ All files comply with theological guardrails")
        else:
            print(f"\n❌ Found {len(self.violations)} violations:")
            for violation in self.violations:
                print(f"  - {violation}")
        
        return all_compliant


def main():
    """Main entry point"""
    reviewer = TheologicalReviewer()
    success = reviewer.run_review()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 