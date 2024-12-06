
import streamlit as st
from chatbot import AcademicChatbot
from typing import Dict, List
import logging

# Configuración del sistema de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def init_session_state():
    """Inicializa el estado de la sesión"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = AcademicChatbot()
    if "carrera" not in st.session_state:
        st.session_state.carrera = "informatica"
    if "carrera_display" not in st.session_state:
        st.session_state.carrera_display = "Ingeniería Informática"

 

def get_welcome_message():
    """Retorna el mensaje de bienvenida"""
    return {
        "role": "assistant",
        "content": f"""
        ¡Hola! 👋 Soy AIDA, tu Asistente Inteligente Digital Académico

        🎓 Carrera: **{st.session_state.carrera_display}**

        Puedo ayudarte con:
        - 📘 Consultas de cursos y ciclos (1-8)
        - 📋 Plan de estudios
        - 🔍 Búsqueda de prerequisitos
        - 📊 Información de créditos y horas
        - 📚 Cursos electivos y recomendaciones de Coursera
        - 📝 Sílabos detallados

        ¿Qué información necesitas?
        """
    }

def display_chat_message(message: Dict[str, str], is_user: bool = False):
    """Muestra un mensaje en el chat"""
    with st.chat_message("user" if is_user else "assistant"):
        st.markdown(message["content"])

def main():
    try:
        st.set_page_config(
            page_title="AIDA - UPCH",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Inicializar componentes
        init_session_state()
        

        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.title("🎓 AIDA - Asistente Académico UPCH")
        

        # Mensaje de bienvenida
        if not st.session_state.messages:
            st.session_state.messages.append(get_welcome_message())

        # Mostrar historial
        for message in st.session_state.messages:
            display_chat_message(message, message["role"] == "user")

        # Input del usuario
        if prompt := st.chat_input("¿Qué deseas consultar?"):
            # Agregar y mostrar mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            display_chat_message(st.session_state.messages[-1], True)

            # Procesar y mostrar respuesta
            with st.chat_message("assistant"):
                with st.spinner("Procesando tu consulta..."):
                    response = st.session_state.chatbot.process_message(
                        f"Carrera: {st.session_state.carrera}. {prompt}",
                        st.session_state.messages
                    )
                    st.markdown(response)
                    
                    # Guardar respuesta en el historial
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })

    except Exception as e:
        logger.error(f"Error en la aplicación: {e}")
        st.error("""
        Ocurrió un error inesperado. 
        Por favor, actualiza la página o intenta más tarde.
        """)

if __name__ == "__main__":
    main()
