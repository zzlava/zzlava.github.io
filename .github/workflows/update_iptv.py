import requests
from bs4 import BeautifulSoup
import traceback
import os

def fetch_and_parse_website():
    url = "http://epg.51zmt.top:8000/sctvmulticast.html"
    
    try:
        print("开始执行更新脚本...")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print("正在请求网页...")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"网页请求状态码: {response.status_code}")
        
        # 使用网页声明的 UTF-8 编码
        response.encoding = 'utf-8'
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解码表格
        tables = soup.find_all('table')
        if not tables:
            print("错误：未找到表格")
            return
        
        print(f"找到表格数量: {len(tables)}")
        
        first_table = tables[0]
        rows = first_table.find_all('tr')
        print(f"表格行数: {len(rows)}")
        
        # 准备 M3U8 文件内容
        m3u8_lines = ['#EXTM3U']
        
        # 更宽松的频道过滤关键词
        keep_keywords = [
            'CCTV', '卫视', 'CDTV', '东南', '重庆', 
            '央视', '高清', '标清', '频道', '台', '纪实', 
            '新闻', '体育', '少儿', '电影', '科技', '熊猫', 
            '大爱', '教育', '家政', '4K', '地方', '传媒',
            '文化', '影视', '生活', '旅游', '财经', '都市'
        ]
        
        # 记录所有频道信息
        all_channels = []
        matched_channels = []
        
        # 跳过标题行，处理数据行
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # 获取频道名称和组播地址
                channel_name = cols[1].get_text(strip=True)
                channel_url = cols[2].get_text(strip=True)
                
                # 记录所有频道
                all_channels.append((channel_name, channel_url))
                
                # 频道过滤
                if any(keyword in channel_name for keyword in keep_keywords):
                    # 转换地址格式并添加到 M3U8 行
                    rtp_url = f'rtp://{channel_url}'
                    m3u8_lines.append(f'#EXTINF:-1 ,{channel_name}')
                    m3u8_lines.append(rtp_url)
                    matched_channels.append((channel_name, channel_url))
        
        # 写入 M3U8 文件
        output_path = 'iptv2.m3u8'
        print(f"准备写入文件: {output_path}")
        print(f"匹配到的频道数: {len(matched_channels)}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(m3u8_lines))
            print(f"文件写入成功，大小: {os.path.getsize(output_path)} 字节")
        except Exception as e:
            print(f"写入文件时出错: {str(e)}")
            raise
        
        # 验证文件是否成功写入
        if os.path.exists(output_path):
            print(f"文件已成功创建: {output_path}")
            with open(output_path, 'r', encoding='utf-8') as f:
                first_few_lines = [next(f) for _ in range(5)]
                print("文件前5行内容:")
                print('\n'.join(first_few_lines))
        else:
            print("错误：文件未能成功创建")
        
    except Exception as e:
        print("处理过程中发生错误:")
        print(traceback.format_exc())
        raise  # 重新抛出异常，确保 GitHub Actions 知道任务失败

if __name__ == "__main__":
    fetch_and_parse_website()
