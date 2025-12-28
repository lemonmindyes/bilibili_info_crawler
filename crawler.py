import json

from bilibili_info_crawler.comment import get_root_comment, get_all_comments

# 测试获取评论数
# oid = '115752287868789'
# response = get_comment_count(oid)
# print(response.json())

# 测试获取一级评论
# oid = '115463233279925'
# comments = get_root_comment(oid)
# with open('comments.json', 'w', encoding='utf-8') as f:
#     json.dump(comments, f, ensure_ascii = False, indent = 4)

# 测试获取所有评论
# oid = '115463233279925'
# comments = get_all_comments(oid)
# with open('comments.json', 'w', encoding='utf-8') as f:
#     json.dump(comments, f, ensure_ascii = False, indent = 4)
