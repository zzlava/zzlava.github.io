import requests
from bs4 import BeautifulSoup
import traceback
import sys

def fetch_and_parse_website():
    url = "http://epg.51zmt.top:8000/sctvmulticast.html"
    
    try:
        # 发送请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)  # 增加超时时间
        
        # 检查响应状态
        print(f"响应状态码: {response.status_code}")
        print(f"响应编码: {response.encoding}")
        
        # 使用网页声明的 UTF-8 编码
        response.encoding = 'utf-8'
        
        # 解析 HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解码表格
        tables = soup.find_all('table')
        if not tables:
            print("未找到表格")
            return False
        
        first_table = tables[0]
        rows = first_table.find_all('tr')
        
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
        
        # 跳过标题行，处理数据行
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                # 获取频道名称和组播地址
                channel_name = cols[1].get_text(strip=True)
                channel_url = cols[2].get_text(strip=True)
                
                # 频道过滤
                if any(keyword in channel_name for keyword in keep_keywords):
                    # 转换地址格式并添加到 M3U8 行
                    rtp_url = f'rtp://{channel_url}'
                    m3u8_lines.append(f'#EXTINF:-1 ,{channel_name}')
                    m3u8_lines.append(rtp_url)
        
        # 写入 M3U8 文件
        with open('iptv2.m3u8', 'w', encoding='utf-8') as f:
            f.write('\n'.join(m3u8_lines))
        
        print(f"成功生成 M3U8 文件，共 {len(m3u8_lines)//2 - 1} 个频道")
        return True
    
    except Exception as e:
        print("处理网页时发生错误:")
        print(traceback.format_exc())
        return False

# 设置返回码
sys.exit(0 if fetch_and_parse_website() else 1)