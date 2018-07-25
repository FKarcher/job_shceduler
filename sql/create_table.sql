CREATE TABLE job
(
    id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
    name varchar(50) NOT NULL COMMENT '任务名称',
    job_id varchar(50) NOT NULL COMMENT '程序指定的任务id，唯一',
    status int DEFAULT 0 NOT NULL COMMENT '-1删除，0停止，1执行中，2暂停',
    executed_times bigint DEFAULT 0 NOT NULL COMMENT '执行次数',
    cron varchar(255) DEFAULT '' COMMENT '执行策略',
    instance_cnt int DEFAULT 0 COMMENT '执行次数',
    type int default 1 comment '1 interval 2 cron',
    create_time timestamp DEFAULT current_timestamp NOT NULL,
    update_time timestamp DEFAULT current_timestamp NOT NULL
)
  comment '定时任务'
  engine = InnoDB default charset=utf8;
CREATE UNIQUE INDEX job_job_id_uindex ON job (job_id);


create table leetcode_problems
(
  id          int auto_increment
    primary key,
  lid         int          null
  comment '前端展现题目号',
  qid         int          null
  comment 'LeetCode题目真正Id',
  title       varchar(100) null
  comment '题目',
  `desc`      text         null
  comment '题干',
  difficulty  int          not null
  comment '1简单 2中等 3困难',
  is_locked   int          not null
  comment '0没锁 1上锁',
  type        int          null
  comment '0算法，1数据库',
  submit_url  varchar(255) null
  comment '代码提交链接',
  code_def    text         null
  comment '代码初始化',
  frequency   float        null
  comment '题目出现频率',
  title_slug  varchar(150) null
  comment '题目的url名称',
  create_time timestamp     not null,
  update_time timestamp  default current_timestamp   not null,
  constraint lid
  unique (lid),
  constraint qid
  unique (qid)
)engine = InnoDB default charset=utf8;

create table leetcode_tag_info
(
  id          int auto_increment
    primary key,
  name        varchar(100) not null
  comment '标签名称',
  slug        varchar(150) not null
  comment '标签url',
  questions   text         null
  comment '题目id',
  create_time datetime     not null,
  update_time datetime  default current_timestamp  not null,
  constraint name
  unique (name),
  constraint slug
  unique (slug)
) engine = InnoDB default charset=utf8;
