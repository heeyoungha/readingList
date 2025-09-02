"""
감정 분석 유틸리티
"""
import re
from typing import Dict, List, Tuple
from loguru import logger


class EmotionAnalyzer:
    """감정 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        self.emotion_keywords = self._load_emotion_keywords()
        self.sentiment_patterns = self._load_sentiment_patterns()
    
    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """감정별 키워드 로드"""
        return {
            "happy": [
                "기쁘다", "즐겁다", "행복하다", "신나다", "재미있다", "웃기다",
                "좋다", "멋지다", "훌륭하다", "완벽하다", "최고다", "최고야",
                "사랑한다", "감동이다", "감사하다", "고맙다", "축하한다",
                "성공했다", "이겼다", "해냈다", "달성했다", "달성했어"
            ],
            "sad": [
                "슬프다", "우울하다", "속상하다", "아프다", "괴롭다", "힘들다",
                "지치다", "피곤하다", "짜증나다", "화나다", "분하다", "답답하다",
                "실망하다", "절망하다", "포기하다", "그만두다", "끝이다",
                "죽고싶다", "살기싫다", "의미없다", "헛되다", "헛되네"
            ],
            "thoughtful": [
                "생각하다", "고민하다", "궁금하다", "의문이다", "궁금해",
                "이해하다", "알다", "모르다", "배우다", "학습하다", "연구하다",
                "분석하다", "조사하다", "탐구하다", "탐색하다", "발견하다",
                "느끼다", "느껴", "깨닫다", "깨달았다", "깨달았어", "깨달아"
            ],
            "excited": [
                "흥미롭다", "재미있다", "신기하다", "놀랍다", "대단하다",
                "멋지다", "훌륭하다", "완벽하다", "최고다", "최고야",
                "기대하다", "기대해", "기대된다", "기대돼", "설레다",
                "떨리다", "떨려", "긴장하다", "긴장해", "집중하다"
            ],
            "calm": [
                "차분하다", "평온하다", "고요하다", "조용하다", "잠잠하다",
                "안정적이다", "안정적이야", "편안하다", "편안해", "여유롭다",
                "여유로워", "느긋하다", "느긋해", "여유있다", "여유있어",
                "마음이", "마음이", "마음이", "마음이", "마음이"
            ],
            "surprised": [
                "놀랍다", "놀라", "깜짝", "갑자기", "갑작스럽게",
                "예상치", "예상치", "예상치", "예상치", "예상치",
                "생각보다", "생각보다", "생각보다", "생각보다", "생각보다",
                "상상보다", "상상보다", "상상보다", "상상보다", "상상보다"
            ]
        }
    
    def _load_sentiment_patterns(self) -> Dict[str, List[str]]:
        """감정 패턴 로드"""
        return {
            "positive": [
                r"좋[은는]?다", r"멋[은는]?다", r"훌륭[한하다]", r"완벽[한하다]",
                r"최고[다야]", r"사랑[한다해]", r"감동[이다이야]", r"감사[하다해]",
                r"성공[했다했어]", r"해냈다", r"달성[했다했어]", r"기쁘[다아]",
                r"즐겁[다아]", r"행복[하다해]", r"신나[다아]", r"재미[있다있어]"
            ],
            "negative": [
                r"나쁘[다아]", r"싫[다아]", r"힘들[다아]", r"어렵[다아]",
                r"복잡[하다해]", r"어려[워워서]", r"실패[했다했어]", r"실망[했다했어]",
                r"절망[했다했어]", r"포기[했다했어]", r"그만[둔다뒀어]",
                r"슬프[다아]", r"우울[하다해]", r"속상[하다해]", r"괴롭[다아]"
            ],
            "neutral": [
                r"보통[이다이야]", r"평범[하다해]", r"일반[적이다적이야]",
                r"그저[그렇다그래]", r"그냥[그렇다그래]", r"별로[다아]",
                r"중간[이다이야]", r"적당[하다해]", r"보통[이다이야]"
            ]
        }
    
    def analyze_emotion_keywords(self, text: str) -> Dict[str, int]:
        """키워드 기반 감정 분석"""
        if not text:
            return {}
        
        emotion_scores = {emotion: 0 for emotion in self.emotion_keywords.keys()}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                count = len(re.findall(keyword, text))
                emotion_scores[emotion] += count
        
        return emotion_scores
    
    def analyze_sentiment_patterns(self, text: str) -> Dict[str, int]:
        """패턴 기반 감정 분석"""
        if not text:
            return {}
        
        sentiment_scores = {sentiment: 0 for sentiment in self.sentiment_patterns.keys()}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            for pattern in patterns:
                count = len(re.findall(pattern, text))
                sentiment_scores[sentiment] += count
        
        return sentiment_scores
    
    def analyze_emotion_tone(self, text: str) -> Dict[str, float]:
        """감정 톤 분석"""
        if not text:
            return {}
        
        # 키워드 기반 감정 점수
        emotion_scores = self.analyze_emotion_keywords(text)
        
        # 패턴 기반 감정 점수
        sentiment_scores = self.analyze_sentiment_patterns(text)
        
        # 전체 점수 계산
        total_emotion_score = sum(emotion_scores.values())
        total_sentiment_score = sum(sentiment_scores.values())
        
        # 감정 분포 계산
        emotion_distribution = {}
        if total_emotion_score > 0:
            for emotion, score in emotion_scores.items():
                emotion_distribution[emotion] = score / total_emotion_score
        else:
            emotion_distribution = {emotion: 0.0 for emotion in emotion_scores.keys()}
        
        # 감정 톤 계산
        positive_ratio = sentiment_scores.get("positive", 0) / max(total_sentiment_score, 1)
        negative_ratio = sentiment_scores.get("negative", 0) / max(total_sentiment_score, 1)
        neutral_ratio = sentiment_scores.get("neutral", 0) / max(total_sentiment_score, 1)
        
        return {
            "emotion_distribution": emotion_distribution,
            "sentiment_ratios": {
                "positive": positive_ratio,
                "negative": negative_ratio,
                "neutral": neutral_ratio
            },
            "dominant_emotion": max(emotion_scores.items(), key=lambda x: x[1])[0] if total_emotion_score > 0 else "neutral",
            "overall_sentiment": "positive" if positive_ratio > negative_ratio else "negative" if negative_ratio > positive_ratio else "neutral"
        }
    
    def get_emotion_summary(self, text: str) -> Dict[str, any]:
        """감정 분석 요약"""
        if not text:
            return {}
        
        # 감정 톤 분석
        emotion_tone = self.analyze_emotion_tone(text)
        
        # 키워드 기반 감정 점수
        emotion_scores = self.analyze_emotion_keywords(text)
        
        # 패턴 기반 감정 점수
        sentiment_scores = self.analyze_sentiment_patterns(text)
        
        return {
            "emotion_tone": emotion_tone,
            "emotion_scores": emotion_scores,
            "sentiment_scores": sentiment_scores,
            "text_length": len(text),
            "analysis_summary": {
                "dominant_emotion": emotion_tone.get("dominant_emotion", "neutral"),
                "overall_sentiment": emotion_tone.get("overall_sentiment", "neutral"),
                "emotion_intensity": max(emotion_scores.values()) if emotion_scores else 0,
                "sentiment_intensity": max(sentiment_scores.values()) if sentiment_scores else 0
            }
        }
    
    def analyze_multiple_texts(self, texts: List[str]) -> Dict[str, any]:
        """여러 텍스트의 감정 분석"""
        if not texts:
            return {}
        
        all_emotions = []
        all_sentiments = []
        
        for text in texts:
            if text:
                emotion_summary = self.get_emotion_summary(text)
                all_emotions.append(emotion_summary.get("emotion_scores", {}))
                all_sentiments.append(emotion_summary.get("sentiment_scores", {}))
        
        # 평균 감정 점수 계산
        avg_emotions = {}
        if all_emotions:
            for emotion in self.emotion_keywords.keys():
                scores = [emotions.get(emotion, 0) for emotions in all_emotions]
                avg_emotions[emotion] = sum(scores) / len(scores)
        
        # 평균 감정 점수 계산
        avg_sentiments = {}
        if all_sentiments:
            for sentiment in self.sentiment_patterns.keys():
                scores = [sentiments.get(sentiment, 0) for sentiments in all_sentiments]
                avg_sentiments[sentiment] = sum(scores) / len(scores)
        
        return {
            "individual_analyses": [self.get_emotion_summary(text) for text in texts if text],
            "average_emotions": avg_emotions,
            "average_sentiments": avg_sentiments,
            "total_texts": len([t for t in texts if t]),
            "overall_dominant_emotion": max(avg_emotions.items(), key=lambda x: x[1])[0] if avg_emotions else "neutral",
            "overall_sentiment": "positive" if avg_sentiments.get("positive", 0) > avg_sentiments.get("negative", 0) else "negative" if avg_sentiments.get("negative", 0) > avg_sentiments.get("positive", 0) else "neutral"
        } 