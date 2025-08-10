import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

from backend.database import Database
from backend.ai_engine import AIEngine
from backend.curriculum import CurriculumGenerator
from utils.github_fetcher import GitHubFetcher
from utils.file_handlers import FileHandler

load_dotenv()

st.set_page_config(
    page_title="Learning Copilot - Learn by Doing",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_services():
    db = Database()
    ai_engine = AIEngine()
    curriculum_gen = CurriculumGenerator(ai_engine)
    github_fetcher = GitHubFetcher()
    file_handler = FileHandler()
    return db, ai_engine, curriculum_gen, github_fetcher, file_handler

db, ai_engine, curriculum_gen, github_fetcher, file_handler = init_services()

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.current_path_id = None
    st.session_state.current_curriculum = None
    st.session_state.chat_history = []
    st.session_state.current_module = None

def main():
    st.title("🚀 Learning Copilot")
    st.markdown("**Learn by doing, inspired by Andrej Karpathy's philosophy**")
    st.markdown("*'What I cannot create, I do not understand'* - Richard Feynman")
    
    with st.sidebar:
        st.header("🎯 Navigation")
        
        if not st.session_state.user_id:
            username = st.text_input("Enter your username to start:", key="username_input")
            if st.button("Start Learning"):
                if username:
                    user_id = db.create_user(username)
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.rerun()
        else:
            st.success(f"Welcome, {st.session_state.username}!")
            
            if st.button("🏠 New Learning Path"):
                st.session_state.current_path_id = None
                st.session_state.current_curriculum = None
                st.session_state.current_module = None
                st.rerun()
            
            st.divider()
            
            st.subheader("📚 Your Learning Paths")
            paths = db.get_learning_paths(st.session_state.user_id)
            
            if paths:
                for path in paths:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(f"📖 {path['title']}", key=f"path_{path['id']}"):
                            st.session_state.current_path_id = path['id']
                            st.session_state.current_curriculum = json.loads(path['curriculum_json'])
                            st.rerun()
                    with col2:
                        st.caption(path['created_at'][:10])
    
    if not st.session_state.user_id:
        st.info("👈 Please enter your username to begin your learning journey!")
        return
    
    if st.session_state.current_path_id:
        display_learning_interface()
    else:
        display_curriculum_creation()

def display_curriculum_creation():
    st.header("🎓 Create Your Learning Path")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Manual Topic", "📄 Upload Syllabus", "🔗 GitHub Repo", "🚀 Quick Start"])
    
    with tab1:
        st.subheader("Enter a topic you want to learn")
        topic = st.text_area(
            "What do you want to learn?",
            placeholder="e.g., 'Build a language model from scratch', 'Web development with React', 'Machine learning fundamentals'",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Your current level:", ["beginner", "intermediate", "advanced"])
        with col2:
            duration = st.selectbox("Preferred duration:", ["2 weeks", "4 weeks", "8 weeks", "12 weeks"])
        
        if st.button("🚀 Generate Curriculum", type="primary"):
            if topic:
                with st.spinner("Creating your personalized curriculum..."):
                    curriculum = curriculum_gen.generate_from_topic(topic, level, duration)
                    
                    if "error" not in curriculum:
                        path_id = db.create_learning_path(
                            st.session_state.user_id,
                            curriculum.get("title", topic),
                            "manual",
                            topic,
                            curriculum
                        )
                        st.session_state.current_path_id = path_id
                        st.session_state.current_curriculum = curriculum
                        st.success("✅ Curriculum created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Error: {curriculum['error']}")
    
    with tab2:
        st.subheader("Upload a course syllabus")
        uploaded_file = st.file_uploader(
            "Choose a file (PDF, TXT, MD)",
            type=['pdf', 'txt', 'md'],
            help="Upload a syllabus or course outline"
        )
        
        if uploaded_file:
            file_result = file_handler.process_uploaded_file(uploaded_file)
            
            if file_result["success"]:
                st.success(f"✅ File processed: {file_result['filename']}")
                
                with st.expander("Preview content"):
                    st.text(file_result["content"][:1000] + "...")
                
                if st.button("🎯 Generate Curriculum from Syllabus", type="primary"):
                    with st.spinner("Analyzing syllabus and creating curriculum..."):
                        structure = file_handler.parse_syllabus_structure(file_result["content"])
                        curriculum = curriculum_gen.generate_from_syllabus(
                            file_result["content"],
                            structure
                        )
                        
                        if "error" not in curriculum:
                            path_id = db.create_learning_path(
                                st.session_state.user_id,
                                curriculum.get("title", "Custom Syllabus"),
                                "syllabus",
                                file_result["content"][:1000],
                                curriculum
                            )
                            st.session_state.current_path_id = path_id
                            st.session_state.current_curriculum = curriculum
                            st.success("✅ Curriculum created from syllabus!")
                            st.rerun()
                        else:
                            st.error(f"Error: {curriculum['error']}")
            else:
                st.error(file_result["error"])
    
    with tab3:
        st.subheader("Learn from a GitHub repository")
        github_url = st.text_input(
            "GitHub Repository URL:",
            placeholder="https://github.com/karpathy/LLM101n"
        )
        
        if github_url:
            if st.button("🔍 Analyze Repository", type="primary"):
                with st.spinner("Fetching and analyzing repository..."):
                    try:
                        repo_analysis = github_fetcher.analyze_repository(github_url)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Language", repo_analysis['language'])
                        with col2:
                            st.metric("Stars", repo_analysis['stars'])
                        with col3:
                            st.metric("Topics", len(repo_analysis['topics']))
                        
                        with st.expander("Repository Structure"):
                            st.json(repo_analysis['structure'])
                        
                        if st.button("🎓 Generate Learning Path", type="primary"):
                            with st.spinner("Creating curriculum from repository..."):
                                curriculum = curriculum_gen.generate_from_github(repo_analysis)
                                
                                if "error" not in curriculum:
                                    path_id = db.create_learning_path(
                                        st.session_state.user_id,
                                        curriculum.get("title", repo_analysis['name']),
                                        "github",
                                        github_url,
                                        curriculum
                                    )
                                    st.session_state.current_path_id = path_id
                                    st.session_state.current_curriculum = curriculum
                                    st.success("✅ Learning path created from repository!")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {curriculum['error']}")
                    
                    except Exception as e:
                        st.error(f"Error analyzing repository: {str(e)}")
    
    with tab4:
        st.subheader("🚀 Quick Start Templates")
        
        templates = {
            "🤖 Build Your Own LLM": "Learn to build language models from scratch, starting with bigrams and progressing to transformers",
            "🌐 Full-Stack Web Dev": "Master web development by building real applications with modern frameworks",
            "📊 Data Science by Doing": "Learn data science through hands-on projects with real datasets",
            "🎮 Game Development": "Create games while learning programming fundamentals",
            "🔧 Systems Programming": "Build low-level tools and understand how computers really work"
        }
        
        for title, description in templates.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{title}**")
                st.caption(description)
            with col2:
                if st.button("Start", key=f"template_{title}"):
                    with st.spinner("Creating curriculum..."):
                        curriculum = curriculum_gen.generate_from_topic(
                            description,
                            "beginner",
                            "4 weeks"
                        )
                        
                        if "error" not in curriculum:
                            path_id = db.create_learning_path(
                                st.session_state.user_id,
                                title,
                                "template",
                                description,
                                curriculum
                            )
                            st.session_state.current_path_id = path_id
                            st.session_state.current_curriculum = curriculum
                            st.success("✅ Template curriculum created!")
                            st.rerun()

def display_learning_interface():
    curriculum = st.session_state.current_curriculum
    
    st.header(f"📚 {curriculum.get('title', 'Learning Path')}")
    st.markdown(curriculum.get('description', ''))
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Curriculum", "💬 Learning Assistant", "📊 Progress", "🛠️ Current Project"])
    
    with tab1:
        display_curriculum_modules()
    
    with tab2:
        display_chat_interface()
    
    with tab3:
        display_progress()
    
    with tab4:
        display_current_project()

def display_curriculum_modules():
    curriculum = st.session_state.current_curriculum
    
    if curriculum.get('prerequisites'):
        with st.expander("📋 Prerequisites"):
            for prereq in curriculum['prerequisites']:
                st.markdown(f"- {prereq}")
    
    st.subheader("🎯 Learning Modules")
    
    modules = curriculum.get('modules', [])
    progress_data = db.get_progress(st.session_state.user_id, st.session_state.current_path_id)
    progress_map = {p['module_id']: p['status'] for p in progress_data}
    
    for idx, module in enumerate(modules):
        module_id = module.get('id', f'module_{idx}')
        status = progress_map.get(module_id, 'not_started')
        
        status_emoji = {
            'not_started': '⭕',
            'in_progress': '🔄',
            'completed': '✅'
        }
        
        with st.expander(f"{status_emoji[status]} Module {idx + 1}: {module['title']}"):
            st.markdown(f"**Description:** {module.get('description', '')}")
            
            if module.get('learning_outcomes'):
                st.markdown("**Learning Outcomes:**")
                for outcome in module['learning_outcomes']:
                    st.markdown(f"- {outcome}")
            
            if module.get('projects'):
                st.markdown("**Projects:**")
                for project in module['projects']:
                    st.markdown(f"- 🔨 **{project['name']}** ({project.get('difficulty', 'intermediate')})")
                    st.caption(f"  {project.get('description', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"Start Module", key=f"start_{module_id}"):
                    st.session_state.current_module = module
                    db.update_progress(
                        st.session_state.user_id,
                        st.session_state.current_path_id,
                        module_id,
                        "in_progress"
                    )
                    st.rerun()
            
            with col2:
                if status == "in_progress":
                    if st.button(f"Mark Complete", key=f"complete_{module_id}"):
                        db.update_progress(
                            st.session_state.user_id,
                            st.session_state.current_path_id,
                            module_id,
                            "completed"
                        )
                        st.success("Module completed! 🎉")
                        st.rerun()
            
            with col3:
                if st.button(f"Generate Project", key=f"project_{module_id}"):
                    with st.spinner("Generating project scaffold..."):
                        project = curriculum_gen.generate_project(module, curriculum)
                        st.session_state.current_module = module
                        st.session_state.current_project = project
                        st.rerun()

def display_chat_interface():
    st.subheader("💬 Learning Assistant")
    st.caption("Ask questions, get hints, and debug your code!")
    
    chat_history = db.get_chat_history(
        st.session_state.user_id,
        st.session_state.current_path_id
    )
    
    for message in chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
    
    if prompt := st.chat_input("Ask a question or paste code for help..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        db.add_chat_message(
            st.session_state.user_id,
            st.session_state.current_path_id,
            "user",
            prompt
        )
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                context = f"Learning: {st.session_state.current_curriculum.get('title', 'Unknown')}"
                if st.session_state.current_module:
                    context += f"\nCurrent Module: {st.session_state.current_module.get('title', 'Unknown')}"
                
                response = ai_engine.get_learning_guidance(
                    prompt,
                    context,
                    st.session_state.current_module.get('title') if st.session_state.current_module else None,
                    chat_history[-5:] if chat_history else None
                )
                
                st.markdown(response)
                
                db.add_chat_message(
                    st.session_state.user_id,
                    st.session_state.current_path_id,
                    "assistant",
                    response
                )

def display_progress():
    st.subheader("📊 Your Progress")
    
    progress_data = db.get_progress(
        st.session_state.user_id,
        st.session_state.current_path_id
    )
    
    if progress_data:
        completed = sum(1 for p in progress_data if p['status'] == 'completed')
        in_progress = sum(1 for p in progress_data if p['status'] == 'in_progress')
        total_modules = len(st.session_state.current_curriculum.get('modules', []))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Completed", f"{completed}/{total_modules}")
        with col2:
            st.metric("In Progress", in_progress)
        with col3:
            completion_rate = (completed / total_modules * 100) if total_modules > 0 else 0
            st.metric("Completion", f"{completion_rate:.0f}%")
        
        st.progress(completion_rate / 100)
        
        st.subheader("📝 Module Status")
        for module in st.session_state.current_curriculum.get('modules', []):
            module_id = module.get('id', '')
            progress = next((p for p in progress_data if p['module_id'] == module_id), None)
            
            if progress:
                status_color = {
                    'completed': 'green',
                    'in_progress': 'orange',
                    'not_started': 'gray'
                }
                
                st.markdown(
                    f":{status_color[progress['status']]}[{module['title']}] - {progress['status'].replace('_', ' ').title()}"
                )
                
                if progress.get('notes'):
                    st.caption(f"Notes: {progress['notes']}")
    else:
        st.info("No progress yet. Start a module to begin tracking!")

def display_current_project():
    if hasattr(st.session_state, 'current_project') and st.session_state.current_project:
        project = st.session_state.current_project
        
        st.subheader(f"🛠️ {project.get('title', 'Current Project')}")
        st.markdown(f"**Goal:** {project.get('goal', '')}")
        
        if project.get('learning_objectives'):
            with st.expander("Learning Objectives"):
                for obj in project['learning_objectives']:
                    st.markdown(f"- {obj}")
        
        if project.get('starter_code'):
            st.subheader("📝 Starter Code")
            st.code(project['starter_code'], language='python')
        
        if project.get('implementation_steps'):
            st.subheader("📋 Implementation Steps")
            for step in project['implementation_steps']:
                with st.expander(f"Step {step['step']}: {step['title']}"):
                    st.markdown(step['description'])
                    if step.get('code_hint'):
                        st.code(step['code_hint'], language='python')
                    if step.get('checkpoint'):
                        st.info(f"✓ Checkpoint: {step['checkpoint']}")
        
        if project.get('test_cases'):
            with st.expander("🧪 Test Cases"):
                for test in project['test_cases']:
                    st.markdown(f"**{test['description']}**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.code(f"Input: {test['input']}", language='python')
                    with col2:
                        st.code(f"Expected: {test['expected_output']}", language='python')
        
        st.subheader("📤 Submit Your Code")
        code_submission = st.text_area(
            "Paste your implementation here:",
            height=300,
            placeholder="# Your code here..."
        )
        
        if st.button("🔍 Analyze Code", type="primary"):
            if code_submission:
                with st.spinner("Analyzing your code..."):
                    analysis = ai_engine.analyze_code_submission(
                        code_submission,
                        project
                    )
                    
                    if analysis.get('requirements_met'):
                        st.success("✅ Great job! Requirements met!")
                    else:
                        st.warning("⚠️ Some requirements need work")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Completeness", f"{analysis.get('completeness_score', 0)}%")
                    
                    if analysis.get('strengths'):
                        st.markdown("**💪 Strengths:**")
                        for strength in analysis['strengths']:
                            st.markdown(f"- {strength}")
                    
                    if analysis.get('improvements'):
                        st.markdown("**📈 Suggested Improvements:**")
                        for improvement in analysis['improvements']:
                            st.markdown(f"- {improvement}")
                    
                    if analysis.get('bugs'):
                        st.markdown("**🐛 Potential Issues:**")
                        for bug in analysis['bugs']:
                            st.markdown(f"- {bug}")
    
    elif st.session_state.current_module:
        st.info("Select 'Generate Project' from a module to create a coding project!")
    else:
        st.info("Select a module to start working on projects!")

if __name__ == "__main__":
    main()