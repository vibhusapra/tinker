import streamlit as st
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random

from backend.database import Database
from backend.ai_engine import AIEngine
from backend.curriculum import CurriculumGenerator
from utils.github_fetcher import GitHubFetcher
from utils.file_handlers import FileHandler
from components.karpathy_wisdom import (
    show_philosophy_banner,
    show_principle_cards,
    show_learning_mantra,
    show_build_pipeline,
    get_socratic_prompt,
    show_experiment_card,
    show_error_celebration,
    show_build_progress,
    show_one_variable_tracker,
    get_karpathy_mode_prompt,
    KARPATHY_PRINCIPLES
)
from components.experiment_journal import ExperimentJournal
from components.tiny_wins import TinyWinsTracker

load_dotenv()

# Page config
st.set_page_config(
    page_title="🔨 Build to Understand - Karpathy Learning",
    page_icon="🔨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS (using minimal, education-friendly style)
css_path = os.path.join(os.path.dirname(__file__), 'static', 'style_minimal.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    try:
        db = Database()
        ai_engine = AIEngine()
        curriculum_gen = CurriculumGenerator(ai_engine)
        github_fetcher = GitHubFetcher()
        file_handler = FileHandler()
        return db, ai_engine, curriculum_gen, github_fetcher, file_handler
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Initialization Error: {str(e)}")
        st.stop()

db, ai_engine, curriculum_gen, github_fetcher, file_handler = init_services()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.current_path_id = None
    st.session_state.current_curriculum = None
    st.session_state.chat_history = []
    st.session_state.current_module = None
    st.session_state.learning_mode = "socratic"
    st.session_state.experiment_journal = ExperimentJournal()
    st.session_state.tiny_wins = TinyWinsTracker()
    st.session_state.current_variable = None
    st.session_state.session_start = datetime.now()
    st.session_state.sixty_min_timer = None

def main():
    # Hero Section with Karpathy Philosophy
    display_hero_section()
    
    # Sidebar with navigation and user management
    with st.sidebar:
        display_sidebar()
    
    # Main content area
    if not st.session_state.user_id:
        display_welcome_screen()
    elif st.session_state.current_path_id:
        display_learning_interface()
    else:
        display_path_creation()

def display_hero_section():
    """Display the hero section with Karpathy philosophy"""
    # Header with animated philosophy quote
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align: center; padding: 1rem;'>
                <h1 style='font-family: monospace; color: #10b981;'>
                    🔨 Build to Understand
                </h1>
                <p style='font-family: monospace; font-size: 1.1em; color: #94a3b8;'>
                    A Karpathy-inspired learning copilot
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Rotating philosophy banner
    show_philosophy_banner()
    
    # Learning mode selector with visual feedback
    st.markdown("### 🎯 Choose Your Learning Mode")
    cols = st.columns(5)
    
    modes = [
        ("🤔", "Socratic", "socratic", "Questions only, no answers"),
        ("🏗️", "From Scratch", "from_scratch", "Build from first principles"),
        ("⚡", "Tight Loop", "tight_loop", "60-min focused sprints"),
        ("📊", "Instrument", "instrument_everything", "Measure everything"),
        ("🧪", "Ablation", "ablation_mode", "Remove to understand"),
    ]
    
    for idx, (icon, name, key, desc) in enumerate(modes):
        with cols[idx]:
            if st.button(
                f"{icon}\n{name}",
                key=f"mode_{key}",
                help=desc,
                use_container_width=True,
                type="primary" if st.session_state.learning_mode == key else "secondary"
            ):
                st.session_state.learning_mode = key
                st.success(f"Switched to {name} mode: {desc}")
                st.rerun()
    
    # Current mode indicator
    current_mode = next((m for m in modes if m[2] == st.session_state.learning_mode), modes[0])
    st.info(f"**Current Mode:** {current_mode[1]} - {current_mode[3]}")

def display_sidebar():
    """Display sidebar with navigation and stats"""
    st.header("🧭 Navigation")
    
    # User management
    if not st.session_state.user_id:
        st.markdown("### 👤 Start Your Journey")
        username = st.text_input("Choose your builder name:", key="username_input")
        if st.button("🚀 Begin Building", type="primary"):
            if username:
                user_id = db.create_user(username)
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
    else:
        # User stats dashboard
        st.success(f"🔨 Builder: **{st.session_state.username}**")
        
        # Session timer
        session_duration = datetime.now() - st.session_state.session_start
        st.metric("Session Time", f"{session_duration.seconds // 60} min")
        
        # Quick stats
        col1, col2 = st.columns(2)
        with col1:
            total_wins = len(st.session_state.tiny_wins.get_recent_wins(100))
            st.metric("🏆 Tiny Wins", total_wins)
        with col2:
            experiments = len(st.session_state.experiment_journal.get_experiments(100))
            st.metric("🧪 Experiments", experiments)
        
        st.divider()
        
        # Navigation buttons
        if st.button("🏠 New Learning Path", use_container_width=True):
            st.session_state.current_path_id = None
            st.session_state.current_curriculum = None
            st.session_state.current_module = None
            st.rerun()
        
        if st.button("📊 View Progress", use_container_width=True):
            st.session_state.view_mode = "progress"
            st.rerun()
        
        if st.button("🧪 Experiment Journal", use_container_width=True):
            st.session_state.view_mode = "journal"
            st.rerun()
        
        st.divider()
        
        # Learning paths
        st.subheader("📚 Your Builds")
        paths = db.get_learning_paths(st.session_state.user_id)
        
        if paths:
            for path in paths[:5]:  # Show only recent 5
                if st.button(
                    f"📦 {path['title'][:25]}...",
                    key=f"path_{path['id']}",
                    use_container_width=True
                ):
                    st.session_state.current_path_id = path['id']
                    st.session_state.current_curriculum = json.loads(path['curriculum_json'])
                    st.rerun()
        else:
            st.info("No builds yet. Start your first one!")
        
        # Daily mantra
        st.divider()
        show_learning_mantra()

def display_welcome_screen():
    """Display welcome screen for new users"""
    st.markdown(
        """
        <div style='text-align: center; padding: 3rem;'>
            <h2 style='color: #10b981;'>Welcome to the Karpathy Way of Learning</h2>
            <p style='font-size: 1.2em; color: #94a3b8;'>
                Where every lesson starts with code that runs.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Core principles grid
    st.markdown("### 🎯 Core Principles We Follow")
    principles = list(KARPATHY_PRINCIPLES.items())[:6]
    show_principle_cards(principles)
    
    # Build pipeline visualization
    st.markdown("### 🔄 The Build Pipeline")
    show_build_pipeline()
    
    # Call to action
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem;'>
            <p style='font-size: 1.3em; color: #f59e0b;'>
                👈 Enter your name in the sidebar to start building!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_path_creation():
    """Display learning path creation with Karpathy philosophy"""
    st.header("🏗️ Start a New Build")
    
    # Karpathy quote for inspiration
    quote = random.choice([
        "Start with the smallest thing that could possibly work.",
        "Build a toy version in 50 lines before reading any docs.",
        "Make it work for one example before generalizing.",
        "Every abstraction must be earned through understanding.",
    ])
    st.markdown(f"> 💭 *\"{quote}\"*")
    
    # Quick start options
    st.markdown("### 🚀 Quick Builds (Start in 60 seconds)")
    
    quick_builds = {
        "🤖 Tiny GPT": "Build a 100-line GPT from scratch",
        "🧮 Backprop": "Implement backpropagation with just numpy",
        "🎮 RL Agent": "Train a agent to play a simple game",
        "🔢 Tokenizer": "Build a byte-pair encoding tokenizer",
        "📊 Autograd": "Create automatic differentiation from scratch",
    }
    
    cols = st.columns(3)
    for idx, (title, desc) in enumerate(quick_builds.items()):
        with cols[idx % 3]:
            if st.button(title, key=f"quick_{idx}", use_container_width=True):
                with st.spinner("🔨 Building curriculum..."):
                    curriculum = curriculum_gen.generate_from_topic(desc, "beginner", "1 week")
                    if "error" not in curriculum:
                        path_id = db.create_learning_path(
                            st.session_state.user_id,
                            title,
                            "quick_build",
                            desc,
                            curriculum
                        )
                        st.session_state.current_path_id = path_id
                        st.session_state.current_curriculum = curriculum
                        # Log a tiny win for starting
                        st.session_state.tiny_wins.add_win("first_run", "Started a new build!")
                        st.success("✅ Build plan created! Let's start coding!")
                        st.rerun()
            st.caption(desc)
    
    st.divider()
    
    # Custom build section
    st.markdown("### 🎯 Custom Build")
    
    tabs = st.tabs(["📝 From Scratch", "📄 From Syllabus", "🔗 From GitHub", "🧪 LLM101n Path"])
    
    with tabs[0]:
        display_scratch_build()
    
    with tabs[1]:
        display_syllabus_build()
    
    with tabs[2]:
        display_github_build()
    
    with tabs[3]:
        display_llm101n_path()

def display_scratch_build():
    """Create curriculum from scratch with Karpathy principles"""
    st.markdown("#### Build Something Small and Real")
    
    # Guided topic input
    topic = st.text_area(
        "What do you want to build?",
        placeholder="Examples:\n- A neural network that learns XOR\n- A regex engine in 200 lines\n- A tiny compiler for arithmetic\n- A gradient descent visualizer",
        height=100
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        complexity = st.selectbox(
            "Starting complexity:",
            ["toy (10 lines)", "minimal (50 lines)", "small (200 lines)"]
        )
    with col2:
        time_bound = st.selectbox(
            "Time to first run:",
            ["30 min", "60 min", "2 hours", "1 day"]
        )
    with col3:
        approach = st.selectbox(
            "Learning approach:",
            ["overfit-first", "from-scratch", "instrument-heavy", "ablation-study"]
        )
    
    if st.button("🔨 Generate Build Plan", type="primary", use_container_width=True):
        if topic:
            with st.spinner("Creating your build plan..."):
                # Add Karpathy-specific context
                enhanced_topic = f"{topic}\nApproach: {approach}\nComplexity: {complexity}\nTime bound: {time_bound}"
                curriculum = curriculum_gen.generate_from_topic(enhanced_topic, "beginner", time_bound)
                
                if "error" not in curriculum:
                    path_id = db.create_learning_path(
                        st.session_state.user_id,
                        f"Build: {topic[:50]}",
                        "scratch",
                        enhanced_topic,
                        curriculum
                    )
                    st.session_state.current_path_id = path_id
                    st.session_state.current_curriculum = curriculum
                    st.success("✅ Build plan ready! Let's start with the tiniest version.")
                    st.rerun()

def display_syllabus_build():
    """Create curriculum from syllabus"""
    st.markdown("#### Transform a Syllabus into Builds")
    
    uploaded_file = st.file_uploader(
        "Upload syllabus (PDF, TXT, MD):",
        type=['pdf', 'txt', 'md'],
        help="We'll extract topics and create hands-on projects for each"
    )
    
    if uploaded_file:
        file_result = file_handler.process_uploaded_file(uploaded_file)
        
        if file_result["success"]:
            st.success(f"✅ Processed: {file_result['filename']}")
            
            with st.expander("Preview extracted content"):
                st.text(file_result["content"][:1000] + "...")
            
            if st.button("🔨 Convert to Build Projects", type="primary", use_container_width=True):
                with st.spinner("Transforming into buildable projects..."):
                    structure = file_handler.parse_syllabus_structure(file_result["content"])
                    curriculum = curriculum_gen.generate_from_syllabus(
                        file_result["content"],
                        structure
                    )
                    
                    if "error" not in curriculum:
                        path_id = db.create_learning_path(
                            st.session_state.user_id,
                            f"Syllabus: {uploaded_file.name[:30]}",
                            "syllabus",
                            file_result["content"][:1000],
                            curriculum
                        )
                        st.session_state.current_path_id = path_id
                        st.session_state.current_curriculum = curriculum
                        st.success("✅ Converted to build projects!")
                        st.rerun()

def display_github_build():
    """Create curriculum from GitHub repo"""
    st.markdown("#### Learn by Rebuilding a Project")
    
    github_url = st.text_input(
        "GitHub Repository URL:",
        placeholder="https://github.com/karpathy/nanoGPT"
    )
    
    if github_url:
        if st.button("🔍 Analyze & Create Build Plan", type="primary", use_container_width=True):
            with st.spinner("Analyzing repository structure..."):
                try:
                    repo_analysis = github_fetcher.analyze_repository(github_url)
                    
                    # Show repo stats
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Language", repo_analysis['language'])
                    with col2:
                        st.metric("Stars", f"{repo_analysis['stars']:,}")
                    with col3:
                        st.metric("Files", len(repo_analysis.get('structure', {})))
                    
                    # Generate curriculum
                    with st.spinner("Creating rebuild plan..."):
                        curriculum = curriculum_gen.generate_from_github(repo_analysis)
                        
                        if "error" not in curriculum:
                            path_id = db.create_learning_path(
                                st.session_state.user_id,
                                f"Rebuild: {repo_analysis['name']}",
                                "github",
                                github_url,
                                curriculum
                            )
                            st.session_state.current_path_id = path_id
                            st.session_state.current_curriculum = curriculum
                            st.success("✅ Rebuild plan created!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def display_llm101n_path():
    """Display the LLM101n learning path"""
    st.markdown("#### Follow Karpathy's LLM101n Path")
    
    st.markdown(
        """
        Build a Storyteller AI from absolute scratch:
        
        1. **Tokenizer** → `tokenizer.py` + round-trip test
        2. **Tiny Transformer** → `gpt_tiny.py` with forward pass
        3. **Training Loop** → `train.py` + loss curves
        4. **Sampling** → `sample.py` + perplexity check
        5. **Optimization** → Ablation studies and scaling
        
        Each step produces working code you can run and modify.
        """
    )
    
    if st.button("🚀 Start LLM101n Journey", type="primary", use_container_width=True):
        with st.spinner("Creating LLM101n curriculum..."):
            llm_topic = """
            Build a Language Model from scratch following Karpathy's approach:
            1. Start with character-level tokenization
            2. Implement bigram model first
            3. Add self-attention
            4. Build transformer block
            5. Stack into GPT architecture
            Each step must be <100 lines and runnable.
            """
            
            curriculum = curriculum_gen.generate_from_topic(llm_topic, "intermediate", "2 weeks")
            
            if "error" not in curriculum:
                path_id = db.create_learning_path(
                    st.session_state.user_id,
                    "LLM101n: Build a Storyteller",
                    "llm101n",
                    llm_topic,
                    curriculum
                )
                st.session_state.current_path_id = path_id
                st.session_state.current_curriculum = curriculum
                st.success("✅ LLM101n path created! Let's build!")
                st.rerun()

def display_learning_interface():
    """Main learning interface with Karpathy philosophy"""
    curriculum = st.session_state.current_curriculum
    
    # Header with progress
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.header(f"🔨 {curriculum.get('title', 'Current Build')}")
    with col2:
        # 60-minute timer if in tight loop mode
        if st.session_state.learning_mode == "tight_loop":
            if st.session_state.sixty_min_timer is None:
                st.session_state.sixty_min_timer = datetime.now()
            
            elapsed = (datetime.now() - st.session_state.sixty_min_timer).seconds
            remaining = max(0, 3600 - elapsed)
            st.metric("⏱️ Time Left", f"{remaining // 60}:{remaining % 60:02d}")
    with col3:
        # Quick win button
        if st.button("🎯 Log Win", help="Record a tiny achievement"):
            st.session_state.tiny_wins.add_win("artifact", "Made progress!")
            st.balloons()
    
    # Tabs for different views
    tabs = st.tabs([
        "🔨 Build",
        "🧪 Experiment",
        "💬 Debug",
        "📊 Instrument",
        "🏆 Progress",
        "📝 Journal"
    ])
    
    with tabs[0]:
        display_build_view(curriculum)
    
    with tabs[1]:
        display_experiment_view()
    
    with tabs[2]:
        display_debug_view()
    
    with tabs[3]:
        display_instrument_view()
    
    with tabs[4]:
        display_progress_view()
    
    with tabs[5]:
        st.session_state.experiment_journal.display_journal()

def display_build_view(curriculum):
    """Display the build interface"""
    # Current module progress
    modules = curriculum.get('modules', [])
    progress_data = db.get_progress(st.session_state.user_id, st.session_state.current_path_id)
    progress_map = {p['module_id']: p['status'] for p in progress_data}
    
    # Build pipeline progress
    st.markdown("### 🔄 Build Pipeline")
    pipeline_items = []
    for idx, module in enumerate(modules[:5]):  # Show first 5
        module_id = module.get('id', f'module_{idx}')
        status = progress_map.get(module_id, 'pending')
        pipeline_items.append({
            'label': module['title'][:30],
            'status': status
        })
    
    show_build_progress(pipeline_items)
    
    # Current module details
    st.markdown("### 📦 Current Build")
    
    for idx, module in enumerate(modules):
        module_id = module.get('id', f'module_{idx}')
        status = progress_map.get(module_id, 'pending')
        
        with st.expander(
            f"{'✅' if status == 'completed' else '🔨'} {module['title']}",
            expanded=(status == 'in_progress')
        ):
            st.markdown(f"**Goal:** {module.get('description', '')}")
            
            # Projects for this module
            if module.get('projects'):
                st.markdown("**Artifacts to Build:**")
                for project in module['projects']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"- 📦 {project['name']}")
                        st.caption(project.get('description', ''))
                    with col2:
                        if st.button("Start", key=f"start_proj_{module_id}_{project['name']}"):
                            # Start experiment for this project
                            hypothesis = f"Build {project['name']} in {project.get('estimated_time', '60 min')}"
                            st.session_state.experiment_journal.start_experiment(hypothesis)
                            st.session_state.current_module = module
                            db.update_progress(
                                st.session_state.user_id,
                                st.session_state.current_path_id,
                                module_id,
                                "in_progress"
                            )
                            st.rerun()
            
            # Module actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if status != "in_progress":
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
                    if st.button(f"Complete", key=f"complete_{module_id}"):
                        db.update_progress(
                            st.session_state.user_id,
                            st.session_state.current_path_id,
                            module_id,
                            "completed"
                        )
                        st.session_state.tiny_wins.add_win("artifact", f"Completed {module['title']}")
                        st.success("Module completed! 🎉")
                        st.rerun()
            
            with col3:
                if st.button(f"Generate Scaffold", key=f"scaffold_{module_id}"):
                    with st.spinner("Generating minimal starter code..."):
                        project = curriculum_gen.generate_project(module, curriculum)
                        st.session_state.current_project = project
                        st.code(project.get('starter_code', '# Starter code'), language='python')

def display_experiment_view():
    """Display experiment tracking interface"""
    st.markdown("### 🧪 Experiment Tracking")
    
    # One variable tracker
    st.markdown("#### 🎯 One Variable at a Time")
    col1, col2, col3 = st.columns(3)
    with col1:
        var_name = st.text_input("Variable:", placeholder="learning_rate")
    with col2:
        old_val = st.text_input("Old Value:", placeholder="0.001")
    with col3:
        new_val = st.text_input("New Value:", placeholder="0.01")
    
    if st.button("Track Change", use_container_width=True):
        if var_name and old_val and new_val:
            show_one_variable_tracker(var_name, old_val, new_val)
            st.session_state.current_variable = (var_name, old_val, new_val)
    
    # Quick experiment templates
    st.markdown("#### 🚀 Quick Experiments")
    
    experiments = [
        ("Overfit Single Example", "Make loss go to zero on one training example"),
        ("Ablation Test", "Remove component X and measure impact"),
        ("Scaling Test", "10x the data, measure time and accuracy"),
        ("Instrumentation", "Add logging to every forward pass"),
    ]
    
    cols = st.columns(2)
    for idx, (name, desc) in enumerate(experiments):
        with cols[idx % 2]:
            if st.button(name, key=f"exp_{idx}", use_container_width=True):
                st.session_state.experiment_journal.start_experiment(desc)
                st.success(f"Started: {name}")
                st.rerun()

def display_debug_view():
    """Display debugging interface with Karpathy philosophy"""
    st.markdown("### 🐛 Debug by Understanding")
    
    # Debugging mantra
    from prompts.karpathy_mode import get_debugging_mantra
    st.info(f"🔍 **Debugging Mantra:** {get_debugging_mantra()}")
    
    # Error celebration
    st.markdown("#### 🎯 Current Error (Learning Opportunity)")
    
    error_input = st.text_area(
        "Paste your error:",
        placeholder="TypeError: unsupported operand type(s) for +: 'int' and 'str'",
        height=100
    )
    
    if error_input:
        # Celebrate the error
        learning_points = [
            "This error reveals a type mismatch in your data flow",
            "The error points to exactly where your assumption broke",
            "This is teaching you about Python's type system",
            "You've discovered an edge case to handle",
        ]
        show_error_celebration(error_input, random.choice(learning_points))
        
        # Socratic debugging questions
        st.markdown("#### 🤔 Debug by Questioning")
        from prompts.karpathy_mode import get_socratic_response
        question = get_socratic_response(error_input)
        st.markdown(f"> {question}")
    
    # Debug checklist
    st.markdown("#### ✅ Debug Checklist")
    debug_steps = [
        "Print shapes of all tensors",
        "Check one example manually",
        "Verify data types match",
        "Plot intermediate values",
        "Simplify until it works",
        "Binary search with comments",
    ]
    
    for step in debug_steps:
        st.checkbox(step, key=f"debug_{step}")

def display_instrument_view():
    """Display instrumentation and measurement interface"""
    st.markdown("### 📊 Instrument Everything")
    
    st.markdown(
        """
        #### What to Measure
        - **Losses**: Training, validation, per-sample
        - **Gradients**: Magnitude, direction, vanishing/exploding
        - **Activations**: Distribution, dead neurons, saturation
        - **Data**: Sample distribution, class balance, outliers
        - **Time**: Forward pass, backward pass, data loading
        """
    )
    
    # Quick instrumentation code
    st.markdown("#### 🔧 Quick Instrumentation")
    
    instrument_type = st.selectbox(
        "What to instrument:",
        ["Loss tracking", "Gradient logging", "Activation histograms", "Timing profiler"]
    )
    
    if instrument_type == "Loss tracking":
        st.code("""
losses = []
for epoch in range(epochs):
    loss = train_step()
    losses.append(loss.item())
    print(f"Epoch {epoch}: {loss:.4f}")
    if epoch % 10 == 0:
        plt.plot(losses)
        plt.savefig(f'loss_{epoch}.png')
""", language='python')
    
    elif instrument_type == "Gradient logging":
        st.code("""
def log_gradients(model):
    for name, param in model.named_parameters():
        if param.grad is not None:
            grad_norm = param.grad.norm().item()
            print(f"{name}: {grad_norm:.4f}")
            if grad_norm > 10:
                print(f"WARNING: Large gradient in {name}")
""", language='python')

def display_progress_view():
    """Display progress with tiny wins"""
    st.markdown("### 🏆 Build Progress")
    
    # Tiny wins tracker
    st.session_state.tiny_wins.display_wins_banner()
    st.session_state.tiny_wins.display_achievement_buttons()
    st.session_state.tiny_wins.display_recent_wins()
    
    # Motivational message
    st.session_state.tiny_wins.display_motivational_banner()
    
    # Progress metrics
    progress_data = db.get_progress(st.session_state.user_id, st.session_state.current_path_id)
    
    if progress_data:
        modules = st.session_state.current_curriculum.get('modules', [])
        completed = sum(1 for p in progress_data if p['status'] == 'completed')
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Modules Completed", f"{completed}/{len(modules)}")
        with col2:
            completion_rate = (completed / len(modules) * 100) if modules else 0
            st.metric("Completion", f"{completion_rate:.0f}%")
        with col3:
            st.metric("Current Streak", st.session_state.tiny_wins.win_streak)
        
        # Visual progress bar
        st.progress(completion_rate / 100)

if __name__ == "__main__":
    main()