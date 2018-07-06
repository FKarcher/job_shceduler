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