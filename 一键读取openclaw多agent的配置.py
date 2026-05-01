#!/usr/bin/env python3
"""
openclaw_agent_inspector.py - OpenClaw Agent配置读取工具
用法: python3 openclaw_agent_inspector.py [--verbose] [--simple] [--output FILE]
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class OpenClawAgentInspector:
    def __init__(self, verbose=False, simple=False, output_file=None):
        self.openclaw_home = Path(os.environ.get('OPENCLAW_HOME', Path.home() / '.openclaw'))
        self.verbose = verbose
        self.simple = simple
        self.output_file = output_file
        self.output_lines = []
        
    def output(self, text: str, color: Optional[str] = None):
        """输出文本（同时保存到文件）"""
        self.output_lines.append(text)
        if not self.simple:  # 简洁模式下不打印到屏幕
            print(text)
    
    def separator(self, char: str = '=', length: int = 80):
        self.output(char * length)
    
    def title(self, text: str):
        self.output("")
        self.separator()
        self.output(f"▶ {text}")
        self.separator()
    
    def subtitle(self, text: str):
        self.output("")
        self.output(f"  📌 {text}")
        self.separator('-', 40)
    
    def check_openclaw(self):
        """检查OpenClaw是否安装"""
        if not self.openclaw_home.exists():
            raise Exception(f"OpenClaw未安装或路径不正确: {self.openclaw_home}")
    
    def read_main_config(self):
        """读取主配置文件"""
        config_file = self.openclaw_home / 'openclaw.json'
        
        if config_file.exists():
            self.subtitle("主配置文件: openclaw.json")
            self.output(f"路径: {config_file}")
            
            with open(config_file) as f:
                config = json.load(f)
            
            # 提取Agent列表
            agents = config.get('agents', {}).get('list', [])
            if agents:
                self.output("")
                self.output("Agent列表（从openclaw.json）:")
                self.output("-" * 40)
                for agent in agents:
                    agent_id = agent.get('id', 'unknown')
                    name = agent.get('name', agent_id)
                    workspace = agent.get('workspace', '默认')
                    self.output(f"  - {agent_id}: {name} [工作空间: {workspace}]")
            
            if self.verbose:
                self.output("")
                self.output("完整配置:")
                self.output("-" * 40)
                self.output(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            self.output(f"⚠️  主配置文件不存在: {config_file}")
    
    def read_agent_config(self, agent_dir: Path):
        """读取单个Agent配置"""
        agent_name = agent_dir.name.replace('workspace-', '')
        
        self.subtitle(f"Agent: {agent_name}")
        self.output(f"路径: {agent_dir}")
        
        # 检查各种配置文件
        config_files = ['AGENTS.md', 'IDENTITY.md', 'SOUL.md', 'MEMORY.md', 'USER.md', 'BOOTSTRAP.md']
        found = False
        
        for file in config_files:
            file_path = agent_dir / file
            if file_path.exists():
                found = True
                self.output("")
                self.output(f"📄 {file}:")
                self.separator('-', 40)
                
                if self.verbose or not self.simple:
                    # 显示文件内容
                    content = file_path.read_text(encoding='utf-8')
                    if self.verbose:
                        self.output(content)
                    else:
                        lines = content.split('\n')[:20]
                        self.output('\n'.join(lines))
                        if len(content.split('\n')) > 20:
                            self.output(f"... (共 {len(content.split(chr(10)))} 行，使用 -v 查看完整内容)")
                else:
                    # 简洁模式
                    size = file_path.stat().st_size
                    self.output(f"文件存在 ({size} 字节)")
        
        if not found:
            self.output("⚠️  未找到配置文件（AGENTS.md、IDENTITY.md等）")
            self.output("这可能是一个未初始化的Agent")
        
        # 显示工作空间内容（详细模式）
        if self.verbose:
            self.output("")
            self.output("工作空间内容:")
            for item in agent_dir.iterdir():
                if item.is_file():
                    self.output(f"  📄 {item.name}")
                elif item.is_dir():
                    self.output(f"  📁 {item.name}/")
    
    def read_all_agents(self):
        """读取所有Agent配置"""
        self.title("OpenClaw Agent配置读取报告")
        self.output(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.output(f"OpenClaw主目录: {self.openclaw_home}")
        
        # 读取主配置
        self.read_main_config()
        
        # 查找所有Agent工作空间
        self.title("Agent工作空间详情")
        
        agent_dirs = list(self.openclaw_home.glob('workspace-*'))
        agent_count = 0
        initialized_count = 0
        
        for agent_dir in sorted(agent_dirs):
            if agent_dir.is_dir():
                agent_count += 1
                self.read_agent_config(agent_dir)
                
                # 检查是否已初始化
                if (agent_dir / 'IDENTITY.md').exists():
                    initialized_count += 1
        
        # 统计摘要
        self.title("统计摘要")
        self.output(f"发现Agent总数: {agent_count}")
        self.output(f"已初始化Agent: {initialized_count}")
        self.output(f"未初始化Agent: {agent_count - initialized_count}")
        
        if agent_count == 0:
            self.output("⚠️  未发现任何Agent工作空间")
    
    def health_check(self):
        """健康检查"""
        if self.simple:
            return
        
        self.title("健康检查")
        
        issues = 0
        
        # 检查主配置文件
        config_file = self.openclaw_home / 'openclaw.json'
        if not config_file.exists():
            self.output("🔴 严重: 主配置文件不存在")
            issues += 1
        
        # 检查各Agent
        for agent_dir in self.openclaw_home.glob('workspace-*'):
            if agent_dir.is_dir():
                agent_name = agent_dir.name.replace('workspace-', '')
                
                # 检查必需文件
                if not (agent_dir / 'IDENTITY.md').exists():
                    self.output(f"🟡 警告: {agent_name} 缺少 IDENTITY.md")
                    issues += 1
                
                if not (agent_dir / 'SOUL.md').exists():
                    self.output(f"🟡 警告: {agent_name} 缺少 SOUL.md")
                    issues += 1
                
                # 检查BOOTSTRAP.md
                if (agent_dir / 'BOOTSTRAP.md').exists():
                    self.output(f"🟡 注意: {agent_name} 还处于引导模式（有BOOTSTRAP.md）")
                    issues += 1
        
        if issues == 0:
            self.output("✅ 所有检查通过，系统配置正常")
        else:
            self.output(f"发现 {issues} 个问题需要关注")
    
    def generate_suggestions(self):
        """生成优化建议"""
        if self.simple:
            return
        
        self.title("优化建议")
        
        # 检查未初始化的Agent
        uninitialized = False
        for agent_dir in self.openclaw_home.glob('workspace-*'):
            if (agent_dir / 'BOOTSTRAP.md').exists():
                uninitialized = True
                break
        
        if uninitialized:
            self.output("1. 发现未初始化的Agent，建议运行以下命令完成初始化:")
            self.output("   openclaw doctor")
            self.output("")
        
        # 检查会议管理助手
        has_meeting_manager = any('meeting' in str(agent_dir) for agent_dir in self.openclaw_home.glob('workspace-*'))
        if not has_meeting_manager:
            self.output("2. 建议将会议管理职责整合到秘书助手(secretary_assistant)中")
            self.output("")
        
        # 检查supervisor配置
        supervisor_file = self.openclaw_home / 'workspace-supervisor' / 'AGENTS.md'
        if supervisor_file.exists():
            content = supervisor_file.read_text()
            if '动态助手创建权' in content:
                self.output("3. 检测到supervisor有动态创建权限，建议评估是否真的需要")
                self.output("")
        
        self.output("4. 定期运行此脚本可以监控Agent配置变化:")
        self.output("   python3 openclaw_agent_inspector.py --output")
    
    def run(self):
        """运行主流程"""
        try:
            self.check_openclaw()
            self.read_all_agents()
            self.health_check()
            self.generate_suggestions()
            
            # 保存到文件
            if self.output_file:
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.output_lines))
                print(f"\n✅ 报告已保存到: {self.output_file}")
                
        except Exception as e:
            print(f"错误: {e}")
            return 1
        
        return 0

def main():
    parser = argparse.ArgumentParser(description='OpenClaw Agent配置读取工具')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示所有详细信息')
    parser.add_argument('-s', '--simple', action='store_true', help='简洁模式，只显示基本状态')
    parser.add_argument('-o', '--output', metavar='FILE', help='输出到文件（自动生成时间戳）')
    parser.add_argument('--no-color', action='store_true', help='禁用颜色输出')
    
    args = parser.parse_args()
    
    # 处理输出文件名
    output_file = None
    if args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"openclaw_agents_report_{timestamp}.txt"
    
    inspector = OpenClawAgentInspector(
        verbose=args.verbose,
        simple=args.simple,
        output_file=output_file
    )
    
    return inspector.run()

if __name__ == '__main__':
    exit(main())
