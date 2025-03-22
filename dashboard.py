import pandas as pd
import plotly.express as px
import streamlit as st
from babel.numbers import format_decimal

def create_daily_user(df_bike_hour):
    daily_user = df_bike_hour.groupby(['dteday']).agg({
        'cnt': 'sum',
        'casual': 'sum',
        'registered': 'sum',
    })
    daily_user = daily_user.reset_index()
    
    return daily_user

def create_sum_user_by_season(df_bike_hour):
    total_user_season = df_bike_hour.groupby(['season']).agg({
        'casual': 'sum',
        'registered': 'sum',
    })
    total_user_season = total_user_season.reset_index()
    
    regist__temp = total_user_season[["season", "registered"]]
    casual__temp = total_user_season.drop(columns=["registered"])
    casual__temp.rename(columns={
        "casual": "total_user",
    }, inplace=True)
    casual__temp['type'] = "casual"

    regist__temp.rename(columns={
        "registered": "total_user",
    }, inplace=True)
    regist__temp['type'] = "registered"

    season__user = pd.concat([casual__temp, regist__temp])
    return season__user

def create_least_usage_days(df_bike_hour):
    bike_usage = df_bike_hour.groupby(['dteday', 'season', 'yr', 'mnth', 'weekday', 'workingday', 'weathersit', ]).agg({
        'casual': 'sum',
        'registered': 'sum',
        'cnt': 'sum',
    })
    bike_usage = bike_usage.reset_index()
    bike_usage = bike_usage.sort_values(by=['cnt', 'yr', 'season', 'mnth', 'weathersit'])
    least_usage = bike_usage.head(20)
    return least_usage

def create_least_season(least_usage_df):
    least_season = least_usage_df.groupby(['season']).agg({
        'dteday': 'count',
    })
    least_season = least_season.reset_index()
    return least_season

def create_least_month(least_usage_df):
    least_month = least_usage_df.groupby(['season', 'mnth']).agg({
        'dteday': 'count',
    })
    least_month = least_month.reset_index()
    least_month.rename(columns={
        "mnth": "month",
        "dteday": "least_day_count"
    }, inplace=True)
    return least_month

def create_least_weather(least_usage_df):
    least_weather = least_usage_df.groupby(['season', 'weathersit']).agg({
        'dteday': 'count',
    })
    least_weather = least_weather.reset_index()
    least_weather.rename(columns={
        "weathersit": "weather",
        "dteday": "least_day_count"
    }, inplace=True)
    return least_weather

def create_weekday_hourly_avg(df_bike_hour):
    weekday_avg = df_bike_hour.groupby(['weekday', 'hr']).agg({
        'cnt': 'mean',
    }).astype(int)
    weekday_avg = weekday_avg.reset_index()
    return weekday_avg

def create_workingday_hourly_avg(df_bike_hour):
    workingday_avg = df_bike_hour.groupby(['workingday', 'hr']).agg({
        'cnt': 'mean',
    }).astype(int)
    workingday_avg = workingday_avg.reset_index()
    return workingday_avg

def create_user_type_hourly(df_bike_hour):
    usertype_hourly_avg = df_bike_hour.groupby(['workingday', 'hr']).agg({
        'casual': 'mean',
        'registered': 'mean',
    }).astype(int)
    usertype_hourly_avg = usertype_hourly_avg.reset_index()

    regist__temp = usertype_hourly_avg[["workingday", "hr", "registered"]]
    casual__temp = usertype_hourly_avg.drop(columns=["registered"])
    casual__temp.rename(columns={
        "casual": "avg_user",
    }, inplace=True)
    casual__temp['type'] = "casual"

    regist__temp.rename(columns={
        "registered": "avg_user",
    }, inplace=True)
    regist__temp['type'] = "registered"

    usertype_hourly_avg = pd.concat([casual__temp, regist__temp])
    return usertype_hourly_avg

def create_weekly_data(df_bike_hour):
    daily_data_df = df_bike_hour.groupby(['dteday', 'weeknumber']).agg({
        'temp': 'mean',
        'atemp': 'mean',
        'hum': 'mean',
        'windspeed': 'mean',
        'cnt': 'sum',
    }).astype(int)
    daily_data_df = daily_data_df.reset_index()

    weekly_data_df = daily_data_df.groupby(['weeknumber']).agg({
        'temp': 'mean',
        'atemp': 'mean',
        'hum': 'mean',
        'windspeed': 'mean',
        'cnt': 'mean',
    }).astype(int)
    weekly_data_df = weekly_data_df.reset_index()
    return weekly_data_df

def create_grouping(weekly_data_df):
    temp_bins = [0, 12, 23, 32]
    labels = ['cold', 'warm', 'hot']
    weekly_data_df['temp_bin'] = pd.cut(weekly_data_df['temp'], temp_bins, labels=labels)

    wind_bins = [0, 13, 20]
    labels = ['not windy', 'windy']
    weekly_data_df['windspeed_bin'] = pd.cut(weekly_data_df['windspeed'], wind_bins, labels=labels)

    weekly_data_df['group'] = weekly_data_df['temp_bin'].astype(str) + ', ' + weekly_data_df['windspeed_bin'].astype(str)

    groupings_ = weekly_data_df.groupby(['group']).agg({
        'cnt': 'sum',
    }).astype(int)
    groupings_ = groupings_.reset_index()
    return groupings_

bike_df = pd.read_csv("bike_hour.csv")
bike_df.sort_values(by="dteday", inplace=True)
bike_df.reset_index(inplace=True)
 
bike_df["dteday"] = pd.to_datetime(bike_df["dteday"])

min_date = bike_df["dteday"].min()
max_date = bike_df["dteday"].max()

with st.sidebar:
    st.title('Bike-Sharing Systems')
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Usage Date',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = bike_df[(bike_df["dteday"] >= str(start_date)) & 
                (bike_df["dteday"] <= str(end_date))]

st.sidebar.write('Select Filter for User Type Behavior')

season_list = bike_df.season.unique()
val = [None]* len(season_list) # this list will store info about which category is selected
for i, season_ in enumerate(season_list):
    # create a checkbox for each category
    val[i] = st.sidebar.checkbox(season_, value=True) # value is the preselect value for first render

# filter data based on selection
bike_df_flt = bike_df[bike_df.season.isin(season_list[val])].reset_index(drop=True)

daily_user_df = create_daily_user(main_df)
sum_user_by_season_df = create_sum_user_by_season(main_df)
least_usage_days_df = create_least_usage_days(main_df)
least_season_df = create_least_season(least_usage_days_df)
least_month_df = create_least_month(least_usage_days_df)
least_weather = create_least_weather(least_usage_days_df)
weekday_hourly_avg_df = create_weekday_hourly_avg(main_df)
workingday_hourly_avg_df = create_workingday_hourly_avg(main_df)
user_type_hourly_df = create_user_type_hourly(bike_df_flt)
weekly_data_df = create_weekly_data(main_df)
grouping_df = create_grouping(weekly_data_df)



st.header('Bike Sharing Usage Dashboard :sparkles:')

st.subheader('Daily Usage')

col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
 
with col1:
    total_users = format_decimal(daily_user_df.cnt.sum(), locale='en_US')
    st.metric("Total Users", value=total_users)
 
with col2:
    total_casual = format_decimal(daily_user_df.casual.sum(), locale='en_US')
    st.metric("Casual Users", value=total_casual)

with col3:
    total_regis = format_decimal(daily_user_df.registered.sum(), locale='en_US')
    st.metric("Registered Users", value=total_regis)

fig_daily_user = px.line(daily_user_df, x="dteday", y="cnt",
                 color_discrete_sequence=["mediumturquoise"],
                 labels={
                        "dteday": "Date",
                        "cnt": "Number of Daily User",
                        },
                 width=800, height=400)
st.plotly_chart(fig_daily_user)


st.subheader('Usage Varies by Season')

fig_user_season = px.bar(sum_user_by_season_df, x="season", y="total_user", color="type",
                  barmode="group", color_discrete_sequence=["mediumaquamarine", "lightcyan"],
                  category_orders={"season": ["Winter", "Spring", "Summer", "Fall"]},
                  labels={
                    "season": "Season",
                    "total_user": "Total User",
                    "type": "User Type"
                    },
                  width=800, height=400)
fig_user_season.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig_user_season)


st.subheader('The Least Favorable Bike-Sharing Usage Time')

col1, col2 = st.columns([0.35,0.65], gap="large")

with col1:
    st.text('By Season')
    fig_lseason = px.pie(least_season_df, values='dteday', names='season',
                        color_discrete_sequence=["skyblue", "khaki", "plum", "tan"],
                        )
    fig_lseason.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig_lseason)

with col2:
    st.text('By Weather Situation')
    fig_lweather = px.bar(least_weather, y='season', x='least_day_count', color='weather',
                        color_discrete_sequence=px.colors.qualitative.Set3, orientation='h',
                        category_orders={"season": ["Winter", "Spring", "Summer", "Fall"]},
                        labels={
                            "season": "Season",
                            "least_day_count": "Number of Days",
                            "weather": "Weather Situation"
                            },
                        )
    fig_lweather.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    st.plotly_chart(fig_lweather)

st.text('By Month')
fig_lmonth = px.bar(least_month_df, y='season', x='least_day_count', color='month',
                    color_discrete_sequence=px.colors.qualitative.Antique, orientation='h',
                    category_orders={
                        "season": ["Winter", "Spring", "Summer", "Fall"],
                        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    },
                    labels={
                        "season": "Season",
                        "least_day_count": "Number of Days",
                        "month": "Month"
                        },
                    )
fig_lmonth.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig_lmonth)


st.subheader('Bike-Sharing Hourly Usage')

fig_hr = px.bar(weekday_hourly_avg_df, x="hr", y="cnt", facet_row="weekday",
             title="By Weekday", barmode="group",
             color_discrete_sequence=["mediumturquoise"],
             category_orders={"weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]},
             labels={
                    "hr": "Hour (h)",
                    "cnt": "Number of User",
                    },
             width=1100, height=800)
fig_hr.for_each_yaxis(lambda y: y.update({'title': ''}))   
fig_hr.add_annotation(
    showarrow=False,
    xanchor='center',
    xref='paper', 
    x=-0.07,
    font=dict(size=14), 
    yanchor='middle',
    yref='paper',
    y=0.5,
    textangle=270,
    text='Average Number of User per Hour'
)
fig_hr.update_xaxes(tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
st.plotly_chart(fig_hr)

st.subheader('User Type Behavior')

fig_hr_type = px.bar(user_type_hourly_df, x="hr", y="avg_user", color="workingday", facet_row="type",
             title="Casual vs Registered User Usage Difference", barmode="group",
             color_discrete_sequence=["lightcoral", "skyblue"],
             labels={
                    "hr": "Hour (h)",
                    "avg_user": "Number of User",
                    },
             width=1400, height=500)
fig_hr_type.for_each_yaxis(lambda y: y.update({'title': ''}))   
fig_hr_type.add_annotation(
    showarrow=False,
    xanchor='center',
    xref='paper', 
    x=-0.08,
    font=dict(size=14), 
    yanchor='middle',
    yref='paper',
    y=0.5,
    textangle=270,
    text='Average Number of User per hour'
)
fig_hr_type.update_xaxes(tickvals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])
fig_hr_type.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig_hr_type)


st.subheader('Week Grouping based on Temperature and Wind Speed')

fig_3d = px.scatter_3d(weekly_data_df, x='temp', y='windspeed', z='weeknumber', 
    size='cnt', 
    color='group',
    color_discrete_sequence=["darkslategrey", "aquamarine", "lightseagreen", "darkkhaki", "tomato"],
    labels={
        'weeknumber': 'Number of Week',
        'temp': 'Temperature (c)',
        'windspeed': 'Wind Speed (km/h)',
        'group': 'Weather Condition'
    },
    width=900, height=600
    )
fig_3d.add_annotation(
    showarrow=False,
    xanchor='center',
    align='left',
    xref='paper', 
    x=1.12,
    font=dict(size=13), 
    yanchor='middle',
    yref='paper',
    y=0.57,
    textangle=0,
    text='Temperature (°C) <br> * Cold: 0-12 <br> * Warm: 13-23 <br> * Hot: 24-35 <br><br> Wind Speed (km/h) <br> * Not Windy: 0-13 <br> * Windy: 14-22'
)
st.plotly_chart(fig_3d)

fig_grouping = px.bar(grouping_df, x='group', y='cnt', 
                       color='group',
                       color_discrete_sequence=["darkslategrey", "aquamarine", "lightseagreen", "darkkhaki", "tomato"],
                       labels={
                        'cnt': 'Total Number of Average Daily User',
                        'group': 'Weather Condition'
                       },
                       width=500, height=350
                       )
st.plotly_chart(fig_grouping)

st.caption('Copyright (c) Khairunnisa 2025')