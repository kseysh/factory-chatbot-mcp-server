from .config import get_logger
from .services import service_get_current_time

logger = get_logger(__name__)

def register_datetime_tools(mcp_server):
    """현재 날짜 및 시간 관련 도구들을 MCP 서버에 등록"""

    @mcp_server.tool(
        name="get_current_time",
        description="현재 로컬 시스템의 날짜와 시간 정보를 조회합니다."
    )
    async def get_current_time() -> str:
        """현재 로컬 시스템의 날짜와 시간 정보를 반환"""
        try:
            logger.info("get_current_time Tool called")
            result = service_get_current_time()
            logger.info(f"get_current_time result: {result}")
            return result
        except Exception as e:
            logger.error(f"get_current_time error: {str(e)}", exc_info=True)
            raise