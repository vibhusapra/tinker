import streamlit as st
from datetime import datetime
from typing import List, Dict

class TinyWinsTracker:
    """Track and celebrate small achievements following Karpathy's philosophy"""
    
    ACHIEVEMENT_TYPES = {
        "first_run": ("🏃", "First Run", "Got code running!"),
        "debug_fix": ("🐛", "Bug Squashed", "Fixed an error"),
        "plot_made": ("📊", "Plot Created", "Visualized data"),
        "baseline": ("📈", "Baseline Set", "Established baseline"),
        "overfit": ("🎯", "Overfit Achieved", "Made it work on one example"),
        "generalize": ("🌍", "Generalized", "Scaled to more examples"),
        "refactor": ("♻️", "Refactored", "Simplified code"),
        "instrument": ("🔍", "Instrumented", "Added logging/metrics"),
        "reproduce": ("🔄", "Reproduced", "Matched expected results"),
        "ablation": ("🧪", "Ablated", "Identified key component"),
        "speedup": ("⚡", "Optimized", "Made it faster"),
        "readable": ("📖", "Clarified", "Made code more readable"),
        "artifact": ("🎁", "Shipped", "Created runnable artifact"),
        "taught": ("👨‍🏫", "Explained", "Documented learning"),
    }
    
    def __init__(self):
        if 'tiny_wins' not in st.session_state:
            st.session_state.tiny_wins = []
        
        if 'win_streak' not in st.session_state:
            st.session_state.win_streak = 0
        
        if 'daily_wins' not in st.session_state:
            st.session_state.daily_wins = 0
    
    def add_win(self, achievement_type: str, details: str = ""):
        """Add a new tiny win"""
        if achievement_type in self.ACHIEVEMENT_TYPES:
            icon, title, default_desc = self.ACHIEVEMENT_TYPES[achievement_type]
            
            win = {
                'type': achievement_type,
                'icon': icon,
                'title': title,
                'description': details or default_desc,
                'timestamp': datetime.now().isoformat(),
            }
            
            st.session_state.tiny_wins.append(win)
            st.session_state.daily_wins += 1
            
            # Update streak
            if len(st.session_state.tiny_wins) > 1:
                last_win = datetime.fromisoformat(st.session_state.tiny_wins[-2]['timestamp'])
                current = datetime.now()
                if (current - last_win).total_seconds() < 3600:  # Within an hour
                    st.session_state.win_streak += 1
                else:
                    st.session_state.win_streak = 1
            else:
                st.session_state.win_streak = 1
            
            return win
        return None
    
    def get_recent_wins(self, limit: int = 10) -> List[Dict]:
        """Get recent wins"""
        return st.session_state.tiny_wins[-limit:]
    
    def display_wins_banner(self):
        """Display the tiny wins banner"""
        st.markdown("### 🏆 Tiny Wins Tracker")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{len(st.session_state.tiny_wins)}</div>
                    <div class="metric-label">Total Wins</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{st.session_state.win_streak}</div>
                    <div class="metric-label">Current Streak</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{st.session_state.daily_wins}</div>
                    <div class="metric-label">Today's Wins</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    def display_achievement_buttons(self):
        """Display quick achievement buttons"""
        st.markdown("#### 🎯 Quick Wins")
        
        # Create a grid of achievement buttons
        cols = st.columns(4)
        for idx, (key, (icon, title, desc)) in enumerate(self.ACHIEVEMENT_TYPES.items()):
            with cols[idx % 4]:
                if st.button(f"{icon} {title}", key=f"win_{key}", help=desc):
                    self.add_win(key)
                    st.success(f"🎉 {title} achieved!")
                    st.balloons()
                    st.rerun()
    
    def display_recent_wins(self):
        """Display recent wins"""
        wins = self.get_recent_wins(5)
        
        if wins:
            st.markdown("#### 📜 Recent Achievements")
            
            for win in reversed(wins):
                timestamp = datetime.fromisoformat(win['timestamp'])
                time_ago = self._format_time_ago(timestamp)
                
                st.markdown(
                    f"""
                    <div class="tiny-win">
                        {win['icon']} <strong>{win['title']}</strong> - {win['description']} 
                        <span style="opacity: 0.7;">({time_ago})</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format timestamp as 'X minutes ago'"""
        delta = datetime.now() - timestamp
        seconds = delta.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} min ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
    
    def get_motivational_message(self) -> str:
        """Get a motivational message based on progress"""
        total_wins = len(st.session_state.tiny_wins)
        
        if total_wins == 0:
            return "🚀 Ready to start building? Every expert was once a beginner!"
        elif total_wins < 5:
            return "💪 Great start! Keep those tiny wins coming!"
        elif total_wins < 10:
            return "🔥 You're on fire! Building momentum one win at a time!"
        elif total_wins < 20:
            return "⭐ Impressive progress! You're embodying the build-to-learn philosophy!"
        else:
            return "🏆 Master builder! You've truly embraced learning by doing!"
    
    def display_motivational_banner(self):
        """Display motivational message"""
        message = self.get_motivational_message()
        st.info(message)
    
    def export_wins(self) -> str:
        """Export wins as formatted text"""
        output = "🏆 TINY WINS LOG\n" + "=" * 40 + "\n\n"
        
        for win in st.session_state.tiny_wins:
            timestamp = datetime.fromisoformat(win['timestamp'])
            output += f"{win['icon']} {win['title']}\n"
            output += f"   {win['description']}\n"
            output += f"   {timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        return output