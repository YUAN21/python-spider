import sqlite3


def test_db():
    conn_db = sqlite3.connect('SQLite.db')
    cursor = conn_db.cursor()  # 游标
    cursor.execute('INSERT INTO test VALUES("anything")')
    cursor.close()
    conn_db.commit()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def write_used_db(house_number, detail_href, describe,
                  total_price_value, total_price_unit, unit_price_value, unit_price_unit,
                  community_href, community_number, community_zone, community_business_zone,
                  build_year, house_type_room, house_type_living, house_type_bathroom,
                  floor_position, floor_sum, house_area, family_structure, building_types,
                  house_toward, building_structure, repair_situation, ladder_household_proportion,
                  equipped_elevator, villa_type, property_right_years, listing_time, trading_authority,
                  last_transaction, housing_use, housing_life, property_ownership, mortgage_information,
                  housing_spare_parts, img_house_layout, img_house_other):   # 37

    update_params = '''
        number = ?,href = ?, describe = ?, total_price_value = ?,
        total_price_unit = ?, unit_price_value = ?, unit_price_unit = ?, img_layout = ?, img_other = ?, community_href = ?, 
        community_number = ?, community_zone = ?, community_business_zone = ?, build_year = ?, 
        room_num = ?, living_num = ?, bathroom_num = ?, floor_position = ?, floor_sum = ?, area_sum = ?, 
        family_structure = ?, building_types = ?, toward = ?, building_structure = ?, repair = ?, 
        ladder_household_proportion = ?, equipped_elevator = ?, villa_type = ?, property_right_years = ?, 
        listing_time = ?, trading_authority = ?, last_transaction = ?, housing_use = ?, housing_life = ?, 
        property_ownership = ?, mortgage_information = ?, housing_spare_parts = ?
        '''
    insert_params = '''
        number,href, describe, total_price_value,
        total_price_unit, unit_price_value, unit_price_unit, img_layout, img_other, community_href, 
        community_number, community_zone, community_business_zone, build_year, 
        room_num, living_num, bathroom_num, floor_position, floor_sum, area_sum, 
        family_structure, building_types, toward, building_structure, repair, 
        ladder_household_proportion, equipped_elevator, villa_type, property_right_years, 
        listing_time, trading_authority, last_transaction, housing_use, housing_life, 
        property_ownership, mortgage_information, housing_spare_parts
        '''
    values = '?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?'
    data = (
        house_number, detail_href, describe,
        total_price_value, total_price_unit, unit_price_value, unit_price_unit, img_house_layout, img_house_other,
        community_href, community_number, community_zone, community_business_zone,
        build_year, house_type_room, house_type_living, house_type_bathroom,
        floor_position, floor_sum, house_area, family_structure, building_types,
        house_toward, building_structure, repair_situation, ladder_household_proportion,
        equipped_elevator, villa_type, property_right_years, listing_time, trading_authority,
        last_transaction, housing_use, housing_life, property_ownership, mortgage_information,
        housing_spare_parts
    )

    try:
        conn_db = sqlite3.connect('SQLite.db')
        conn_db.row_factory = dict_factory
        cursor = conn_db.cursor()  # 游标

        cursor.execute(
            'SELECT count(*) AS num FROM bei_ke_house_used WHERE number = ' + "'" + house_number + "'")
        if cursor.fetchone()["num"] == 0:
            cursor.execute('INSERT INTO bei_ke_house_used(' +
                           insert_params + ') VALUES(' + values + ')', data)
        else:
            cursor.execute('UPDATE bei_ke_house_used SET ' +
                           update_params + ' WHERE number = ' + "'" + house_number + "'", data)

        cursor.close()
        conn_db.commit()
    except Exception:
        print(Exception)
