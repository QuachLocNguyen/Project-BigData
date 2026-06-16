import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

st.set_page_config(
    page_title="Big Data – Tech News Analysis",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Phân tích bài báo công nghệ")
st.caption("MapReduce · Hadoop · Hive · Pig  —  Kết quả trực quan hóa")
st.divider()

# ── Helper: tìm file dù chạy từ thư mục nào ──────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

def data_path(filename):
    """Thử cạnh app.py trước, rồi thử trong charts/"""
    for candidate in [
        os.path.join(BASE, filename),
        os.path.join(BASE, 'charts', filename),
    ]:
        if os.path.exists(candidate):
            return candidate
    return None

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔤 Bigram (Chủ đề 1)",
    "😊 Sentiment (Chủ đề 2)",
    "📏 Độ dài bài viết (Chủ đề 3)",
])

# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — Bigram
# ────────────────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Top 10 cặp từ khóa (Bigram) phổ biến nhất")
    path = data_path('result_bigram.txt')
    if path is None:
        st.warning("Không tìm thấy file `result_bigram.txt`. Hãy đặt file cạnh `app.py`.")
    else:
        try:
            df_bg = pd.read_csv(path, sep='\t', names=['Source', 'Bigram', 'Count'])
            sources = df_bg['Source'].unique()
            cols = st.columns(len(sources))
            for col, source in zip(cols, sources):
                sub_df = df_bg[df_bg['Source'] == source].nlargest(10, 'Count')
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(data=sub_df, x='Count', y='Bigram',
                            hue='Bigram', palette='viridis', legend=False, ax=ax)
                ax.set_title(f'Nguồn: {source}', fontsize=13, fontweight='bold')
                ax.set_xlabel('Số lần xuất hiện', fontsize=11)
                ax.set_ylabel('Cặp từ khóa', fontsize=11)
                plt.tight_layout()
                col.pyplot(fig)
                plt.close()
        except Exception as e:
            st.error(f"Lỗi đọc dữ liệu Bigram: {e}")

# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — Sentiment
# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("So sánh sắc thái bài viết (Sentiment Analysis)")
    path = data_path('result_sentiment.txt')
    if path is None:
        st.warning("Không tìm thấy file `result_sentiment.txt`. Hãy đặt file cạnh `app.py`.")
    else:
        try:
            df_st = pd.read_csv(path, sep='\t', names=['Source', 'Sentiment', 'Count'])
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=df_st, x='Sentiment', y='Count',
                        hue='Source', palette='Set2', ax=ax)
            ax.set_title('So sánh sắc thái bài viết', fontsize=14, fontweight='bold')
            ax.set_xlabel('Sắc thái', fontsize=12)
            ax.set_ylabel('Số lượng bài viết', fontsize=12)
            ax.legend(title='Nguồn bài viết')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            # Bảng số liệu thu gọn
            with st.expander("Xem bảng số liệu"):
                st.dataframe(
                    df_st.pivot_table(index='Sentiment', columns='Source',
                                      values='Count', aggfunc='sum'),
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Lỗi đọc dữ liệu Sentiment: {e}")

# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — Article Length
# ────────────────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Phân loại độ dài bài viết & Mức độ chuyên sâu")
    path = data_path('result_length.txt')
    if path is None:
        st.warning("Không tìm thấy file `result_length.txt`. Hãy đặt file cạnh `app.py`.")
    else:
        try:
            df_len = pd.read_csv(path, sep='\t', names=['Source', 'Length_Group', 'Count'])
            df_len = df_len.groupby(['Source', 'Length_Group'], as_index=False)['Count'].sum()
            ORDER = ['Short (<300 words)', 'Medium (300-1000 words)', 'Long (>1000 words)']
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(data=df_len, x='Length_Group', y='Count',
                        hue='Source', palette='muted', order=ORDER, ax=ax)
            ax.set_title('Phân loại độ dài bài viết', fontsize=14, fontweight='bold')
            ax.set_xlabel('Nhóm độ dài', fontsize=12)
            ax.set_ylabel('Số lượng bài viết', fontsize=12)
            ax.legend(title='Nguồn bài viết')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()

            with st.expander("Xem bảng số liệu"):
                st.dataframe(df_len, use_container_width=True)
        except Exception as e:
            st.error(f"Lỗi đọc dữ liệu Độ dài: {e}")
