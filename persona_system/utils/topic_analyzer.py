"""
토픽 모델링 유틸리티
"""
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
from loguru import logger

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn이 설치되지 않았습니다. 토픽 모델링이 제한됩니다.")


class TopicAnalyzer:
    """토픽 분석 클래스"""
    
    def __init__(self, n_topics: int = 5, random_state: int = 42):
        """초기화"""
        self.n_topics = n_topics
        self.random_state = random_state
        self.vectorizer = None
        self.lda_model = None
        self.kmeans_model = None
        
        # 한국어 관련 키워드 카테고리
        self.topic_categories = self._load_topic_categories()
    
    def _load_topic_categories(self) -> Dict[str, List[str]]:
        """토픽 카테고리 키워드 로드"""
        return {
            "technology": [
                "기술", "프로그래밍", "코딩", "소프트웨어", "하드웨어", "인터넷",
                "컴퓨터", "알고리즘", "데이터", "AI", "인공지능", "머신러닝",
                "블록체인", "클라우드", "모바일", "웹", "앱", "디지털"
            ],
            "business": [
                "비즈니스", "경영", "마케팅", "전략", "리더십", "경제",
                "투자", "창업", "스타트업", "기업", "회사", "직장",
                "일", "업무", "프로젝트", "성과", "성장", "혁신"
            ],
            "education": [
                "교육", "학습", "공부", "학교", "대학", "강의",
                "책", "독서", "지식", "학문", "연구", "탐구",
                "성장", "발전", "자기계발", "스킬", "능력", "실력"
            ],
            "health": [
                "건강", "운동", "식단", "의료", "병원", "치료",
                "예방", "웰빙", "피트니스", "요가", "명상", "스트레스",
                "수면", "영양", "면역력", "체력", "정신건강"
            ],
            "lifestyle": [
                "라이프스타일", "취미", "여행", "음식", "패션", "뷰티",
                "인테리어", "가족", "친구", "관계", "사랑", "결혼",
                "육아", "반려동물", "문화", "예술", "음악", "영화"
            ],
            "philosophy": [
                "철학", "사상", "종교", "윤리", "도덕", "가치관",
                "인생", "의미", "목적", "자아", "정체성", "존재",
                "자유", "평등", "정의", "진리", "아름다움", "선"
            ],
            "science": [
                "과학", "물리학", "화학", "생물학", "천문학", "지구과학",
                "수학", "통계", "실험", "연구", "발견", "이론",
                "법칙", "원리", "현상", "자연", "우주", "생명"
            ],
            "social": [
                "사회", "정치", "역사", "문화", "인권", "평등",
                "다양성", "포용", "공동체", "협력", "봉사", "기부",
                "환경", "지속가능", "기후변화", "에너지", "자원"
            ]
        }
    
    def extract_keywords(self, text: str, min_length: int = 2) -> List[str]:
        """텍스트에서 키워드 추출"""
        if not text:
            return []
        
        # 한글, 영문, 숫자만 추출
        words = re.findall(r'[가-힣a-zA-Z0-9]+', text)
        
        # 길이 필터링
        keywords = [word for word in words if len(word) >= min_length]
        
        # 빈도수 계산
        keyword_freq = Counter(keywords)
        
        # 상위 키워드 반환 (빈도수 기준)
        return [word for word, freq in keyword_freq.most_common(50)]
    
    def categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """키워드를 카테고리별로 분류"""
        if not keywords:
            return {}
        
        categorized = {category: [] for category in self.topic_categories.keys()}
        
        for keyword in keywords:
            for category, category_keywords in self.topic_categories.items():
                if any(cat_keyword in keyword or keyword in cat_keyword 
                       for cat_keyword in category_keywords):
                    categorized[category].append(keyword)
                    break
        
        return categorized
    
    def analyze_topic_distribution(self, texts: List[str]) -> Dict[str, any]:
        """토픽 분포 분석"""
        if not texts or not SKLEARN_AVAILABLE:
            return {}
        
        try:
            # TF-IDF 벡터화
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # 한국어는 별도 처리
                min_df=2,
                max_df=0.95
            )
            
            # 텍스트 전처리 (키워드 추출)
            processed_texts = []
            for text in texts:
                if text:
                    keywords = self.extract_keywords(text)
                    processed_texts.append(' '.join(keywords))
            
            if not processed_texts:
                return {}
            
            # TF-IDF 행렬 생성
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            
            # LDA 모델 학습
            self.lda_model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=self.random_state,
                max_iter=100
            )
            
            lda_output = self.lda_model.fit_transform(tfidf_matrix)
            
            # 토픽별 키워드 추출
            feature_names = self.vectorizer.get_feature_names_out()
            topic_keywords = []
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_keywords_idx = topic.argsort()[-10:][::-1]
                top_keywords = [feature_names[i] for i in top_keywords_idx]
                topic_keywords.append(top_keywords)
            
            # K-means 클러스터링
            self.kmeans_model = KMeans(
                n_clusters=self.n_topics,
                random_state=self.random_state
            )
            
            kmeans_labels = self.kmeans_model.fit_predict(tfidf_matrix)
            
            return {
                "lda_topics": topic_keywords,
                "lda_distribution": lda_output.tolist(),
                "kmeans_clusters": kmeans_labels.tolist(),
                "feature_names": feature_names.tolist(),
                "tfidf_matrix_shape": tfidf_matrix.shape,
                "n_topics": self.n_topics
            }
            
        except Exception as e:
            logger.error(f"토픽 분석 중 오류: {e}")
            return {}
    
    def get_topic_summary(self, texts: List[str]) -> Dict[str, any]:
        """토픽 분석 요약"""
        if not texts:
            return {}
        
        # 키워드 추출
        all_keywords = []
        for text in texts:
            if text:
                keywords = self.extract_keywords(text)
                all_keywords.extend(keywords)
        
        # 키워드 빈도수 계산
        keyword_freq = Counter(all_keywords)
        top_keywords = keyword_freq.most_common(20)
        
        # 카테고리별 분류
        categorized = self.categorize_keywords([word for word, freq in top_keywords])
        
        # 토픽 모델링
        topic_analysis = self.analyze_topic_distribution(texts)
        
        return {
            "top_keywords": top_keywords,
            "categorized_keywords": categorized,
            "topic_analysis": topic_analysis,
            "total_texts": len([t for t in texts if t]),
            "unique_keywords": len(set(all_keywords)),
            "keyword_diversity": len(set(all_keywords)) / max(len(all_keywords), 1)
        }
    
    def suggest_topics(self, text: str, n_suggestions: int = 5) -> List[str]:
        """텍스트 기반 토픽 제안"""
        if not text:
            return []
        
        # 키워드 추출
        keywords = self.extract_keywords(text)
        
        # 카테고리별 분류
        categorized = self.categorize_keywords(keywords)
        
        # 가장 많이 매칭된 카테고리 찾기
        category_scores = {}
        for category, category_keywords in categorized.items():
            score = len(category_keywords)
            category_scores[category] = score
        
        # 상위 카테고리 선택
        top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        suggestions = []
        for category, score in top_categories[:n_suggestions]:
            if score > 0:
                suggestions.append(f"{category} 관련 토픽")
        
        return suggestions 