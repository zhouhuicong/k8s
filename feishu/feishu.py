import os
import json
import requests
import arrow

from flask import Flask
from flask import request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def send():
    if request.method == 'POST':
        post_data = request.get_data()
        send_alert(bytes2json(post_data))
        return 'success'
    else:
        return 'weclome to use prometheus alertmanager dingtalk webhook server!'


def bytes2json(data_bytes):
    data = data_bytes.decode('utf8').replace("'", '"')
    return json.loads(data)


def send_alert(data):
    token = os.getenv('ROBOT_TOKEN')
    if not token:
        print('you must set ROBOT_TOKEN env')
        return
    url = 'https://open.feishu.cn/open-apis/bot/v2/hook/%s' % token
    #url = 'https://open.feishu.cn/open-apis/bot/v2/hook/********'
    for output in data['alerts'][:]:
        try:
            pod_name = output['labels']['pod']
        except KeyError:
            try:
                pod_name = output['labels']['pod_name']
            except KeyError:
                pod_name = 'null'

        try:
            namespace = output['labels']['namespace']
        except KeyError:
            namespace = 'null'

        try:
            message = output['annotations']['message']
        except KeyError:
            try:
                message = output['annotations']['description']
            except KeyError:
                message = 'null'
        MESSAGE = os.getenv('ROBOT_MESSAGE')
        MESSAGE_URL = os.getenv('ROBOT_MESSAGE_URL')
        send_data = {
			    "msg_type": "post",
			    "content": {
			        "post": {
			            "zh_cn": {
			                "title": "%s" % MESSAGE ,
			                "content": [
			                    [
			                        {
			                            "tag": "text",
			                            "text": "## 告警程序: %s \n" % MESSAGE +
						                        "**告警级别**: %s \n\n" % output['labels']['severity'] +
						                        "**告警类型**: %s \n\n" % output['labels']['alertname'] +
						                        "**故障pod**: %s \n\n" % pod_name +
						                        "**故障namespace**: %s \n\n" % namespace +
						                        "**告警详情**: %s \n\n" % message +
						                        "**告警状态**: %s \n\n" % output['status'] +
						                        "**触发时间**: %s \n\n" % arrow.get(output['startsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ') +
						                        "**触发结束时间**: %s \n" % arrow.get(output['endsAt']).to('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss ZZ')
			                        },
			                        {
			                            "tag": "a",
			                            "text": "具体请查看",
			                            "href": "%s" % MESSAGE_URL
			                        }
			                    ]
			                ]
			            }
			        }
			    }
			}
        req = requests.post(url, json=send_data)
        result = req.json()
        if result['errcode'] != 0:
            print('notify dingtalk error: %s' % result['errcode'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)








