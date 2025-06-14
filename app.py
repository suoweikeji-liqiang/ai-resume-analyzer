import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import PyPDF2
import requests
import os
from dotenv import load_dotenv
import json
import io
from typing import List, Dict, Any
import time
from datetime import datetime
from api_client import RobustAPIClient, APIException
# API秘钥检查功能
def check_api_key_status(api_client: RobustAPIClient):
    """检查API秘钥状态，类似cherrystudio的秘钥检查"""
    st.subheader("🔑 API秘钥状态")
    
    # 获取API秘钥信息
    api_key = api_client.api_key if hasattr(api_client, 'api_key') else None
    base_url = api_client.base_url if hasattr(api_client, 'base_url') else "https://openrouter.ai/api/v1"
    
    if not api_key:
        st.error("❌ 未配置API秘钥")
        st.info("请在环境变量中设置 OPENROUTER_API_KEY")
        return
    
    # 显示秘钥信息（脱敏）
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    st.success(f"✅ API秘钥已配置: {masked_key}")
    st.info(f"🌐 服务端点: {base_url}")
    
    # 模型选择和测试区域
    with st.expander("🔍 API秘钥测试", expanded=False):
        # 免费模型列表
        free_models = {
            "deepseek/deepseek-chat-v3-0324:free": "🌟 DeepSeek Chat V3",
            "deepseek/deepseek-r1-0528:free": "🔥 DeepSeek R1 (0528)",
            "deepseek/deepseek-r1:free": "🚀 DeepSeek R1",
            "qwen/qwen3-32b:free": "🎯 Qwen3-32B",
            "google/gemini-2.0-flash-exp:free": "✨ Gemini 2.0 Flash (实验版)"
        }
        
        selected_model = st.selectbox(
            "选择用于测试的模型:",
            options=list(free_models.keys()),
            format_func=lambda x: free_models[x],
            key="test_model_select"
        )
        
        if st.button("🚀 开始测试", key="start_test"):
                with st.spinner("检查中..."):
                    try:
                        # 发送简单的测试请求
                        start_time = time.time()
                        result = api_client.health_check(selected_model)
                        response_time = time.time() - start_time
                        
                        if result and result.get('status') == 'healthy':
                            st.success(f"✅ 秘钥有效 (响应时间: {response_time:.2f}s)")
                            st.success(f"🤖 测试模型: {free_models[selected_model]}")
                            st.info(f"📊 状态码: {result.get('status_code', 'N/A')}")
                        else:
                            st.error("❌ 秘钥无效或服务不可用")
                            if result and 'error' in result:
                                st.error(f"错误详情: {result['error']}")
                            elif result:
                                st.error(f"状态: {result.get('status', '未知')}")
                                
                    except Exception as e:
                        st.error(f"❌ 检查失败: {str(e)}")
                        if "401" in str(e) or "unauthorized" in str(e).lower():
                            st.error("🔐 秘钥无效，请检查API秘钥是否正确")
                        elif "403" in str(e) or "forbidden" in str(e).lower():
                            st.error("🚫 访问被拒绝，请检查秘钥权限")
                        elif "429" in str(e) or "rate limit" in str(e).lower():
                            st.warning("⏰ 请求频率过高，请稍后再试")
                        else:
                            st.error("🌐 网络连接问题或服务不可用")


    
    # 显示配置信息
    with st.expander("🔧 配置详情"):
        st.code(f"""
API端点: {base_url}
API秘钥: {masked_key}
配置来源: 环境变量 OPENROUTER_API_KEY
""")
        
        st.markdown("""
        **💡 提示:**
        - 确保API秘钥有效且有足够的配额
        - 免费模型通常有请求频率限制
        - 如遇问题，请检查网络连接和秘钥权限
        """)
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pdf_fix import PDFExporter
import base64

# 加载环境变量
load_dotenv()

# 配置页面
st.set_page_config(
    page_title="AI简历智能分析系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/resume-analyzer',
        'Report a bug': 'https://github.com/your-repo/resume-analyzer/issues',
        'About': '# AI简历智能分析系统\n基于OpenRouter免费模型的智能简历分析工具'
    }
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .candidate-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        margin: 0.25rem;
    }
    .score-excellent { background-color: #d4edda; color: #155724; }
    .score-good { background-color: #d1ecf1; color: #0c5460; }
    .score-average { background-color: #fff3cd; color: #856404; }
    .score-poor { background-color: #f8d7da; color: #721c24; }
    
    .ranking-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: white;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .ranking-card:hover {
        transform: translateY(-5px);
    }
    .rank-1 { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
    .rank-2 { background: linear-gradient(135deg, #C0C0C0 0%, #808080 100%); }
    .rank-3 { background: linear-gradient(135deg, #CD7F32 0%, #8B4513 100%); }
    
    .rank-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .candidate-name {
        font-size: 16px;
        margin-bottom: 5px;
    }
    .overall-score {
        font-size: 24px;
        font-weight: bold;
    }
    
    .strengths-section, .concerns-section {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .strength-item {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .concern-item {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 4px;
    }
    .summary-section {
        background-color: #e7f3ff;
        border-left: 4px solid #007bff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
        font-style: italic;
    }
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

class ResumeAnalyzer:
    def __init__(self, api_key=None):
        self.api_client = self._setup_api_client(api_key)
        self.pdf_exporter = PDFExporter()
        
    def _setup_api_client(self, api_key=None) -> RobustAPIClient:
        """设置稳定的API客户端"""
        # 优先使用传入的API Key，其次使用session state中的，最后使用环境变量
        final_api_key = None
        
        if api_key:
            final_api_key = api_key
        elif hasattr(st.session_state, 'api_key') and st.session_state.api_key:
            final_api_key = st.session_state.api_key
        else:
            env_api_key = os.getenv('OPENROUTER_API_KEY')
            if env_api_key:
                final_api_key = env_api_key
            else:
                # 使用免费模型，不需要API密钥
                final_api_key = "free_model"
        
        # 创建稳定的API客户端，包含重试机制和降级策略
        return RobustAPIClient(
            api_key=final_api_key,
            max_retries=3,  # 最大重试次数
            timeout=30      # 请求超时时间
        )
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """从PDF文件中提取文本"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"PDF解析失败: {str(e)}")
            return ""
    
    def analyze_resume_with_ai(self, resume_text: str, candidate_name: str) -> Dict[str, Any]:
        """使用稳定的API客户端分析简历"""
        if not self.api_client:
            return self._get_default_scores(candidate_name)
        
        # API调用开始
        
        # 获取模型配置
        model_config = st.session_state.get('model_config', {
            'model': 'deepseek/deepseek-chat-v3-0324:free',
            'temperature': 0.3,
            'max_tokens': 2000
        })
        
        # 获取岗位配置
        job_config = st.session_state.get('job_config', {})
        
        # 构建岗位要求部分
        job_context = ""
        if job_config.get('job_title') or job_config.get('job_requirements'):
            job_context = f"""
            
            招聘岗位信息：
            - 岗位名称：{job_config.get('job_title', '未指定')}
            - 公司名称：{job_config.get('company_info', '未指定')}
            - 薪资范围：{job_config.get('salary_range', '未指定')}
            - 工作地点：{job_config.get('work_location', '未指定')}
            - 岗位要求：{job_config.get('job_requirements', '未指定')}
            
            请结合以上岗位要求来评估候选人的匹配度。
            """
        
        prompt = f"""
        作为一名资深HR专家和技术面试官，请对以下简历进行深度分析和评估。请从专业角度提供详细、客观、有建设性的评价。
        
        简历内容：
        {resume_text}
        {job_context}
        
        请按照以下5个维度进行详细分析和评分（1-10分，其中1-3分为不合格，4-6分为一般，7-8分为良好，9-10分为优秀）：
        
        1. 教育背景 (education_score): 
           - 学历层次与岗位要求的匹配度
           - 院校声誉和专业排名
           - 专业课程与工作内容的相关性
           - 学习成绩、获奖情况、学术活动参与度
           - 持续学习能力（如在职教育、认证等）
        
        2. 工作经验 (experience_score):
           - 工作年限与岗位要求的匹配度
           - 职业发展轨迹的合理性和上升趋势
           - 行业背景与目标岗位的相关性
           - 公司规模、知名度对经验价值的影响
           - 跨行业、跨职能经验的加分项
           - 工作稳定性分析（跳槽频率、在职时长）
        
        3. 技能匹配 (skills_score):
           - 核心技术技能与岗位要求的匹配程度
           - 技能的深度和广度评估
           - 新技术学习和应用能力
           - 相关认证、证书的含金量
           - 软技能（沟通、协作、解决问题等）
           - 语言能力（如适用）
        
        4. 项目经验 (projects_score):
           - 项目规模、复杂度和技术难度
           - 在项目中承担的角色和职责
           - 项目成果和业务价值
           - 技术创新和解决方案的独特性
           - 团队协作和领导能力体现
           - 项目管理和执行能力
        
        5. 综合素质 (overall_score):
           - 职业素养和工作态度
           - 学习能力和适应性
           - 沟通表达和人际交往能力
           - 领导潜质和团队合作精神
           - 抗压能力和问题解决能力
           - 职业规划的清晰度和合理性
        
        请提供详细的JSON格式分析结果，每个评价字段要求至少50字的详细分析：
        
        {{
            "education_score": 分数,
            "experience_score": 分数,
            "skills_score": 分数,
            "projects_score": 分数,
            "overall_score": 分数,
            "education_evaluation": "详细分析教育背景的优势和不足，包括学历匹配度、院校水平、专业相关性等方面的具体评价",
            "experience_evaluation": "深入分析工作经验的质量，包括职业发展轨迹、行业相关性、公司背景、工作稳定性等",
            "skills_evaluation": "全面评估技能匹配情况，包括核心技能掌握程度、技能广度深度、学习能力、认证情况等",
            "projects_evaluation": "详细评价项目经验的价值，包括项目复杂度、承担角色、技术难度、创新性、团队协作等",
            "overall_evaluation": "综合评估候选人的整体素质，包括职业素养、发展潜力、适应能力、沟通协作等软实力",
            "strengths": ["具体优势1的详细描述", "具体优势2的详细描述", "具体优势3的详细描述"],
            "concerns": ["具体关注点1的详细说明", "具体关注点2的详细说明", "具体关注点3的详细说明"],
            "summary": "提供一个全面的总结评价，包括候选人的整体水平、与岗位的匹配度、发展潜力、建议薪资范围、面试重点关注事项等",
            "interview_suggestions": "针对此候选人的面试建议，包括重点考察的技能点、可能的面试问题方向、需要验证的能力等",
            "development_potential": "分析候选人的发展潜力和成长空间，包括技能提升方向、职业发展路径建议等"
        }}
        
        注意：请确保分析客观、专业、有建设性，避免主观偏见，重点关注与岗位要求的匹配度。
        """
        
        # 使用稳定的API客户端进行调用，包含重试机制和降级策略
        try:
            result = self.api_client.call_api_with_retry(prompt, model_config, candidate_name)
            # API调用成功
            response_time = result.pop('_response_time', 1.0)
            return result
        except Exception as e:
            # API调用失败，使用默认评分
            return self._get_default_scores(candidate_name)
    
    def _get_default_scores(self, candidate_name: str) -> Dict[str, Any]:
        """返回默认评分（当AI不可用时）"""
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
    
    def export_candidate_to_pdf(self, candidate_data: Dict[str, Any], interview_questions: List[tuple]) -> bytes:
        """导出单个候选人的分析结果和面试问题为PDF"""
        return self.pdf_exporter.export_candidate_to_pdf(candidate_data, interview_questions)

def main():
    # 持久化缓存文件路径
    cache_file = '.streamlit_cache.json'
    
    # 加载持久化缓存
    def load_cache():
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            'api_key_cache': '',
            'job_config_cache': {
                'job_title': '',
                'job_requirements': '',
                'company_info': '',
                'salary_range': '',
                'work_location': ''
            }
        }
    
    # 保存持久化缓存
    def save_cache(cache_data):
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    # 初始化session state缓存
    if 'cache_loaded' not in st.session_state:
        cached_data = load_cache()
        st.session_state.api_key_cache = cached_data.get('api_key_cache', '')
        st.session_state.job_config_cache = cached_data.get('job_config_cache', {
            'job_title': '',
            'job_requirements': '',
            'company_info': '',
            'salary_range': '',
            'work_location': ''
        })
        st.session_state.cache_loaded = True
    
    if 'api_key_cache' not in st.session_state:
        st.session_state.api_key_cache = ''
    if 'job_config_cache' not in st.session_state:
        st.session_state.job_config_cache = {
            'job_title': '',
            'job_requirements': '',
            'company_info': '',
            'salary_range': '',
            'work_location': ''
        }
    
    # 主标题区域
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI简历智能分析系统 <span style="font-size: 0.6em; opacity: 0.8;">v1.3.0</span></h1>
        <p>基于OpenRouter免费模型的专业简历评估工具</p>
        <p><small>支持批量分析 • 多维度评分 • 智能对比 • 可视化展示</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示当前时间和系统状态
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 当前时间", datetime.now().strftime("%H:%M:%S"))
    with col2:
        # 动态显示当前选择的模型
        current_model = st.session_state.get('model_config', {}).get('model', 'deepseek/deepseek-chat-v3-0324:free')
        model_display_names = {
            "deepseek/deepseek-r1-0528:free": "DeepSeek-R1",
            "deepseek/deepseek-chat-v3-0324:free": "DeepSeek-Chat-V3",
            "meta-llama/llama-3.1-8b-instruct:free": "Llama-3.1-8B", 
            "google/gemma-2-9b-it:free": "Gemma-2-9B",
            "mistralai/mistral-7b-instruct:free": "Mistral-7B",
            "qwen/qwen-2.5-7b-instruct:free": "Qwen-2.5-7B",
            "huggingfaceh4/zephyr-7b-beta:free": "Zephyr-7B",
            "openchat/openchat-7b:free": "OpenChat-7B",
            "anthropic/claude-3-5-sonnet": "Claude-3.5-Sonnet",
            "openai/gpt-4o": "GPT-4o",
            "openai/gpt-3.5-turbo": "GPT-3.5-Turbo",
            "google/gemini-pro": "Gemini-Pro"
        }
        display_name = model_display_names.get(current_model, current_model.split('/')[-1].split(':')[0])
        st.metric("🔧 AI模型", display_name)
    with col3:
        st.metric("💰 费用", "免费")
    with col4:
        if 'analysis_results' in st.session_state:
            st.metric("📊 已分析", f"{len(st.session_state.analysis_results)}份")
        else:
            st.metric("📊 已分析", "0份")
    
    # 初始化分析器
    api_key = st.session_state.get('api_key', '')
    analyzer = ResumeAnalyzer(api_key if api_key else None)
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
        st.header("⚙️ 系统配置")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 招聘需求配置（突出显示）
        st.subheader("👥 招聘需求配置")
        st.markdown("**💼 请先配置招聘需求，系统将根据此需求分析简历匹配度**")
        
        # 岗位信息
        job_title = st.text_input(
            "🎯 招聘岗位", 
            value=st.session_state.job_config_cache['job_title'],
            placeholder="例如：高级Python开发工程师", 
            help="输入具体的招聘岗位名称"
        )
        
        # 岗位要求
        job_requirements = st.text_area(
            "📋 岗位要求", 
            value=st.session_state.job_config_cache['job_requirements'],
            placeholder="例如：\n- 3年以上Python开发经验\n- 熟悉Django/Flask框架\n- 有数据库设计经验\n- 良好的团队协作能力",
            height=120,
            help="详细描述岗位的技能要求、经验要求等"
        )
        
        # 公司信息
        company_info = st.text_input(
            "🏢 公司名称", 
            value=st.session_state.job_config_cache['company_info'],
            placeholder="例如：科技创新有限公司", 
            help="输入公司名称"
        )
        
        # 薪资范围
        salary_range = st.text_input(
            "💰 薪资范围", 
            value=st.session_state.job_config_cache['salary_range'],
            placeholder="例如：15K-25K", 
            help="输入薪资范围"
        )
        
        # 工作地点
        work_location = st.text_input(
            "📍 工作地点", 
            value=st.session_state.job_config_cache['work_location'],
            placeholder="例如：北京市朝阳区", 
            help="输入工作地点"
        )
        
        # 保存招聘需求到缓存和session state
        job_config_data = {
            'job_title': job_title,
            'job_requirements': job_requirements,
            'company_info': company_info,
            'salary_range': salary_range,
            'work_location': work_location
        }
        
        # 更新缓存
        st.session_state.job_config_cache.update(job_config_data)
        
        # 保存到持久化缓存
        cache_data = {
            'api_key_cache': st.session_state.api_key_cache,
            'job_config_cache': st.session_state.job_config_cache
        }
        save_cache(cache_data)
        
        # 更新当前配置
        if 'job_config' not in st.session_state:
            st.session_state.job_config = {}
        st.session_state.job_config.update(job_config_data)
        
        # 显示配置预览
        if job_title or job_requirements:
            with st.expander("👀 配置预览"):
                if job_title:
                    st.write(f"**岗位：** {job_title}")
                if company_info:
                    st.write(f"**公司：** {company_info}")
                if salary_range:
                    st.write(f"**薪资：** {salary_range}")
                if work_location:
                    st.write(f"**地点：** {work_location}")
                if job_requirements:
                    st.write(f"**要求：** {job_requirements[:100]}..." if len(job_requirements) > 100 else f"**要求：** {job_requirements}")
        
        st.markdown("---")
        
        # API配置区域（收起）
        with st.expander("🔑 API配置", expanded=False):
            # API Key输入（带缓存功能）
            api_key = st.text_input(
                "OpenRouter API Key",
                value=st.session_state.api_key_cache,
                type="password",
                placeholder="输入您的OpenRouter API Key (必需)",
                help="OpenRouter所有模型（包括免费模型）都需要配置API Key。获取API Key: https://openrouter.ai/keys"
            )
            
            # 保存API Key到缓存和session state
            if api_key:
                st.session_state.api_key_cache = api_key
                st.session_state.api_key = api_key
                # 保存到持久化缓存
                cache_data = {
                    'api_key_cache': st.session_state.api_key_cache,
                    'job_config_cache': st.session_state.job_config_cache
                }
                save_cache(cache_data)
                st.success("✅ API Key已配置并缓存")
            elif st.session_state.api_key_cache:
                st.session_state.api_key = st.session_state.api_key_cache
                st.info("💡 使用缓存的API Key")
            else:
                st.session_state.api_key = None
                st.warning("⚠️ 请配置OpenRouter API Key以使用AI模型")
        
        # API状态监控
        # API秘钥检查功能
        if analyzer.api_client and hasattr(analyzer.api_client, 'api_key') and analyzer.api_client.api_key:
            check_api_key_status(analyzer.api_client)
        
        # 模型配置区域（收起）
        with st.expander("🤖 AI模型配置", expanded=False):
            # OpenRouter免费模型列表
            free_models = {
                "deepseek/deepseek-chat-v3-0324:free": "🌟 DeepSeek Chat V3",
                "deepseek/deepseek-r1-0528:free": "🔥 DeepSeek R1 (0528)",
                "deepseek/deepseek-r1:free": "🚀 DeepSeek R1",
                "deepseek/deepseek-r1-0528-qwen3-8b:free": "💫 DeepSeek R1 Qwen3-8B",
                "qwen/qwen3-32b:free": "🎯 Qwen3-32B",
                "qwen/qwen3-235b-a22b:free": "⭐ Qwen3-235B-A22B",
                "qwen/qwen3-30b-a3b:free": "💎 Qwen3-30B-A3B",
                "qwen/qwen3-8b:free": "🔷 Qwen3-8B",
                "google/gemini-2.0-flash-exp:free": "✨ Gemini 2.0 Flash (实验版)"
            }
            
            paid_models = {
                "anthropic/claude-3-5-sonnet": "🧠 Claude-3.5-Sonnet (付费)",
                "openai/gpt-4o": "🤖 GPT-4o (付费)",
                "openai/gpt-3.5-turbo": "⚡ GPT-3.5-Turbo (付费)",
                "google/gemini-pro": "✨ Gemini-Pro (付费)"
            }
            
            # 根据是否有API Key显示不同的模型选项
            if st.session_state.api_key:
                all_models = {**free_models, **paid_models}
                model_help = "已配置API Key，可使用所有模型。免费模型无额外费用，付费模型按使用量计费。"
            else:
                all_models = free_models
                model_help = "⚠️ 需要配置API Key才能使用模型。OpenRouter所有模型都需要API Key认证。"
            
            selected_model = st.selectbox(
                "选择AI模型",
                options=list(all_models.keys()),
                format_func=lambda x: all_models[x],
                index=0,
                help=model_help
            )
            
            # 手动输入模型选项
            use_custom_model = st.checkbox("🔧 手动输入模型", help="勾选此项可手动输入自定义模型名称")
            
            if use_custom_model:
                custom_model = st.text_input(
                    "自定义模型名称",
                    placeholder="例如: deepseek/deepseek-chat-v3-0324:free",
                    help="输入完整的模型名称，格式通常为: provider/model-name:version"
                )
                if custom_model.strip():
                    selected_model = custom_model.strip()
                    st.info(f"✅ 使用自定义模型: {selected_model}")
            
            final_model = selected_model
            
            # 保存模型配置到session state
            if 'model_config' not in st.session_state:
                st.session_state.model_config = {}
            
            st.session_state.model_config.update({
                'model': final_model
            })
        
        # 模型参数配置（独立expander）
        with st.expander("🔧 高级参数", expanded=False):
            temperature = st.slider("创造性 (Temperature)", 0.0, 1.0, 0.2, 0.1, help="控制AI回答的创造性，值越高越有创意。分析任务建议使用较低值。")
            max_tokens = st.slider("最大输出长度", 1000, 8000, 4000, 500, help="控制AI回答的最大长度。更长的输出可以获得更详细的分析。")
            
            # 更新模型参数到session state
            st.session_state.model_config.update({
                'temperature': temperature,
                'max_tokens': max_tokens
            })
        
        # 添加缓存管理
        with st.expander("🗑️ 缓存管理", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ 清除招聘需求缓存", help="清除已保存的招聘需求信息"):
                    st.session_state.job_config_cache = {
                        'job_title': '',
                        'job_requirements': '',
                        'company_info': '',
                        'salary_range': '',
                        'work_location': ''
                    }
                    # 更新持久化缓存
                    cache_data = {
                        'api_key_cache': st.session_state.api_key_cache,
                        'job_config_cache': st.session_state.job_config_cache
                    }
                    save_cache(cache_data)
                    st.success("✅ 招聘需求缓存已清除")
                    st.rerun()
            with col2:
                if st.button("🗑️ 清除API Key缓存", help="清除已保存的API Key"):
                    st.session_state.api_key_cache = ''
                    st.session_state.api_key = None
                    # 更新持久化缓存
                    cache_data = {
                        'api_key_cache': st.session_state.api_key_cache,
                        'job_config_cache': st.session_state.job_config_cache
                    }
                    save_cache(cache_data)
                    st.success("✅ API Key缓存已清除")
                    st.rerun()
            
            # 显示缓存状态
            st.markdown("**缓存状态:**")
            if st.session_state.api_key_cache:
                st.info(f"🔑 API Key: 已缓存 ({st.session_state.api_key_cache[:8]}...)")
            else:
                st.info("🔑 API Key: 未缓存")
            
            if any(st.session_state.job_config_cache.values()):
                cached_items = [k for k, v in st.session_state.job_config_cache.items() if v]
                st.info(f"👥 招聘需求: 已缓存 ({len(cached_items)}/5 项)")
            else:
                st.info("👥 招聘需求: 未缓存")
        
        st.markdown("---")
        
        st.markdown("---")
        
        # 演示模式和使用说明
        with st.expander("🎭 演示模式 & 📖 使用说明", expanded=False):
            demo_mode = st.checkbox("启用演示模式", help="使用示例数据进行演示，无需API密钥")
            
            if demo_mode:
                st.success("🎯 演示模式已启用")
                if st.button("📊 加载示例数据", type="primary"):
                    from test_data import get_sample_data
                    st.session_state.analysis_results = get_sample_data()
                    st.success("✅ 示例数据加载完成！")
                    st.balloons()
            
            st.markdown("---")
            st.markdown("""
            **🎭 演示模式**: 快速体验工具功能
            - 无需API密钥
            - 使用预设示例数据
            - 可查看所有功能
            
            **💼 正式模式**: 分析真实简历
            - 需要配置OpenRouter API密钥（所有模型必需）
            - 上传PDF简历文件
            - AI智能分析评分
            
            **💡 使用提示**:
            1. 先配置招聘需求（会自动缓存）
            2. 选择合适的AI模型
            3. 上传简历文件进行分析
            4. 查看评分结果和对比分析
            """)
        
        # 版本信息显示
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; padding: 10px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 8px; color: white; margin-top: 10px;">
                <small>🤖 <strong>AI简历智能分析系统</strong></small><br>
                <small>📦 版本 v1.3.0 | 🚀 基于OpenRouter免费模型</small>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # 主界面
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 上传简历", "📊 评分结果", "📈 对比分析", "🎯 HR初筛指南", "💼 面试官题库"])
    
    with tab1:
        st.header("上传简历文件")
        
        uploaded_files = st.file_uploader(
            "选择PDF简历文件",
            type=['pdf'],
            accept_multiple_files=True,
            help="支持同时上传多个PDF格式的简历文件"
        )
        
        if uploaded_files:
            st.success(f"已上传 {len(uploaded_files)} 个文件")
            
            # 显示上传的文件列表
            for i, file in enumerate(uploaded_files):
                st.write(f"{i+1}. {file.name}")
            
            if st.button("🚀 开始分析", type="primary"):
                # 存储分析结果
                if 'analysis_results' not in st.session_state:
                    st.session_state.analysis_results = []
                
                st.session_state.analysis_results.clear()
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"正在分析: {file.name}")
                    
                    # 提取PDF文本
                    resume_text = analyzer.extract_text_from_pdf(file)
                    
                    if resume_text:
                        # AI分析
                        candidate_name = file.name.replace('.pdf', '')
                        result = analyzer.analyze_resume_with_ai(resume_text, candidate_name)
                        st.session_state.analysis_results.append(result)
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("✅ 分析完成！")
                st.success("所有简历分析完成，请查看评分结果和对比分析。")
    
    with tab2:
        st.header("📊 详细评分结果")
        
        # 安全提取各维度分数的辅助函数
        def safe_get_score(result, score_key, default=0):
            score = result.get(score_key, default)
            try:
                if isinstance(score, str):
                    import re
                    numbers = re.findall(r'\d+\.?\d*', score)
                    if numbers:
                        return float(numbers[0])
                    else:
                        return float(default)
                else:
                    return float(score)
            except (ValueError, TypeError):
                return float(default)
        
        # 调试函数：检查数据结构
        def debug_analysis_results():
            if 'analysis_results' in st.session_state and st.session_state.analysis_results:
                st.write("**调试信息：分析结果数据结构**")
                for i, result in enumerate(st.session_state.analysis_results):
                    with st.expander(f"候选人 {i+1}: {result.get('candidate_name', '未知')} - 数据结构"):
                        st.json(result)
                        st.write("**评分字段检查：**")
                        st.write(f"- education_score: {result.get('education_score', '缺失')} (类型: {type(result.get('education_score', None))})")
                        st.write(f"- experience_score: {result.get('experience_score', '缺失')} (类型: {type(result.get('experience_score', None))})")
                        st.write(f"- skills_score: {result.get('skills_score', '缺失')} (类型: {type(result.get('skills_score', None))})")
                        st.write(f"- projects_score: {result.get('projects_score', '缺失')} (类型: {type(result.get('projects_score', None))})")
                        st.write(f"- overall_score: {result.get('overall_score', '缺失')} (类型: {type(result.get('overall_score', None))})")
        
        if 'analysis_results' in st.session_state and st.session_state.analysis_results:
            # 添加总览统计
            st.subheader("📈 分析总览")
            total_candidates = len(st.session_state.analysis_results)
            # 安全地计算平均分数，处理可能缺失overall_score字段的情况
            valid_scores = []
            for r in st.session_state.analysis_results:
                if 'overall_score' in r:
                    score = r.get('overall_score', 0)
                    # 安全地转换score为数字类型
                    try:
                        if isinstance(score, str):
                            # 尝试从字符串中提取数字
                            import re
                            numbers = re.findall(r'\d+\.?\d*', score)
                            if numbers:
                                numeric_score = float(numbers[0])
                            else:
                                numeric_score = 6.0  # 默认分数
                        else:
                            numeric_score = float(score)
                    except (ValueError, TypeError):
                        numeric_score = 6.0  # 默认分数
                    valid_scores.append(numeric_score)
            avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("👥 候选人数量", total_candidates)
            with col2:
                st.metric("📊 平均得分", f"{avg_score:.1f}")
            with col3:
                # 安全地找到最高得分候选人
                valid_candidates = [r for r in st.session_state.analysis_results if 'overall_score' in r]
                if valid_candidates:
                    def get_numeric_score(candidate):
                        score = candidate.get('overall_score', 0)
                        try:
                            if isinstance(score, str):
                                # 尝试从字符串中提取数字
                                import re
                                numbers = re.findall(r'\d+\.?\d*', score)
                                if numbers:
                                    return float(numbers[0])
                                else:
                                    return 6.0  # 默认分数
                            else:
                                return float(score)
                        except (ValueError, TypeError):
                            return 6.0  # 默认分数
                    
                    best_candidate = max(valid_candidates, key=get_numeric_score)
                    best_score = get_numeric_score(best_candidate)
                    st.metric("🏆 最高得分", f"{best_score:.1f}")
                else:
                    st.metric("🏆 最高得分", "N/A")
            with col4:
                if valid_candidates:
                    def get_numeric_score_col4(candidate):
                        score = candidate.get('overall_score', 0)
                        try:
                            if isinstance(score, str):
                                # 尝试从字符串中提取数字
                                import re
                                numbers = re.findall(r'\d+\.?\d*', score)
                                if numbers:
                                    return float(numbers[0])
                                else:
                                    return 6.0  # 默认分数
                            else:
                                return float(score)
                        except (ValueError, TypeError):
                            return 6.0  # 默认分数
                    
                    best_candidate_col4 = max(valid_candidates, key=get_numeric_score_col4)
                    candidate_name = best_candidate_col4.get('candidate_name', '未知')
                    display_name = candidate_name[:10] + "..." if len(candidate_name) > 10 else candidate_name
                    st.metric("📋 最佳候选人", display_name)
                else:
                    st.metric("📋 最佳候选人", "N/A")
            
            st.markdown("---")
            
            # 候选人详细信息
            for i, result in enumerate(st.session_state.analysis_results):
                # 计算评分等级
                def get_score_class(score):
                    if score >= 8.5: return "score-excellent"
                    elif score >= 7: return "score-good"
                    elif score >= 5: return "score-average"
                    else: return "score-poor"
                
                def get_score_emoji(score):
                    if score >= 8.5: return "🌟"
                    elif score >= 7: return "✅"
                    elif score >= 5: return "⚠️"
                    else: return "❌"
                
                overall_score = result.get('overall_score', 0)
                # 安全地转换overall_score为数字类型
                try:
                    if isinstance(overall_score, str):
                        # 尝试从字符串中提取数字
                        import re
                        numbers = re.findall(r'\d+\.?\d*', overall_score)
                        if numbers:
                            numeric_overall_score = float(numbers[0])
                        else:
                            numeric_overall_score = 6.0  # 默认分数
                    else:
                        numeric_overall_score = float(overall_score)
                except (ValueError, TypeError):
                    numeric_overall_score = 6.0  # 默认分数
                
                with st.expander(f"📋 {result.get('candidate_name', '未知候选人')} {get_score_emoji(numeric_overall_score)} (综合得分: {numeric_overall_score:.1f})", expanded=i==0):
                    st.markdown(f'<div class="candidate-card">', unsafe_allow_html=True)
                    
                    # 评分徽章
                    st.markdown("**🎯 快速评分概览**")
                    score_badges = ""
                    scores = [
                        ("教育", safe_get_score(result, 'education_score', 0)),
                        ("经验", safe_get_score(result, 'experience_score', 0)),
                        ("技能", safe_get_score(result, 'skills_score', 0)),
                        ("项目", safe_get_score(result, 'projects_score', 0)),
                        ("综合", numeric_overall_score)
                    ]
                    
                    for name, score in scores:
                        # 确保score是数字类型
                        numeric_score = float(score) if isinstance(score, str) else score
                        class_name = get_score_class(numeric_score)
                        score_badges += f'<span class="score-badge {class_name}">{name}: {numeric_score:.1f}</span>'
                    
                    st.markdown(score_badges, unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("📊 详细评分")
                        
                        # 评分维度和分数
                        dimensions = [
                            ('🎓 教育背景', safe_get_score(result, 'education_score', 0), result.get('education_evaluation', '暂无评价')),
                            ('💼 工作经验', safe_get_score(result, 'experience_score', 0), result.get('experience_evaluation', '暂无评价')),
                            ('🛠️ 技能匹配', safe_get_score(result, 'skills_score', 0), result.get('skills_evaluation', '暂无评价')),
                            ('🚀 项目经验', safe_get_score(result, 'projects_score', 0), result.get('projects_evaluation', '暂无评价')),
                            ('⭐ 综合素质', overall_score, result.get('overall_evaluation', '暂无评价'))
                        ]
                        
                        for dimension, score, evaluation in dimensions:
                            # 评分显示
                            col_dim, col_score = st.columns([3, 1])
                            with col_dim:
                                st.write(f"**{dimension}**")
                            with col_score:
                                if score >= 8:
                                    st.success(f"**{score}/10**")
                                elif score >= 6:
                                    st.info(f"**{score}/10**")
                                elif score >= 4:
                                    st.warning(f"**{score}/10**")
                                else:
                                    st.error(f"**{score}/10**")
                            
                            # 详细评价（使用折叠区域）
                            with st.container():
                                if st.button(f"查看 {dimension} 详细评价", key=f"btn_{result.get('candidate_name', '未知')}_{dimension}"):
                                    st.info(evaluation)
                                else:
                                    st.caption(f"点击查看 {dimension} 的详细评价...")
                    
                    with col2:
                        st.subheader("🎯 雷达图")
                        
                        # 创建雷达图
                        categories = ['教育背景', '工作经验', '技能匹配', '项目经验', '综合素质']
                        values = [
                            safe_get_score(result, 'education_score', 0),
                            safe_get_score(result, 'experience_score', 0),
                            safe_get_score(result, 'skills_score', 0),
                            safe_get_score(result, 'projects_score', 0),
                            overall_score
                        ]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself',
                            name=result.get('candidate_name', '未知')
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 10]
                                )
                            ),
                            showlegend=True,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # 详细分析
                    st.markdown("---")
                    col3, col4 = st.columns([1, 1])
                    
                    with col3:
                        st.markdown("### ✅ **核心优势**")
                        st.markdown('<div class="strengths-section">', unsafe_allow_html=True)
                        for i, strength in enumerate(result['strengths'], 1):
                            st.markdown(f'<div class="strength-item">💪 {strength}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown("### ⚠️ **需要关注**")
                        st.markdown('<div class="concerns-section">', unsafe_allow_html=True)
                        for i, concern in enumerate(result['concerns'], 1):
                            st.markdown(f'<div class="concern-item">🔍 {concern}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("### 📝 **AI 综合评价**")
                    st.markdown(f'<div class="summary-section">{result["summary"]}</div>', unsafe_allow_html=True)
                    
                    # 面试建议
                    if 'interview_suggestions' in result:
                        st.markdown("### 🎯 **面试建议**")
                        st.markdown(f'<div class="summary-section">{result["interview_suggestions"]}</div>', unsafe_allow_html=True)
                    
                    # 发展潜力
                    if 'development_potential' in result:
                        st.markdown("### 🚀 **发展潜力**")
                        st.markdown(f'<div class="summary-section">{result["development_potential"]}</div>', unsafe_allow_html=True)
                    
                    # PDF导出按钮
                    st.markdown("---")
                    col_export1, col_export2 = st.columns([1, 3])
                    with col_export1:
                        if st.button(f"📄 导出PDF报告", key=f"export_{result.get('candidate_name', '未知')}", type="primary"):
                            # 准备面试问题数据
                            interview_questions = [
                                ("技术问题", [
                                    {"question": "请详细介绍您最有挑战性的技术项目", "focus": "技术深度和解决问题能力"},
                                    {"question": "如何保证代码质量和项目进度的平衡", "focus": "项目管理和质量意识"},
                                    {"question": "遇到技术难题时的解决思路", "focus": "学习能力和思维方式"}
                                ]),
                                ("项目经验", [
                                    {"question": "描述一个您主导的重要项目", "focus": "领导能力和项目管理"},
                                    {"question": "项目中遇到的最大困难及解决方案", "focus": "问题解决能力"},
                                    {"question": "如何与团队成员协作完成项目", "focus": "团队协作能力"}
                                ]),
                                ("综合素质", [
                                    {"question": "您的职业规划和发展目标", "focus": "职业规划和发展潜力"},
                                    {"question": "如何持续学习和提升自己", "focus": "学习能力和自我驱动力"},
                                    {"question": "对我们公司和岗位的了解", "focus": "求职动机和匹配度"}
                                ])
                            ]
                            
                            try:
                                pdf_bytes = analyzer.export_candidate_to_pdf(result, interview_questions)
                                st.download_button(
                                    label="💾 下载PDF报告",
                                    data=pdf_bytes,
                                    file_name=f"{result.get('candidate_name', '未知')}_分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{result.get('candidate_name', '未知')}"
                                )
                                st.success("PDF报告生成成功！")
                            except ImportError as e:
                                st.error(f"缺少必要的依赖库: {str(e)}")
                                st.info("请检查requirements.txt中是否包含reportlab>=3.6.0")
                            except PermissionError as e:
                                st.error(f"文件权限错误: {str(e)}")
                                st.info("部署环境可能限制了文件系统访问权限")
                            except Exception as e:
                                st.error(f"PDF生成失败: {str(e)}")
                                st.info("💡 可能的解决方案：")
                                st.markdown("""
                                - 检查部署环境的字体支持
                                - 确认reportlab库已正确安装
                                - 如果在Streamlit Cloud，请确保fonts目录包含中文字体文件
                                - 查看应用日志获取详细错误信息
                                """)
                    with col_export2:
                        st.caption("点击导出按钮生成包含完整分析结果和面试问题的PDF报告")
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # 关闭candidate-card
        else:
            st.info("请先在'上传简历'标签页中上传并分析简历文件。")
    
    with tab3:
        st.header("🔍 智能对比分析")
        
        # 添加调试开关
        debug_mode = st.checkbox("🔧 显示调试信息", help="显示分析结果的数据结构，用于排查问题")
        if debug_mode:
            debug_analysis_results()
            st.markdown("---")
        
        if 'analysis_results' in st.session_state and len(st.session_state.analysis_results) > 1:
            # 安全提取数字分数的辅助函数
            def safe_get_numeric_score(candidate):
                score = candidate.get('overall_score', 0)
                try:
                    if isinstance(score, str):
                        import re
                        numbers = re.findall(r'\d+\.?\d*', score)
                        if numbers:
                            return float(numbers[0])
                        else:
                            return 6.0
                    else:
                        return float(score)
                except (ValueError, TypeError):
                    return 6.0
            
            # 排序候选人
            sorted_results = sorted(st.session_state.analysis_results, key=safe_get_numeric_score, reverse=True)
            
            # 显示排名概览
            st.subheader("🏆 候选人排名")
            ranking_cols = st.columns(min(len(sorted_results), 3))
            
            for i, result in enumerate(sorted_results[:3]):
                with ranking_cols[i]:
                    rank_emoji = ["🥇", "🥈", "🥉"][i]
                    st.markdown(f"""
                    <div class="ranking-card rank-{i+1}">
                        <div class="rank-header">{rank_emoji} 第 {i+1} 名</div>
                        <div class="candidate-name">{result.get('candidate_name', '未知')}</div>
                        <div class="overall-score">{safe_get_numeric_score(result):.1f} 分</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 创建对比表格
            if not sorted_results:
                st.warning("⚠️ 没有找到有效的分析结果数据")
                return
            
            # 验证数据完整性
            valid_results = []
            for result in sorted_results:
                if isinstance(result, dict) and result.get('candidate_name'):
                    valid_results.append(result)
                else:
                    st.warning(f"⚠️ 发现无效的分析结果数据: {result}")
            
            if not valid_results:
                st.error("❌ 所有分析结果数据都无效，无法生成对比表格")
                return
            
            comparison_data = {
                '排名': [f"#{i+1}" for i in range(len(valid_results))],
                '👤 候选人': [result.get('candidate_name', '未知') for result in valid_results],
                '🎓 教育': [f"{safe_get_score(result, 'education_score', 0):.1f}" for result in valid_results],
                '💼 经验': [f"{safe_get_score(result, 'experience_score', 0):.1f}" for result in valid_results],
                '🛠️ 技能': [f"{safe_get_score(result, 'skills_score', 0):.1f}" for result in valid_results],
                '🚀 项目': [f"{safe_get_score(result, 'projects_score', 0):.1f}" for result in valid_results],
                '⭐ 综合': [f"{safe_get_numeric_score(result):.1f}" for result in valid_results]
            }
            
            # 检查是否所有评分都是默认值
            all_scores = []
            for result in valid_results:
                all_scores.extend([
                    safe_get_score(result, 'education_score', 0),
                    safe_get_score(result, 'experience_score', 0),
                    safe_get_score(result, 'skills_score', 0),
                    safe_get_score(result, 'projects_score', 0)
                ])
            
            if all(score == 0 for score in all_scores):
                st.warning("⚠️ 检测到所有评分都为0，可能是API分析失败或数据解析错误")
                st.info("💡 建议检查：\n- API密钥是否有效\n- 网络连接是否正常\n- 简历内容是否完整")
            
            # 缓存对比表格数据到session_state
            if 'comparison_df' not in st.session_state or st.session_state.get('comparison_data_hash') != hash(str(comparison_data)):
                st.session_state.comparison_df = pd.DataFrame(comparison_data)
                st.session_state.comparison_data_hash = hash(str(comparison_data))
            
            # 显示对比表格
            st.subheader("📊 详细评分对比")
            
            # 添加CSS样式防止高分辨率下的表格抖动
            st.markdown("""
            <style>
            .stDataFrame {
                position: relative !important;
                transform: translateZ(0) !important;
                backface-visibility: hidden !important;
                will-change: auto !important;
            }
            .stDataFrame > div {
                overflow: hidden !important;
                contain: layout style paint !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # 使用固定占位符避免表格抖动
            if 'comparison_table_placeholder' not in st.session_state:
                st.session_state.comparison_table_placeholder = st.empty()
            
            with st.session_state.comparison_table_placeholder.container():
                st.dataframe(
                    st.session_state.comparison_df, 
                    use_container_width=True, 
                    hide_index=True
                )
            
            # 创建对比图表
            st.markdown("---")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📈 各维度评分对比")
                
                # 准备柱状图数据
                chart_data = []
                for result in valid_results:
                    candidate_name = result.get('candidate_name', '未知')
                    chart_data.extend([
                        {'候选人': candidate_name, '维度': '🎓 教育', '得分': safe_get_score(result, 'education_score', 0)},
                        {'候选人': candidate_name, '维度': '💼 经验', '得分': safe_get_score(result, 'experience_score', 0)},
                        {'候选人': candidate_name, '维度': '🛠️ 技能', '得分': safe_get_score(result, 'skills_score', 0)},
                        {'候选人': candidate_name, '维度': '🚀 项目', '得分': safe_get_score(result, 'projects_score', 0)},
                        {'候选人': candidate_name, '维度': '⭐ 综合', '得分': safe_get_numeric_score(result)}
                    ])
                
                chart_df = pd.DataFrame(chart_data)
                
                # 柱状图对比
                fig_bar = px.bar(
                    chart_df,
                    x='维度',
                    y='得分',
                    color='候选人',
                    barmode='group',
                    title='各维度评分详细对比',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_bar.update_layout(
                    height=450,
                    title_font_size=16,
                    xaxis_title="评分维度",
                    yaxis_title="得分 (0-10)",
                    legend_title="候选人"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.subheader("🎯 多维度雷达图对比")
                
                # 多人雷达图对比
                fig_radar = go.Figure()
                
                categories = ['🎓 教育背景', '💼 工作经验', '🛠️ 技能匹配', '🚀 项目经验', '⭐ 综合素质']
                colors = px.colors.qualitative.Set1
                
                for i, result in enumerate(valid_results):
                    values = [
                        safe_get_score(result, 'education_score', 0),
                        safe_get_score(result, 'experience_score', 0),
                        safe_get_score(result, 'skills_score', 0),
                        safe_get_score(result, 'projects_score', 0),
                        safe_get_numeric_score(result)
                    ]
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name=result.get('candidate_name', '未知'),
                        line_color=colors[i % len(colors)],
                        fillcolor=colors[i % len(colors)],
                        opacity=0.6
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 10],
                            tickmode='linear',
                            tick0=0,
                            dtick=2
                        )
                    ),
                    showlegend=True,
                    height=450,
                    title="候选人能力雷达图对比",
                    title_font_size=16
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # 智能推荐分析
            st.markdown("---")
            st.subheader("🤖 AI 智能推荐")
            
            # 生成推荐报告
            top_candidate = valid_results[0]
            st.success(f"**🏆 推荐候选人：{top_candidate.get('candidate_name', '未知')}**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**综合得分：{safe_get_numeric_score(top_candidate):.1f}/10**")
            with col2:
                # 找出最强项
                scores = {
                    '教育': safe_get_score(top_candidate, 'education_score', 0),
                    '经验': safe_get_score(top_candidate, 'experience_score', 0), 
                    '技能': safe_get_score(top_candidate, 'skills_score', 0),
                    '项目': safe_get_score(top_candidate, 'projects_score', 0)
                }
                best_skill = max(scores, key=scores.get)
                st.info(f"**最强项：{best_skill} ({scores[best_skill]:.1f}分)**")
            with col3:
                # 计算优势程度
                if len(valid_results) > 1:
                    advantage = safe_get_numeric_score(top_candidate) - safe_get_numeric_score(valid_results[1])
                    st.info(f"**领先优势：{advantage:.1f}分**")
                else:
                    st.info("**唯一候选人**")
            
            # 详细分析报告
            with st.expander("📋 详细推荐分析报告", expanded=False):
                st.markdown(f"**候选人：{top_candidate.get('candidate_name', '未知')}**")
                st.markdown(f"**推荐理由：**")
                st.write(f"• 综合评分最高：{safe_get_numeric_score(top_candidate):.1f}/10")
                st.write(f"• 核心优势：{top_candidate['summary'][:100]}...")
                
                if len(valid_results) > 1:
                    st.markdown("**与其他候选人对比：**")
                    for i, candidate in enumerate(valid_results[1:3], 2):
                        diff = safe_get_numeric_score(top_candidate) - safe_get_numeric_score(candidate)
                        st.write(f"• 比第{i}名 {candidate.get('candidate_name', '未知')} 高出 {diff:.1f} 分")
            
            # 完整排名表
            st.subheader("📊 完整排名表")
            
            # 计算详细排名数据
            ranking_data = []
            for i, result in enumerate(valid_results):
                # 找出最强项和最弱项
                scores_dict = {
                    '教育': safe_get_score(result, 'education_score', 0),
                    '经验': safe_get_score(result, 'experience_score', 0),
                    '技能': safe_get_score(result, 'skills_score', 0),
                    '项目': safe_get_score(result, 'projects_score', 0)
                }
                best_skill = max(scores_dict, key=scores_dict.get)
                worst_skill = min(scores_dict, key=scores_dict.get)
                
                ranking_data.append({
                    '排名': f"#{i+1}",
                    '候选人': result.get('candidate_name', '未知'),
                    '综合得分': f"{safe_get_numeric_score(result):.1f}",
                    '最强项': f"{best_skill}({scores_dict[best_skill]:.1f})",
                    '待提升': f"{worst_skill}({scores_dict[worst_skill]:.1f})",
                    '推荐度': "🌟🌟🌟🌟🌟" if i == 0 else "🌟🌟🌟🌟" if i == 1 else "🌟🌟🌟" if i == 2 else "🌟🌟"
                })
            
            # 缓存排名表格数据到session_state
            if 'ranking_df' not in st.session_state or st.session_state.get('ranking_data_hash') != hash(str(ranking_data)):
                st.session_state.ranking_df = pd.DataFrame(ranking_data)
                st.session_state.ranking_data_hash = hash(str(ranking_data))
            
            # 使用固定占位符避免表格抖动
            if 'ranking_table_placeholder' not in st.session_state:
                st.session_state.ranking_table_placeholder = st.empty()
            
            with st.session_state.ranking_table_placeholder.container():
                st.dataframe(
                    st.session_state.ranking_df, 
                    use_container_width=True, 
                    hide_index=True
                )
            
        elif 'analysis_results' in st.session_state and len(st.session_state.analysis_results) == 1:
            st.info("只有一个候选人，无法进行对比分析。请上传更多简历文件。")
        else:
            st.info("请先在'上传简历'标签页中上传并分析至少2个简历文件。")
    
    with tab4:
        st.header("🎯 HR初筛指南")
        st.markdown("""专业的HR初筛技巧和标准，帮助您快速识别优质候选人""")
        
        # 初筛流程指南
        st.subheader("📋 初筛标准流程")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""### 🔍 **第一轮：硬性条件筛选**
            
            **教育背景核查：**
            - ✅ 学历要求是否匹配
            - ✅ 专业背景是否相关
            - ✅ 毕业院校层次
            - ✅ 学习成绩和获奖情况
            
            **工作经验验证：**
            - ✅ 工作年限是否达标
            - ✅ 行业经验是否相关
            - ✅ 公司规模和知名度
            - ✅ 职位层级发展轨迹
            
            **技能匹配度：**
            - ✅ 核心技能是否具备
            - ✅ 技术栈是否匹配
            - ✅ 相关认证和证书
            - ✅ 语言能力要求
            """)
        
        with col2:
            st.markdown("""### 💡 **第二轮：软性素质评估**
            
            **职业稳定性：**
            - 🔍 跳槽频率分析
            - 🔍 在职时长统计
            - 🔍 离职原因合理性
            - 🔍 职业发展连贯性
            
            **学习成长能力：**
            - 🔍 技能更新频率
            - 🔍 自我提升意识
            - 🔍 新技术接受度
            - 🔍 持续学习证据
            
            **项目经验质量：**
            - 🔍 项目复杂度评估
            - 🔍 承担角色重要性
            - 🔍 技术难度挑战
            - 🔍 业务价值贡献
            """)
        
        st.markdown("---")
        
        # 初筛问题库
        st.subheader("❓ 初筛关键问题")
        
        # 创建问题分类
        question_categories = {
            "基础信息确认": [
                {
                    "问题": "请简单介绍一下您的教育背景和工作经历？",
                    "目的": "核实简历真实性，了解基本情况",
                    "关注点": "信息一致性、表达清晰度、时间逻辑性",
                    "标准答案": "应包含：学历专业、毕业时间、主要工作经历、职责描述，信息与简历一致"
                },
                {
                    "问题": "您目前的薪资水平和期望薪资是多少？",
                    "目的": "了解薪资匹配度，避免后期谈判困难",
                    "关注点": "期望合理性、涨幅幅度、谈判空间",
                    "标准答案": "期望薪资应在市场合理范围内，涨幅一般不超过30-50%"
                }
            ],
            "技能能力验证": [
                {
                    "问题": "请描述您最擅长的技术栈，以及是如何掌握的？",
                    "目的": "验证技术能力真实性和学习能力",
                    "关注点": "技术深度、学习路径、实践经验",
                    "标准答案": "应包含：具体技术名称、掌握程度、学习方式、实际应用场景"
                },
                {
                    "问题": "在您的项目经验中，遇到过最大的技术挑战是什么？如何解决的？",
                    "目的": "评估问题解决能力和技术深度",
                    "关注点": "问题复杂度、解决思路、学习能力",
                    "标准答案": "应包含：具体问题描述、分析过程、解决方案、经验总结"
                }
            ],
            "职业发展规划": [
                {
                    "问题": "您为什么想要离开当前公司？",
                    "目的": "了解离职动机，评估稳定性",
                    "关注点": "原因合理性、是否有负面情绪、发展需求",
                    "标准答案": "应避免抱怨前公司，重点说明发展需求和职业规划"
                },
                {
                    "问题": "您的3-5年职业规划是什么？",
                    "目的": "评估职业目标清晰度和与岗位匹配度",
                    "关注点": "目标明确性、实现路径、与公司发展匹配",
                    "标准答案": "应包含：明确的职业目标、具体的发展路径、技能提升计划"
                }
            ]
        }
        
        for category, questions in question_categories.items():
            with st.expander(f"📝 {category}", expanded=False):
                for i, q in enumerate(questions, 1):
                    st.markdown(f"**问题 {i}：{q['问题']}**")
                    st.markdown(f"**🎯 提问目的：** {q['目的']}")
                    st.markdown(f"**👀 关注点：** {q['关注点']}")
                    st.markdown(f"**✅ 标准答案：** {q['标准答案']}")
                    st.markdown("---")
        
        # 初筛评分标准
        st.subheader("📊 初筛评分标准")
        
        scoring_criteria = {
            "优秀 (8-10分)": {
                "描述": "完全符合岗位要求，具备突出优势",
                "标准": [
                    "教育背景完全匹配，名校毕业或相关专业优秀",
                    "工作经验丰富，有知名企业或相关行业背景",
                    "技能全面且深入，有相关认证或项目经验",
                    "沟通表达清晰，职业素养高",
                    "职业规划明确，与公司发展方向一致"
                ]
            },
            "良好 (6-7分)": {
                "描述": "基本符合岗位要求，有一定优势",
                "标准": [
                    "教育背景基本匹配，专业相关",
                    "工作经验满足要求，有一定行业经验",
                    "核心技能具备，需要一定培训",
                    "沟通能力良好，学习意愿强",
                    "有基本的职业规划"
                ]
            },
            "一般 (4-5分)": {
                "描述": "勉强达到最低要求，需要重点培养",
                "标准": [
                    "教育背景一般，专业不完全匹配",
                    "工作经验刚好达标，缺乏相关行业经验",
                    "基础技能具备，但需要大量培训",
                    "沟通能力一般，需要指导",
                    "职业规划不够清晰"
                ]
            },
            "不合格 (1-3分)": {
                "描述": "不符合基本要求，不建议录用",
                "标准": [
                    "教育背景不匹配，专业差距较大",
                    "工作经验不足，缺乏相关经验",
                    "技能不匹配，培训成本过高",
                    "沟通能力差，职业素养不足",
                    "无明确职业规划或规划不合理"
                ]
            }
        }
        
        for level, criteria in scoring_criteria.items():
            with st.expander(f"🎯 {level}", expanded=False):
                st.markdown(f"**{criteria['描述']}**")
                for standard in criteria['标准']:
                    st.markdown(f"• {standard}")
    
    with tab5:
        st.header("💼 面试官专业题库")
        st.markdown("""资深面试官必备的专业问题库，涵盖技术、管理、综合素质等多个维度""")
        
        # 面试问题分类
        interview_categories = {
            "技术能力评估": {
                "初级技术问题": [
                    {
                        "问题": "请解释一下您最熟悉的编程语言的核心特性？",
                        "考察点": "技术基础、理解深度、表达能力",
                        "参考答案": "应包含语言特性、适用场景、优缺点对比，体现深度理解",
                        "追问": "与其他语言相比有什么优势？在什么场景下会选择使用？"
                    },
                    {
                        "问题": "描述一下您在项目中使用的技术架构？",
                        "考察点": "架构理解、技术选型、实践经验",
                        "参考答案": "应包含架构图、技术选型理由、性能考虑、扩展性设计",
                        "追问": "为什么选择这种架构？如果重新设计会有什么改进？"
                    }
                ],
                "高级技术问题": [
                    {
                        "问题": "如何设计一个高并发、高可用的系统？",
                        "考察点": "系统设计能力、架构思维、技术深度",
                        "参考答案": "应包含负载均衡、缓存策略、数据库优化、容错机制、监控体系",
                        "追问": "如何处理数据一致性问题？如何进行性能监控和优化？"
                    },
                    {
                        "问题": "请设计一个分布式缓存系统？",
                        "考察点": "分布式系统理解、缓存策略、数据一致性",
                        "参考答案": "应包含一致性哈希、缓存淘汰策略、数据同步、故障恢复",
                        "追问": "如何解决缓存雪崩和缓存穿透问题？"
                    }
                ]
            },
            "项目经验深挖": {
                "项目背景了解": [
                    {
                        "问题": "请详细介绍您参与的最有挑战性的项目？",
                        "考察点": "项目复杂度、承担角色、解决能力",
                        "参考答案": "应包含项目背景、技术难点、个人贡献、最终成果",
                        "追问": "项目中遇到的最大困难是什么？是如何克服的？"
                    },
                    {
                        "问题": "在团队协作中，您是如何处理技术分歧的？",
                        "考察点": "沟通能力、团队协作、技术判断",
                        "参考答案": "应体现理性分析、有效沟通、妥协精神、技术权衡",
                        "追问": "能举个具体的例子吗？最终是如何达成一致的？"
                    }
                ],
                "技术决策能力": [
                    {
                        "问题": "如何进行技术选型？您的决策依据是什么？",
                        "考察点": "技术判断力、决策思路、风险评估",
                        "参考答案": "应包含需求分析、技术对比、风险评估、团队能力考虑",
                        "追问": "如何平衡技术先进性和项目稳定性？"
                    },
                    {
                        "问题": "如何评估和优化系统性能？",
                        "考察点": "性能优化思路、监控体系、问题定位",
                        "参考答案": "应包含性能指标、监控工具、瓶颈分析、优化策略",
                        "追问": "能分享一个具体的性能优化案例吗？"
                    }
                ]
            },
            "管理能力评估": {
                "团队管理": [
                    {
                        "问题": "如何管理一个技术团队？您的管理理念是什么？",
                        "考察点": "管理理念、团队建设、人员发展",
                        "参考答案": "应包含团队目标、人员培养、激励机制、沟通方式",
                        "追问": "如何处理团队成员的绩效问题？如何激发团队创新？"
                    },
                    {
                        "问题": "如何平衡技术债务和业务需求？",
                        "考察点": "技术管理、业务理解、优先级判断",
                        "参考答案": "应体现技术与业务的平衡、长远规划、风险控制",
                        "追问": "能举例说明如何说服业务方投入技术重构？"
                    }
                ],
                "项目管理": [
                    {
                        "问题": "如何确保项目按时交付？您的项目管理方法是什么？",
                        "考察点": "项目管理能力、风险控制、资源协调",
                        "参考答案": "应包含项目规划、风险识别、进度控制、质量保证",
                        "追问": "项目延期时如何处理？如何与各方沟通？"
                    }
                ]
            },
            "综合素质考察": {
                "学习能力": [
                    {
                        "问题": "您是如何保持技术更新的？最近学习了什么新技术？",
                        "考察点": "学习意愿、学习方法、技术敏感度",
                        "参考答案": "应包含学习渠道、学习计划、实践应用、知识分享",
                        "追问": "如何评估新技术的价值？如何在工作中应用新技术？"
                    },
                    {
                        "问题": "面对不熟悉的技术领域，您是如何快速上手的？",
                        "考察点": "学习能力、适应能力、解决问题思路",
                        "参考答案": "应体现系统性学习方法、实践验证、寻求帮助",
                        "追问": "能分享一个具体的快速学习案例吗？"
                    }
                ],
                "抗压能力": [
                    {
                        "问题": "在高压环境下，您是如何保证工作质量的？",
                        "考察点": "抗压能力、时间管理、质量意识",
                        "参考答案": "应包含压力管理、优先级排序、质量控制、团队协作",
                        "追问": "能描述一次在紧急情况下解决问题的经历吗？"
                    }
                ],
                "沟通协作": [
                    {
                        "问题": "如何与非技术人员沟通技术问题？",
                        "考察点": "沟通能力、表达能力、换位思考",
                        "参考答案": "应体现简化表达、类比说明、关注对方需求",
                        "追问": "如何让业务方理解技术方案的价值？"
                    }
                ]
            }
        }
        
        # 显示问题库
        for main_category, sub_categories in interview_categories.items():
            st.subheader(f"🎯 {main_category}")
            
            for sub_category, questions in sub_categories.items():
                with st.expander(f"📋 {sub_category}", expanded=False):
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"### 问题 {i}")
                        st.markdown(f"**❓ 问题：** {q['问题']}")
                        st.markdown(f"**🎯 考察点：** {q['考察点']}")
                        st.markdown(f"**✅ 参考答案：** {q['参考答案']}")
                        st.markdown(f"**🔄 追问建议：** {q['追问']}")
                        st.markdown("---")
        
        # 面试技巧指南
        st.subheader("💡 面试技巧指南")
        
        interview_tips = {
            "提问技巧": [
                "🎯 **STAR法则**：引导候选人按照Situation(情境)、Task(任务)、Action(行动)、Result(结果)的结构回答",
                "🔍 **层层深入**：从基础问题开始，逐步深入到技术细节和思维过程",
                "💡 **开放式问题**：多使用'如何'、'为什么'、'请描述'等开放式问题",
                "🎭 **情景模拟**：设置具体的工作场景，考察候选人的实际应对能力"
            ],
            "观察要点": [
                "👀 **表达逻辑**：观察候选人的思维逻辑是否清晰，表达是否有条理",
                "🧠 **思考过程**：关注解决问题的思路和方法，而不仅仅是结果",
                "💪 **学习能力**：通过不熟悉的问题考察学习和适应能力",
                "🤝 **团队协作**：观察沟通方式和团队合作意识"
            ],
            "评分标准": [
                "⭐ **技术能力 (40%)**：专业技能、技术深度、解决问题能力",
                "⭐ **项目经验 (25%)**：项目复杂度、承担角色、成果贡献",
                "⭐ **综合素质 (20%)**：学习能力、沟通能力、团队协作",
                "⭐ **文化匹配 (15%)**：价值观契合、工作态度、发展意愿"
            ]
        }
        
        for category, tips in interview_tips.items():
            with st.expander(f"📚 {category}", expanded=False):
                for tip in tips:
                    st.markdown(tip)
        
        # 面试流程建议
        st.subheader("⏰ 面试流程建议")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""### 🕐 **技术面试流程 (60-90分钟)**
            
            **开场 (5分钟)**
            - 自我介绍和简历确认
            - 缓解紧张情绪
            
            **技术基础 (20分钟)**
            - 核心技能验证
            - 基础概念理解
            
            **项目深挖 (25分钟)**
            - 项目经验详述
            - 技术难点分析
            
            **系统设计 (20分钟)**
            - 架构设计能力
            - 技术选型思路
            
            **综合评估 (15分钟)**
            - 学习能力考察
            - 团队协作评估
            
            **答疑环节 (5分钟)**
            - 候选人提问
            - 公司介绍
            """)
        
        with col2:
            st.markdown("""### 🕑 **管理面试流程 (45-60分钟)**
            
            **背景了解 (10分钟)**
            - 管理经验介绍
            - 团队规模和结构
            
            **管理理念 (15分钟)**
            - 管理风格和方法
            - 团队建设思路
            
            **案例分析 (15分钟)**
            - 具体管理案例
            - 问题解决过程
            
            **业务理解 (10分钟)**
            - 技术与业务平衡
            - 战略思维能力
            
            **发展规划 (10分钟)**
            - 个人发展目标
            - 团队发展规划
            """)

if __name__ == "__main__":
    main()