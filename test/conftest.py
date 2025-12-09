"""
pytest configuration file
테스트 실행 시 프로젝트 루트를 Python path에 추가합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# pytest test/ -v 사용으로 테스트 가능