"""
Simplified agent implementation for the Gamaliel Prompts CLI tool.
Based on existing chat_agent.py but simplified for CLI usage.
"""

import json
import openai
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, Template

from .config import Config
from .tools import SCRIPTURE_TOOLS, execute_tool


class SimpleAgent:
    """Simplified agent for CLI usage."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = openai.OpenAI(api_key=config.get("llm.api_key"))
        self.model_name = config.get("llm.model", "gpt-4o-mini")
        self.max_tokens = config.get("llm.max_tokens", 1000)
        
        # Load profiles and theologies
        self.profiles = self._load_profiles()
        self.theologies = self._load_theologies()
        
        # Setup Jinja2 environment for templates
        self.template_env = self._setup_template_env()
    
    def _setup_template_env(self) -> Environment:
        """Setup Jinja2 environment for template rendering."""
        # Look for templates in the gamaliel-prompts directory
        template_paths = [
            Path.cwd() / "templates",  # Current working directory
            Path(__file__).parent.parent / "templates",  # Relative to CLI directory
            Path.cwd().parent / "templates",  # Parent directory
        ]
        
        # Find the first valid template path
        valid_paths = []
        for path in template_paths:
            if path.exists():
                valid_paths.append(str(path.resolve()))
        
        if not valid_paths:
            # Fallback to current directory
            valid_paths = ["."]
            print("Warning: No template paths found, using current directory")
        
        return Environment(
            loader=FileSystemLoader(valid_paths),
            autoescape=True
        )
    
    def _load_profiles(self) -> Dict[str, Any]:
        """Load user profiles from YAML files."""
        profiles = {}
        # Look for profiles in the project root directory
        profile_paths = [
            Path.cwd() / "profiles",  # Current working directory
            Path(__file__).parent.parent / "profiles",  # Relative to CLI directory
            Path.cwd().parent / "profiles",  # Parent directory
        ]
        
        for profile_dir in profile_paths:
            if profile_dir.exists():
                for profile_file in profile_dir.glob("*.yml"):
                    try:
                        with open(profile_file, 'r') as f:
                            profile_data = yaml.safe_load(f)
                            if profile_data:
                                # Use filename without extension as key, or slug if available
                                key = profile_data.get('slug', profile_file.stem)
                                profiles[key] = profile_data
                    except Exception as e:
                        print(f"Warning: Could not load profile {profile_file}: {e}")
                break  # Use first valid profile directory found
        
        return profiles
    
    def _load_theologies(self) -> Dict[str, Any]:
        """Load theology guidelines from YAML files."""
        theologies = {}
        # Look for theologies in the project root directory
        theology_paths = [
            Path.cwd() / "theologies",  # Current working directory
            Path(__file__).parent.parent / "theologies",  # Relative to CLI directory
            Path.cwd().parent / "theologies",  # Parent directory
        ]
        
        for theology_dir in theology_paths:
            if theology_dir.exists():
                for theology_file in theology_dir.glob("*.yml"):
                    try:
                        with open(theology_file, 'r') as f:
                            theology_data = yaml.safe_load(f)
                            if theology_data:
                                # Use filename without extension as key, or slug if available
                                key = theology_data.get('slug', theology_file.stem)
                                theologies[key] = theology_data
                    except Exception as e:
                        print(f"Warning: Could not load theology {theology_file}: {e}")
                break  # Use first valid theology directory found
        
        return theologies
    
    def render_prompt(self, template_name: str, **kwargs) -> str:
        """Render a prompt template with given parameters."""
        try:
            template = self.template_env.get_template(f"{template_name}/instructions.j2")
            return template.render(**kwargs)
        except Exception as e:
            print(f"Warning: Could not render template {template_name}: {e}")
            # Return a simple fallback
            return f"Please respond to: {kwargs.get('input', 'the user question')}"
    
    def chat(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
             profile: Optional[str] = None, theology: Optional[str] = None, 
             verbose: bool = False) -> str:
        """Simple chat without streaming."""
        
        # Get profile and theology data
        profile_data = self.profiles.get(profile) if profile else {}
        theology_data = self.theologies.get(theology) if theology else {}
        
        # Prepare the system message
        system_message = self._build_system_message(profile_data, theology_data)
        
        # Prepare the user message using the input.j2 template
        user_message = self._build_user_message(prompt, context, profile_data)
        
        # Print verbose information if requested
        if verbose:
            print("=== INSTRUCTIONS (System Message) ===")
            print(system_message)
            print("=== INPUT (User Message) ===")
            print(user_message)
            print("=== END INPUT===\n")
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                tools=SCRIPTURE_TOOLS,
                tool_choice="auto",
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            # Handle tool calls if any
            message = response.choices[0].message
            if message.tool_calls:
                return self._handle_tool_calls(message, prompt, verbose)
            else:
                return message.content or "No response generated"
                
        except Exception as e:
            return f"Error calling OpenAI API: {str(e)}"
    
    def _build_system_message(self, profile_data: Dict[str, Any], 
                             theology_data: Dict[str, Any]) -> str:
        """Build the system message from profile and theology data."""
        system_parts = []
        
        # Add core theological guardrails (always included)
        guardrails_paths = [
            Path(__file__).parent.parent / "guardrails.md",  # Relative to CLI directory
            Path.cwd() / "guardrails.md",  # Current working directory
            Path.cwd().parent / "guardrails.md",  # Parent directory
        ]
        
        guardrails_loaded = False
        for guardrails_path in guardrails_paths:
            if guardrails_path.exists():
                try:
                    with open(guardrails_path, 'r') as f:
                        guardrails_content = f.read()
                        system_parts.append(f"Core Theological Guardrails:\n{guardrails_content}")
                        guardrails_loaded = True
                        break
                except Exception as e:
                    continue
        
        if not guardrails_loaded:
            print(f"Warning: Could not load guardrails from any path")
        
        # Add theology guidelines
        if theology_data and 'instructions' in theology_data:
            system_parts.append(f"Theology Guidelines: {theology_data['instructions']}")
        
        # Add profile characteristics
        if profile_data and 'instructions' in profile_data:
            system_parts.append(f"User Profile: {profile_data['instructions']}")
        
        # Add default system message
        system_parts.append(
            "You are a helpful AI assistant for biblical study and theological discussion. "
            "Use the available tools to provide accurate scripture references and insights. "
            "Be respectful, accurate, and helpful in your responses."
        )
        
        return "\n\n".join(system_parts)
    
    def _build_user_message(self, prompt: str, context: Optional[Dict[str, Any]], 
                           profile_data: Optional[Dict[str, Any]] = None) -> str:
        """Build the user message using the input.j2 template."""
        try:
            # Prepare template context data
            template_context = {
                "prompt": prompt
            }
            
            # Add context data if provided
            if context:
                # Handle book/chapter context for scripture
                if "book" in context and "chapter" in context:
                    # Fetch the actual scripture content
                    book = context["book"]
                    chapter = context["chapter"]
                    
                    # Get scripture content using the tools (no verse parameter)
                    scripture_result = execute_tool("get_scripture", book=book, chapter=chapter)
                    chapter_content = ""
                    
                    if "error" not in scripture_result:
                        chapter_content = scripture_result.get("text", "")
                    
                    template_context.update({
                        "bible_id": "bsb",
                        "book": book,
                        "chapter": chapter,
                        "chapter_content": chapter_content
                    })
                
                # Add other context fields
                for key, value in context.items():
                    if key not in ["book", "chapter", "chapter_content"]:
                        template_context[key] = value
            
            # Add profile data if available
            if profile_data:
                template_context["profile"] = profile_data
            
            # Render the input.j2 template
            template = self.template_env.get_template("chat_agent/input.j2")
            return template.render(**template_context)
            
        except Exception as e:
            print(f"Warning: Could not render input template: {e}")
            # Fallback to simple formatting
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                return f"Context:\n{context_str}\n\nQuestion: {prompt}"
            else:
                return prompt
    
    def _handle_tool_calls(self, message, original_prompt: str, verbose: bool = False) -> str:
        """Handle tool calls and generate final response."""
        tool_results = []
        
        if verbose:
            print("=== TOOL QUERIES ===")
        
        for tool_call in message.tool_calls:
            try:
                # Parse tool call arguments
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if verbose:
                    print(f"=== Tool: {function_name} ===")
                    print(json.dumps(arguments, indent=2))
                
                # Execute the tool
                result = execute_tool(function_name, **arguments)
                tool_results.append({
                    "tool": function_name,
                    "result": result
                })
                
                if verbose:
                    print(f"=== Result ===")
                    print(f"{json.dumps(result, indent=2)}\n")
                
            except Exception as e:
                tool_results.append({
                    "tool": tool_call.function.name,
                    "result": {"error": f"Tool execution failed: {str(e)}"}
                })
                
                if verbose:
                    print(f"Error: {str(e)}\n")
        
        if verbose:
            print("=== END TOOL QUERIES ===\n")
        
        # Generate final response with tool results
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Use the tool results to answer the user's question."},
                    {"role": "user", "content": f"Question: {original_prompt}\n\nTool Results: {json.dumps(tool_results, indent=2)}"},
                    {"role": "assistant", "content": message.content or ""}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "No response generated"
            
        except Exception as e:
            return f"Error generating final response: {str(e)}"
    
    def test_template(self, template_name: str, **kwargs) -> str:
        """Test a template by rendering it without calling the LLM."""
        return self.render_prompt(template_name, **kwargs)
