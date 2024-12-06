import json
from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AcademicProcessor:
    def __init__(self, config):
        self.config = config
        self._load_data()
    
    def _load_data(self):
        try:
            # Cargar plan de estudios
            with open('plan_estudio.json', 'r', encoding='utf-8') as f:
                self.plan_estudios = json.load(f)
            
            # Cargar cursos por ciclo
            self.cursos_detallados = {}
            for ciclo in range(1, 9):
                try:
                    with open(f'ciclo_{ciclo}.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        for curso in data.get('cursos', []):
                            self.cursos_detallados[curso['codigo']] = curso
                except FileNotFoundError:
                    continue
            #Cursos electivo
            with open('cursos_electivos.json', 'r', encoding='utf-8') as f:
                self.electivos = json.load(f)

            # Cargar electivos detallados
            with open('cursos_electivos_detallados.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for curso in data.get('cursos electivos', []):
                    self.cursos_detallados[curso['codigo']] = curso
            
            # Cargar cursos de Coursera
            with open('coursera_courses.json', 'r', encoding='utf-8') as f:
                self.coursera_courses = json.load(f)
        
                    
        except Exception as e:
            logger.error(f"Error cargando datos: {str(e)}")
            raise

    #Coursera
    def get_coursera_recommendations(self, curso_nombre: str) -> List[Dict]:
        curso_keywords = {
            # Basic Sciences & Mathematics
            'filosofia': ['philosophy', 'critical thinking', 'ethics', 'philosophical foundations', 'moral philosophy'],
            'comunicacion': ['communication', 'writing', 'academic writing', 'speech', 'technical communication'],
            'calculo diferencial': ['differential calculus', 'mathematical analysis', 'calculus', 'derivatives', 'limits'],
            'calculo integral': ['integral calculus', 'integration', 'definite integrals', 'antiderivatives'],
            'calculo vectorial': ['vector calculus', 'multivariable calculus', 'vector analysis', 'vector fields'],
            'algebra matricial': ['matrix algebra', 'linear algebra', 'matrices', 'vector spaces'],
            'geometria analitica': ['analytic geometry', 'geometry', 'coordinates', 'geometric analysis'],
            'quimica general': ['general chemistry', 'chemistry', 'chemical principles', 'molecular chemistry'],
            'quimica computacional': ['computational chemistry', 'molecular modeling', 'chemical simulations'],
            'fisica': ['physics', 'mechanics', 'electromagnetism', 'engineering physics', 'thermodynamics'],
            'biologia': ['biology', 'life sciences', 'bioengineering', 'biological systems'],
            'estadistica': ['statistics', 'probability', 'statistical analysis', 'data analysis'],
            'ecuaciones diferenciales': ['differential equations', 'mathematical modeling', 'dynamical systems'],

            # Computer Science & Programming
            'ingenieria informatica': ['computer science', 'informatics', 'computing', 'software engineering'],
            'programacion': ['programming', 'coding', 'software development', 'algorithms'],
            'objetos': ['object oriented programming', 'OOP', 'software design patterns', 'java programming'],
            'estructuras discretas': ['discrete mathematics', 'discrete structures', 'computational structures'],
            'algoritmos': ['algorithms', 'data structures', 'algorithmic thinking', 'computational complexity'],
            'sistemas operativos': ['operating systems', 'system architecture', 'OS design', 'system programming'],
            'arquitectura computadores': ['computer architecture', 'hardware design', 'processor architecture'],
            'redes': ['computer networks', 'networking', 'data communications', 'network protocols'],
            'machine learning': ['machine learning', 'artificial intelligence', 'deep learning', 'neural networks'],
            'bases datos': ['databases', 'SQL', 'data management', 'database systems'],
            'seguridad informatica': ['cybersecurity', 'information security', 'network security', 'cryptography'],
            
            # Advanced Topics
            'sistemas web': ['web development', 'web design', 'frontend', 'backend', 'full stack'],
            'sistemas moviles': ['mobile development', 'app development', 'iOS', 'Android'],
            'computacion paralela': ['parallel computing', 'distributed systems', 'concurrent programming'],
            'software': ['software engineering', 'software architecture', 'software design'],
            'visualizacion': ['data visualization', 'visual analytics', 'information visualization'],
            
            # Professional Skills
            'desarrollo profesional': ['professional development', 'career planning', 'soft skills'],
            'ingles': ['english', 'technical english', 'business english', 'academic english'],
            'etica': ['ethics', 'professional ethics', 'technology ethics'],
            'tesis': ['research methods', 'thesis writing', 'academic research'],
            'derecho informatico': ['IT law', 'information law', 'cyber law', 'digital rights']
            }

        curso_lower = curso_nombre.lower()
        keywords = []
        
        for curso, terms in curso_keywords.items():
            if any(term in curso_lower for term in curso.split()):
                keywords.extend(terms)

        if not keywords:
            keywords = curso_lower.split()

        recomendaciones = []
        for curso in self.coursera_courses:
            curso_title = curso['Course Name'].lower()
            if any(keyword in curso_title for keyword in keywords):
                recomendaciones.append({
                    'titulo': curso['Course Name'],
                    'universidad': curso['University / Industry Partner Name'],
                    'nivel': curso['Difficulty Level'],
                    'Course URL': curso['Course URL']
                })

        return sorted(recomendaciones, 
                        key=lambda x: sum(k in x['titulo'].lower() for k in keywords), 
                        reverse=True)[:5]
    #Plan de estudio
    def get_plan_estudios(self, carrera: str) -> str:
        """Obtiene el plan de estudios directamente del JSON"""
        try:
            resultado = ["**Plan de Estudios - Ingeniería Informática**\n"]
            plan_regular = self.plan_estudios.get('plan_regular', {})
            
            for ciclo in range(1, 11):
                ciclo_key = f"ciclo {ciclo}"
                if ciclo_key in plan_regular:
                    resultado.append(f"\n**{ciclo_key.upper()}:**")
                    for curso in plan_regular[ciclo_key]:
                        resultado.append(
                            f"- **{curso['nombre']}** ({curso['codigo']}) "
                            f"- Créditos: {curso.get('creditos', 'No especificado')}"
                        )
            
            return "\n".join(resultado)
        except Exception as e:
            logger.error(f"Error obteniendo plan de estudios: {e}")
            return "Error al obtener el plan de estudios"
    #Cursos electivos
    def get_electivos(self, carrera: str) -> str:
        """Obtiene lista formateada de electivos"""
        try:
            if not hasattr(self, 'electivos'):
              return "Error: Datos de electivos no cargados"
            
            electivos = self.electivos.get('cursos_electivos', [])
            if not electivos:
                return "No se encontraron cursos electivos"
                
            resultado = ["**Cursos Electivos Disponibles:**\n"]
            for electivo in electivos:
                resultado.append(
                    f"- **{electivo['nombre']}** ({electivo['codigo']}) "
                    f"- Créditos: {electivo.get('creditos', 'No especificado')}"
                )
            return "\n".join(resultado)
        except Exception as e:
            logger.error(f"Error obteniendo electivos: {e}")
            return "Error al obtener los cursos electivos"
    #Informacion del curso por codigo
    def get_curso_info(self, carrera: str, codigo: str) -> Optional[Dict]:
        """Obtiene información detallada de un curso por su código"""
        try:
            # Buscar primero en el diccionario de cursos detallados
            if codigo in self.cursos_detallados:
                return self.cursos_detallados[codigo]
                
            # Si no se encuentra, buscar en el plan de estudios
            for ciclo_data in self.plan_estudios['plan_regular'].values():
                for curso in ciclo_data:
                    if curso['codigo'] == codigo:
                        return curso
                        
            return None
            
        except Exception as e:
            logger.error(f"Error buscando curso {codigo}: {e}")
            return None
    #Cursos por ciclos
    def get_cursos_por_ciclo(self, carrera: str, ciclo: int) -> List[Dict[str, Any]]:
        """Obtiene los cursos de un ciclo específico"""
        try:
            if not 1<= ciclo<=10:
                return[]
            ciclo_key = f"ciclo {ciclo}"
            if ciclo_key in self.plan_estudios['plan_regular']:
                cursos = self.plan_estudios['plan_regular'][ciclo_key]
                resultado = []
                for curso in cursos:
                    curso_info = {
                        'nombre': curso['nombre'],
                        'codigo': curso['codigo'],
                        'creditos': curso.get('creditos', 'No especificado'),
                        'tipo': curso.get('tipo_estudios', 'OBLIGATORIO')
                    }
                    resultado.append(curso_info)
                return resultado
            return []
        except Exception as e:
            logger.error(f"Error obteniendo cursos del ciclo {ciclo}: {e}")
            return []
    #Prerequisito
    def get_prerequisitos(self, codigo: str) -> str:
        """Obtiene y formatea los prerequisitos de un curso"""
        curso = self.get_curso_info("informatica", codigo)
        if not curso:
            return f"No se encontró información para el curso con código {codigo}"

        info = [f"📚 **{curso['nombre']}** ({curso['codigo']})"]
        
        # Tipo de curso
        tipo = curso.get('tipo_estudios', curso.get('tipo', 'No especificado'))
        info.append(f"- Tipo: {tipo}")
        
        # Solo prerequisitos
        prereqs = curso.get('prerequisito', [])
        if not prereqs:
            info.append("- Prerequisitos: Ninguno")
        elif isinstance(prereqs, list):
            info.append(f"- Prerequisitos: {', '.join(prereqs)}")
        else:
            info.append(f"- Prerequisitos: {prereqs}")
        
        return "\n".join(info)
   
    def format_curso_info(self, curso: Dict) -> str:
        """Formatea la información completa de un curso"""
        if not curso:
            return "Curso no encontrado"

        info = [f"📚 **{curso['nombre']}** ({curso['codigo']})"]
        
        # Información básica
        if 'tipo_estudios' in curso:
            info.append(f"- Tipo: {curso['tipo_estudios']}")
        elif 'tipo' in curso:
            info.append(f"- Tipo: {curso['tipo']}")
            
        if 'creditos' in curso:
            info.append(f"- Créditos: {curso['creditos']}")
            
        if 'modalidad' in curso:
            info.append(f"- Modalidad: {curso['modalidad']}")
            
        # Prerequisitos
        prereqs = curso.get('prerequisito', [])
        if prereqs:
            if isinstance(prereqs, list):
                info.append(f"- Prerequisitos: {', '.join(prereqs)}")
            else:
                info.append(f"- Prerequisito: {prereqs}")
        else:
            info.append("- Prerequisitos: Ninguno")
            
        # Información detallada
        if 'sumilla' in curso:
            info.append(f"\n📝 **Sumilla:**\n{curso['sumilla']}")        
        if 'resultados_aprendizaje' in curso:
            info.append("\n🎯 **Resultados de Aprendizaje:**")
            for resultado in curso['resultados_aprendizaje']:
                info.append(f"- {resultado}")
            
        if 'bibliografia' in curso and curso['bibliografia'].get('basica'):
            info.append("\n📚 **Bibliografía Básica:**")
            for biblio in curso['bibliografia']['basica']:
                info.append(f"- {biblio}")

        return "\n".join(info)
    #informacion de cursos electivos por codigo
    def get_electivo_detallado(self, codigo: str) -> str:
        """Obtiene información detallada de un electivo"""
        try:
            curso = self.cursos_detallados.get(codigo)
            if curso:
                return self.format_curso_info(curso)
            return (f"Lo sentimos, el curso {codigo} actualmente no se encuentra aperturado en la carrera de Ingeniería Informática. ")
        except Exception as e:
            logger.error(f"Error obteniendo detalle del electivo {codigo}: {e}")
            return "Error al obtener información detallada del electivo"
