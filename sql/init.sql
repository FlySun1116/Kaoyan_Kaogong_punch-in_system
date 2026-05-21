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
    foreign key (parent_id) references plans(id) on delete cascade,
    foreign key (subject_id) references subjects(id) on delete set null
);


--打卡记录表