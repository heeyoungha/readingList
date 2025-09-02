"""
페르소나 시스템 테스트 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.text_preprocessor import TextPreprocessor
from utils.emotion_analyzer import EmotionAnalyzer
from utils.topic_analyzer import TopicAnalyzer
from models.persona_generator import PersonaGenerator


def test_text_preprocessing():
    """텍스트 전처리 테스트"""
    print("=== 텍스트 전처리 테스트 ===")
    
    preprocessor = TextPreprocessor()
    
    # 테스트 텍스트
    test_text = """
    <p>이 책은 정말 <strong>훌륭하다</strong>고 생각합니다! 😊</p>
    독서를 통해 많은 것을 배웠고, 특히 인생에 대한 깊은 통찰을 얻었습니다.
    저는 이 책을 읽으면서 행복감을 느꼈고, 앞으로 더 많은 책을 읽고 싶다는 생각이 들었습니다.
    """
    
    print(f"원본 텍스트: {test_text[:100]}...")
    
    # 전처리
    result = preprocessor.preprocess_text(test_text)
    
    print(f"정제된 텍스트: {result['cleaned'][:100]}...")
    print(f"토큰 수: {result['word_count']}")
    print(f"문자 수: {result['char_count']}")
    print(f"청크 수: {len(result['chunks'])}")
    
    # 글쓰기 스타일 분석
    style = preprocessor.analyze_writing_style(test_text)
    print(f"글쓰기 스타일: {style}")
    
    print()


def test_emotion_analysis():
    """감정 분석 테스트"""
    print("=== 감정 분석 테스트 ===")
    
    analyzer = EmotionAnalyzer()
    
    # 테스트 텍스트들
    test_texts = [
        "이 책은 정말 훌륭하고 재미있습니다! 기쁘고 행복합니다.",
        "이 내용은 너무 어렵고 복잡해서 이해하기 힘듭니다. 실망스럽습니다.",
        "이 주제에 대해 깊이 생각해보게 되었습니다. 궁금하고 흥미롭습니다."
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"텍스트 {i}: {text}")
        
        # 감정 분석
        emotion_summary = analyzer.get_emotion_summary(text)
        
        print(f"  주요 감정: {emotion_summary['analysis_summary']['dominant_emotion']}")
        print(f"  전체 톤: {emotion_summary['analysis_summary']['overall_sentiment']}")
        print(f"  감정 점수: {emotion_summary['emotion_scores']}")
        print()
    
    # 여러 텍스트 분석
    print("=== 여러 텍스트 통합 분석 ===")
    batch_result = analyzer.analyze_multiple_texts(test_texts)
    print(f"전체 주요 감정: {batch_result['overall_dominant_emotion']}")
    print(f"전체 톤: {batch_result['overall_sentiment']}")
    print()


def test_topic_analysis():
    """토픽 분석 테스트"""
    print("=== 토픽 분석 테스트 ===")
    
    analyzer = TopicAnalyzer()
    
    # 테스트 텍스트들
    test_texts = [
        "프로그래밍과 코딩에 대해 배웠습니다. 알고리즘과 데이터 구조가 흥미로웠습니다.",
        "비즈니스와 마케팅 전략에 대한 새로운 아이디어를 얻었습니다.",
        "건강과 웰빙에 대한 정보가 유용했습니다. 운동과 식단 관리가 중요합니다."
    ]
    
    # 토픽 분석
    result = analyzer.get_topic_summary(test_texts)
    
    print(f"상위 키워드: {result['top_keywords'][:10]}")
    print(f"카테고리별 분류: {result['categorized_keywords']}")
    print(f"키워드 다양성: {result['keyword_diversity']:.2f}")
    
    # 개별 텍스트 토픽 제안
    print("\n=== 개별 텍스트 토픽 제안 ===")
    for i, text in enumerate(test_texts, 1):
        suggestions = analyzer.suggest_topics(text)
        print(f"텍스트 {i}: {suggestions}")
    
    print()


def test_persona_generation():
    """페르소나 생성 테스트"""
    print("=== 페르소나 생성 테스트 ===")
    
    generator = PersonaGenerator()
    
    # 테스트 사용자 데이터
    test_user_data = {
        "id": "test_user_001",
        "name": "김독서",
        "books": [
            {
                "title": "프로그래밍의 정석",
                "review": "정말 훌륭한 책입니다! 프로그래밍에 대한 깊은 이해를 얻었고, 특히 알고리즘 부분이 흥미로웠습니다. 이 책을 통해 코딩 실력이 크게 향상되었습니다.",
                "rating": 5,
                "emotion": "excited",
                "emotion_score": 9,
                "genre": "technology"
            },
            {
                "title": "마음의 평화",
                "review": "마음의 평화를 찾는 방법에 대해 깊이 생각해보게 되었습니다. 명상과 마음챙김의 중요성을 깨달았고, 일상에서 실천할 수 있는 방법들을 배웠습니다.",
                "rating": 4,
                "emotion": "calm",
                "emotion_score": 7,
                "genre": "philosophy"
            }
        ],
        "action_lists": [
            {
                "title": "프로그래밍 프로젝트 시작",
                "content": "이번 달에 웹 애플리케이션을 만들어보겠습니다. React와 Node.js를 사용해서 독서 관리 앱을 개발하고 싶습니다.",
                "status": "진행중"
            },
            {
                "title": "명상 습관 만들기",
                "content": "매일 아침 10분씩 명상을 하면서 마음의 평화를 찾아보겠습니다. 스트레스 관리에도 도움이 될 것 같습니다.",
                "status": "진행전"
            }
        ]
    }
    
    # 페르소나 생성
    persona = generator.generate_persona(test_user_data)
    
    print(f"사용자: {persona['name']}")
    print(f"페르소나 설명: {persona['persona_description']}")
    print(f"성격 특성: {', '.join(persona['personality_traits'])}")
    print(f"의사소통 스타일: {persona['communication_style']['overall_style']}")
    print(f"성장 영역: {', '.join(persona['growth_areas'])}")
    
    # 페르소나 저장 테스트
    output_path = "test_persona.json"
    if generator.save_persona(persona, output_path):
        print(f"페르소나가 {output_path}에 저장되었습니다.")
        
        # 저장된 페르소나 로드 테스트
        loaded_persona = generator.load_persona(output_path)
        if loaded_persona:
            print("페르소나 로드 성공!")
        
        # 테스트 파일 삭제
        try:
            os.remove(output_path)
            print("테스트 파일이 삭제되었습니다.")
        except:
            pass
    
    print()


def main():
    """메인 테스트 함수"""
    print("🤖 페르소나 시스템 테스트 시작\n")
    
    try:
        # 각 모듈 테스트
        test_text_preprocessing()
        test_emotion_analysis()
        test_topic_analysis()
        test_persona_generation()
        
        print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류가 발생했습니다: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 