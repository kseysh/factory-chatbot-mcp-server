from src.config import setup_logging
from fastmcp import FastMCP
from src.electricity_tools import register_electricity_tools
from src.forecast_tools import register_forecast_tools
from src.datetime_tools import register_datetime_tools

# MCP 서버 인스턴스 생성
mcp_server = FastMCP(
    name="Inha Campus Electricity Server",
    instructions="""
    이 서버는 인하대학교 내 건물들의 누적 유효 전력량(KWH) 정보를 조회 및 분석하는 MCP 서버입니다.
    """
)

# 도구 등록
def register_all_tools():
    register_electricity_tools(mcp_server)
    register_forecast_tools(mcp_server)
    register_datetime_tools(mcp_server)

# 서버 실행
if __name__ == "__main__":
    # 로깅 초기화
    setup_logging()
    register_all_tools()
    # 서버 실행
    mcp_server.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp",
        log_level="debug",
    )