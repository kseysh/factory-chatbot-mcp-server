from .config import get_logger
from .services import service_control_power
import json

logger = get_logger(__name__)

def register_power_control_tools(mcp_server):
    """전력 제어 관련 도구들을 MCP 서버에 등록"""

    @mcp_server.tool(
        name="control_power",
        description="전력 제어 시스템에 명령을 전송합니다. 전력 사용을 중단하거나 재개할 수 있습니다."
    )
    async def control_power(action: str) -> str:
        """
        전력 제어 시스템에 명령을 전송합니다.

        Args:
        - action: 제어 명령 ('on' 또는 'off')
            - 'off': 전력 사용 중단
            - 'on': 전력 사용 재개

        Returns:
        - JSON 형식의 제어 결과:
        {
            "action": "<명령>",
            "success": <성공 여부 (true/false)>,
            "message": "<결과 메시지>"
        }
        """
        try:
            logger.info(f"control_power called: action={action}")

            # action 유효성 검증
            if action not in ['on', 'off']:
                return json.dumps({
                    "error": "유효하지 않은 action입니다. 'on' 또는 'off'를 사용하세요."
                }, ensure_ascii=False)

            result = await service_control_power(action)
            logger.info(f"control_power result: {result}")
            return result
        except Exception as e:
            logger.error(f"control_power error: {str(e)}", exc_info=True)
            return json.dumps({"error": f"전력 제어 실패: {str(e)}"}, ensure_ascii=False)
