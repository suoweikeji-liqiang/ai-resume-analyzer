import requests
import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from functools import wraps
import streamlit as st
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIException(Exception):
    """API调用异常"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

class RobustAPIClient:
    """稳定的API客户端，包含重试机制、错误处理和降级策略"""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3, timeout: int = 30):
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # 重试配置
        self.retry_delays = [1, 2, 4]  # 指数退避：1秒、2秒、4秒
        self.retry_status_codes = [429, 500, 502, 503, 504]  # 需要重试的状态码
        
        # 降级策略配置
        self.fallback_models = [
            "deepseek/deepseek-chat-v3-0324:free",
            "deepseek/deepseek-r1:free",
            "qwen/qwen3-32b:free",
            "google/gemini-2.0-flash-exp:free"
        ]
        
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """创建带有重试策略的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=self.retry_status_codes,
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo/resume-analyzer",
            "X-Title": "Resume Analyzer"
        }
        
        # 只有在有API密钥时才添加Authorization头部
        if self.api_key and self.api_key != "free_model":
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        return headers
    
    def _prepare_request_data(self, prompt: str, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """准备请求数据"""
        return {
            "model": model_config['model'],
            "messages": [
                {"role": "system", "content": "你是一个专业的HR助手，擅长分析简历并给出客观评价。请严格按照JSON格式返回结果。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": model_config.get('temperature', 0.7),
            "max_tokens": model_config.get('max_tokens', 2000)
        }
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理API响应"""
        if response.status_code == 200:
            try:
                result_data = response.json()
                result_text = result_data['choices'][0]['message']['content']
                
                # 清理可能的markdown格式
                if "```json" in result_text:
                    result_text = result_text.split("```json")[1].split("```")[0]
                elif "```" in result_text:
                    result_text = result_text.split("```")[1]
                
                # 解析JSON
                parsed_result = json.loads(result_text.strip())
                return parsed_result
                
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                logger.error(f"响应解析失败: {e}")
                raise APIException(f"响应格式错误: {str(e)}", response.status_code, response.text[:200])
        else:
            # 处理错误响应
            try:
                error_detail = response.json().get('error', {}).get('message', '未知错误')
            except:
                error_detail = f"HTTP {response.status_code}"
            
            raise APIException(f"API调用失败: {error_detail}", response.status_code, response.text[:200])
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
            
        # 网络错误重试
        if isinstance(exception, requests.exceptions.RequestException):
            return True
            
        # 特定状态码重试
        if isinstance(exception, APIException):
            return exception.status_code in self.retry_status_codes
            
        return False
    
    def _log_retry(self, attempt: int, exception: Exception, delay: float):
        """记录重试信息"""
        logger.warning(f"API调用失败 (尝试 {attempt}/{self.max_retries}): {str(exception)}")
        if attempt < self.max_retries:
            logger.info(f"将在 {delay} 秒后重试...")
            if hasattr(st, 'warning'):
                st.warning(f"API调用失败，{delay}秒后重试... (尝试 {attempt}/{self.max_retries})")
    
    def call_api_with_retry(self, prompt: str, model_config: Dict[str, Any], candidate_name: str) -> Dict[str, Any]:
        """带重试机制的API调用"""
        headers = self._get_headers()
        data = self._prepare_request_data(prompt, model_config)
        
        last_exception = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"API调用尝试 {attempt}/{self.max_retries}")
                
                # 记录开始时间
                start_time = time.time()
                
                response = self.session.post(
                    self.base_url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )
                
                # 计算响应时间
                response_time = time.time() - start_time
                
                result = self._handle_response(response)
                result['candidate_name'] = candidate_name
                result['_response_time'] = response_time  # 添加响应时间信息
                
                # 成功时清除之前的警告
                if attempt > 1 and hasattr(st, 'success'):
                    st.success(f"✅ API调用成功 (尝试 {attempt} 次)")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if self._should_retry(e, attempt):
                    delay = self.retry_delays[min(attempt - 1, len(self.retry_delays) - 1)]
                    self._log_retry(attempt, e, delay)
                    time.sleep(delay)
                else:
                    break
        
        # 所有重试都失败了，尝试降级策略
        return self._fallback_strategy(prompt, model_config, candidate_name, last_exception)
    
    def _fallback_strategy(self, prompt: str, model_config: Dict[str, Any], candidate_name: str, last_exception: Exception) -> Dict[str, Any]:
        """降级策略：尝试其他模型或返回默认结果"""
        logger.error(f"主要API调用失败，启动降级策略: {str(last_exception)}")
        
        # 如果当前不是免费模型，尝试切换到免费模型
        current_model = model_config.get('model', '')
        if current_model not in self.fallback_models:
            for fallback_model in self.fallback_models:
                try:
                    logger.info(f"尝试降级模型: {fallback_model}")
                    if hasattr(st, 'info'):
                        st.info(f"🔄 尝试备用模型: {fallback_model}")
                    
                    fallback_config = model_config.copy()
                    fallback_config['model'] = fallback_model
                    
                    # 使用更短的超时时间进行快速尝试
                    original_timeout = self.timeout
                    self.timeout = 15
                    
                    headers = self._get_headers()
                    data = self._prepare_request_data(prompt, fallback_config)
                    
                    response = self.session.post(
                        self.base_url,
                        headers=headers,
                        json=data,
                        timeout=self.timeout
                    )
                    
                    result = self._handle_response(response)
                    result['candidate_name'] = candidate_name
                    
                    # 恢复原始超时时间
                    self.timeout = original_timeout
                    
                    if hasattr(st, 'success'):
                        st.success(f"✅ 备用模型调用成功: {fallback_model}")
                    
                    return result
                    
                except Exception as e:
                    logger.warning(f"降级模型 {fallback_model} 也失败了: {str(e)}")
                    self.timeout = original_timeout
                    continue
        
        # 所有降级策略都失败，返回默认结果
        logger.error("所有API调用策略都失败，返回默认评分")
        if hasattr(st, 'error'):
            st.error(f"❌ API服务暂时不可用，使用默认评分。错误信息: {str(last_exception)}")
        
        return self._get_default_scores(candidate_name)
    
    def _get_default_scores(self, candidate_name: str) -> Dict[str, Any]:
        """返回默认评分（当所有API调用都失败时）"""
        return {
            'candidate_name': candidate_name,
            'education_score': 7,
            'experience_score': 6,
            'skills_score': 7,
            'projects_score': 6,
            'overall_score': 6.5,
            'education_evaluation': 'AI分析服务暂时不可用，无法对教育背景进行详细评估。建议人工审核学历层次、院校背景、专业匹配度等关键信息。',
            'experience_evaluation': 'AI分析服务暂时不可用，无法对工作经验进行深入分析。建议重点关注工作年限、职业发展轨迹、行业相关性等要素。',
            'skills_evaluation': 'AI分析服务暂时不可用，无法评估技能匹配情况。建议仔细核查核心技能、技术能力、相关认证等关键技能点。',
            'projects_evaluation': 'AI分析服务暂时不可用，无法分析项目经验价值。建议重点评估项目复杂度、承担角色、技术难度和创新性等方面。',
            'overall_evaluation': 'AI分析服务暂时不可用，无法进行综合素质评估。建议通过面试等方式全面了解候选人的职业素养和发展潜力。',
            'strengths': ['AI分析服务暂时不可用，建议人工识别候选人的核心优势', '请通过详细面试了解候选人的专业能力和个人特质', '建议重点关注简历中的亮点和成就'],
            'concerns': ['AI分析功能暂时不可用，可能影响评估准确性', '建议增加人工审核环节确保评估质量', '请注意核实简历信息的真实性和完整性'],
            'summary': '由于AI分析服务暂时不可用，无法提供详细的候选人评估报告。建议采用传统的人工审核方式，重点关注教育背景、工作经验、技能匹配度、项目经验等关键维度，并通过面试深入了解候选人的综合素质和发展潜力。',
            'interview_suggestions': 'AI分析服务不可用期间，建议面试官重点关注：1）核心技能的深度验证；2）项目经验的真实性和复杂度；3）学习能力和适应性评估；4）沟通协作能力考察。',
            'development_potential': '无法通过AI分析评估发展潜力，建议通过面试深入了解候选人的学习意愿、职业规划、技能提升计划等方面，人工判断其成长空间和发展前景。'
        }
    
    def health_check(self, model: str = "deepseek/deepseek-chat-v3-0324:free") -> Dict[str, Any]:
        """API健康检查"""
        try:
            # 检查是否有有效的API密钥
            if not self.api_key or self.api_key == "free_model":
                return {
                    "status": "unhealthy",
                    "error": "需要有效的API密钥才能进行健康检查",
                    "timestamp": time.time()
                }
            
            # 发送一个简单的测试请求
            test_data = {
                "model": model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            start_time = time.time()
            response = self.session.post(
                self.base_url,
                headers=self._get_headers(),
                json=test_data,
                timeout=10
            )
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """装饰器：为函数添加重试机制"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"函数 {func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                    else:
                        logger.error(f"函数 {func.__name__} 所有重试都失败了")
            
            raise last_exception
        return wrapper
    return decorator