# -*- coding: utf-8 -*-
"""
PDF导出功能修复版本
解决中文字体显示异常问题
"""

import io
import os
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFExporter:
    def __init__(self):
        self.font_registered = False
        self._register_chinese_font()
    
    def _register_chinese_font(self):
        """注册中文字体"""
        try:
            # 尝试注册系统中的中文字体
            font_paths = [
                # Windows 系统字体路径
                'C:/Windows/Fonts/simsun.ttc',  # 宋体
                'C:/Windows/Fonts/simhei.ttf',  # 黑体
                'C:/Windows/Fonts/msyh.ttc',    # 微软雅黑
                'C:/Windows/Fonts/simkai.ttf',  # 楷体
                # 其他可能的字体路径
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        if font_path.endswith('.ttc'):
                            # TTC字体文件需要指定字体索引
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                        else:
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.font_registered = True
                        print(f"成功注册中文字体: {font_path}")
                        break
                    except Exception as e:
                        print(f"注册字体失败 {font_path}: {e}")
                        continue
            
            if not self.font_registered:
                print("警告: 未找到可用的中文字体，将使用默认字体")
                
        except Exception as e:
            print(f"字体注册过程出错: {e}")
    
    def _get_font_name(self):
        """获取字体名称"""
        return 'ChineseFont' if self.font_registered else 'Helvetica'
    
    def _create_styles(self):
        """创建PDF样式"""
        styles = getSampleStyleSheet()
        font_name = self._get_font_name()
        
        # 标题样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # 居中
            textColor=colors.darkblue
        )
        
        # 标题样式
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # 正文样式
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            spaceAfter=6
        )
        
        # 类别样式
        category_style = ParagraphStyle(
            'CategoryStyle',
            parent=styles['Heading3'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.darkgreen,
            spaceAfter=6
        )
        
        # 焦点样式
        focus_style = ParagraphStyle(
            'FocusStyle',
            parent=normal_style,
            fontSize=9,
            textColor=colors.grey,
            leftIndent=20
        )
        
        return {
            'title': title_style,
            'heading': heading_style,
            'normal': normal_style,
            'category': category_style,
            'focus': focus_style
        }
    
    def export_candidate_to_pdf(self, candidate_data: Dict[str, Any], interview_questions: List[tuple]) -> bytes:
        """导出单个候选人的分析结果和面试问题为PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=72
        )
        
        # 获取样式
        styles = self._create_styles()
        
        # 构建PDF内容
        story = []
        
        # 标题
        title_text = f"候选人分析报告 - {candidate_data.get('candidate_name', '未知')}"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 12))
        
        # 基本信息
        story.append(Paragraph("基本信息", styles['heading']))
        basic_info = [
            ['候选人姓名', candidate_data.get('candidate_name', '未知')],
            ['生成时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['总体评分', f"{candidate_data.get('overall_score', 0):.1f}/10"]
        ]
        
        basic_table = Table(basic_info, colWidths=[2*inch, 3*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self._get_font_name()),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # 详细评分
        story.append(Paragraph("详细评分", styles['heading']))
        
        # 创建表格样式，用于评价列的文本
        eval_style = ParagraphStyle(
            'EvalStyle',
            parent=styles['normal'],
            fontSize=9,
            leading=12,
            wordWrap='CJK',
            spaceBefore=2,
            spaceAfter=2
        )
        
        # 安全处理evaluation字段，确保是字符串类型
        def safe_get_evaluation(data, key, default='暂无评价'):
            value = data.get(key, default)
            if isinstance(value, list):
                return ' '.join(str(item) for item in value) if value else default
            return str(value) if value else default
        
        score_data = [
            ['评估维度', '得分', '评价'],
            ['教育背景', f"{candidate_data.get('education_score', 0)}/10", 
             Paragraph(safe_get_evaluation(candidate_data, 'education_evaluation'), eval_style)],
            ['工作经验', f"{candidate_data.get('experience_score', 0)}/10", 
             Paragraph(safe_get_evaluation(candidate_data, 'experience_evaluation'), eval_style)],
            ['技能匹配', f"{candidate_data.get('skills_score', 0)}/10", 
             Paragraph(safe_get_evaluation(candidate_data, 'skills_evaluation'), eval_style)],
            ['项目经验', f"{candidate_data.get('projects_score', 0)}/10", 
             Paragraph(safe_get_evaluation(candidate_data, 'projects_evaluation'), eval_style)],
        ]
        
        # 调整列宽，确保内容不会超出
        score_table = Table(score_data, colWidths=[1.8*inch, 0.8*inch, 3.4*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self._get_font_name()),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # 优势和关注点
        story.append(Paragraph("优势分析", styles['heading']))
        strengths = candidate_data.get('strengths', [])
        if strengths and isinstance(strengths, list):
            for i, strength in enumerate(strengths, 1):
                story.append(Paragraph(f"{i}. {str(strength)}", styles['normal']))
        elif strengths and isinstance(strengths, str):
            story.append(Paragraph(strengths, styles['normal']))
        else:
            story.append(Paragraph("暂无优势信息", styles['normal']))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("关注点", styles['heading']))
        concerns = candidate_data.get('concerns', [])
        if concerns and isinstance(concerns, list):
            for i, concern in enumerate(concerns, 1):
                story.append(Paragraph(f"{i}. {str(concern)}", styles['normal']))
        elif concerns and isinstance(concerns, str):
            story.append(Paragraph(concerns, styles['normal']))
        else:
            story.append(Paragraph("暂无关注点", styles['normal']))
        story.append(Spacer(1, 20))
        
        # 综合评价
        story.append(Paragraph("综合评价", styles['heading']))
        summary = candidate_data.get('summary', '暂无综合评价')
        summary_text = str(summary) if summary else '暂无综合评价'
        story.append(Paragraph(summary_text, styles['normal']))
        story.append(Spacer(1, 20))
        
        # 面试建议
        story.append(Paragraph("面试建议", styles['heading']))
        interview_suggestions = candidate_data.get('interview_suggestions', '暂无面试建议')
        suggestions_text = str(interview_suggestions) if interview_suggestions else '暂无面试建议'
        story.append(Paragraph(suggestions_text, styles['normal']))
        story.append(Spacer(1, 20))
        
        # 发展潜力
        story.append(Paragraph("发展潜力", styles['heading']))
        development_potential = candidate_data.get('development_potential', '暂无发展潜力评估')
        potential_text = str(development_potential) if development_potential else '暂无发展潜力评估'
        story.append(Paragraph(potential_text, styles['normal']))
        story.append(Spacer(1, 30))
        
        # 面试问题
        story.append(Paragraph("推荐面试问题", styles['heading']))
        if interview_questions:
            # 创建问题表格样式
            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['normal'],
                fontSize=9,
                leading=12,
                wordWrap='CJK',
                spaceBefore=2,
                spaceAfter=2
            )
            
            focus_style_table = ParagraphStyle(
                'FocusStyleTable',
                parent=styles['normal'],
                fontSize=8,
                textColor=colors.grey,
                leading=10,
                wordWrap='CJK'
            )
            
            for category, questions in interview_questions:
                story.append(Paragraph(f"{category}", styles['category']))
                
                # 创建问题表格
                question_data = [['序号', '面试问题', '关注点']]
                
                for i, q in enumerate(questions[:3], 1):  # 每个类别最多显示3个问题
                    if isinstance(q, dict):
                        question_text = str(q.get('question', '暂无问题'))
                        focus_text = str(q.get('focus', '综合能力'))
                    else:
                        question_text = str(q) if q else '暂无问题'
                        focus_text = '综合能力'
                    
                    question_data.append([
                        str(i),
                        Paragraph(question_text, question_style),
                        Paragraph(focus_text, focus_style_table)
                    ])
                
                question_table = Table(question_data, colWidths=[0.5*inch, 3.5*inch, 2*inch])
                question_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # 序号居中
                    ('ALIGN', (1, 0), (-1, -1), 'LEFT'),   # 其他左对齐
                    ('FONTNAME', (0, 0), (-1, -1), self._get_font_name()),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                story.append(question_table)
                story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("暂无面试问题", styles['normal']))
        
        # 生成PDF
        try:
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            print(f"PDF生成错误: {e}")
            # 创建错误信息PDF
            return self._create_error_pdf(str(e))
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """截断文本"""
        if not text:
            return '暂无信息'
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    def _create_error_pdf(self, error_message: str) -> bytes:
        """创建错误信息PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = [
            Paragraph("PDF生成错误", styles['Title']),
            Spacer(1, 12),
            Paragraph(f"错误信息: {error_message}", styles['Normal']),
            Spacer(1, 12),
            Paragraph("请联系技术支持解决此问题。", styles['Normal'])
        ]
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

# 测试函数
def test_pdf_export():
    """测试PDF导出功能"""
    exporter = PDFExporter()
    
    # 测试数据
    test_data = {
        'candidate_name': '张三',
        'overall_score': 8.5,
        'education_score': 9,
        'education_evaluation': '教育背景优秀，具有相关专业学位',
        'experience_score': 8,
        'experience_evaluation': '工作经验丰富，有相关行业背景',
        'skills_score': 8,
        'skills_evaluation': '技能匹配度高，掌握核心技术',
        'projects_score': 9,
        'projects_evaluation': '项目经验丰富，有成功案例',
        'strengths': ['技术能力强', '学习能力好', '沟通能力佳'],
        'concerns': ['缺乏管理经验', '需要提升英语水平'],
        'summary': '综合来看，该候选人具有很强的技术能力和学习能力，适合技术岗位。',
        'interview_suggestions': '建议重点考察其技术深度和团队协作能力。',
        'development_potential': '发展潜力较大，可以考虑培养为技术专家。'
    }
    
    test_questions = [
        ('技术问题', [
            {'question': '请介绍一下你最熟悉的技术栈', 'focus': '技术深度'},
            {'question': '如何解决性能优化问题', 'focus': '问题解决能力'}
        ]),
        ('项目经验', [
            {'question': '描述一个你主导的项目', 'focus': '项目管理能力'},
            {'question': '遇到的最大挑战是什么', 'focus': '抗压能力'}
        ])
    ]
    
    try:
        pdf_bytes = exporter.export_candidate_to_pdf(test_data, test_questions)
        
        # 保存测试PDF
        with open('test_output.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print("PDF测试成功！文件已保存为 test_output.pdf")
        return True
    except Exception as e:
        print(f"PDF测试失败: {e}")
        return False

if __name__ == "__main__":
    test_pdf_export()