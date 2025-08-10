import os
import re
from typing import Dict, List, Optional
from github import Github
from github.Repository import Repository
from github.ContentFile import ContentFile
import base64

class GitHubFetcher:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GITHUB_ACCESS_TOKEN")
        self.github = Github(self.token) if self.token else Github()
    
    def parse_github_url(self, url: str) -> tuple:
        patterns = [
            r"github\.com/([^/]+)/([^/]+)/?$",
            r"github\.com/([^/]+)/([^/]+)/tree/[^/]+/?(.*)$",
            r"github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)$",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner = match.group(1)
                repo = match.group(2).replace(".git", "")
                path = match.group(3) if len(match.groups()) > 2 else None
                return owner, repo, path
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def get_repository(self, owner: str, repo: str) -> Repository:
        try:
            return self.github.get_repo(f"{owner}/{repo}")
        except Exception as e:
            raise Exception(f"Failed to access repository: {str(e)}")
    
    def get_readme(self, repo: Repository) -> str:
        try:
            readme = repo.get_readme()
            return base64.b64decode(readme.content).decode('utf-8')
        except:
            return "No README found"
    
    def get_file_content(self, repo: Repository, path: str) -> str:
        try:
            file_content = repo.get_contents(path)
            if isinstance(file_content, list):
                return "Path is a directory, not a file"
            return base64.b64decode(file_content.content).decode('utf-8')
        except Exception as e:
            return f"Error fetching file: {str(e)}"
    
    def get_directory_structure(
        self,
        repo: Repository,
        path: str = "",
        max_depth: int = 3,
        current_depth: int = 0
    ) -> Dict:
        if current_depth >= max_depth:
            return {"truncated": True}
        
        structure = {}
        try:
            contents = repo.get_contents(path)
            if not isinstance(contents, list):
                contents = [contents]
            
            for content in contents:
                if content.type == "dir":
                    structure[content.name] = self.get_directory_structure(
                        repo,
                        content.path,
                        max_depth,
                        current_depth + 1
                    )
                else:
                    structure[content.name] = {
                        "type": "file",
                        "size": content.size,
                        "path": content.path
                    }
        except Exception as e:
            structure["error"] = str(e)
        
        return structure
    
    def analyze_repository(self, url: str) -> Dict:
        owner, repo_name, path = self.parse_github_url(url)
        repo = self.get_repository(owner, repo_name)
        
        analysis = {
            "name": repo.name,
            "description": repo.description,
            "url": repo.html_url,
            "language": repo.language,
            "topics": repo.get_topics(),
            "stars": repo.stargazers_count,
            "structure": {},
            "readme": "",
            "key_files": []
        }
        
        analysis["readme"] = self.get_readme(repo)
        
        analysis["structure"] = self.get_directory_structure(repo, max_depth=2)
        
        important_files = [
            "requirements.txt",
            "package.json",
            "setup.py",
            "Makefile",
            ".gitignore",
            "LICENSE"
        ]
        
        for file_name in important_files:
            try:
                content = self.get_file_content(repo, file_name)
                if "Error" not in content:
                    analysis["key_files"].append({
                        "name": file_name,
                        "content": content[:500]
                    })
            except:
                pass
        
        if path:
            specific_content = self.get_file_content(repo, path)
            analysis["specific_path"] = {
                "path": path,
                "content": specific_content
            }
        
        return analysis
    
    def extract_learning_content(self, repo_analysis: Dict) -> str:
        content = f"# Repository: {repo_analysis['name']}\n\n"
        
        if repo_analysis['description']:
            content += f"## Description\n{repo_analysis['description']}\n\n"
        
        if repo_analysis['readme']:
            content += f"## README Content\n{repo_analysis['readme'][:2000]}\n\n"
        
        content += f"## Primary Language: {repo_analysis['language']}\n\n"
        
        if repo_analysis['topics']:
            content += f"## Topics: {', '.join(repo_analysis['topics'])}\n\n"
        
        content += "## Repository Structure\n"
        content += self._format_structure(repo_analysis['structure'])
        
        if repo_analysis['key_files']:
            content += "\n## Key Configuration Files\n"
            for file in repo_analysis['key_files']:
                content += f"\n### {file['name']}\n```\n{file['content']}\n```\n"
        
        return content
    
    def _format_structure(self, structure: Dict, indent: int = 0) -> str:
        result = ""
        for key, value in structure.items():
            if key == "truncated":
                result += "  " * indent + "...(truncated)\n"
            elif isinstance(value, dict):
                if value.get("type") == "file":
                    result += "  " * indent + f"📄 {key}\n"
                else:
                    result += "  " * indent + f"📁 {key}/\n"
                    result += self._format_structure(value, indent + 1)
            else:
                result += "  " * indent + f"{key}\n"
        return result