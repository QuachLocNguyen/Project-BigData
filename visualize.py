import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

output_dir = './charts'
os.makedirs(output_dir, exist_ok=True)

print("Biểu đồ chủ đề 1")
try:
	df_bg = pd.read_csv('result_bigram.txt', sep='\t', names=['Source', 'Bigram', 'Count'])
	for source in df_bg['Source'].unique():
		sub_df = df_bg[df_bg['Source'] == source].nlargest(10, 'Count')
	
		plt.figure(figsize=(10,6))
		sns.barplot(data=sub_df, x = 'Count', y= 'Bigram', hue='Bigram', palette='viridis', legend=False)
		plt.title(f'Top 10 phổ biến nhất - Nguồn {source}', fontsize=14, fontweight='bold')
		plt.xlabel('Số lân xuất hiện', fontsize=12)
		plt.ylabel('Cặp từ khóa (Bigram)', fontsize=12)
		plt.tight_layout()
		plt.savefig(f'{output_dir}/bigram_{source}.png', dpi=300)
		plt.close()
except Exception as e:
	print(f"Lỗi vẽ biểu đồ Bigram: {e}")

print("Biểu đồ chủ dề 2")
try:
	df_st = pd.read_csv('result_sentiment.txt', sep='\t', names=['Source', 'Sentiment', 'Count'])
	
	plt.figure(figsize=(10, 6))
	sns.barplot(data=df_st, x='Sentiment', y='Count', hue='Source', palette='Set2')
	plt.title('So sánh sắc thái bài viết (Sentiment Analysis)', fontsize=14, fontweight='bold')
	plt.xlabel('Sắc thái', fontsize=12)
	plt.ylabel('Số lượng bài viết', fontsize=12)
	plt.legend(title='Nguồn bài viết')
	plt.tight_layout()
	plt.savefig(f'{output_dir}/sentiment_analysis.png', dpi=300)
	plt.close()
except Exception as e:
	print(f"Lỗi vẽ biểu đồ Sentiment: {e}")

print("Biểu đồ chủ đề 3")
try:
	df_len = pd.read_csv('result_length.txt', sep='\t', names=['Source', 'Length_Group', 'Count'])
		
	plt.figure(figsize=(10, 6))
	sns.barplot(data=df_len, x='Length_Group', y='Count', hue='Source', palette='muted',
		order=['Short (<300 words)', 'Medium (300-1000 words)', 'Long (>1000 words)'])
	plt.title('Phân loại độ dài bài viết & Mức độ chuyên sâu', fontsize=14, fontweight='bold')
	plt.xlabel('Nhóm độ dài', fontsize=12)
	plt.ylabel('Số lượng bài viết', fontsize=12)
	plt.legend(title='Nguồn bài viết')
	plt.tight_layout()
	plt.savefig(f'{output_dir}/article_length.png', dpi=300)
	plt.close()
except Exception as e:
	print(f"Lỗi vẽ biểu đồ Độ dài: {e}")
print(f"Vẽ biểu đồ thành công!")
