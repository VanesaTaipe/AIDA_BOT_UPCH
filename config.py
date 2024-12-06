import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        load_dotenv()
        self._init_paths()
        self._load_api_keys()
        self.data_cache: Dict[str, Any] = {}

    def _init_paths(self):
        self.BASE_DIR = Path(__file__).parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.COURSERA_FILE = self.BASE_DIR / "coursera_courses.json"
        
        # Validar que existan los directorios necesarios
        if not self.DATA_DIR.exists():
            self.DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _load_api_keys(self):
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

    def _init_functions(self):
        self.FUNCTIONS = [
            {
                "name": "get_plan_estudios",
                "description": "Get study plan for a career",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "carrera": {
                            "type": "string",
                            "description": "Career name (informatica, ambiental)"
                        },
                        "año": {
                            "type": "string",
                            "description": "Study plan year"
                        }
                    },
                    "required": ["carrera"]
                }
            },
            {
                "name": "get_cursos_por_ciclo",
                "description": "Get courses for a specific cycle",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "carrera": {
                            "type": "string",
                            "description": "Career name"
                        },
                        "ciclo": {
                            "type": "integer",
                            "description": "Cycle number (1-10)"
                        }
                    },
                    "required": ["carrera", "ciclo"]
                }
            },
            {
                "name": "get_curso_info",
                "description": "Get detailed course information",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "carrera": {
                            "type": "string",
                            "description": "Career name"
                        },
                        "codigo_curso": {
                            "type": "string",
                            "description": "Course code"
                        }
                    },
                    "required": ["carrera", "codigo_curso"]
                }
            }
        ]