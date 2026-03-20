import requests
import urllib3
import pandas as pd
import time
import re
import os  # 用於檢查檔案是否存在

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 在這裡貼上你的 Discord Webhook URL ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1481486099263262861/B5qzMw56OEMVEzGw27i_chHv_QBxVQfKw8gnOTQt99JYUjQySkDWbMfyk5aP4O7aVQDy"

def send_to_discord(filepath, stock_no):
    """將生成的 CSV 傳送到 Discord"""
    if not os.path.exists(filepath):
        print("❌ 找不到檔案，無法傳送至 Discord")
        return

    payload = {"content": f"📊 股票代碼 {stock_no} 的近六個月簡化資料已生成！"}
    
    with open(filepath, "rb") as f:
        files = {
            "file": (filepath, f, "text/csv")
        }
        response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
        
    if response.status_code == 200 or response.status_code == 204:
        print("🚀 檔案已成功回傳至 Discord！")
    else:
        print(f"❌ Discord 傳送失敗，狀態碼：{response.status_code}")

def get_multi_month_data(stock_no, months_list):
    all_df = [] 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    for date_str in months_list:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_no}"
        
        try:
            print(f"⏳ 正在抓取 {date_str[:6]} 的資料...")
            response = requests.get(url, headers=headers, verify=False)
            data = response.json()
            
            if data.get('stat') == 'OK':
                raw_data = data['data']
                processed_data = [row[:9] for row in raw_data] 
                
                columns = ['交易日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
                df = pd.DataFrame(processed_data, columns=columns)
                
                def convert_date(d):
                    parts = d.split('/')
                    return f"{int(parts[0]) + 1911}/{parts[1]}/{parts[2]}"

                df['交易日期'] = df['交易日期'].apply(convert_date)
                
                for col in columns[1:]:
                    df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                simple_df = df[['交易日期', '收盤價', '漲跌價差']].copy()
                all_df.append(simple_df)
                print(f"✅ {date_str[:6]} 抓取成功")
            else:
                print(f"⚠️ {date_str[:6]} 查無資料")
            
            time.sleep(7) # 避免被 TWSE 封鎖
            
        except Exception as e:
            print(f"❌ 發生錯誤：{e}")
            break
    
    if all_df:
        final_df = pd.concat(all_df, ignore_index=True)
        final_df['交易日期'] = pd.to_datetime(final_df['交易日期'])
        final_df = final_df.sort_values('交易日期')
       
        filename = f"stock_{stock_no}_6months_simple.csv"
        final_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n🎉 任務完成！檔案存至：{filename}")
        
        # --- 執行回傳 Discord ---
        send_to_discord(filename, stock_no)
    else:
        print("\n❌ 未抓取到資料。")

if __name__ == "__main__":
    stock = input("請輸入股票代碼: ")
    # 注意：2026 年 3 月尚未結束，可能只有部分資料或無資料
    months_list = ["20251001", "20251101", "20251201", "20260101", "20260201", "20260301"]
    get_multi_month_data(stock, months_list)