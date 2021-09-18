import folium,random
act='pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'
from faker import Faker
fake = Faker()
# 上海地图
# m = folium.Map(location= [23.132191,113.266530],
m = folium.Map(location= [22.55,114.05],
               tiles='https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token='+act,
               zoom_start=14,
                prefer_canvas=True,
               attr=r'Map data &copy; OpenStreetMap contributors, <a target="_blank" href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery Â© <a target="_blank" href="https://www.mapbox.com/" > Mapbox < / a > ',
)
for _ in range(500):
    folium.Circle(radius=50, location=(fake.coordinate(center=22.55, radius=0.05) , fake.coordinate(center=114.05, radius=0.05)), popup="用户:{0}".format(fake.safe_email()),
                         color='green',fill=True, fill_color='green').add_to(m)
m.save('../output/index.html')



def plot_map(self, all_data):
    plot_map = folium.Map(location=[all_data['lat'].mean(), all_data['lon'].mean()],
                          zoom_start=10,
                          tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                          attr="http://ditu.amap.com/")

    color = ['#F0EDF9', '#E2DBF3', '#D3CAEE', '#B7A6E2', '#A895DD', '#9A83D7', '#8C71D1', '#7D60CC', '#6F4EC6',
             '#613DC1', '#5938B0', '#50329E', '#472D8D', '#3E277B', '#35226A', '#2D1C58', '#241747', '#1B1135',
             '#F0EDF9', '#E2DBF3', '#D3CAEE', '#C5B8E8', '#B7A6E2', '#A895DD', '#9A83D7', '#8C71D1', '#7D60CC',
             '#6F4EC6', '#613DC1', '#5938B0', '#50329E', '#472D8D', '#3E277B', '#35226A', '#2D1C58', '#241747',
             '#1B1135']  # 37种

    for name, row in all_data.iterrows():
        if int(row['classlabel']) == -1:
            folium.Circle(radius=20, location=[row["lat"], row["lon"]], popup="离群--停车点:{0}".format(name),
                          color='black', fill=True, fill_color='black').add_to(plot_map)
        else:
            i = int(row['classlabel'])
            folium.Circle(radius=20, location=[row["lat"], row["lon"]], popup="{0}类--停车点:{1}".format(i, name),
                          color=color[i], fill=True, fill_color=color[i]).add_to(plot_map)

    return plot_map
