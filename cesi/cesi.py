# -*- coding: utf-8 -*-

import xmlrpclib
import ConfigParser
from datetime import datetime, timedelta
from flask import jsonify

CONFIG_FILE = "/etc/cesi.conf"
class Config:

    def __init__(self, CFILE):
        '''
        读配置文件: [<类型>:<名字>]
            取类型名称,比如:
            主机名, 组名, 环境名
        '''
        self.CFILE = CFILE
        self.cfg = ConfigParser.ConfigParser()
        self.cfg.read(self.CFILE)

        self.node_list = []
        for name in self.cfg.sections():
            if name[:4] == 'node':
                self.node_list.append(name[5:])

        self.environment_list = []
        for name in self.cfg.sections():
            if name[:11] == 'environment':
                self.environment_list.append(name[12:])

        self.group_list = []
        for name in self.cfg.sections():
            if name[:5] == 'group':
                self.group_list.append(name[6:])


    def getNodeConfig(self, node_name):
        '''
        通过主机名称来查找主机详细信息
        '''
        self.node_name = "node:%s" % (node_name)                    # node:<参数>
        self.username = self.cfg.get(self.node_name, 'username')    # conf 里 node 下的用户名
        self.password = self.cfg.get(self.node_name, 'password')    # 密码
        self.host = self.cfg.get(self.node_name, 'host')            # ip地址
        self.port = self.cfg.get(self.node_name, 'port')            # 端口
        self.node_config = NodeConfig(self.node_name, self.host, self.port, self.username, self.password)
        # 返回类属性: self.node_name = 'node:server1', self.host = '192.168.0.85', self.port = 9001, self.username = 'test', self.password = 'test'
        return self.node_config

    def getMemberNames(self, environment_name):
        '''
        通过环å¢名称来获取下属主机列表
        '''
        self.environment_name = "environment:%s" % (environment_name)
        self.member_list = self.cfg.get(self.environment_name, 'members')
        self.member_list = self.member_list.split(', ')
        # 返回列表: self.member_list = [ 'server1', 'server2', 'server3' ]
        return self.member_list

    def getDatabase(self):
        '''
        获取数据库地址
        '''
        return str(self.cfg.get('cesi', 'database'))

    def getActivityLog(self):
        '''
        获取日志地址
        '''
        return str(self.cfg.get('cesi', 'activity_log'))

    def getHost(self):
        '''
        获取监听主机
        '''
        return str(self.cfg.get('cesi', 'host'))

class NodeConfig:
    '''
    主机信息加载到类, 方便调用
    '''
    def __init__(self, node_name, host, port, username, password):
        self.node_name = node_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password


class Node:
    '''
    通过主机信息来获取该主机进程列表
    '''
    def __init__(self, node_config):
        self.long_name = node_config.node_name      # 'node:server1'
        self.name = node_config.node_name[5:]       # server1
        self.connection = Connection(node_config.host, node_config.port, node_config.username, node_config.password).getConnection()    # 连接上xmlrpc
        self.process_list=[]
        self.process_dict2={}
        for p in self.connection.supervisor.getAllProcessInfo():            # 获取主机上的全部进程信息
            self.process_list.append(ProcessInfo(p))                        # 某个进程信息列表
            self.process_dict2[p['group']+':'+p['name']] = ProcessInfo(p)   # { '进程组名:进程名': '进程信息' }
        self.process_dict = self.connection.supervisor.getAllProcessInfo()  # 获取主机上的全部进程信息


class Connection:
    '''
    连接 supervisorctl 管理进程
    '''
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.address = "http://%s:%s@%s:%s/RPC2" %(self.username, self.password, self.host, self.port)  # 'http://test:test@192.168.0.85:9001/RPC2'

    def getConnection(self):
        # 返回 <ServerProxy for 192.168.0.85:9001/RPC2> 对象
        return xmlrpclib.Server(self.address)


class ProcessInfo:
    '''
    格式化某个进程的信息:
    {
        'description': 'pid 29367, uptime 8:12:50',
        'exitstatus': 0,
        'group': 'test',
        'logfile': '/var/log/supervisor/test.log',
        'name': 'test',
        'now': 1506506033,
        'pid': 29367,
        'spawnerr': '',
        'start': 1506476463,
        'state': 20,
        'statename': 'RUNNING',
        'stderr_logfile': '/var/log/supervisor/test.log',
        'stdout_logfile': '/var/log/supervisor/test.log',
        'stop': 0
    }
    self.dictionary = dictionary
    self.name = 'test'
    self.group = 'test'
    self.start = 1506476463     # 启动时间, 时间戳
    self.start_hr = 把时间戳转换成 %H:%M:%S
    self.stop_hr =              # 停止时间
停止时间¶间
    self.stop = 0
    self.now = 1506506033
    self.state = 20
    self.statename = 'RUNNING'
    self.spawnerr = ''
    self.exitstatus = 0
    self.stdout_logfile = '/var/log/supervisor/test.log'
    self.stderr_logfile = '/var/log/supervisor/test.log'
    self.pid = 29367
    self.seconds = self.now - self.start    # 运行时长 (当前时间减去启动时间)
    self.uptime = 格式化成字符串
    '''
    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.name = self.dictionary['name']
        self.group = self.dictionary['group']
        self.start = self.dictionary['start']
        self.start_hr = datetime.fromtimestamp(self.dictionary['start']).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.stop_hr = datetime.fromtimestamp(self.dictionary['stop']).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.now_hr = datetime.fromtimestamp(self.dictionary['now']).strftime('%Y-%m-%d %H:%M:%S')[11:]
        self.stop = self.dictionary['stop']
        self.now = self.dictionary['now']
        self.state = self.dictionary['state']
        self.statename = self.dictionary['statename']
        self.spawnerr = self.dictionary['spawnerr']
        self.exitstatus = self.dictionary['exitstatus']
        self.stdout_logfile = self.dictionary['stdout_logfile']
        self.stderr_logfile = self.dictionary['stderr_logfile']
        self.pid = self.dictionary['pid']
        self.seconds = self.now - self.start
        self.uptime = str(timedelta(seconds=self.seconds))

class JsonValue:
    '''
    通过进程名称, 主机名称, 事件来获取和该主机有关的一切
    '''
    def __init__(self, process_name, node_name, event):
        self.process_name = process_name
        self.event = event
        self.node_name = node_name
        self.node_config = Config(CONFIG_FILE).getNodeConfig(self.node_name)
        self.node = Node(self.node_config)

    def success(self):
        '事件触发成功'
        return jsonify(status = "Success",
                       code = 80,
                       message = "%s %s %s event succesfully" %(self.node_name, self.process_name, self.event),
                       nodename = self.node_name,
                       data = self.node.connection.supervisor.getProcessInfo(self.process_name))

    def error(self, code, payload):
        '事件触发失败'
        self.code = code
        self.payload = payload
        return jsonify(status = "Error",
                       code = self.code,
                       message = "%s %s %s event unsuccesful" %(self.node_name, self.process_name, self.event),
                       nodename = self.node_name,
                       payload = self.payload)

