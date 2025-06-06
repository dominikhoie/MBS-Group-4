import whisper
import io
import tempfile
import os
import asyncio
import functools
import logging
from typing import Tuple, Optional

# 尝试导入音频处理库
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    logging.warning("pydub not available - audio conversion disabled")

class VoiceProcessor:
    def __init__(self, model_size: str = "base"):
        """
        初始化语音处理器
        
        Args:
            model_size: Whisper模型大小 ("tiny", "base", "small", "medium", "large")
        """
        self.model = None
        self.available = False
        self.model_size = model_size
        
        try:
            logging.info(f"Loading Whisper model: {model_size}")
            self.model = whisper.load_model(model_size)
            self.available = True
            logging.info("Whisper model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            self.model = None
            self.available = False
    
    async def transcribe_voice(self, voice_file_bytes: bytes) -> Tuple[str, str]:
        """
        异步转录语音文件
        
        Args:
            voice_file_bytes: 语音文件的字节数据
            
        Returns:
            Tuple[str, str]: (转录文本, 语言代码)
        """
        if not self.available:
            logging.error("Whisper model not available")
            return "", "en"
            
        if not voice_file_bytes:
            logging.error("Empty voice file bytes")
            return "", "en"
            
        try:
            # 在线程池中运行CPU密集型任务
            loop = asyncio.get_event_loop()
            text, language = await loop.run_in_executor(
                None, 
                self._transcribe_sync, 
                voice_file_bytes
            )
            
            return text, language
            
        except Exception as e:
            logging.error(f"Voice transcription error: {e}")
            return "", "en"
    
    def _transcribe_sync(self, voice_file_bytes: bytes) -> Tuple[str, str]:
        """
        同步转录方法，在线程池中运行
        
        Args:
            voice_file_bytes: 语音文件的字节数据
            
        Returns:
            Tuple[str, str]: (转录文本, 语言代码)
        """
        temp_path = None
        converted_path = None
        
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_file:
                temp_file.write(voice_file_bytes)
                temp_path = temp_file.name

            # 尝试音频格式转换（如果需要）
            audio_path = self._convert_audio_if_needed(temp_path)
            if audio_path != temp_path:
                converted_path = audio_path

            # 执行转录
            logging.info(f"Transcribing audio file: {audio_path}")
            result = self.model.transcribe(
                audio_path,
                fp16=False,  # 在CPU上禁用fp16
                language=None,  # 自动检测语言
                task="transcribe"
            )
            
            # 安全地提取结果
            text = result.get("text", "").strip() if result else ""
            detected_language = result.get("language", "en") if result else "en"
            
            # 确保 detected_language 不为 None
            if not detected_language or not isinstance(detected_language, str):
                detected_language = "en"
            
            # 语言映射
            language_map = {
                "german": "de",
                "deutsch": "de", 
                "de": "de",
                "english": "en",
                "en": "en"
            }
            
            # 安全地处理语言检测
            try:
                language = language_map.get(detected_language.lower().strip(), "en")
            except (AttributeError, TypeError):
                language = "en"
            
            logging.info(f"Transcribed: '{text}' (detected: {detected_language} -> {language})")
            
            # 验证转录结果
            if not text or len(text.strip()) < 1:
                logging.warning("Empty or too short transcription result")
                return "", "en"
            
            return text, language
            
        except Exception as e:
            logging.error(f"Sync transcription error: {e}")
            return "", "en"
        finally:
            # 清理临时文件
            for path in [temp_path, converted_path]:
                if path and os.path.exists(path):
                    try:
                        os.unlink(path)
                        logging.debug(f"Cleaned up temp file: {path}")
                    except Exception as cleanup_error:
                        logging.warning(f"Failed to cleanup temp file {path}: {cleanup_error}")
    
    def _convert_audio_if_needed(self, input_path: str) -> str:
        """
        如果需要，转换音频格式
        
        Args:
            input_path: 输入音频文件路径
            
        Returns:
            str: 转换后的音频文件路径（如果不需要转换则返回原路径）
        """
        if not PYDUB_AVAILABLE:
            return input_path
            
        try:
            # 检测文件格式
            file_ext = os.path.splitext(input_path)[1].lower()
            
            # 如果是Whisper支持的格式，直接返回
            supported_formats = ['.wav', '.mp3', '.m4a', '.flac']
            if file_ext in supported_formats:
                return input_path
            
            # 转换为WAV格式
            logging.info(f"Converting {file_ext} to WAV format")
            audio = AudioSegment.from_file(input_path)
            
            # 转换为单声道，16kHz采样率（Whisper推荐）
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # 创建转换后的临时文件
            converted_path = input_path.replace('.ogg', '_converted.wav')
            audio.export(converted_path, format="wav")
            
            logging.info(f"Audio converted successfully: {converted_path}")
            return converted_path
            
        except Exception as e:
            logging.warning(f"Audio conversion failed: {e}, using original file")
            return input_path
    
    def get_model_info(self) -> dict:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "available": self.available,
            "model_size": self.model_size,
            "pydub_available": PYDUB_AVAILABLE,
            "model_loaded": self.model is not None
        }