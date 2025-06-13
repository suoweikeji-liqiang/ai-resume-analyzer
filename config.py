# 简历分析配置文件

# 评分维度配置
SCORING_DIMENSIONS = {
    'education': {
        'name': '教育背景',
        'weight': 0.2,  # 权重
        'description': '学历层次、学校声誉、专业匹配度'
    },
    'experience': {
        'name': '工作经验',
        'weight': 0.3,
        'description': '工作年限、职位层级、行业相关性'
    },
    'skills': {
        'name': '技能匹配',
        'weight': 0.25,
        'description': '专业技能、技术能力、证书资质'
    },
    'projects': {
        'name': '项目经验',
        'weight': 0.15,
        'description': '项目复杂度、成果展示、创新性'
    },
    'overall': {
        'name': '综合素质',
        'weight': 0.1,
        'description': '沟通能力、领导力、学习能力'
    }
}

# OpenAI API配置
OPENAI_CONFIG = {
    'model': 'gpt-3.5-turbo',
    'temperature': 0.3,
    'max_tokens': 2000
}

# 评分标准说明
SCORING_CRITERIA = {
    'education': {
        '9-10': '顶尖院校硕士/博士学位，专业高度匹配',
        '7-8': '知名院校本科/硕士学位，专业匹配',
        '5-6': '普通院校本科学位，专业相关',
        '3-4': '专科学历或专业不太匹配',
        '1-2': '学历较低或专业完全不匹配'
    },
    'experience': {
        '9-10': '5年以上相关经验，担任过管理职位',
        '7-8': '3-5年相关经验，有一定责任',
        '5-6': '1-3年相关经验',
        '3-4': '有工作经验但相关性不强',
        '1-2': '无相关工作经验'
    },
    'skills': {
        '9-10': '技能全面且深入，有权威认证',
        '7-8': '技能较为全面，有相关证书',
        '5-6': '基本技能满足要求',
        '3-4': '技能有限，需要培训',
        '1-2': '技能严重不足'
    },
    'projects': {
        '9-10': '主导过复杂项目，成果显著',
        '7-8': '参与过重要项目，有明确贡献',
        '5-6': '有项目经验，表现一般',
        '3-4': '项目经验有限',
        '1-2': '缺乏项目经验'
    },
    'overall': {
        '9-10': '综合素质优秀，表达清晰，有领导力',
        '7-8': '综合素质良好，沟通能力强',
        '5-6': '综合素质一般',
        '3-4': '综合素质有待提升',
        '1-2': '综合素质较差'
    }
}

# 行业特定配置（可根据需要扩展）
INDUSTRY_CONFIGS = {
    'tech': {
        'name': '技术行业',
        'key_skills': ['编程', '算法', '系统设计', '数据库'],
        'education_weight': 0.15,
        'skills_weight': 0.35
    },
    'finance': {
        'name': '金融行业',
        'key_skills': ['财务分析', '风险管理', '投资', '合规'],
        'education_weight': 0.25,
        'experience_weight': 0.35
    },
    'marketing': {
        'name': '市场营销',
        'key_skills': ['市场分析', '品牌管理', '数字营销', '客户关系'],
        'projects_weight': 0.25,
        'overall_weight': 0.15
    }
}

# UI配置
UI_CONFIG = {
    'page_title': '简历比较工具',
    'page_icon': '📄',
    'layout': 'wide',
    'theme': {
        'primary_color': '#1f77b4',
        'background_color': '#ffffff',
        'secondary_background_color': '#f0f2f6'
    }
}

# 文件处理配置
FILE_CONFIG = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_extensions': ['.pdf'],
    'max_files': 10
}

# 分析结果缓存配置
CACHE_CONFIG = {
    'enable_cache': True,
    'cache_ttl': 3600,  # 1小时
    'max_cache_size': 100
}