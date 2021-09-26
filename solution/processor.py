# 处理数据以及html文件
#  lng lat city_cn zone flow ucc
# 1. 用户分布 客诉
#       lng lat city_cn
# 2. 三合一
# city_cn zone sum(flow) sum(ucc) count(1)
import os
import pandas as pd
import matplotlib.path as mpltPath
import numpy as np
def get_path_list(coordinates, geometry_type):
    path_list = []

    if geometry_type == 'MultiPolygon':
        for i in coordinates:
            for j in i:
                path_list.append(mpltPath.Path(j))

    else:
        for i in coordinates:
            path_list.append(mpltPath.Path(i))

    return path_list


point_df = pd.read_json('../data/result_json_20210830.json')
point_df.drop(columns=["cellId", "lac", "mnc", "mcc", "imei", "iso2"], inplace=True)
file_dir = "../path"
# 获取所有区path
all_file_list = os.listdir(file_dir)
all_data_frame=None
for single_file in all_file_list:
    if (single_file == '440000_full.json'):
        continue
    # 逐个读取
    single_data_frame = pd.read_json(
        os.path.join(file_dir, single_file))
    if single_file == all_file_list[0]:
        all_data_frame = single_data_frame
    else:  # 进行concat操作
        all_data_frame = pd.concat([all_data_frame,
                                    single_data_frame], ignore_index=True)
all_data_frame['matplotpath'] = all_data_frame.geometry.apply(
    lambda x: get_path_list(x.get('coordinates'), x.get('type')))
all_data_frame['zone_name'] = all_data_frame.properties.apply(
    lambda x: x.get('name'))
all_data_frame['zone_adcode'] = all_data_frame.properties.apply(
    lambda x: x.get('adcode'))


# 组装point 经纬度
point_df['point'] = [[x, y] for x, y in zip(point_df.lng, point_df.lat)]

point_df['zone_name'] = np.nan
point_df['zone_adcode'] = np.nan
# 处理未获取经纬度
point_df['zone_name']= point_df['zone_name'].fillna(point_df['lng'].isna().map({True: '经纬度缺失', False: np.nan}))
# point_df['zone_adcode']= point_df['zone_adcode'].fillna(point_df['lng'].isna().map({True: '经纬度缺失', False: np.nan}))
# point_df['zone_adcode']= point_df['zone_adcode'].fillna(point_df['province'].eq('CN-44').map({False: '外省', True: np.nan}))
point_df['zone_adcode']= point_df['zone_name']

for paths, zone_name,zone_adcode in zip(all_data_frame['matplotpath'], all_data_frame['zone_name'],all_data_frame['zone_adcode']):
    # print(zone_name)
    for path in paths:
        df1 = point_df[point_df['zone_name'].isna()]
        if(df1.empty):
            break
        points_list = df1.point.tolist()
        inside = path.contains_points(points_list)
        point_df.loc[df1[inside].index.to_list(), 'zone_name'] = zone_name
        point_df.loc[df1[inside].index.to_list(), 'zone_adcode'] = str(zone_adcode)
        # 反过来修改错误province city数据 经纬度数据定位出来的adcode 转成CN形式然后对比
        point_df.loc[df1[inside].index.to_list(), 'province'] = 'CN-'+str(zone_adcode)[0:2]
        point_df.loc[df1[inside].index.to_list(), 'city'] = 'CN-'+str(zone_adcode)[0:2]+'-'+str(zone_adcode)[2:4]

# 处理省外
point_df['zone_name']= point_df['zone_name'].fillna(point_df['province'].eq('CN-44').map({False: '外省', True: np.nan}))

# 处理未查询到
point_df['zone_name']=point_df['zone_name'].fillna('未知')
point_df['zone_adcode']=point_df['zone_adcode'].fillna('未知')

point_df.loc[point_df['city']=='null', 'city'] = '未知'
point_df.loc[point_df['province']=='null', 'province'] = '未知'

# 展示数据详情
print((point_df['zone_name']=='未知').sum())
point_df.to_csv('result.csv',index=False)
point_df.to_json('result.json',orient="records")
agg_df1=point_df.groupby(["city","zone_name"]).agg({"flowsize": np.sum,"ucc_count": np.sum, "zone_adcode": np.size}).reset_index()
agg_df2=point_df.groupby(["city"]).agg({"flowsize": np.sum,"ucc_count": np.sum, "zone_adcode": np.size}).reset_index()
agg_df=pd.concat([agg_df1,agg_df2])
agg_df.to_csv('result_agg.csv')
agg_df.to_json('result_agg.json',orient="records")