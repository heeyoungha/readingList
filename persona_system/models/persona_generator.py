"""
페르소나 생성기
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from loguru import logger

from utils.text_preprocessor import TextPreprocessor
from utils.emotion_analyzer import EmotionAnalyzer
from utils.topic_analyzer import TopicAnalyzer


class PersonaGenerator:
    """페르소나 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.text_preprocessor = TextPreprocessor()
        self.emotion_analyzer = EmotionAnalyzer()
        self.topic_analyzer = TopicAnalyzer()
    
    def generate_persona(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 데이터로부터 페르소나 생성"""
        try:
            # 기본 정보 추출
            user_id = user_data.get("id", "unknown")
            name = user_data.get("name", "사용자")
            
            # 텍스트 데이터 수집
            texts = self._collect_texts(user_data)
            
            if not texts:
                logger.warning(f"사용자 {user_id}의 텍스트 데이터가 없습니다.")
                return self._create_default_persona(user_id, name)
            
            # 텍스트 전처리
            processed_texts = []
            for text in texts:
                if text:
                    processed = self.text_preprocessor.preprocess_text(text)
                    processed_texts.append(processed)
            
            # 글쓰기 스타일 분석
            writing_style = self._analyze_writing_style(processed_texts)
            
            # 감정 분석
            emotion_analysis = self.emotion_analyzer.analyze_multiple_texts(texts)
            
            # 토픽 분석
            topic_analysis = self.topic_analyzer.get_topic_summary(texts)
            
            # 페르소나 생성
            persona = self._create_persona(
                user_id=user_id,
                name=name,
                writing_style=writing_style,
                emotion_analysis=emotion_analysis,
                topic_analysis=topic_analysis,
                user_data=user_data
            )
            
            return persona
            
        except Exception as e:
            logger.error(f"페르소나 생성 중 오류: {e}")
            return self._create_default_persona(user_data.get("id", "unknown"), user_data.get("name", "사용자"))
    
    def _collect_texts(self, user_data: Dict[str, Any]) -> List[str]:
        """사용자 데이터에서 텍스트 수집"""
        texts = []
        
        # 독후감
        if "books" in user_data:
            for book in user_data["books"]:
                if book.get("review"):
                    texts.append(book["review"])
        
        # 액션 리스트
        if "action_lists" in user_data:
            for action in user_data["action_lists"]:
                if action.get("content"):
                    texts.append(action["content"])
        
        # 기타 텍스트 데이터
        if "notes" in user_data:
            for note in user_data["notes"]:
                if note.get("content"):
                    texts.append(note["content"])
        
        return texts
    
    def _analyze_writing_style(self, processed_texts: List[Dict]) -> Dict[str, Any]:
        """글쓰기 스타일 분석"""
        if not processed_texts:
            return {}
        
        # 평균 글쓰기 스타일 계산
        total_style = {
            "avg_sentence_length": 0,
            "avg_word_length": 0,
            "sentence_count": 0,
            "word_count": 0,
            "emoji_count": 0,
            "punctuation_count": 0,
            "complexity_score": 0
        }
        
        count = 0
        for processed in processed_texts:
            if processed.get("cleaned"):
                style = self.text_preprocessor.analyze_writing_style(processed["cleaned"])
                if style:
                    for key in total_style:
                        if key in style:
                            total_style[key] += style[key]
                    count += 1
        
        # 평균 계산
        if count > 0:
            for key in total_style:
                total_style[key] /= count
        
        # 스타일 분류
        style_category = self._classify_writing_style(total_style)
        
        return {
            **total_style,
            "style_category": style_category,
            "analyzed_texts": count
        }
    
    def _classify_writing_style(self, style_data: Dict[str, float]) -> str:
        """글쓰기 스타일 분류"""
        avg_sentence_length = style_data.get("avg_sentence_length", 0)
        avg_word_length = style_data.get("avg_word_length", 0)
        complexity_score = style_data.get("complexity_score", 0)
        
        if complexity_score > 100:
            return "복잡하고 정교한"
        elif complexity_score > 50:
            return "균형잡힌"
        elif avg_sentence_length > 30:
            return "상세하고 설명적인"
        elif avg_sentence_length < 15:
            return "간결하고 핵심적인"
        else:
            return "보통 수준의"
    
    def _create_persona(self, user_id: str, name: str, writing_style: Dict,
                        emotion_analysis: Dict, topic_analysis: Dict,
                        user_data: Dict) -> Dict[str, Any]:
        """페르소나 생성"""
        # 감정 프로필
        dominant_emotion = emotion_analysis.get("overall_dominant_emotion", "neutral")
        overall_sentiment = emotion_analysis.get("overall_sentiment", "neutral")
        
        # 관심사 분석
        top_keywords = topic_analysis.get("top_keywords", [])
        top_interests = [word for word, freq in top_keywords[:5]]
        
        # 독서 패턴
        reading_pattern = self._analyze_reading_pattern(user_data)
        
        # 페르소나 설명 생성
        persona_description = self._generate_persona_description(
            name, writing_style, dominant_emotion, overall_sentiment, top_interests
        )
        
        return {
            "user_id": user_id,
            "name": name,
            "generated_at": datetime.now().isoformat(),
            "persona_description": persona_description,
            "writing_style": writing_style,
            "emotion_profile": {
                "dominant_emotion": dominant_emotion,
                "overall_sentiment": overall_sentiment,
                "emotion_distribution": emotion_analysis.get("average_emotions", {}),
                "sentiment_ratios": emotion_analysis.get("average_sentiments", {})
            },
            "interests": {
                "top_keywords": top_interests,
                "categorized": topic_analysis.get("categorized_keywords", {}),
                "topic_distribution": topic_analysis.get("topic_analysis", {})
            },
            "reading_pattern": reading_pattern,
            "personality_traits": self._extract_personality_traits(
                writing_style, emotion_analysis, topic_analysis
            ),
            "communication_style": self._analyze_communication_style(writing_style),
            "growth_areas": self._identify_growth_areas(emotion_analysis, topic_analysis)
        }
    
    def _analyze_reading_pattern(self, user_data: Dict) -> Dict[str, Any]:
        """독서 패턴 분석"""
        if "books" not in user_data:
            return {}
        
        books = user_data["books"]
        if not books:
            return {}
        
        # 장르별 선호도
        genre_preferences = {}
        for book in books:
            genre = book.get("genre", "unknown")
            if genre not in genre_preferences:
                genre_preferences[genre] = 0
            genre_preferences[genre] += 1
        
        # 평점 패턴
        ratings = [book.get("rating", 0) for book in books if book.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # 감정 점수 패턴
        emotion_scores = [book.get("emotion_score", 0) for book in books if book.get("emotion_score")]
        avg_emotion_score = sum(emotion_scores) / len(emotion_scores) if emotion_scores else 0
        
        return {
            "total_books": len(books),
            "genre_preferences": genre_preferences,
            "average_rating": avg_rating,
            "average_emotion_score": avg_emotion_score,
            "reading_frequency": "regular" if len(books) > 10 else "moderate" if len(books) > 5 else "occasional"
        }
    
    def _generate_persona_description(self, name: str, writing_style: Dict,
                                    dominant_emotion: str, overall_sentiment: str,
                                    top_interests: List[str]) -> str:
        """페르소나 설명 생성"""
        style_category = writing_style.get("style_category", "보통 수준의")
        
        description = f"{name}님은 {style_category} 글쓰기 스타일을 가지고 있으며, "
        
        # 감정 프로필
        if dominant_emotion == "happy":
            description += "전반적으로 긍정적이고 밝은 감정을 표현하는 경향이 있습니다. "
        elif dominant_emotion == "thoughtful":
            description += "사색적이고 깊이 있는 사고를 하는 경향이 있습니다. "
        elif dominant_emotion == "excited":
            description += "열정적이고 흥미를 보이는 경향이 있습니다. "
        else:
            description += "균형잡힌 감정 표현을 하는 경향이 있습니다. "
        
        # 관심사
        if top_interests:
            interests_str = ", ".join(top_interests[:3])
            description += f"주로 {interests_str}와 관련된 주제에 관심을 보입니다. "
        
        # 글쓰기 스타일
        avg_sentence_length = writing_style.get("avg_sentence_length", 0)
        if avg_sentence_length > 25:
            description += "상세하고 설명적인 글쓰기를 선호합니다."
        elif avg_sentence_length < 15:
            description += "간결하고 핵심적인 글쓰기를 선호합니다."
        else:
            description += "균형잡힌 글쓰기 스타일을 가지고 있습니다."
        
        return description
    
    def _extract_personality_traits(self, writing_style: Dict, emotion_analysis: Dict,
                                   topic_analysis: Dict) -> List[str]:
        """성격 특성 추출"""
        traits = []
        
        # 글쓰기 스타일 기반
        complexity_score = writing_style.get("complexity_score", 0)
        if complexity_score > 80:
            traits.append("사고가 깊고 정교함")
        elif complexity_score < 30:
            traits.append("직관적이고 단순함")
        
        # 감정 프로필 기반
        dominant_emotion = emotion_analysis.get("overall_dominant_emotion", "neutral")
        if dominant_emotion == "thoughtful":
            traits.append("사색적이고 분석적")
        elif dominant_emotion == "excited":
            traits.append("열정적이고 적극적")
        elif dominant_emotion == "calm":
            traits.append("차분하고 안정적")
        
        # 관심사 다양성 기반
        keyword_diversity = topic_analysis.get("keyword_diversity", 0)
        if keyword_diversity > 0.7:
            traits.append("다양한 관심사를 가짐")
        elif keyword_diversity < 0.3:
            traits.append("특정 분야에 집중함")
        
        return traits
    
    def _analyze_communication_style(self, writing_style: Dict) -> Dict[str, str]:
        """의사소통 스타일 분석"""
        avg_sentence_length = writing_style.get("avg_sentence_length", 0)
        emoji_count = writing_style.get("emoji_count", 0)
        punctuation_count = writing_style.get("punctuation_count", 0)
        
        # 문장 길이 기반
        if avg_sentence_length > 30:
            sentence_style = "상세하고 설명적인"
        elif avg_sentence_length < 15:
            sentence_style = "간결하고 핵심적인"
        else:
            sentence_style = "균형잡힌"
        
        # 이모지 사용 기반
        if emoji_count > 5:
            emoji_style = "표현력이 풍부한"
        elif emoji_count > 0:
            emoji_style = "적절한 표현을 사용하는"
        else:
            emoji_style = "정형화된 표현을 사용하는"
        
        return {
            "sentence_style": sentence_style,
            "emoji_style": emoji_style,
            "overall_style": f"{sentence_style} {emoji_style} 의사소통 스타일"
        }
    
    def _identify_growth_areas(self, emotion_analysis: Dict, topic_analysis: Dict) -> List[str]:
        """성장 영역 식별"""
        growth_areas = []
        
        # 감정 다양성
        emotion_distribution = emotion_analysis.get("average_emotions", {})
        if emotion_distribution:
            emotion_variety = len([score for score in emotion_distribution.values() if score > 0])
            if emotion_variety < 3:
                growth_areas.append("감정 표현의 다양성 확대")
        
        # 관심사 확장
        keyword_diversity = topic_analysis.get("keyword_diversity", 0)
        if keyword_diversity < 0.5:
            growth_areas.append("다양한 주제에 대한 관심 확대")
        
        # 긍정적 감정
        sentiment_ratios = emotion_analysis.get("average_sentiments", {})
        positive_ratio = sentiment_ratios.get("positive", 0)
        if positive_ratio < 0.4:
            growth_areas.append("긍정적 사고 패턴 개발")
        
        return growth_areas
    
    def _create_default_persona(self, user_id: str, name: str) -> Dict[str, Any]:
        """기본 페르소나 생성"""
        return {
            "user_id": user_id,
            "name": name,
            "generated_at": datetime.now().isoformat(),
            "persona_description": f"{name}님의 페르소나를 생성하기 위한 충분한 데이터가 없습니다.",
            "writing_style": {},
            "emotion_profile": {},
            "interests": {},
            "reading_pattern": {},
            "personality_traits": [],
            "communication_style": {},
            "growth_areas": ["더 많은 독후감과 액션 리스트 작성"]
        }
    
    def save_persona(self, persona: Dict[str, Any], filepath: str) -> bool:
        """페르소나를 파일로 저장"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(persona, f, ensure_ascii=False, indent=2)
            logger.info(f"페르소나가 {filepath}에 저장되었습니다.")
            return True
        except Exception as e:
            logger.error(f"페르소나 저장 중 오류: {e}")
            return False
    
    def load_persona(self, filepath: str) -> Optional[Dict[str, Any]]:
        """파일에서 페르소나 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                persona = json.load(f)
            logger.info(f"페르소나가 {filepath}에서 로드되었습니다.")
            return persona
        except Exception as e:
            logger.error(f"페르소나 로드 중 오류: {e}")
            return None 