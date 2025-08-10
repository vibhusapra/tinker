import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

class ExperimentJournal:
    """Track experiments following Karpathy's methodology"""
    
    def __init__(self):
        if 'experiments' not in st.session_state:
            st.session_state.experiments = []
        
        if 'current_experiment' not in st.session_state:
            st.session_state.current_experiment = None
    
    def start_experiment(self, hypothesis: str, config: Dict = None):
        """Start a new experiment with hypothesis"""
        experiment = {
            'id': len(st.session_state.experiments) + 1,
            'timestamp': datetime.now().isoformat(),
            'hypothesis': hypothesis,
            'config': config or {},
            'status': 'running',
            'result': None,
            'insight': None,
            'duration': None,
            'artifacts': [],
            'metrics': {}
        }
        
        st.session_state.current_experiment = experiment
        st.session_state.experiments.append(experiment)
        
        return experiment['id']
    
    def log_metric(self, name: str, value: float):
        """Log a metric for the current experiment"""
        if st.session_state.current_experiment:
            st.session_state.current_experiment['metrics'][name] = value
    
    def add_artifact(self, name: str, content: str):
        """Add an artifact (code, plot, etc.) to current experiment"""
        if st.session_state.current_experiment:
            st.session_state.current_experiment['artifacts'].append({
                'name': name,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
    
    def complete_experiment(self, result: str, insight: str):
        """Complete the current experiment with results and insights"""
        if st.session_state.current_experiment:
            exp = st.session_state.current_experiment
            exp['status'] = 'completed'
            exp['result'] = result
            exp['insight'] = insight
            exp['duration'] = (
                datetime.now() - datetime.fromisoformat(exp['timestamp'])
            ).total_seconds()
            
            st.session_state.current_experiment = None
            return exp
        return None
    
    def get_experiments(self, limit: int = 10) -> List[Dict]:
        """Get recent experiments"""
        return st.session_state.experiments[-limit:]
    
    def display_journal(self):
        """Display the experiment journal UI"""
        st.markdown("### 🧪 Experiment Journal")
        
        # Current experiment status
        if st.session_state.current_experiment:
            exp = st.session_state.current_experiment
            with st.container():
                st.markdown(
                    f"""
                    <div class="experiment-card">
                        <div style="color: #f59e0b;">🔬 Experiment #{exp['id']} - IN PROGRESS</div>
                        <div class="experiment-hypothesis">Hypothesis: {exp['hypothesis']}</div>
                        <div style="color: #94a3b8;">Started: {exp['timestamp'][:19]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Quick complete form
                col1, col2 = st.columns(2)
                with col1:
                    result = st.text_input("Result:", key="exp_result")
                with col2:
                    insight = st.text_input("Key Insight:", key="exp_insight")
                
                if st.button("Complete Experiment", type="primary"):
                    if result and insight:
                        self.complete_experiment(result, insight)
                        st.success("Experiment completed!")
                        st.rerun()
        
        # New experiment form
        else:
            with st.expander("🚀 Start New Experiment"):
                hypothesis = st.text_area(
                    "Hypothesis:",
                    placeholder="If I change X, then Y will happen because...",
                    height=80
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    learning_rate = st.number_input("Learning Rate:", value=0.001, format="%.4f")
                    batch_size = st.number_input("Batch Size:", value=32)
                
                with col2:
                    epochs = st.number_input("Epochs:", value=10)
                    seed = st.number_input("Random Seed:", value=42)
                
                if st.button("Start Experiment", type="primary"):
                    if hypothesis:
                        config = {
                            'learning_rate': learning_rate,
                            'batch_size': batch_size,
                            'epochs': epochs,
                            'seed': seed
                        }
                        exp_id = self.start_experiment(hypothesis, config)
                        st.success(f"Started Experiment #{exp_id}")
                        st.rerun()
        
        # Recent experiments
        st.markdown("#### 📜 Recent Experiments")
        experiments = self.get_experiments(5)
        
        if experiments:
            for exp in reversed(experiments):
                status_color = "#22c55e" if exp['status'] == 'completed' else "#f59e0b"
                status_icon = "✅" if exp['status'] == 'completed' else "🔬"
                
                with st.expander(f"{status_icon} Experiment #{exp['id']} - {exp['hypothesis'][:50]}..."):
                    st.markdown(f"**Status:** <span style='color: {status_color}'>{exp['status'].upper()}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Timestamp:** {exp['timestamp'][:19]}")
                    
                    if exp['config']:
                        st.markdown("**Config:**")
                        st.json(exp['config'])
                    
                    if exp['result']:
                        st.markdown(f"**Result:** {exp['result']}")
                    
                    if exp['insight']:
                        st.markdown(f"**💡 Insight:** {exp['insight']}")
                    
                    if exp['metrics']:
                        st.markdown("**Metrics:**")
                        cols = st.columns(len(exp['metrics']))
                        for idx, (name, value) in enumerate(exp['metrics'].items()):
                            with cols[idx]:
                                st.metric(name, f"{value:.4f}")
                    
                    if exp['duration']:
                        st.markdown(f"**Duration:** {exp['duration']:.1f} seconds")
        else:
            st.info("No experiments yet. Start your first one above!")
    
    def export_journal(self) -> str:
        """Export journal as JSON"""
        return json.dumps(st.session_state.experiments, indent=2)
    
    def get_insights_summary(self) -> List[str]:
        """Get all insights from completed experiments"""
        insights = []
        for exp in st.session_state.experiments:
            if exp['status'] == 'completed' and exp['insight']:
                insights.append(f"Exp #{exp['id']}: {exp['insight']}")
        return insights