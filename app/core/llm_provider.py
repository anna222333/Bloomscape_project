# app/core/llm_provider.py
import re
import streamlit as st
from google import genai
from google.genai import types
import app.config
from app.config import LOCATION

class GeminiInterface:
    """
    Инкапсуляция работы с Gemini LLM.
    Управляет клиентом и парсингом структурированных тегов в ответах.
    """
    
    def __init__(self, api_key=None, credentials=None, location=LOCATION, project_id=None):
        """
        Инициализирует Gemini клиент.
        
        Args:
            api_key: Google Gemini API ключ (если используется прямое подключение)
            credentials: Google auth credentials (для Vertex AI)
            location: Регион для Vertex AI
            project_id: ID проекта GCP
        """
        self.client = None
        self.credentials = credentials
        self.project_id = project_id or app.config.PROJECT_ID
        self.location = location
        
        if api_key:
            self._init_with_api_key(api_key)
        elif credentials:
            self._init_with_vertex_ai(credentials)
    
    def _init_with_api_key(self, api_key):
        """Инициализация с API ключом."""
        try:
            self.client = genai.Client(api_key=api_key)
            st.sidebar.success("✅ Подключено через API Key")
        except Exception as e:
            st.error(f"Ошибка инициализации Gemini с API Key: {e}")
            raise
    
    def _init_with_vertex_ai(self, credentials):
        """Инициализация с Vertex AI через credentials."""
        try:
            self.client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )
            st.sidebar.info("ℹ️ Подключено через Vertex AI (ADC)")
        except Exception as e:
            st.error(f"Ошибка инициализации Vertex AI: {e}")
            raise
    
    def generate_content(self, model_id, prompt, system_instruction, image_bytes=None):
        """
        Генерирует контент через Gemini.
        
        Args:
            model_id: ID модели (например, "gemini-3.1-pro-preview")
            prompt: Текст запроса
            system_instruction: Системная инструкция
            image_bytes: Опциональное изображение в байтах
        
        Returns:
            Текст ответа от модели
        """
        if not self.client:
            return "❌ Ошибка: Gemini клиент не инициализирован."
        
        try:
            contents = []
            if image_bytes:
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/png"))
            contents.append(prompt)
            
            response = self.client.models.generate_content(
                model=model_id,
                config=types.GenerateContentConfig(system_instruction=system_instruction),
                contents=contents
            )
            return response.text if response and response.text else "⚠️ Пустой ответ."
        except Exception as e:
            return f"❌ Ошибка Gemini: {str(e)}"
    
    def parse_tags(self, text):
        """
        Парсит структурированные теги из ответа LLM.
        
        Поддерживаемые теги:
        - [WRITE_ADR: name | content]
        - [WRITE_DOC: path | content]
        - [UPDATE_MASTER: content]
        - [GIT_PUSH]
        - [READ_FILE: path]
        - [GENERATE_IMAGE: prompt]
        - [PUBLISH_IMAGE: prompt]
        - [LOG_ACTION: action_text]
        
        Args:
            text: Текст для парсинга
        
        Returns:
            Словарь с найденными тегами и их значениями
        """
        tags = {}
        
        # [WRITE_ADR: name | content]
        if "[WRITE_ADR:" in text:
            try:
                content = text.split("[WRITE_ADR:")[1].split("]")[0].strip()
                parts = content.split("|")
                if len(parts) >= 2:
                    tags["write_adr"] = {
                        "name": parts[0].strip(),
                        "content": "|".join(parts[1:]).strip()
                    }
            except Exception as e:
                st.warning(f"Ошибка парсинга [WRITE_ADR]: {e}")
        
        # [WRITE_DOC: path | content]
        if "[WRITE_DOC:" in text:
            try:
                content = text.split("[WRITE_DOC:")[1].split("]")[0].strip()
                parts = content.split("|")
                if len(parts) >= 2:
                    tags["write_doc"] = {
                        "path": parts[0].strip(),
                        "content": "|".join(parts[1:]).strip()
                    }
            except Exception as e:
                st.warning(f"Ошибка парсинга [WRITE_DOC]: {e}")
        
        # [UPDATE_MASTER: content]
        if "[UPDATE_MASTER:" in text:
            try:
                content = text.split("[UPDATE_MASTER:")[1].split("]")[0].strip()
                tags["update_master"] = content
            except Exception as e:
                st.warning(f"Ошибка парсинга [UPDATE_MASTER]: {e}")
        
        # [GIT_PUSH]
        if "[GIT_PUSH]" in text:
            tags["git_push"] = True
        
        # [READ_FILE: path]  — может быть несколько тегов в одном ответе
        if "[READ_FILE:" in text:
            try:
                parts = text.split("[READ_FILE:")
                paths = []
                for part in parts[1:]:  # пропускаем часть до первого тега
                    file_path = part.split("]")[0].strip()
                    if file_path:
                        paths.append(file_path)
                if paths:
                    tags["read_file"] = paths  # всегда список
            except Exception as e:
                st.warning(f"Ошибка парсинга [READ_FILE]: {e}")
        
        # [GENERATE_IMAGE: prompt]
        if "[GENERATE_IMAGE:" in text:
            try:
                prompt = text.split("[GENERATE_IMAGE:")[1].split("]")[0].strip()
                tags["generate_image"] = prompt
            except Exception as e:
                st.warning(f"Ошибка парсинга [GENERATE_IMAGE]: {e}")
        
        # [PUBLISH_IMAGE: prompt]
        if "[PUBLISH_IMAGE:" in text:
            try:
                prompt = text.split("[PUBLISH_IMAGE:")[1].split("]")[0].strip()
                tags["publish_image"] = prompt
            except Exception as e:
                st.warning(f"Ошибка парсинга [PUBLISH_IMAGE]: {e}")
        
        # [LOG_ACTION: action_text]
        if "[LOG_ACTION:" in text:
            try:
                action = text.split("[LOG_ACTION:")[1].split("]")[0].strip()
                tags["log_action"] = action
            except Exception as e:
                st.warning(f"Ошибка парсинга [LOG_ACTION]: {e}")
        
        return tags
