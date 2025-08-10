import random
import streamlit as st

KARPATHY_QUOTES = [
    ("Build small, real things.", "Start with tiny, working implementations"),
    ("What I cannot create, I do not understand.", "True understanding comes from building"),
    ("Clarity beats cleverness.", "Write code that explains itself"),
    ("Plots > opinions.", "Let the data speak through visualization"),
    ("Own the stack end-to-end.", "Understand every layer of your system"),
    ("One experiment, one lesson.", "Each iteration should teach you something"),
    ("Overfit first, then generalize.", "Make it work on one example before scaling"),
    ("Debugging is the curriculum.", "Errors are your best teachers"),
    ("Tight loops, fast feedback.", "Short experiments, quick iterations"),
    ("Instrument everything.", "Measure, plot, understand"),
    ("Data ≫ lore.", "Inspect your data before trusting assumptions"),
    ("Simple > fancy.", "Complexity must be earned"),
    ("Reproduce & ablate.", "Rebuild results, then remove pieces"),
    ("Readable code wins.", "Small files, clear names, zero magic"),
    ("Teach to learn.", "Explaining solidifies understanding"),
]

KARPATHY_PRINCIPLES = {
    "🔨 Do the Thing": "Implement tiny, working versions before reading/watching more.",
    "🏗️ From Scratch First": "Write minimal reference code you can step through line-by-line.",
    "🔄 End-to-End Mindset": "Own the whole pipeline (data → model → train → eval → deploy).",
    "🎯 Overfit Then Generalize": "Make it work on a toy problem, then scale.",
    "📊 Instrument Everything": "Plot losses, grads, activations; let the graphs teach you.",
    "🔍 Data ≫ Lore": "Inspect samples, labels, splits; catch leaks and shortcuts early.",
    "✨ Simple > Fancy": "Fewer layers, fewer knobs; complexity is earned.",
    "🧪 Reproduce & Ablate": "Rebuild results, then remove pieces to see what truly matters.",
    "⚡ Tight Loops": "Short experiments, fast iteration, frequent checkpoints.",
    "📖 Readable Code": "Small files, clear names, zero magic; comments explain why, not what.",
    "🎁 Concrete Artifacts": "Every lesson ends with something you can run or demo.",
    "👨‍🏫 Teach to Learn": "Write notes, explain decisions, log what surprised you.",
}

LEARNING_MANTRAS = [
    "Start each session with a small experiment you can finish in ≤60 min.",
    "Keep a run journal: config, seed, commit hash, hypothesis, result, next step.",
    "Treat errors as data—debugging is the curriculum.",
    "Prefer deterministic baselines over 'maybe better' tweaks.",
    "One variable at a time: change it, measure it, document it.",
    "Read the source (yours and upstream) when confused; the code is the spec.",
]

ANTI_PATTERNS = [
    "❌ Broad tutorials with no artifact",
    "❌ Giant refactors before passing baseline",
    "❌ Tuning hyperparams without plots or notes",
    "❌ 'It trains' without checking splits or leakage",
    "❌ Multiple changes at once",
    "❌ Complexity before understanding",
]

def show_philosophy_banner():
    """Display a rotating Karpathy philosophy quote"""
    quote, context = random.choice(KARPATHY_QUOTES)
    
    st.markdown(
        f"""
        <div class="philosophy-banner">
            <p class="philosophy-quote">"{quote}"</p>
            <p class="philosophy-author">— {context}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_principle_cards(selected_principles=None):
    """Display principle cards in a grid"""
    if selected_principles is None:
        selected_principles = list(KARPATHY_PRINCIPLES.items())[:6]
    
    cols = st.columns(3)
    for idx, (title, description) in enumerate(selected_principles):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="principle-card">
                    <div class="principle-title">{title}</div>
                    <div class="principle-description">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def show_learning_mantra():
    """Display a random learning mantra"""
    mantra = random.choice(LEARNING_MANTRAS)
    st.info(f"💡 **Today's Practice:** {mantra}")

def show_anti_patterns():
    """Display anti-patterns to avoid"""
    with st.expander("⚠️ Anti-patterns We Avoid"):
        for pattern in ANTI_PATTERNS:
            st.markdown(pattern)

def get_socratic_prompt(topic, level="beginner"):
    """Generate Socratic-style prompts based on Karpathy's philosophy"""
    prompts = {
        "beginner": [
            f"What's the smallest working version of {topic} you can build?",
            f"Can you implement {topic} in under 100 lines?",
            f"What would a toy example of {topic} look like?",
            f"How would you test if your {topic} implementation works?",
        ],
        "intermediate": [
            f"What happens if you remove half the code from {topic}?",
            f"Can you plot the internals of {topic} as it runs?",
            f"What's the simplest baseline for {topic}?",
            f"How would you instrument {topic} to understand it better?",
        ],
        "advanced": [
            f"What's the minimal reproduction of {topic}'s core behavior?",
            f"How would you ablate components of {topic}?",
            f"What unexpected behavior emerges in {topic} at scale?",
            f"Can you rebuild {topic} from memory in 30 minutes?",
        ]
    }
    
    return random.choice(prompts.get(level, prompts["beginner"]))

def show_build_pipeline(stages=None):
    """Display the build pipeline visualization"""
    if stages is None:
        stages = [
            ("📊", "Data"),
            ("🧠", "Model"),
            ("🏋️", "Train"),
            ("📈", "Eval"),
            ("🚀", "Deploy")
        ]
    
    st.markdown('<div class="pipeline-container">', unsafe_allow_html=True)
    
    cols = st.columns(len(stages))
    for idx, (icon, label) in enumerate(stages):
        with cols[idx]:
            st.markdown(
                f"""
                <div class="pipeline-step">
                    <div class="pipeline-icon">{icon}</div>
                    <div class="pipeline-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_experiment_card(hypothesis, result=None, insight=None):
    """Display an experiment card"""
    st.markdown(
        f"""
        <div class="experiment-card">
            <div class="experiment-hypothesis">📝 Hypothesis: {hypothesis}</div>
            {f'<div class="experiment-result">🔬 Result: {result}</div>' if result else ''}
            {f'<div class="experiment-insight">💡 Insight: {insight}</div>' if insight else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def show_error_celebration(error_message, learning_point):
    """Celebrate errors as learning opportunities"""
    st.markdown(
        f"""
        <div class="error-celebration">
            <div class="error-title">🎯 Debugging Opportunity Found!</div>
            <div class="error-message">
                <strong>Error:</strong> {error_message}<br>
                <strong>Learning:</strong> {learning_point}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_build_progress(items):
    """Display build progress with custom styling"""
    st.markdown('<div class="build-progress">', unsafe_allow_html=True)
    
    for item in items:
        status_class = item['status'].replace('_', '-')
        status_icon = {
            'completed': '✓',
            'in_progress': '•',
            'pending': '○'
        }.get(item['status'], '○')
        
        st.markdown(
            f"""
            <div class="progress-item">
                <div class="progress-status {status_class}">{status_icon}</div>
                <div class="progress-label">{item['label']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_metric_card(value, label, delta=None):
    """Display a custom metric card"""
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def get_karpathy_mode_prompt(mode):
    """Get mode-specific prompts following Karpathy's philosophy"""
    modes = {
        "socratic": "I'll guide you with questions, not answers. What's your hypothesis?",
        "from_scratch": "No libraries, pure implementation. Let's build it from first principles.",
        "tight_loop": "60-minute sprint. One clear goal. What are we building?",
        "instrument": "Measure everything. Plot everything. What metrics matter?",
        "ablation": "Remove components one by one. What's truly essential?",
    }
    
    return modes.get(mode, "Let's build something small and real.")

def show_one_variable_tracker(variable_name, old_value, new_value):
    """Display the one-variable-at-a-time tracker"""
    st.markdown(
        f"""
        <div class="variable-tracker">
            <div class="variable-name">Changed: {variable_name}</div>
            <div class="variable-change">{old_value} → {new_value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )