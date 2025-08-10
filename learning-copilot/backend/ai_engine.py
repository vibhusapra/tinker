import os
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIEngine:
    def __init__(self, model: str = None, temperature: float = None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key or self.api_key == "your-openai-api-key-here":
            raise ValueError(
                "Please set your OpenAI API key in the .env file.\n"
                "Get your API key from: https://platform.openai.com/api-keys"
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model or os.getenv("MODEL_NAME", "gpt-5-mini")
        self.temperature = temperature or float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict] = None,
        verbosity: str = "medium",
        reasoning_effort: str = "medium"
    ) -> str:
        try:
            params = {
                "model": self.model,
                "messages": messages,
            }
            
            # GPT-5 models only support default temperature (1.0)
            if self.model.startswith("gpt-5"):
                # Don't set temperature for GPT-5 models (uses default of 1.0)
                params["max_completion_tokens"] = max_tokens or self.max_tokens
                params["verbosity"] = verbosity
                params["reasoning_effort"] = reasoning_effort
            elif self.model.startswith("o1"):
                # o1 models also have restrictions
                params["max_completion_tokens"] = max_tokens or self.max_tokens
            else:
                # GPT-4 and earlier models
                params["temperature"] = temperature or self.temperature
                params["max_tokens"] = max_tokens or self.max_tokens
            
            if response_format:
                params["response_format"] = response_format
            
            response = self.client.chat.completions.create(**params)
            return response.choices[0].message.content
        
        except Exception as e:
            # Retry with alternative parameter if it's a parameter error
            if "max_tokens" in str(e) and "max_completion_tokens" in str(e):
                print(f"Retrying with max_completion_tokens parameter...")
                if "max_tokens" in params:
                    params["max_completion_tokens"] = params.pop("max_tokens")
                    try:
                        response = self.client.chat.completions.create(**params)
                        return response.choices[0].message.content
                    except Exception as retry_error:
                        print(f"Retry failed: {str(retry_error)}")
                        raise retry_error
            
            print(f"Error generating completion: {str(e)}")
            raise
    
    def generate_curriculum(
        self,
        input_content: str,
        source_type: str,
        learning_style: str = "project-based"
    ) -> Dict[str, Any]:
        system_prompt = """You are an expert educator following Andrej Karpathy's "learn by doing" philosophy.
        You create structured, project-based curricula that emphasize building over theory.
        Every concept should be learned through implementation and hands-on coding."""
        
        user_prompt = f"""Given the following {source_type} content:

{input_content}

Generate a comprehensive, project-based curriculum that:
1. Breaks concepts into buildable projects (not just theory)
2. Each module includes hands-on coding exercises
3. Projects build on each other progressively
4. Focuses on implementation and practical understanding
5. Includes clear learning outcomes
6. Suggests real-world applications

Return as JSON with this structure:
{{
    "title": "Course title",
    "description": "Brief course description",
    "prerequisites": ["list", "of", "prerequisites"],
    "estimated_duration": "X weeks",
    "modules": [
        {{
            "id": "module_1",
            "title": "Module title",
            "description": "What you'll build",
            "learning_outcomes": ["outcome1", "outcome2"],
            "concepts": ["concept1", "concept2"],
            "projects": [
                {{
                    "name": "Project name",
                    "description": "What you'll build",
                    "difficulty": "beginner/intermediate/advanced",
                    "estimated_time": "X hours",
                    "skills_practiced": ["skill1", "skill2"]
                }}
            ],
            "exercises": [
                {{
                    "type": "coding/debugging/optimization",
                    "description": "Exercise description",
                    "difficulty": "easy/medium/hard"
                }}
            ]
        }}
    ],
    "capstone_project": {{
        "title": "Final project title",
        "description": "Comprehensive project description",
        "requirements": ["req1", "req2"],
        "deliverables": ["deliverable1", "deliverable2"]
    }}
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.generate_completion(
            messages,
            response_format={"type": "json_object"},
            verbosity="high",
            reasoning_effort="high"
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse curriculum", "raw_response": response}
    
    def generate_project_scaffold(
        self,
        topic: str,
        prerequisites: List[str],
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        prompt = f"""Design a hands-on coding project for learning: {topic}

Prerequisites: {', '.join(prerequisites)}
Difficulty: {difficulty}

Create a detailed project specification including:
1. Clear project goal and what the learner will build
2. Step-by-step implementation guide with milestones
3. Starter code template with TODO comments
4. Test cases to verify completion
5. Extension challenges for advanced learners
6. Common pitfalls and debugging tips

Make it engaging, practical, and focused on building real understanding through implementation.

Return as JSON with structure:
{{
    "title": "Project title",
    "goal": "What you'll build",
    "learning_objectives": ["obj1", "obj2"],
    "implementation_steps": [
        {{
            "step": 1,
            "title": "Step title",
            "description": "What to do",
            "code_hint": "Optional code snippet",
            "checkpoint": "How to verify this step works"
        }}
    ],
    "starter_code": "Complete starter code with TODOs",
    "test_cases": [
        {{
            "description": "Test description",
            "input": "Test input",
            "expected_output": "Expected result"
        }}
    ],
    "extensions": ["challenge1", "challenge2"],
    "debugging_tips": ["tip1", "tip2"]
}}"""
        
        messages = [
            {"role": "system", "content": "You are a coding instructor who creates engaging, practical projects."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.generate_completion(
            messages,
            response_format={"type": "json_object"},
            verbosity="high"
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse project scaffold", "raw_response": response}
    
    def get_learning_guidance(
        self,
        question: str,
        context: str,
        current_module: Optional[str] = None,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        system_prompt = """You are a supportive coding instructor following the "learn by doing" philosophy.
        Guide learners through implementation, encourage experimentation, and help debug issues.
        Focus on understanding through building rather than just explaining theory.
        When helping with code, provide hints and guidance rather than complete solutions."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history:
            for msg in chat_history[-5:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        user_message = f"Context: {context}"
        if current_module:
            user_message += f"\nCurrent Module: {current_module}"
        user_message += f"\n\nQuestion: {question}"
        
        messages.append({"role": "user", "content": user_message})
        
        return self.generate_completion(
            messages,
            verbosity="medium",
            reasoning_effort="medium"
        )
    
    def analyze_code_submission(
        self,
        code: str,
        project_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""Analyze this code submission for a learning project:

Project Requirements:
{json.dumps(project_requirements, indent=2)}

Submitted Code:
```
{code}
```

Provide constructive feedback including:
1. Whether requirements are met
2. Code quality and style
3. Potential improvements
4. Bug identification
5. Learning suggestions

Return as JSON:
{{
    "requirements_met": true/false,
    "completeness_score": 0-100,
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "bugs": ["bug1", "bug2"],
    "next_steps": ["suggestion1", "suggestion2"]
}}"""
        
        messages = [
            {"role": "system", "content": "You are a code reviewer focused on learning and improvement."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.generate_completion(
            messages,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse analysis", "raw_response": response}