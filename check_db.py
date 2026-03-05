import sqlite3
conn = sqlite3.connect('D:/File/CodeWorld/bilibili-rag/data/bilibili_rag.db')
c = conn.cursor()

# 检查视频数量
c.execute("SELECT COUNT(*) FROM favorite_videos")
print("收藏夹视频数:", c.fetchone()[0])

# 检查状态
c.execute("SELECT status, COUNT(*) FROM favorite_videos GROUP BY status")
print("\n状态分布:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}个")

# 检查已处理的视频
c.execute("SELECT title, asr_status FROM favorite_videos WHERE asr_status = 'completed'")
print("\n已完成的ASR视频:")
for row in c.fetchall():
    print(f"  - {row[0][:50]}")