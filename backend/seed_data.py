"""初始化种子数据（含演示数据）"""
from datetime import datetime, timedelta
from database import SessionLocal, init_db
from models import (
    Organization, OrgLevel,
    User, UserRole,
    Customer,
    ServiceCategory, ServiceItem, TechnicianSkill,
    WorkOrder, OrderStatus, WorkOrderLog,
    TechnicianWallet,
)
from utils.auth import hash_password


def seed():
    init_db()
    db = SessionLocal()

    # ── 1. 组织 ──
    if db.query(Organization).count() > 0:
        print("Data already exists, skipping.")
        db.close()
        return

    hq = Organization(name="云匠-全国总部", level=OrgLevel.HEADQUARTERS, city="佛山", status="active")
    db.add(hq)
    gz = Organization(name="广州分公司", parent_id=1, level=OrgLevel.BRANCH, city="广州", status="active")
    db.add(gz)
    sz = Organization(name="深圳分公司", parent_id=1, level=OrgLevel.BRANCH, city="深圳", status="active")
    db.add(sz)
    db.flush()
    print("[OK] 创建了 3 个组织")

    # ── 2. 用户 ──
    admin = User(name="管理员", phone="13800138000", password_hash=hash_password("admin123"),
                 role=UserRole.ADMIN, status="active")
    db.add(admin)

    disp = User(name="调度员小李", phone="13800138001", password_hash=hash_password("123456"),
                role=UserRole.DISPATCHER, org_id=2, status="active")
    db.add(disp)

    techs = [
        User(name="张师傅", phone="13900139001", password_hash=hash_password("123456"),
             role=UserRole.TECHNICIAN, org_id=2, status="active"),
        User(name="李师傅", phone="13900139002", password_hash=hash_password("123456"),
             role=UserRole.TECHNICIAN, org_id=2, status="active"),
        User(name="王师傅", phone="13900139003", password_hash=hash_password("123456"),
             role=UserRole.TECHNICIAN, org_id=3, status="active"),
        User(name="赵阿姨", phone="13900139004", password_hash=hash_password("123456"),
             role=UserRole.TECHNICIAN, org_id=2, status="active"),
    ]
    db.add_all(techs)
    db.flush()
    print("[OK] 创建了 6 个用户（1管理员+1调度+4师傅）")

    # ── 3. 服务分类与项目 ──
    cats = [
        ServiceCategory(name="家电维修", icon="repair", description="空调/冰箱/洗衣机/热水器等维修", sort_order=1),
        ServiceCategory(name="家政保洁", icon="clean", description="日常保洁/深度保洁/开荒保洁", sort_order=2),
        ServiceCategory(name="清洗服务", icon="wash", description="油烟机/空调/冰箱清洗等", sort_order=3),
    ]
    db.add_all(cats)
    db.flush()

    items_data = [
        (1, "空调维修", "次", 80), (1, "冰箱维修", "次", 80), (1, "洗衣机维修", "次", 60),
        (1, "热水器维修", "次", 60), (1, "油烟机维修", "次", 60), (1, "电视维修", "次", 80),
        (2, "日常保洁", "小时", 40), (2, "深度保洁", "㎡", 8), (2, "开荒保洁", "㎡", 10),
        (2, "擦玻璃", "次", 150), (2, "收纳整理", "小时", 50),
        (3, "油烟机清洗", "台", 120), (3, "空调清洗", "台", 100), (3, "洗衣机清洗", "台", 80),
        (3, "冰箱清洗", "台", 80), (3, "热水器清洗", "台", 80),
    ]
    items = []
    for cat_id, name, unit, price in items_data:
        item = ServiceItem(category_id=cat_id, name=name, level=1, unit_type=unit, default_price=price)
        db.add(item)
        items.append(item)
    db.flush()
    print(f"[OK] 创建了 3 个服务大类 + {len(items_data)} 个服务项目")

    # ── 4. 师傅技能 ──
    # 张师傅：维修类技能
    for item in items[:4]:  # 前4个维修项目
        db.add(TechnicianSkill(user_id=techs[0].id, service_item_id=item.id))
    # 李师傅：维修+清洗
    for item in items[2:6] + items[11:13]:
        db.add(TechnicianSkill(user_id=techs[1].id, service_item_id=item.id))
    # 王师傅：清洗类
    for item in items[11:16]:
        db.add(TechnicianSkill(user_id=techs[2].id, service_item_id=item.id))
    # 赵阿姨：保洁类
    for item in items[6:11]:
        db.add(TechnicianSkill(user_id=techs[3].id, service_item_id=item.id))
    print("[OK] 配置了师傅技能")

    # ── 5. 客户 ──
    customers = [
        Customer(name="张三", phone="13912345678", address="广州市天河区中山大道100号", city="广州"),
        Customer(name="李四", phone="13912345679", address="广州市番禺区市桥街200号", city="广州"),
        Customer(name="王五", phone="13912345680", address="广州市海珠区新港路300号", city="广州"),
        Customer(name="赵六", phone="13912345681", address="深圳市南山区科技园南路50号", city="深圳"),
        Customer(name="陈小姐", phone="13912345682", address="广州市越秀区北京路50号", city="广州"),
    ]
    db.add_all(customers)
    db.flush()
    print(f"[OK] 创建了 {len(customers)} 个客户")

    # ── 6. 演示工单 ──
    now = datetime.now()
    demo_orders = [
        WorkOrder(order_no="DEMO20260605001", customer_id=1, service_item_id=1, category_type="家电维修",
                  fault_description="空调不制冷，已使用5年", address="广州市天河区中山大道100号",
                  status=OrderStatus.PENDING, source="qrcode", created_at=now - timedelta(hours=2)),
        WorkOrder(order_no="DEMO20260605002", customer_id=2, service_item_id=12, category_type="清洗服务",
                  fault_description="油烟机清洗，半年没洗了", address="广州市番禺区市桥街200号",
                  status=OrderStatus.PENDING, source="qrcode", created_at=now - timedelta(hours=1)),
        WorkOrder(order_no="DEMO20260605003", customer_id=3, service_item_id=7, category_type="家政保洁",
                  fault_description="日常保洁3小时", address="广州市海珠区新港路300号",
                  status=OrderStatus.DISPATCHED, technician_id=techs[3].id,
                  source="phone", created_at=now - timedelta(hours=4)),
        WorkOrder(order_no="DEMO20260605004", customer_id=4, service_item_id=13, category_type="清洗服务",
                  fault_description="空调清洗，两台挂机", address="深圳市南山区科技园南路50号",
                  status=OrderStatus.IN_PROGRESS, technician_id=techs[2].id,
                  source="qrcode", created_at=now - timedelta(hours=6)),
        WorkOrder(order_no="DEMO20260605005", customer_id=5, service_item_id=3, category_type="家电维修",
                  fault_description="洗衣机不脱水", address="广州市越秀区北京路50号",
                  status=OrderStatus.COMPLETED, technician_id=techs[0].id,
                  source="qrcode", total_fee=180, material_fee=30, service_fee=150,
                  created_at=now - timedelta(days=1), completed_at=now - timedelta(hours=20)),
    ]
    db.add_all(demo_orders)
    print(f"[OK] 创建了 {len(demo_orders)} 个演示工单")

    # ── 7. 师傅钱包 ──
    for tech in techs:
        db.add(TechnicianWallet(user_id=tech.id, total_earned=0))
    print("[OK] 创建了师傅钱包")

    db.commit()
    db.close()
    print(f"\n{'='*40}")
    print("  初始化完成！")
    print(f"{'='*40}")
    print(f"  管理员: 13800138000 / admin123")
    print(f"  调度员: 13800138001 / 123456")
    print(f"  师傅端: 13900139001~39004 / 123456")
    print(f"  客人端: http://localhost:8000/")
    print(f"  API:    http://localhost:8000/docs")
    print(f"{'='*40}")


if __name__ == "__main__":
    seed()
