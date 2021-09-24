import pymongo
import matplotlib.path as mpltPath
import pandas as pd
import numpy as np
import app

client = pymongo.MongoClient(host='10.1.77.164', port=27017, )
client.oss_perflog_saas3.authenticate("osstest", "123456", mechanism='SCRAM-SHA-1')
db = client.oss_perflog_saas3
strength_table = db.t_ssim_str
province_table = db.t_province_boundary


def inside_points(row, points_df):
    flag = None
    for path in row.matplotpath:
        for point in points_df.point.tolist():
            # inside = set(path.contains_points(points_list))
            # if inside.__contains__(True):
            if path.contains_point(point):
                flag = 99.99
                return flag
    return flag


if False:
    find_field = {'mcc': 1, 'rat': 1, 'plmn': 1, 'lat': 1, 'lng': 1, 'strength': 1}
    group_dict = {'_id': {'mcc': '$mcc', 'mnc': '$mnc', 'lat': '$lat', 'lng': "$lng", 'rat': '$rat'},
                  'strength': {'$max': "$strength"}}

    strength_list = strength_table.aggregate(
        [{'$group': group_dict},
         {'$project': {'strength': 1, 'plmn': {'$concat': ["$_id.mcc", "$_id.mnc"]}}}],
        allowDiskUse=True)

    strength_pd = pd.DataFrame(strength_list)
    str_df = pd.concat([pd.DataFrame(strength_pd._id.values.tolist()), strength_pd], axis=1)
    str_df.drop(columns='_id', inplace=True)
    str_df.to_csv('group.csv', index=False, sep='\t')
# 获取各province 边界数据

# 3. 获取各省份边界数据 将省份shapeID 添加到各个点上

type_dict = {'mcc': str, 'mnc': str, 'lat': np.float64, 'lng': np.float64, 'rat': int,
             'strength': np.float64, 'plmn': str}

mcc_str_df = pd.read_csv('group.csv', sep='\t', dtype=type_dict)

mcc_str_df.dropna(subset=['lat'], inplace=True)
mcc_str_df['point'] = [[x, y] for x, y in zip(mcc_str_df.lng, mcc_str_df.lat)]

province_df = pd.DataFrame(province_table.find())

province_df['matplotpath'] = province_df.geometry.apply(
    lambda x: app.get_path_list(x.get('coordinates'), x.get('type')))

# # noinspection PyTypeChecker
# province_df['avg_strength'] = province_df.apply(
#     lambda x: inside_points(x, mcc_str_df.point.tolist()), axis=1)
mcc_str_df['shapeID']=np.nan
for paths,properties in  zip(province_df['matplotpath'], province_df['properties']):
    shapeID=properties.get('shapeID')
    print(shapeID)
    for path in paths:
        df1=mcc_str_df[mcc_str_df['shapeID'].isna()]
        points_list=df1.point.tolist()
        inside=path.contains_points(points_list)
        mcc_str_df.loc[df1[inside].index.to_list(),'shapeID']=shapeID

        # mcc_str_df[mcc_str_df['shapeID'].isna()][inside].loc[:,'shpaeID']=shapeID

mcc_str_df.to_csv('result.csv',index=False)
pass
