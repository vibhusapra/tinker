import json
from typing import Dict, List, Any, Optional
from backend.ai_engine import AIEngine
from prompts.curriculum_gen import get_curriculum_prompt, get_project_prompt

class CurriculumGenerator:
    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
    
    def generate_from_topic(
        self,
        topic: str,
        level: str = "beginner",
        duration: str = "4 weeks"
    ) -> Dict[str, Any]:
        prompt = get_curriculum_prompt(topic, level)
        curriculum = self.ai_engine.generate_curriculum(
            input_content=topic,
            source_type="topic",
            learning_style="project-based"
        )
        
        if "error" not in curriculum:
            curriculum["generated_from"] = "topic"
            curriculum["input_topic"] = topic
            curriculum["level"] = level
        
        return curriculum
    
    def generate_from_syllabus(
        self,
        syllabus_content: str,
        extracted_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        enhanced_content = f"""Syllabus Analysis:
Topics: {', '.join(extracted_structure.get('topics', [])[:10])}
Prerequisites: {', '.join(extracted_structure.get('prerequisites', [])[:5])}
Learning Outcomes: {', '.join(extracted_structure.get('learning_outcomes', [])[:5])}

Raw Content:
{syllabus_content[:3000]}"""
        
        curriculum = self.ai_engine.generate_curriculum(
            input_content=enhanced_content,
            source_type="syllabus",
            learning_style="project-based"
        )
        
        if "error" not in curriculum:
            curriculum["generated_from"] = "syllabus"
            curriculum["syllabus_structure"] = extracted_structure
        
        return curriculum
    
    def generate_from_github(
        self,
        repo_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        learning_content = self._extract_learning_topics(repo_analysis)
        
        curriculum = self.ai_engine.generate_curriculum(
            input_content=learning_content,
            source_type="github_repository",
            learning_style="project-based"
        )
        
        if "error" not in curriculum:
            curriculum["generated_from"] = "github"
            curriculum["repository"] = {
                "name": repo_analysis["name"],
                "url": repo_analysis["url"],
                "language": repo_analysis["language"]
            }
        
        return curriculum
    
    def generate_project(
        self,
        module: Dict[str, Any],
        curriculum_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        prerequisites = []
        
        for idx, mod in enumerate(curriculum_context.get("modules", [])):
            if mod["id"] == module["id"]:
                break
            prerequisites.extend(mod.get("concepts", []))
        
        project = self.ai_engine.generate_project_scaffold(
            topic=module["title"],
            prerequisites=prerequisites[:5],
            difficulty=self._determine_difficulty(module, curriculum_context)
        )
        
        return project
    
    def adapt_curriculum(
        self,
        curriculum: Dict[str, Any],
        user_progress: List[Dict[str, Any]],
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        completed_modules = [p["module_id"] for p in user_progress if p["status"] == "completed"]
        in_progress = [p["module_id"] for p in user_progress if p["status"] == "in_progress"]
        
        adaptation_context = f"""Current Curriculum: {curriculum['title']}
Completed Modules: {', '.join(completed_modules)}
In Progress: {', '.join(in_progress)}
User Feedback: {user_feedback or 'None'}"""
        
        system_prompt = """You are an adaptive learning system that personalizes curricula based on progress."""
        
        user_prompt = f"""{adaptation_context}

Suggest adaptations:
1. Should any modules be simplified or expanded?
2. Are there missing topics based on progress?
3. Should the pace be adjusted?
4. What additional projects would help?

Return as JSON with structure:
{{
    "recommendations": ["rec1", "rec2"],
    "pace_adjustment": "faster/slower/maintain",
    "additional_projects": [{{project specs}}],
    "module_modifications": [{{module changes}}]
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.ai_engine.generate_completion(
            messages,
            response_format={"type": "json_object"}
        )
        
        try:
            adaptations = json.loads(response)
            return {
                "original_curriculum": curriculum,
                "adaptations": adaptations,
                "based_on_progress": len(completed_modules)
            }
        except:
            return {"error": "Failed to generate adaptations"}
    
    def _extract_learning_topics(self, repo_analysis: Dict[str, Any]) -> str:
        content = f"""Repository: {repo_analysis['name']}
Description: {repo_analysis.get('description', 'N/A')}
Language: {repo_analysis.get('language', 'Unknown')}
Topics: {', '.join(repo_analysis.get('topics', []))}

README Excerpt:
{repo_analysis.get('readme', '')[:2000]}

Structure Overview:
{self._format_structure_summary(repo_analysis.get('structure', {}))}
"""
        return content
    
    def _format_structure_summary(self, structure: Dict, max_items: int = 20) -> str:
        summary = []
        count = 0
        
        def traverse(d, path=""):
            nonlocal count
            if count >= max_items:
                return
            
            for key, value in d.items():
                if count >= max_items:
                    break
                
                current_path = f"{path}/{key}" if path else key
                
                if isinstance(value, dict) and value.get("type") == "file":
                    summary.append(f"- {current_path}")
                    count += 1
                elif isinstance(value, dict):
                    summary.append(f"- {current_path}/")
                    count += 1
                    traverse(value, current_path)
        
        traverse(structure)
        return "\n".join(summary)
    
    def _determine_difficulty(
        self,
        module: Dict[str, Any],
        curriculum: Dict[str, Any]
    ) -> str:
        module_index = 0
        for idx, mod in enumerate(curriculum.get("modules", [])):
            if mod["id"] == module["id"]:
                module_index = idx
                break
        
        total_modules = len(curriculum.get("modules", []))
        
        if module_index < total_modules * 0.33:
            return "beginner"
        elif module_index < total_modules * 0.66:
            return "intermediate"
        else:
            return "advanced"