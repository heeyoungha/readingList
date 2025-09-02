#!/usr/bin/env python3
"""
페르소나 시스템 백엔드 실행 스크립트
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import uvicorn
from config import settings


def main():
    """백엔드 서버 실행"""
    print("🤖 페르소나 시스템 백엔드 시작...")
    print(f"서버 주소: http://{settings.host}:{settings.port}")
    print(f"API 문서: http://{settings.host}:{settings.port}/docs")
    print("Ctrl+C로 서버를 중지할 수 있습니다.\n")
    
    try:
        uvicorn.run(
            "backend.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\n\n🛑 서버가 중지되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 