
### 爬虫启动domain

name: start_domain

field:
- domain
- start_url

index:
- domain


### 调度爬虫domain

临时建立数据表,无索引

name: raw_doc_${bizdate}

field:
- domain
- url
- html

### 候选domain

由分析raw_doc_${bizdate}，提取出候选的domain和start_url
审核后进入start_domain

name: candidate_domain

field:
- domain
- start_url
- status # 0代表待审核，1代表是blog，2代表非blog

index:
- domain
 
### 处理好的文档 

name: doc_${bizdate}

field:
- url
- text
- summary
- domain

index:
- url
