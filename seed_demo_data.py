"""
演示数据种子脚本：分别生成一套常见的「考研」和「考公」打卡数据。

每个演示用户包含：
- 账号（密码统一 demo123）
- 科目（按 exam_type 模板：考研=政治/英语/数学/专业课；考公=行测/申论/面试）
- 四级计划树：总计划 -> 月计划 -> 周计划(×4) -> 日计划(每天每科)
- 近 28 天的打卡记录（含休息日跳过、若干补卡）
- 当月补卡次数统计 makeup_usages

可重复运行：会先清除同名演示用户及其全部数据再重建。

用法：
    .venv/bin/python seed_demo_data.py
"""
import random
from datetime import date, timedelta

from app.database import SessionLocal, engine, Base
from app.models import (
    User, Subject, Plan, PunchRecord, MakeupUsage,
)
from app.security import hash_password
from app.utils.time_util import now_str

random.seed(42)

TODAY = date.today()
WINDOW_DAYS = 28                      # 打卡/日计划覆盖最近 28 天
START = TODAY - timedelta(days=WINDOW_DAYS - 1)


# ---------- 两个演示用户的配置 ----------
DEMOS = [
    {
        "username": "kaoyan_demo",
        "exam_type": "考研",
        "target_exam_date": "2026-12-26",
        "plan_title": "2026 考研全程备考计划",
        "month_title": "考研冲刺月计划",
        # 科目: (名称, 权重, 颜色, 每日目标分钟, 学习内容样例)
        "subjects": [
            ("政治", 1.0, "#e63946", 50, ["马原 选择题", "毛中特 背诵", "史纲 时间线", "肖秀荣 1000题", "时政整理"]),
            ("英语", 1.2, "#457b9d", 90, ["阅读真题 2 篇", "背单词 100", "长难句精析", "作文模板", "完形填空"]),
            ("数学", 1.5, "#2a9d8f", 120, ["高数 极限/微分", "线代 矩阵", "概率论 分布", "660 题", "真题套卷"]),
            ("专业课", 1.3, "#f4a261", 80, ["教材精读", "课后习题", "框架笔记", "真题回顾", "名词解释背诵"]),
        ],
    },
    {
        "username": "kaogong_demo",
        "exam_type": "考公",
        "target_exam_date": "2026-11-29",
        "plan_title": "2026 国考全程备考计划",
        "month_title": "国考冲刺月计划",
        "subjects": [
            ("行测", 1.3, "#264653", 90, ["言语理解 30 题", "判断推理专项", "资料分析", "数量关系", "常识积累"]),
            ("申论", 1.2, "#e76f51", 90, ["归纳概括", "综合分析", "大作文 1 篇", "范文抄写", "热点素材"]),
            ("面试", 1.0, "#8338ec", 30, ["综合分析题", "计划组织协调", "人际关系", "模拟答题", "热点评论"]),
        ],
    },
]


def _week_index(d: date) -> int:
    """该日期落在第几周窗口(0..3)"""
    return (d - START).days // 7


def _clear_user(db, username: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return
    uid = user.id
    # 按依赖顺序删除，避免 subject 的 RESTRICT 外键阻塞
    db.query(PunchRecord).filter(PunchRecord.user_id == uid).delete()
    db.query(Plan).filter(Plan.user_id == uid).delete()
    db.query(Subject).filter(Subject.user_id == uid).delete()
    db.query(MakeupUsage).filter(MakeupUsage.user_id == uid).delete()
    db.delete(user)
    db.commit()
    print(f"[seed] 已清除旧的演示用户: {username}")


def _build_for(db, cfg: dict):
    now = now_str()

    # 1) 用户
    user = User(
        username=cfg["username"],
        password_hash=hash_password("demo123"),
        role="user",
        exam_type=cfg["exam_type"],
        target_exam_date=cfg["target_exam_date"],
        is_active=1,
        created_at=now,
    )
    db.add(user)
    db.flush()

    # 2) 科目
    subjects = []
    for i, (name, weight, color, daily, contents) in enumerate(cfg["subjects"], start=1):
        s = Subject(
            user_id=user.id, name=name, weight=weight, color=color,
            description=f"{cfg['exam_type']}科目 - {name}",
            sort_order=i, is_activate=1, created_at=now, updated_at=now,
        )
        db.add(s)
        db.flush()
        subjects.append({"obj": s, "daily": daily, "contents": contents})

    # 3) 计划树：总 -> 月 -> 周×4 -> 日(每天每科)
    total = Plan(
        user_id=user.id, parent_id=None, plan_type="total",
        title=cfg["plan_title"], subject_id=None, target_minutes=0,
        content="全程备考总目标", period_start=START.strftime("%Y-%m-%d"),
        period_end=cfg["target_exam_date"], status="进行中",
        sort_order=1, created_at=now, updated_at=now,
    )
    db.add(total)
    db.flush()

    month_end = TODAY + timedelta(days=14)
    month = Plan(
        user_id=user.id, parent_id=total.id, plan_type="month",
        title=cfg["month_title"], subject_id=None, target_minutes=0,
        content="本阶段月度目标", period_start=START.strftime("%Y-%m-%d"),
        period_end=month_end.strftime("%Y-%m-%d"), status="进行中",
        sort_order=1, created_at=now, updated_at=now,
    )
    db.add(month)
    db.flush()

    # 4 个周计划
    weeks = []
    for w in range(4):
        ws = START + timedelta(days=w * 7)
        we = ws + timedelta(days=6)
        wk = Plan(
            user_id=user.id, parent_id=month.id, plan_type="week",
            title=f"第 {w + 1} 周计划", subject_id=None, target_minutes=0,
            content=f"{ws.strftime('%m/%d')}–{we.strftime('%m/%d')} 周目标",
            period_start=ws.strftime("%Y-%m-%d"), period_end=we.strftime("%Y-%m-%d"),
            status="已完成" if we < TODAY else "进行中",
            sort_order=w + 1, created_at=now, updated_at=now,
        )
        db.add(wk)
        db.flush()
        weeks.append(wk)

    # 日计划（每天每科一条，挂到所属周）
    day_plan_count = 0
    for offset in range(WINDOW_DAYS):
        d = START + timedelta(days=offset)
        wk = weeks[_week_index(d)]
        for sub in subjects:
            dp = Plan(
                user_id=user.id, parent_id=wk.id, plan_type="day",
                title=f"{d.strftime('%m/%d')} {sub['obj'].name}",
                subject_id=sub["obj"].id, target_minutes=sub["daily"],
                content=f"{sub['obj'].name}日目标 {sub['daily']} 分钟",
                period_start=d.strftime("%Y-%m-%d"), period_end=d.strftime("%Y-%m-%d"),
                status="已完成" if d < TODAY else "进行中",
                sort_order=sub["obj"].sort_order, created_at=now, updated_at=now,
            )
            db.add(dp)
            day_plan_count += 1

    # 4) 打卡记录
    punch_count = 0
    makeup_count = 0
    for offset in range(WINDOW_DAYS):
        d = START + timedelta(days=offset)
        ds = d.strftime("%Y-%m-%d")
        is_weekend = d.weekday() >= 5

        # 每周约休息一天（周日大概率整天不打卡）
        rest_day = (d.weekday() == 6 and random.random() < 0.6)
        if rest_day:
            continue

        for sub in subjects:
            # 单科当天是否学习：工作日高概率，周末稍低
            study_prob = 0.78 if not is_weekend else 0.55
            if random.random() > study_prob:
                continue

            target = sub["daily"]
            factor = random.uniform(0.6, 1.3)
            actual = max(15, int(round(target * factor / 5) * 5))

            # 近 7 天内的少量记录标记为补卡
            days_ago = (TODAY - d).days
            is_makeup = 1 if (0 < days_ago <= 7 and random.random() < 0.12) else 0
            if is_makeup:
                makeup_count += 1

            db.add(PunchRecord(
                user_id=user.id, punch_date=ds, subject_id=sub["obj"].id,
                actual_minutes=actual, content=random.choice(sub["contents"]),
                is_makeup=is_makeup, created_at=now, updated_at=now,
            ))
            punch_count += 1

    # 5) 当月补卡次数统计
    if makeup_count:
        ym = TODAY.strftime("%Y-%m")
        db.add(MakeupUsage(
            user_id=user.id, year_month=ym,
            used_count=min(makeup_count, 5), updated_at=now,
        ))

    db.commit()
    print(
        f"[seed] {cfg['username']} ({cfg['exam_type']}): "
        f"科目 {len(subjects)}，日计划 {day_plan_count}，打卡 {punch_count}，"
        f"补卡 {makeup_count}，区间 {START} ~ {TODAY}"
    )


def main():
    # 确保表存在
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for cfg in DEMOS:
            _clear_user(db, cfg["username"])
            _build_for(db, cfg)
    finally:
        db.close()
    print("\n[seed] 完成。演示账号：")
    print("  考研: kaoyan_demo / demo123")
    print("  考公: kaogong_demo / demo123")


if __name__ == "__main__":
    main()
