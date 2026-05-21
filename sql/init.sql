pragma foreign_keys =on;

-- 科目表
create table if not exists subjects(
    id int primary key autoincrement,
    name text not null unique,
    weight real not null default 1.0,
    color text,
    description text,
    sort_order int not null default 0,
    is_activate int not null default 1, -- 1启用，0禁用
    created_at text not null default (datetime('now','localtime')),
    updated_at text not null default (datetime('now','localtime'))
);

-- 计划表 总/年/月/日，树形结构
create table if not exists plans(
    id int primary key autoincrement,
    parent_id int,
    plan_type text not null check(plan_type in ('total','month','week','day')),
    title text not null,
    subject_id int,
    target_minutes int not null default 0,
    content text,
    period_start text not null,--格式 YYYY-MM-DD
    period_end text not null,
    status text not null default '未开始'
                                check(status in ('未开始','进行中','已完成','已过期')),
    sort_order int not null default 0,
    created_at text not null default (datetime('now','localtime')),
    updated_at text not null default (datetime('now','localtime')),
    foreign key (parent_id) references plans(id) on delete cascade,-- 多级联删除，即删除父计划，就删除子计划
    foreign key (subject_id) references subjects(id) on delete restrict-- 计划存在并引用该科目表，就不允许删除该科目
);

-- 数据库性能优化

-- 打卡记录表
create table if not exists punch_recodes(
    id int primary key autoincrement,
    punch_date text not null,--打卡日期，格式YYYY-MM-DD
    subject_id int not null,
    actual_minutes int not null default 0,
    content text,
    is_makeup int not null default 0,-- 1补卡 0正常
    created_at text not null default (datetime('now','localtime')),
    updated_at text not null default(datetime('now','localtime')),
    foreign key (subject_id) references subjects(id) on delete restrict,-- 如果还有计划引用这个科目，就不许删除这个科目
    unique(punch_date,subject_id)-- 联合约束，打卡日期和打卡的科目不能相同

)