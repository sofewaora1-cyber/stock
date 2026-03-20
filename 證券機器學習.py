import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# --- 1. 資料讀取與預處理 ---
def load_and_prepare_data(file_name, window_size=5):
    try:
        df = pd.read_csv(file_name)
        df['報酬率'] = df['收盤價'].pct_change()
        clean_df = df.dropna(subset=['報酬率']).reset_index(drop=True)
        
        features, target = [], []
        for i in range(len(clean_df) - window_size):
            features.append(clean_df['報酬率'].iloc[i : i + window_size].values)
            target.append(1 if clean_df['報酬率'].iloc[i + window_size] > 0 else 0)
            
        return np.array(features), np.array(target), clean_df
    except FileNotFoundError:
        print(f"❌ 找不到檔案 {file_name}"); return None, None, None

# --- 2. 執行主程式 ---
window_size = 5
X, y, clean_df = load_and_prepare_data('stock_2330_6months_simple.csv', window_size)

if X is not None and len(X) >= 5:
    # 切分訓練與測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)
    
    # 定義模型
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Logistic Regression": LogisticRegression(),
        "SVM": SVC(probability=True)
    }
    
    results = {}
    print(f"📖 訓練集：{len(X_train)} 筆 | 測試集：{len(X_test)} 筆\n" + "-"*30)

    # 訓練與評估
    for name, m in models.items():
        m.fit(X_train, y_train)
        acc = accuracy_score(y_test, m.predict(X_test))
        results[name] = acc
        print(f"✅ {name:19} 準確率: {acc * 100:>6.2f}%")

    # 預測最新趨勢 (以隨機森林為例)
    latest_feat = clean_df['報酬率'].tail(window_size).values.reshape(1, -1)
    pred = models["Random Forest"].predict(latest_feat)[0]
    print(f"-"*30 + f"\n🔮 隨機森林預測下一日趨勢：{'🚀 漲' if pred == 1 else '📉 跌'}")

    # 繪圖
    plt.figure(figsize=(8, 5))
    plt.bar(results.keys(), [v * 100 for v in results.values()], color=['#3498db', '#e74c3c', '#2ecc71'])
    plt.ylabel('Accuracy (%)'); plt.title('Model Comparison'); plt.ylim(0, 100)
    plt.show()
else:
    print("⚠️ 資料量不足。")