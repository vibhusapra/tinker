SYSTEM_PROMPTS = {
    "curriculum_expert": """You are an expert curriculum designer inspired by Andrej Karpathy's teaching philosophy.
Your core principles:
- "What I cannot create, I do not understand" - learning through building
- Every concept must be implemented in code
- Theory serves practice, not the other way around
- Start simple, build complexity gradually
- Projects should be exciting and immediately useful
- Debugging and failure are essential learning tools""",
    
    "project_designer": """You design hands-on coding projects that teach through implementation.
Your projects should:
- Have clear, achievable goals that excite learners
- Build real, working systems (not toy examples)
- Include intentional bugs to teach debugging
- Progressively increase in complexity
- Connect to real-world applications
- Encourage experimentation and modification""",
    
    "learning_coach": """You are a supportive coding mentor who guides through implementation.
Your approach:
- Give hints, not solutions
- Encourage experimentation and "productive failure"
- Celebrate debugging as learning
- Connect code to concepts
- Suggest "what if" modifications
- Build confidence through incremental success"""
}

CURRICULUM_TEMPLATES = {
    "llm_course": """Create a curriculum for building Language Models from scratch.
Start with character-level models and progress to transformer architecture.
Each module should result in a working implementation that students can experiment with.
Include projects like:
- Bigram language model
- N-gram model with smoothing
- Simple RNN
- LSTM text generator
- Attention mechanism
- Mini-GPT implementation""",
    
    "web_dev": """Design a full-stack web development curriculum.
Focus on building real applications from day one.
Progress from static sites to dynamic applications.
Include projects like:
- Personal portfolio
- Interactive todo app
- Real-time chat application
- Social media clone
- E-commerce platform
- API development""",
    
    "data_science": """Create a data science curriculum through practical projects.
Emphasize understanding through implementation.
Build custom implementations before using libraries.
Include projects like:
- Data parser from scratch
- Statistical analyzer
- Visualization engine
- ML algorithm implementations
- Neural network from numpy
- Real dataset analysis"""
}

def get_curriculum_prompt(topic: str, level: str = "beginner") -> str:
    base_prompt = f"""Design a comprehensive curriculum for: {topic}
    
Learning Level: {level}
Philosophy: Learn by building, inspired by Karpathy's approach

Structure Required:
1. Clear learning path with 5-8 modules
2. Each module has 2-3 hands-on projects
3. Projects build upon previous work
4. Include debugging challenges
5. Real-world applications
6. Estimated time commitments

For each module provide:
- Title and core concept
- What you'll build (specific project)
- Key skills practiced
- Common mistakes to learn from
- Extension challenges

Make it exciting and immediately practical!"""
    
    return base_prompt

def get_project_prompt(concept: str, prerequisites: list) -> str:
    prereq_str = ", ".join(prerequisites) if prerequisites else "None"
    
    return f"""Design a hands-on project to learn: {concept}

Prerequisites: {prereq_str}

Create an engaging project that:
1. Teaches {concept} through building something real
2. Starts with working code that needs modification
3. Includes intentional bugs to fix
4. Has clear checkpoints for progress
5. Suggests experiments and variations

Structure:
- Project goal (what they'll build)
- Starter code with TODOs
- Step-by-step implementation guide
- Test cases for validation
- Common errors and fixes
- "What if" experiments
- Extension challenges

Make it fun and immediately useful!"""

def get_explanation_prompt(code: str, error: str = None) -> str:
    if error:
        return f"""A learner encountered this error while coding:

Code:
```
{code}
```

Error:
```
{error}
```

Provide guidance that:
1. Helps them understand WHY the error occurred
2. Guides them to find the solution (don't give it directly)
3. Suggests debugging strategies
4. Explains the underlying concept
5. Prevents similar errors in future

Be encouraging and treat errors as learning opportunities!"""
    
    else:
        return f"""Explain this code in the context of learning by doing:

Code:
```
{code}
```

Provide:
1. What the code does (in plain language)
2. Key concepts demonstrated
3. Potential modifications to explore
4. Common mistakes to avoid
5. Real-world applications

Focus on building intuition through experimentation!"""

def get_review_prompt(code: str, requirements: str) -> str:
    return f"""Review this learning project submission:

Requirements:
{requirements}

Submitted Code:
```
{code}
```

Provide constructive feedback:
1. What works well (be specific)
2. Requirements completion status
3. Code quality observations
4. Bugs or potential issues
5. Improvement suggestions
6. Next learning steps

Be encouraging while pushing for excellence!"""