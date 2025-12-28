import hashlib
import time
import urllib

def get_wrid_wts(params: dict):
    wts = int(time.time())
    pagination_str = urllib.parse.quote(params['pagination_str'])
    a = "ea1db124af3c7062474693fa704f4ff8"
    if 'seek_rpid' in params:
        v = (f'mode={params["mode"]}' + f'&oid={params["oid"]}' + f'&pagination_str={pagination_str}' +
             f'&plat={params["plat"]}' + f'&seek_rpid={params["seek_rpid"]}' + f'&type={params["type"]}' +
             f'&web_location={params["web_location"]}' + f'&wts={wts}' + a)
    else:
        v = (f'mode={params["mode"]}' + f'&oid={params["oid"]}' + f'&pagination_str={pagination_str}' +
             f'&plat={params["plat"]}' + f'&type={params["type"]}' + f'&web_location={params["web_location"]}' +
             f'&wts={wts}' + a)
    md5 = hashlib.md5()
    md5.update(v.encode("utf-8"))
    w_rid = md5.hexdigest()
    return w_rid, wts
