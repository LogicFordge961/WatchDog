import psutil
import random
import re
from typing import Dict, List, Tuple
import ollama
import subprocess
import platform
import os
import json
from datetime import datetime

# Ollama AI integration
MODEL_NAME = "llama3.2"  # Default Ollama model

OS = platform.system()

SYSTEM_PROMPT = f"""You are NEXUS, an AI assistant that helps control the user's computer.

You can:
- Open and close applications
- Read system stats (CPU, RAM, disk, network)
- List and kill processes
- Browse the file system
- Run shell commands
- Take screenshots
- Control system volume

Operating system: {OS}

When the user asks you to DO something, respond with what you would do, but don't actually execute commands - the system will handle that.
Be direct and helpful."""

class OllamaAI:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = model_name
        self.history: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Send a natural language message and get response from Ollama."""
        try:
            # Add user message to history
            self.history.append({"role": "user", "content": user_message})

            # Prepare messages for Ollama
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.history[-10:]  # Keep last 10 messages

            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={"temperature": 0.7, "top_p": 0.9}
            )

            reply = response['message']['content'].strip()

            # Add response to history
            self.history.append({"role": "assistant", "content": reply})

            return reply

        except Exception as e:
            return f"Sorry, I encountered an error: {e}"

    def clear(self):
        """Clear conversation memory."""
        self.history = []

class AIPoweredAssistant:
    def __init__(self):
        self.use_ollama = False
        self.ollama_ai = None
        
        # Check if Ollama is available
        try:
            # Test Ollama connection
            ollama.list()
            self.ollama_ai = OllamaAI()
            self.use_ollama = True
        except Exception as e:
            print(f"Warning: Could not initialize Ollama AI: {e}. Falling back to basic assistant.")
        
        if not self.use_ollama:
            self.conversation_history = []
            self.system_context = {}
    
    def query_ai(self, user_input: str) -> Dict[str, any]:
        if self.use_ollama:
            # Use Ollama AI for natural language responses
            response = self.ollama_ai.chat(user_input)
            return {
                'response': response,
                'command': 'ollama_response',
                'arguments': [],
                'confidence': 1.0,
                'needs_confirmation': False
            }
        else:
            # Fallback to basic assistant
            return self._basic_query(user_input)
    
    def _basic_query(self, user_input: str) -> Dict[str, any]:
        """Basic fallback implementation"""
        try:
            self.system_context = self._get_system_context()
            response = self._generate_natural_response(user_input)
            interpreted_command = self._interpret_command(user_input)
            
            return {
                'response': response,
                'command': interpreted_command['command'],
                'arguments': interpreted_command['arguments'],
                'confidence': interpreted_command['confidence'],
                'needs_confirmation': interpreted_command['needs_confirmation']
            }
        except Exception as e:
            return {
                'response': f"Oops! I had trouble understanding that: {str(e)}",
                'command': 'unknown',
                'arguments': [],
                'confidence': 0.0,
                'needs_confirmation': False
            }
    
    def _get_system_context(self) -> Dict:
        """Get current system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.5)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('C:') if psutil.disk_usage('C:') else None
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_free_gb': round(memory.available / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk_percent': disk.percent if disk else 0,
                'disk_free_gb': round(disk.free / (1024**3), 2) if disk else 0,
                'running_processes': len(psutil.pids())
            }
        except:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'memory_free_gb': 0,
                'memory_total_gb': 0,
                'disk_percent': 0,
                'disk_free_gb': 0,
                'running_processes': 0
            }
    
    def _generate_natural_response(self, user_input: str) -> str:
        """Generate natural, conversational response"""
        cleaned_input = user_input.lower().strip()
        
        # Performance-related questions
        if any(word in cleaned_input for word in ['slow', 'fast', 'performance', 'speed']):
            return self._analyze_performance()
        
        elif any(word in cleaned_input for word in ['cpu', 'processor', 'core']):
            return self._analyze_cpu()
        
        elif any(word in cleaned_input for word in ['ram', 'memory', 'space']):
            return self._analyze_memory()
        
        elif any(word in cleaned_input for word in ['disk', 'drive', 'storage']):
            return self._analyze_disk()
        
        elif any(word in cleaned_input for word in ['fine', 'okay', 'good', 'bad', 'running']):
            return self._analyze_overall_health()
        
        elif any(word in cleaned_input for word in ['most', 'highest', 'top']):
            if 'cpu' in cleaned_input:
                return self._find_highest_cpu_process()
            elif 'memory' in cleaned_input or 'ram' in cleaned_input:
                return self._find_highest_memory_process()
        
        # Launch/open commands
        elif any(word in cleaned_input for word in ['open', 'launch', 'start', 'run']):
            apps = self._extract_app_names(cleaned_input)
            if apps:
                return f"I can help you launch {', '.join(apps)}. Just say 'launch {apps[0]}' to get started!"
            else:
                return "I'd be happy to help you launch an application. Just tell me what you want to open!"
        
        # Greetings
        elif any(word in cleaned_input for word in ['hello', 'hi', 'hey', 'greetings']):
            return random.choice([
                "Hello there! How can I help you today?",
                "Hi! What can I do for you?",
                "Hey! Ready to assist with your system.",
                "Greetings! Need some tech help?"
            ])
        
        # Farewells
        elif any(word in cleaned_input for word in ['bye', 'goodbye', 'exit', 'quit']):
            return random.choice([
                "Goodbye! Take care of your system!",
                "See you later! Stay productive!",
                "Bye for now! I'll be here when you need me."
            ])
        
        # General response
        else:
            return self._general_response()
    
    def _interpret_command(self, user_input: str) -> Dict:
        """Interpret user input and determine intended command"""
        cleaned_input = user_input.lower().strip()
        
        # Command confidence scoring
        command_scores = {}
        
        # Launch/Open command detection
        if any(word in cleaned_input for word in ['open', 'launch', 'start', 'run']):
            apps = self._extract_app_names(cleaned_input)
            if apps:
                command_scores['launch'] = {
                    'score': 0.9,
                    'arguments': [apps[0]],  # Use first detected app
                    'needs_confirmation': True
                }
            else:
                # Try to extract app from general request
                app_guess = self._guess_app_from_context(cleaned_input)
                if app_guess:
                    command_scores['launch'] = {
                        'score': 0.7,
                        'arguments': [app_guess],
                        'needs_confirmation': True
                    }
        
        # Kill/Terminate command detection
        if any(word in cleaned_input for word in ['kill', 'close', 'stop', 'terminate', 'end']):
            apps = self._extract_app_names(cleaned_input)
            if apps:
                command_scores['kill'] = {
                    'score': 0.9,
                    'arguments': [apps[0]],
                    'needs_confirmation': True
                }
            else:
                # Try to extract process from context
                proc_guess = self._guess_process_from_context(cleaned_input)
                if proc_guess:
                    command_scores['kill'] = {
                        'score': 0.7,
                        'arguments': [proc_guess],
                        'needs_confirmation': True
                    }
        
        # Monitor command detection
        if any(word in cleaned_input for word in ['monitor', 'watch', 'check', 'see']):
            command_scores['monitor'] = {
                'score': 0.8,
                'arguments': [],
                'needs_confirmation': False
            }
        
        # Scan command detection
        if any(word in cleaned_input for word in ['scan', 'find', 'list', 'search']):
            command_scores['scan'] = {
                'score': 0.8,
                'arguments': [],
                'needs_confirmation': False
            }
        
        # Help command detection
        if any(word in cleaned_input for word in ['help', 'what can', 'how to', 'guide']):
            command_scores['help'] = {
                'score': 0.9,
                'arguments': [],
                'needs_confirmation': False
            }
        
        # Exit command detection
        if any(word in cleaned_input for word in ['exit', 'quit', 'bye', 'goodbye']):
            command_scores['exit'] = {
                'score': 0.95,
                'arguments': [],
                'needs_confirmation': False
            }
        
        # If no specific command detected, default to help/info
        if not command_scores:
            command_scores['info'] = {
                'score': 0.6,
                'arguments': [],
                'needs_confirmation': False
            }
        
        # Find highest confidence command
        best_command = max(command_scores.items(), key=lambda x: x[1]['score'])
        
        return {
            'command': best_command[0],
            'arguments': best_command[1]['arguments'],
            'confidence': best_command[1]['score'],
            'needs_confirmation': best_command[1]['needs_confirmation']
        }
    
    def _extract_app_names(self, text: str) -> List[str]:
        """Extract likely application names from text"""
        common_apps = [
            'chrome', 'firefox', 'edge', 'safari', 'opera',
            'notepad', 'notepad++', 'vscode', 'sublime', 'word', 'excel',
            'calculator', 'calc', 'spotify', 'steam', 'discord',
            'photoshop', 'vlc', 'media player', 'itunes', 'skype',
            'teams', 'zoom', 'outlook', 'thunderbird', 'settings',
            'task manager', 'cmd', 'powershell', 'explorer'
        ]
        
        found_apps = []
        text_lower = text.lower()
        
        for app in common_apps:
            if app in text_lower:
                found_apps.append(app)
        
        return found_apps
    
    def _guess_app_from_context(self, text: str) -> str:
        """Guess app name from context (handles typos)"""
        text_lower = text.lower()
        
        # Common typo corrections
        typo_corrections = {
            'broser': 'browser',
            'chrom': 'chrome',
            'notpad': 'notepad',
            'calcuator': 'calculator',
            'discort': 'discord',
            'stam': 'steam'
        }
        
        # Apply corrections
        for typo, correction in typo_corrections.items():
            if typo in text_lower:
                return correction
        
        # Check for partial matches
        if 'browse' in text_lower or 'web' in text_lower:
            return 'chrome'
        elif 'note' in text_lower or 'text' in text_lower:
            return 'notepad'
        elif 'calculate' in text_lower or 'math' in text_lower:
            return 'calculator'
        elif 'music' in text_lower:
            return 'spotify'
        elif 'game' in text_lower:
            return 'steam'
        
        return ''
    
    def _guess_process_from_context(self, text: str) -> str:
        """Guess process name from context"""
        return self._guess_app_from_context(text)
    
    def _analyze_performance(self) -> str:
        """Analyze overall system performance"""
        cpu = self.system_context['cpu_percent']
        mem = self.system_context['memory_percent']
        disk = self.system_context['disk_percent']
        
        responses = []
        
        # CPU analysis
        if cpu > 80:
            responses.append(f"Your CPU is running pretty hot at {cpu}% - that's quite busy!")
        elif cpu > 50:
            responses.append(f"CPU usage is at {cpu}% - moderate load.")
        else:
            responses.append(f"CPU looks good at {cpu}% - nice and relaxed!")
        
        # Memory analysis
        if mem > 80:
            responses.append(f"Memory is getting full ({mem}% used) - you might want to close some apps.")
        elif mem > 60:
            responses.append(f"Memory usage is at {mem}% - still plenty of room.")
        else:
            responses.append(f"You've got plenty of RAM free ({100-mem}% available).")
        
        # Disk analysis
        if disk > 90:
            responses.append(f"Disk is almost full ({disk}% used) - time for some cleanup!")
        elif disk > 70:
            responses.append(f"Disk usage is at {disk}% - getting a bit crowded.")
        else:
            responses.append(f"Plenty of disk space left ({100-disk}% free).")
        
        # Overall recommendation
        if cpu > 80 or mem > 80 or disk > 90:
            responses.append("I'd recommend closing some unused programs to free up resources.")
        else:
            responses.append("Overall, your system seems to be doing great!")
        
        return " ".join(responses)
    
    def _analyze_cpu(self) -> str:
        """Analyze CPU usage"""
        cpu = self.system_context['cpu_percent']
        if cpu > 90:
            return f"Your CPU is maxed out at {cpu}%! Something's really working hard - maybe too hard!"
        elif cpu > 70:
            return f"CPU is at {cpu}% - pretty busy. What's keeping it so occupied?"
        elif cpu > 40:
            return f"CPU usage is at {cpu}% - nice balanced load there!"
        else:
            return f"CPU is only at {cpu}% - barely breaking a sweat!"
    
    def _analyze_memory(self) -> str:
        """Analyze memory usage"""
        mem_percent = self.system_context['memory_percent']
        mem_free = self.system_context['memory_free_gb']
        if mem_percent > 85:
            return f"Yikes! You're using {mem_percent}% of your RAM ({mem_free}GB free). That's really tight - you should definitely close some apps!"
        elif mem_percent > 70:
            return f"You're using {mem_percent}% of RAM ({mem_free}GB free). Not terrible, but consider closing unused programs."
        elif mem_percent > 50:
            return f"Memory usage is at {mem_percent}% ({mem_free}GB free) - you've got room to spare!"
        else:
            return f"Only {mem_percent}% of RAM is being used ({mem_free}GB free) - your system has plenty of breathing room!"
    
    def _analyze_disk(self) -> str:
        """Analyze disk usage"""
        disk_percent = self.system_context['disk_percent']
        disk_free = self.system_context['disk_free_gb']
        if disk_percent > 95:
            return f"Uh oh! Your disk is {disk_percent}% full ({disk_free}GB free)! You're running dangerously low on space!"
        elif disk_percent > 85:
            return f"Disk usage is at {disk_percent}% ({disk_free}GB free) - time to do some cleanup!"
        elif disk_percent > 70:
            return f"Disk is at {disk_percent}% capacity ({disk_free}GB free) - getting a bit crowded."
        else:
            return f"You've got plenty of disk space left ({100-disk_percent}% free, {disk_free}GB available) - no worries there!"
    
    def _analyze_overall_health(self) -> str:
        """Analyze overall system health"""
        cpu = self.system_context['cpu_percent']
        mem = self.system_context['memory_percent']
        disk = self.system_context['disk_percent']
        
        if cpu > 80 or mem > 80 or disk > 90:
            return "Your system is working pretty hard right now. CPU, memory, or disk usage is high. Consider closing some programs."
        elif cpu > 50 or mem > 60 or disk > 70:
            return "Your system is running with moderate load. Everything seems to be working fine!"
        else:
            return "Your system is running smoothly with low resource usage. Everything looks good!"
    
    def _find_highest_cpu_process(self) -> str:
        """Find process using the most CPU"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            sorted_procs = sorted(processes, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)
            if sorted_procs and sorted_procs[0].get('cpu_percent', 0) > 0:
                top_proc = sorted_procs[0]
                return f"The process using the most CPU is {top_proc['name']} (PID: {top_proc['pid']}) at {top_proc['cpu_percent']:.1f}%"
            else:
                return "I don't see any processes using significant CPU right now."
        except Exception as e:
            return f"Having trouble checking processes: {e}"
    
    def _find_highest_memory_process(self) -> str:
        """Find process using the most memory"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'memory_info']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by memory usage
            sorted_procs = sorted(processes, key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
            if sorted_procs and sorted_procs[0].get('memory_percent', 0) > 0:
                top_proc = sorted_procs[0]
                mem_mb = (top_proc['memory_info'].rss / 1024 / 1024) if top_proc.get('memory_info') else 0
                return f"The process using the most memory is {top_proc['name']} (PID: {top_proc['pid']}) at {top_proc['memory_percent']:.1f}% ({mem_mb:.1f}MB)"
            else:
                return "I don't see any processes using significant memory right now."
        except Exception as e:
            return f"Having trouble checking processes: {e}"
    
    def _general_response(self) -> str:
        """General response with system context"""
        cpu = self.system_context['cpu_percent']
        mem = self.system_context['memory_percent']
        disk = self.system_context['disk_percent']
        
        responses = [
            f"I'm here to help! Your system stats: CPU {cpu}%, Memory {mem}%, Disk {disk}% used.",
            f"How can I assist you today? I see you have {self.system_context['running_processes']} processes running.",
            f"I'm your personal system assistant. Your system has {self.system_context['memory_free_gb']}GB free RAM.",
            f"What would you like me to help you with? I can launch apps, monitor processes, or optimize your system."
        ]
        return random.choice(responses)

# Global instance
ai_assistant = AIPoweredAssistant()