from src.config import setup_logging
from src.tools import mcp

if __name__ == "__main__":
    # 로깅 초기화
    setup_logging()
    
    # 서버 실행
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
        log_level="debug",
    )