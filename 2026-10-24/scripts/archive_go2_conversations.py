"""Export user-visible project conversations from local Codex records.

Does not contact or control the robot. Excludes internal reasoning/context and
redacts credential values. Remote material is explicitly a partial recovery.
"""
import base64
import collections
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'reports/2026-10-24/conversations'
CUTOFF = '2026-10-24T10:13:22.000Z'
DAY_START = '2026-10-23T16:00:00.000Z'
REMOTE = '01a16bf4-16fd-7822-92b1-9e847736d64d'
TITLES = {
    '01a14a70-d183-7fe2-b56c-80c868e63278': ('local-main', '电子狗理论'),
    '01a14ebe-bf57-7d12-b122-2cc4cd02271c': ('local-ssh', '配置狗的远程连接'),
    '01a15e0c-3f61-70d1-a664-bf65817515b4': ('local-survey', 'Survey CyberDog control benchmarks'),
}
REDACTIONS = collections.Counter()
SKIP_TYPES = {'reasoning', 'Reasoning', 'ContextCompaction'}


def sanitize(value):
    if isinstance(value, dict):
        if value.get('type') in SKIP_TYPES:
            return {'omitted': 'internal_context'}
        result = {}
        for key, item in value.items():
            if key in {'internal_chat_message_metadata_passthrough', 'encrypted_content', 'raw_content'}:
                continue
            if key.lower() in {'password', 'passwd', 'api_key', 'access_token', 'refresh_token', 'id_token', 'client_secret'} and item:
                result[key] = '[已脱敏]'
                REDACTIONS['credential_fields'] += 1
            else:
                result[key] = sanitize(item)
        return result
    if isinstance(value, list):
        return [sanitize(x) for x in value if not (isinstance(x, dict) and x.get('type') in SKIP_TYPES)]
    if not isinstance(value, str):
        return value
    # Parse nested JSON from MCP results so hidden fields can be removed structurally.
    if value.lstrip().startswith(('{', '[')):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (dict, list)):
                return json.dumps(sanitize(parsed), ensure_ascii=False)
        except (ValueError, RecursionError):
            pass
    patterns = [
        (r'(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]{12,}', r'\1[已脱敏]'),
        (r'(?<![\w-])sk-[A-Za-z0-9_-]{16,}', '[已脱敏 API key]'),
        (r'(?i)((?:password|passwd|api_key|access_token|refresh_token|client_secret)\s*[=:]\s*[\x22\x27]?)([^\s\x22\x27,;}`]{3,})', r'\1[已脱敏]'),
        (r'(密码(?:为|是)?\s*[:：=]?\s*[`*\x22\x27]*)([A-Za-z0-9!@#$%^&._+-]{3,})', r'\1[已脱敏]'),
        (r'(?i)((?:password|passwd|密码)[^\n]{0,12}?[`\x22\x27])123([`\x22\x27])', r'\1[已脱敏]\2'),
        (r'(?i)((?:verification code|device code|验证码|one-time code)[^\n]{0,45}?)[A-Z0-9]{4,5}-[A-Z0-9]{4,5}', r'\1[已脱敏设备码]'),
        (r'(?<![A-Z0-9])[A-Z0-9]{4}-[A-Z0-9]{5}(?![A-Z0-9])', '[已脱敏设备码]'),
        (r'(?i)((?:[\x22\x27]?chars[\x22\x27]?)\s*[:=]\s*[\x22\x27])123(?:\\n|\n)?', r'\1[已脱敏输入]'),
        (r'-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?-----END [^-]*PRIVATE KEY-----', '[已脱敏私钥]'),
    ]
    for pattern, replacement in patterns:
        value, n = re.subn(pattern, replacement, value)
        REDACTIONS['text_values'] += n
    return value


def local_time(ts):
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00')).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return str(ts)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def write_jsonl(path, rows):
    path.write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in rows), encoding='utf-8')


def message_text(payload, folder):
    parts = []
    for item in payload.get('content', []):
        if 'text' in item:
            parts.append(item['text'])
        elif item.get('type') in {'input_image', 'image'}:
            url = item.get('image_url', item.get('url', ''))
            if isinstance(url, dict): url = url.get('url', '')
            if isinstance(url, str) and url.startswith('data:image/') and ';base64,' in url:
                header, data = url.split(';base64,', 1)
                try:
                    raw = base64.b64decode(data)
                    ext = header.split('/')[1].split(';')[0].replace('jpeg', 'jpg')
                    name = hashlib.sha256(raw).hexdigest()[:20]+'.'+ext
                    media = DEST / 'media'; media.mkdir(exist_ok=True)
                    (media/name).write_bytes(raw)
                    parts.append('![会话图片](../media/%s)' % name)
                except (ValueError, TypeError):
                    parts.append('[图片载荷无法解码]')
            else:
                parts.append('[会话图片引用：%s]' % url)
    return sanitize('\n'.join(parts))


def write_markdown(path, title, rows, notice=''):
    lines = ['# '+title, '', notice, '时间均为北京时间（Asia/Shanghai）。', '']
    for i, row in enumerate(rows, 1):
        role = {'user':'用户', 'assistant':'助手', 'coordinator':'本地协调器'}.get(row.get('role'), row.get('role', '记录'))
        lines += ['## %d · %s · %s' % (i, local_time(row.get('timestamp')), role), '', row.get('text', ''), '']
    path.write_text('\n'.join(lines), encoding='utf-8')


def export():
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = {'date':'2026-10-24', 'timezone':'Asia/Shanghai', 'cutoff_utc':CUTOFF,
                'cutoff_local':local_time(CUTOFF), 'local':[], 'remote':{},
                'scope':'Project conversations; complete retained visible local messages through cutoff, partial remote recovery; credentials redacted; internal context excluded.'}
    remote_records = []
    remote_messages = {}
    embedded = []

    def remember(row):
        text = row.get('text', '')
        if not text: return
        key = row.get('id') or hashlib.sha256((row.get('role', '')+text).encode()).hexdigest()
        old = remote_messages.get(key)
        if not old or len(text) > len(old.get('text', '')):
            remote_messages[key] = row

    seen_threads = set()
    # Resume shards can repeat the same session id with no records before cutoff.
    # The original chronological file owns this historical snapshot; do not let
    # a later empty shard overwrite its already exported messages.
    for source in sorted(Path.home().joinpath('.codex/sessions').rglob('*.jsonl')):
        try:
            with source.open(encoding='utf-8') as f: meta=json.loads(f.readline()).get('payload', {})
        except (OSError, ValueError): continue
        identity = meta.get('id')
        if identity not in TITLES or identity in seen_threads: continue
        seen_threads.add(identity)
        name,title = TITLES[identity]; folder=DEST/name; folder.mkdir(exist_ok=True)
        messages=[]; tool_records=[]; count=0; digest=hashlib.sha256(); compactions=0
        for raw in source.read_bytes().splitlines(keepends=True):
            try: record=json.loads(raw)
            except ValueError: continue
            ts=record.get('timestamp','')
            if ts>CUTOFF: continue
            digest.update(raw);count+=1
            p=record.get('payload',{});typ=p.get('type')
            if record.get('metadata',{}).get('compaction_output'):
                compactions+=1;continue
            if record.get('type')=='response_item' and typ=='message' and p.get('role') in {'user','assistant'}:
                if p.get('channel')=='analysis':continue
                text=message_text(p,folder)
                if p.get('role')=='user' and text.lstrip().startswith(('<environment_context>','<codex_internal_context','<turn_aborted>')):continue
                if text:
                    row={'timestamp':ts,'id':p.get('id'),'role':p['role'],'phase':p.get('phase'), 'text':text}
                    messages.append(row)
                    if name=='local-main' and DAY_START<=ts and p['role']=='user' and any(x in text for x in ('本轮','已恢复有效前进','未达到稳定控制目标')) and any(x in text for x in ('EFFICIENT_REPORT','诊断','验收')):
                        embedded.append(dict(row, provenance='user_pasted_remote_report'))
            if record.get('type')=='response_item' and typ in {'function_call','custom_tool_call','function_call_output','custom_tool_call_output'}:
                tool_records.append(sanitize({'timestamp':ts,'source_line':count,'record':p}))
            item=p.get('item',{})
            if record.get('type')=='event_msg' and typ=='item_completed' and item.get('type') in {'CommandExecution','McpToolCall','FileChange','ImageView','Extension'}:
                tool_records.append(sanitize({'timestamp':ts,'source_line':count,'record':item}))
            if item.get('type')=='McpToolCall' and item.get('tool') in {'read_thread','wait_threads','send_message_to_thread'} and REMOTE in json.dumps(item.get('arguments',{})):
                remote_records.append(sanitize({'observed_at':ts,'record':item}))
                if item['tool']=='send_message_to_thread':
                    remember({'id':item.get('id'),'timestamp':ts,'role':'coordinator','text':sanitize(item['arguments'].get('prompt','')),'provenance':'local dispatch log'})
                for c in item.get('result',{}).get('content',[]):
                    try:data=json.loads(c.get('text',''))
                    except ValueError:continue
                    for turn in data.get('turns',[]):
                        for entry in turn.get('items',[]):
                            if entry.get('type') in {'agentMessage','userMessage'} and entry.get('text'):
                                remember({'id':entry.get('id'),'timestamp':ts,'role':'assistant' if entry['type']=='agentMessage' else 'user','text':sanitize(entry['text']),'phase':entry.get('phase'),'turn_id':turn.get('id'),'turn_started_at':turn.get('startedAt'),'provenance':'read_thread snapshot; timestamp is retrieval time'})
                    for poll in data.get('polls',[]):
                        entry=poll.get('latestAssistantMessage') or {}
                        if isinstance(entry,dict) and entry.get('text'):
                            remember({'id':entry.get('id') or poll.get('latestAssistantMessageId'),'timestamp':ts,'role':'assistant','text':sanitize(entry['text']),'phase':entry.get('phase'),'turn_id':entry.get('turnId'),'provenance':'wait_threads snapshot; timestamp is retrieval time'})
        today=[x for x in messages if DAY_START<=x['timestamp']<=CUTOFF]
        write_jsonl(folder/'messages-full.jsonl',messages)
        write_jsonl(folder/'tools-full.jsonl',tool_records)
        write_jsonl(folder/'messages-today.jsonl',today)
        write_markdown(folder/'完整对话.md',title,messages,'本地保留记录的完整可见对话，截止 '+local_time(CUTOFF)+'；不含内部上下文。')
        write_markdown(folder/'今日对话.md',title+' · 今日',today)
        manifest['local'].append({'thread_id':identity,'title':title,'source_path':str(source),'source_prefix_sha256':digest.hexdigest(),'source_records_before_cutoff':count,'messages':len(messages),'today_messages':len(today),'tool_records':len(tool_records),'excluded_compaction_messages':compactions,'folder':name})

    remote_dir=DEST/'robot-recovered';remote_dir.mkdir(exist_ok=True)
    recovered=sorted(remote_messages.values(),key=lambda x:x['timestamp'])
    write_jsonl(remote_dir/'recovered-messages.jsonl',recovered)
    write_jsonl(remote_dir/'coordination-tool-records.jsonl',remote_records)
    write_jsonl(remote_dir/'user-pasted-reports.jsonl',embedded)
    write_markdown(remote_dir/'远端协调对话-部分恢复.md','修复 Go2 运动方向并验证 · 部分恢复',recovered,'按本地接收时间排序；不是狗上完整原始会话。回报可能是中途快照或旧总结，实验结果以对应日志为准。')
    write_markdown(remote_dir/'用户转贴的狗上报告.md','用户转贴的狗上报告',embedded,'保留在本地会话中的用户转贴，不能代替完整远端原始会话。')
    pasted=Path.home()/'.codex/attachments/2d7a16ec-f7f9-4b93-a75f-40c278515e05/已粘贴的文本.txt'
    raw=pasted.read_bytes();text=raw.decode('utf-8-sig')
    (remote_dir/'狗上早期完整转贴.md').write_text(sanitize(text),encoding='utf-8')
    manifest['remote']={'thread_id':REMOTE,'title':'修复 Go2 运动方向并验证','original_full_session_retrieved':False,'reason':'robot SSH and remote read_thread unavailable at export','recovered_messages':len(recovered),'coordination_records':len(remote_records),'user_pasted_reports':len(embedded),'pasted_source_path':str(pasted),'pasted_source_sha256':hashlib.sha256(raw).hexdigest(),'pasted_scope':'user supplied early thread export; not all later turns','last_snapshot_time':max((x['observed_at'] for x in remote_records),default=None)}
    manifest['redactions']=dict(REDACTIONS)
    write_json(DEST/'manifest.json',manifest)
    lines=['# 对话归档索引 · 2026-10-24','','截止：'+local_time(CUTOFF)+'（北京时间）。报告覆盖今天，完整对话另保留此前历史。','','## 本地可见对话','']
    for entry in manifest['local']:
        lines.append('- [%s](%s/完整对话.md)：%d条消息，今天%d条；另有%d条工具记录。'%(entry['title'],entry['folder'],entry['messages'],entry['today_messages'],entry['tool_records']))
    lines+=['','每个目录含完整Markdown、今日Markdown及JSONL。工具日志另存，避免打断阅读；内嵌图片在media目录。密码、令牌、设备码做脱敏，未复制登录配置和私钥。','','## 狗上对话：部分恢复','',
            '- [早期聊天完整转贴](robot-recovered/狗上早期完整转贴.md)：用户在13:38提供的导出文本。',
            '- [后续协调对话](robot-recovered/远端协调对话-部分恢复.md)：从本地调用记录恢复%d条消息。'%len(recovered),
            '- [用户转贴报告](robot-recovered/用户转贴的狗上报告.md)：%d条。'%len(embedded),
            '- `coordination-tool-records.jsonl`保留%d条远端调用记录，可追溯片段和截断状态。'%len(remote_records),'',
            '**狗离线，尚未取得狗上完整原始会话文件。** 中途未被本地读取或转贴的内容可能缺失。不能把这些文件称为“全部狗上对话已备份”。下次连接后应补取该thread_id对应的远端session，并保留本次恢复记录作比对。',
            '', '机器可读来源与数量见`manifest.json`，归档文件校验见上级目录`SHA256SUMS`。']
    (DEST/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'local':manifest['local'],'remote':manifest['remote'],'redactions':manifest['redactions']},ensure_ascii=False,indent=2))


if __name__=='__main__':export()
