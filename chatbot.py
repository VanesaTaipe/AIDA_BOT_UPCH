import openai
import json
import re
from typing import List, Dict, Any, Optional
from config import Config
from academic_processor import AcademicProcessor
import logging

logger = logging.getLogger(__name__)

class AcademicChatbot:
    def __init__(self):
        self.config = Config()
        self.processor = AcademicProcessor(config=self.config)
        self.current_carrera = "informatica"
        openai.api_key = self.config.OPENAI_API_KEY
        self.model = "gpt-3.5-turbo"

    def _get_system_prompt(self) -> str:
        return """Eres AIDA (Asistente Inteligente Digital Académico) de la UPCH 👩‍🏫

        📚 Información disponible:
        - Planes de estudio de la carrera
        - Sílabos de cursos
        - Cursos electivos y actividades complementarias
        - Prerequisitos y créditos
        - Cursos recomendados de Coursera desde ciclo 3 al 8

        🎯 Servicios especializados:
        1. Información académica detallada
        2. Recomendaciones de cursos complementarios
        3. Guía de prerequisitos
        4. Enlaces a recursos externos

        💡 Capacidades:
        - Búsqueda precisa de información de cursos
        - Recomendación personalizada de electivos
        - Sugerencias de cursos online relacionados
        - Orientación sobre cursos electivos

        🤝 Estilo de interacción:
        - Comunicación clara y profesional
        - Respuestas estructuradas y concisas
        - Orientación constructiva
        - Soporte académico integral
        Recordar que solo existe informacion de 6 cursos electivos:
        -C0359 - Tópicos Avanzados en Sistemas de Información
        -C8294 - Métodos Numéricos y Optimización para Machine Learning
        -C8295 - Visión Computacional
        -C8306 - Gestión de Proyectos de Software
        -C9854 - Natural Language Processing
        -C9853 - Calidad de Software
         También, ten un toque ligero de humor, siempre que sea respetuoso y adecuado para la situación.
         Además, dependiendo del contexto, agregar pequeños emojis amistosos puede hacer la conversación más visualmente atractiva y menos formal. Pero evitar usar lenguaje demasiado informal o 
         familiar que podría incomodar al usuario.
         
         """
    def _extract_course_code(self, message: str) -> Optional[str]:
        """Extrae el código del curso del mensaje"""
        pattern = r'[A-Z]\d{4}'
        matches = re.findall(pattern, message.upper())
        return matches[0] if matches else None
    def process_message(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        try:
            if "Carrera:" in message:
                carrera = message.split("Carrera:")[1].split(".")[0].strip()
                self.current_carrera = carrera

            message_lower = message.lower()

            # Prerequisitos 
            if any(keyword in message_lower for keyword in ["prerequisito", "prereq", "requisito"]):
                pattern = r'[A-Z]\d{4}'
                matches = re.findall(pattern, message.upper())
                codigo = matches[0] if matches else None
                if codigo:
                    return self.processor.get_prerequisitos(codigo)
                return "Por favor, especifica el código del curso para consultar sus prerequisitos."

            # Plan de estudios
            if "plan de estudio" in message_lower:
                return self.processor.get_plan_estudios(self.current_carrera)

            # Consulta de ciclo
            if "ciclo" in message_lower:
                numbers = ''.join(filter(str.isdigit, message_lower))
                if numbers:
                    ciclo = int(numbers)
                    if 1 <= ciclo <= 10:
                        cursos = self.processor.get_cursos_por_ciclo(self.current_carrera, ciclo)
                        if cursos:
                            response = [f"📚 Cursos del ciclo {ciclo}:\n"]
                            for curso in cursos:
                                response.append(
                                    f"- **{curso['nombre']}** ({curso['codigo']})\n"
                                    f"  Créditos: {curso.get('creditos', 'No especificado')}\n"
                                    f"  Tipo: {curso.get('tipo', 'Obligatorio')}"
                                )
                            return "\n".join(response)
                        return f"No se encontraron cursos para el ciclo {ciclo}"
                    return "Por favor, especifica un número de ciclo válido (1-8)"

            # Información de curso
            pattern = r'[A-Z]\d{4}'
            matches = re.findall(pattern, message.upper())
            if matches:
                codigo = matches[0]
                if "informacion" in message_lower or "información" in message_lower or "detalle" in message_lower:
                    if codigo.startswith('C'):
                        return self.processor.get_electivo_detallado(codigo)
                    curso = self.processor.get_curso_info(self.current_carrera, codigo)
                    if curso:
                        return self.processor.format_curso_info(curso)
                    return f"No se encontró información para el curso con código {codigo}"

            # Electivos
            if "electivo" in message_lower:
                return self.processor.get_electivos(self.current_carrera)
            #COURSERA
            if "coursera" in message_lower:
            # Extraer el nombre del curso
                curso_nombre = None
                
                if "para" in message_lower:
                    curso_nombre = message_lower.split("para")[-1].strip()
                elif "relacionados" in message_lower:
                    curso_nombre = message_lower.split("relacionados a")[-1].strip()
                elif "recomiendas" in message_lower:
                    curso_nombre = message_lower.split("para")[-1].strip()
                    
                if curso_nombre:
                    recomendaciones = self.processor.get_coursera_recommendations(curso_nombre)
                    if recomendaciones:
                        response = [f"📚 Cursos de Coursera recomendados:"]
                        for rec in recomendaciones:
                            response.append(
                                f"- **{rec['titulo']}**\n"
                                f"  📍 Universidad: {rec['universidad']}\n"
                                f"  ⭐ Nivel: {rec['nivel']}\n"
                                f"  🔗 Link: {rec['Course URL']}"
                            )
                        return "\n".join(response)
                    return "No se encontraron cursos relacionados. Por favor, intenta con otras palabras clave."
                
                return "Por favor, especifica el nombre del curso (ejemplo: 'cursos de coursera para Estructuras Discretas')"
                
                
            # Consulta general usando GPT
            context = (
                "Estás respondiendo consultas sobre la carrera de Ingeniería Informática de la UPCH. "
                "Los ciclos disponibles son del 1 al 8."
            )

            messages = [
                {"role": "system", "content": self._get_system_prompt() + "\n" + context},
                *conversation_history[-3:],
                {"role": "user", "content": message}
            ]

            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=800,
                presence_penalty=0.3,
                frequency_penalty=0.3
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            return "Lo siento, ocurrió un error. Por favor, intenta de nuevo."
        
    def set_gpt_model(self, use_mini: bool = True):
        """Permite cambiar entre GPT-4-0 y GPT-4-0-mini"""
        self.model = "gpt-4-0-mini" if use_mini else "gpt-4-0"
