import time

import requests
from fake_useragent import UserAgent

from bilibili_info_crawler.config import *
from bilibili_info_crawler.utils import get_wrid_wts


# 这个拿到的数好像不是真实的评论数，我去数了一下的
def get_comment_count(oid: [int | str]):
    url = BASE_COMMENT_COUNT_URL
    headers = {
        "User-Agent": UserAgent().random
    }
    # 添加必要参数
    params = BASE_PARAM
    params['oid'] = oid
    w_rid, wts = get_wrid_wts(params)
    params['w_rid'] = w_rid
    params['wts'] = wts
    # 请求返回结果
    response = requests.get(url, headers = headers, params = params)
    return response


def get_root_comment(oid: [int | str]):
    print("开始获取一级评论！")
    url = BASE_COMMENT_URL
    headers = {
        "Cookie": Cookie,
        "User-Agent": UserAgent().random
    }
    # 添加必要参数
    params = BASE_PARAM.copy()
    params['oid'] = oid
    w_rid, wts = get_wrid_wts(params)
    params['w_rid'] = w_rid
    params['wts'] = wts

    reply_count = 0
    next_offset = ''
    pre_comments_count = 0
    comments = []
    is_first = True

    while True:
        try:
            if not is_first:
                params['pagination_str'] = '{"offset":"' + next_offset + '"}'
                w_rid, wts = get_wrid_wts(params)
                params['w_rid'] = w_rid
                params['wts'] = wts

            response = requests.get(url, headers=headers, params=params)
            data = response.json().get('data', {})

            if is_first:
                params.pop('seek_rpid', None)
                is_first = False
        except:
            reply_count += 1
            if reply_count > 3:
                print("超过最大重试次数！")
                return comments
            time.sleep(1)
            continue

        cursor = data.get('cursor', {})
        pagination_reply = cursor.get('pagination_reply', {})
        next_offset = pagination_reply.get('next_offset', '')

        # 置顶评论
        for reply in data.get('top_replies', []) or []:
            comments.append({
                reply['rpid']: {
                    'like': reply['like'],
                    'message': reply['content']['message'],
                    'rcount': reply['rcount'],
                }
            })

        # 普通一级评论
        for reply in data.get('replies', []) or []:
            comments.append({
                reply['rpid']: {
                    'like': reply['like'],
                    'message': reply['content']['message'],
                    'rcount': reply['rcount'],
                }
            })

        if pre_comments_count >= len(comments):
            break

        pre_comments_count = len(comments)
        print(f'已获取 [{len(comments)}] 条一级评论！')

    return comments


# TODO: AI生成的
def build_reply_tree(root_rpid: int, replies: list[dict]) -> list[dict]:
    """
    把 flat replies 构建成 parent -> child 树
    """
    node_map = {}
    roots = []

    # 1️⃣ 建 rpid -> node
    for r in replies:
        node_map[r["rpid"]] = {
            **r,
            "children": []
        }

    # 2️⃣ 挂 parent
    for rpid, node in node_map.items():
        parent = node["parent"]

        if parent == root_rpid:
            # 直接回复一级评论
            roots.append(node)
        else:
            parent_node = node_map.get(parent)
            if parent_node:
                parent_node["children"].append(node)
            else:
                # 父评论不在当前 replies 里，兜底
                roots.append(node)

    return roots


def get_all_comments(oid: int | str):
    # total_comment_count = get_comment_count(oid).json()["data"]["count"]
    comments = get_root_comment(oid)  # 一级评论列表
    print("开始获取二级评论！")

    url = BASE_COMMENT_REPLY_URL
    headers = {
        "Cookie": Cookie,
        "User-Agent": UserAgent().random
    }

    base_params = {
        "oid": oid,
        "type": 1,
        "ps": 10,
        "web_location": "333.788"
    }

    cur_comment_count = len(comments)

    # 通过已经评论的key收集收集二级评论
    for item in comments:
        # item: {rpid: {...}}
        root = next(iter(item))
        root_info = item[root]

        rcount = root_info.get("rcount", 0)
        # rcount小于0代表该一级评论没有二级评论回复
        if rcount <= 0:
            continue

        replies = [] # 二级评论
        pn = 1 # 第一页
        retry = 0 # 重试次数

        while True:
            params = {
                **base_params,
                "root": root,
                "pn": pn
            }

            try:
                resp = requests.get(url, headers = headers, params = params)
                data = resp.json()["data"]
            except:
                retry += 1
                if retry >= 3:
                    print(f"root={root} 二级评论请求失败")
                    break
                time.sleep(1)
                continue

            page_replies = data.get("replies") or []
            if not page_replies:
                break

            for reply in page_replies:
                replies.append({
                    "rpid": reply["rpid"],
                    "parent": reply["parent"],
                    "message": reply["content"]["message"],
                    "like": reply["like"],
                })
                cur_comment_count += 1
                if cur_comment_count % 50 == 0:
                    print(f"已获取 [{cur_comment_count}] 条评论")

            pn += 1

            # ✅ 建 parent → child 树
        root_info["replies"] = build_reply_tree(root, replies)

    print(f"总共获取 [{cur_comment_count}] 条评论")

    return comments



