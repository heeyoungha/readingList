"""
텍스트 전처리 유틸리티
"""
import re
import html
from typing import List, Optional
from loguru import logger

try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False
    logger.warning("KoNLPy가 설치되지 않았습니다. 한국어 형태소 분석이 제한됩니다.")


class TextPreprocessor:
    """텍스트 전처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.okt = Okt() if KONLPY_AVAILABLE else None
        self.stop_words = self._load_stop_words()
    
    def _load_stop_words(self) -> set:
        """한국어 불용어 목록 로드"""
        return {
            '이', '그', '저', '것', '수', '등', '때', '곳', '말', '일',
            '때문', '그것', '그런', '이런', '저런', '아무', '어떤', '어느',
            '무슨', '몇', '얼마', '언제', '어디', '어떻게', '왜', '무엇',
            '있다', '없다', '하다', '되다', '있다', '없다', '그리고', '하지만',
            '또는', '또한', '그러나', '그런데', '그래서', '따라서', '그러면'
        }
    
    def clean_html(self, text: str) -> str:
        """HTML 태그 제거"""
        if not text:
            return ""
        
        # HTML 엔티티 디코딩
        text = html.unescape(text)
        
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def clean_special_chars(self, text: str) -> str:
        """특수문자 정리"""
        if not text:
            return ""
        
        # 이모지 제거
        text = re.sub(r'[^\w\s가-힣]', '', text)
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def normalize_text(self, text: str) -> str:
        """텍스트 정규화"""
        if not text:
            return ""
        
        # 소문자 변환 (영어의 경우)
        text = text.lower()
        
        # 연속된 공백 정리
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize_korean(self, text: str) -> List[str]:
        """한국어 형태소 분석"""
        if not text or not self.okt:
            return []
        
        try:
            # 형태소 분석
            morphs = self.okt.morphs(text)
            
            # 불용어 제거
            tokens = [token for token in morphs if token not in self.stop_words]
            
            return tokens
        except Exception as e:
            logger.error(f"한국어 형태소 분석 중 오류: {e}")
            return []
    
    def chunk_text(self, text: str, max_tokens: int = 512) -> List[str]:
        """텍스트를 청크로 분할"""
        if not text:
            return []
        
        # 문장 단위로 분할
        sentences = re.split(r'[.!?。！？]', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 현재 청크에 문장 추가
            if len(current_chunk) + len(sentence) <= max_tokens:
                current_chunk += sentence + ". "
            else:
                # 현재 청크가 가득 찬 경우 저장
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def preprocess_text(self, text: str, chunk_size: int = 512) -> dict:
        """전체 텍스트 전처리"""
        if not text:
            return {
                "original": "",
                "cleaned": "",
                "tokens": [],
                "chunks": [],
                "word_count": 0,
                "char_count": 0
            }
        
        # HTML 태그 제거
        cleaned_html = self.clean_html(text)
        
        # 특수문자 정리
        cleaned_chars = self.clean_special_chars(cleaned_html)
        
        # 텍스트 정규화
        normalized = self.normalize_text(cleaned_chars)
        
        # 한국어 토큰화
        tokens = self.tokenize_korean(normalized)
        
        # 청크 분할
        chunks = self.chunk_text(normalized, chunk_size)
        
        return {
            "original": text,
            "cleaned": normalized,
            "tokens": tokens,
            "chunks": chunks,
            "word_count": len(tokens),
            "char_count": len(normalized)
        }
    
    def analyze_writing_style(self, text: str) -> dict:
        """글쓰기 스타일 분석"""
        if not text:
            return {}
        
        # 문장 길이 분석
        sentences = re.split(r'[.!?。！？]', text)
        sentence_lengths = [len(s.strip()) for s in sentences if s.strip()]
        
        # 단어 길이 분석
        words = text.split()
        word_lengths = [len(w) for w in words if w]
        
        # 이모지 사용 분석
        emoji_count = len(re.findall(r'[^\w\s가-힣]', text))
        
        # 문장 부호 사용 분석
        punctuation_count = len(re.findall(r'[,.!?;:]', text))
        
        return {
            "avg_sentence_length": sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            "avg_word_length": sum(word_lengths) / len(word_lengths) if word_lengths else 0,
            "sentence_count": len(sentence_lengths),
            "word_count": len(word_lengths),
            "emoji_count": emoji_count,
            "punctuation_count": punctuation_count,
            "complexity_score": (sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0) * 
                               (sum(word_lengths) / len(word_lengths) if word_lengths else 0)
        } 