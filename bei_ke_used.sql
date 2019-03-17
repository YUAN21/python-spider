
create table bei_ke_house_used
(
    id integer not null,
    --id
    number varchar(100) not null,
    --房子的贝壳编码
    href varchar(100),
    --详情页面链接
    describe text,
    --标题 - 描述
    total_price_value float,
    --总价
    total_price_unit varchar(100),
    --总价单位
    unit_price_value float,
    -- 均价
    unit_price_unit varchar(10),
    --均价单位
    img_layout text,
    --户型图
    img_other text,
    --房源照片
    community_href varchar(100),
    --小区链接
    community_number varchar(100),
    --小区编号
    community_zone varchar(200),
    -- 小区所在区
    community_business_zone varchar(200),
    --小区所在商圈
    build_year int,
    --建造年代
    room_num int,
    --室
    living_num int,
    --厅
    bathroom_num int,
    --卫
    floor_position varchar(20),
    --楼层位置
    floor_sum int,
    --总楼层
    area_sum float,
    --总面积
    family_structure varchar(30),
    --户型结构
    building_types varchar(30),
    --建筑类型
    toward varchar(30),
    --房屋朝向
    building_structure varchar(30),
    --建筑结构
    repair varchar(30),
    --装修情况
    ladder_household_proportion varchar(30),
    --梯户比例
    equipped_elevator varchar(30),
    --配备电梯
    villa_type varchar(30),
    --别墅类型
    property_right_years int,
    --产权年限
    listing_time varchar(30),
    --挂牌时间
    trading_authority varchar(30),
    --交易权属
    last_transaction varchar(30),
    --上次交易
    housing_use varchar(30),
    --房屋用途
    housing_life varchar(30),
    --房屋年限
    property_ownership varchar(30),
    --产权所属
    mortgage_information varchar(30),
    --抵押信息
    housing_spare_parts varchar(30),
    --房本备件
    create_time integer
    --抓取时间s
);

create unique index bei_ke_house_used_id_uindex
  on bei_ke_house_used (id);

create unique index bei_ke_house_used_number_uindex
  on bei_ke_house_used (number);
;

