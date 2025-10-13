import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.graph_objects as go
from pandas.tseries.offsets import BDay
import math

# --- Database connection ---
DB_CONN_STRING = (
    "mssql+pyodbc://@RESEARCH/HistoricalData?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)
engine = create_engine(DB_CONN_STRING)

# --- Data loaders ---
def load_minute_data(prod, start, end):
    sql = text("""
      SELECT [time],[open],[high],[low],[close],[volume]
      FROM dbo.RawIntradayData
      WHERE contract_id = :prod
        AND interval = '1min'
        AND [time] BETWEEN :start AND :end
      ORDER BY [time];
    """)
    return pd.read_sql(sql, engine, params={
        'prod': prod,
        'start': f"{start} 00:00:00",
        'end':   f"{end}   23:59:59"
    }, parse_dates=['time'])

def load_daily_data(prod, start, end):
    sql = text("""
      SELECT [time],[open],[high],[low],[close],[volume]
      FROM dbo.DailyData
      WHERE contract_id = :prod
        AND [time] BETWEEN :start AND :end
      ORDER BY [time];
    """)
    df = pd.read_sql(sql, engine, params={
        'prod': prod,
        'start': f"{start} 00:00:00",
        'end':   f"{end}   23:59:59"
    }, parse_dates=['time'])
    df['date'] = df['time'].dt.date
    return df[['date','open','close','volume']]

# --- Stats & trimming ---
def compute_hourly_stats(df):
    df = df.copy()
    df['pct_chg'] = (df.close - df.open)/df.open
    df['rng']     = df.high - df.low
    grp = df.groupby(df.time.dt.hour)
    return grp['pct_chg'].mean(), grp['pct_chg'].var(), grp['rng'].mean(), grp['rng'].var()

def compute_minute_stats(df, hour):
    df = df[df.time.dt.hour == hour].copy()
    df['pct_chg'] = (df.close - df.open)/df.open
    df['rng']     = df.high - df.low
    grp = df.groupby(df.time.dt.minute)
    return grp['pct_chg'].mean(), grp['pct_chg'].var(), grp['rng'].mean(), grp['rng'].var()

def trim_extremes(df):
    low_pc, high_pc = df['pct_chg'].quantile([0.05,0.95])
    low_r,  high_r  = df['rng'].quantile([0.05,0.95])
    trimmed = df[df.pct_chg.between(low_pc,high_pc) & df.rng.between(low_r,high_r)]
    return trimmed if not trimmed.empty else df

def apply_filters(min_df, daily_df, filters, vol_thr, pct_thr):
    df = min_df.copy()
    df['date'] = df.time.dt.date
    df['prev_date'] = (pd.to_datetime(df.date) - BDay(1)).dt.date

    daily_df['10d_avg_vol'] = daily_df.volume.rolling(10, min_periods=1).mean()
    prev = daily_df.rename(columns={'open':'p_open','close':'p_close','volume':'p_vol','10d_avg_vol':'p_10d_avg_vol'})
    df = df.merge(prev[['date','p_open','p_close','p_vol','p_10d_avg_vol']], left_on='prev_date', right_on='date', how='left')

    df.dropna(subset=['p_open'], inplace=True)

    # weekday
    weekdays = ['monday','tuesday','wednesday','thursday','friday']
    sel = [f for f in filters if f in weekdays]
    if sel and set(sel)!=set(weekdays):
        df = df[df.time.dt.day_name().str.lower().isin(sel)]

    # prev-day
    if 'prev_pos' in filters: df = df[df.p_close>df.p_open]
    if 'prev_neg' in filters: df = df[df.p_close<df.p_open]

    # prev-day % thresholds
    df['p_pct'] = (df.p_close-df.p_open)/df.p_open*100
    if 'prev_pct_pos' in filters and pct_thr is not None: df = df[df.p_pct>=pct_thr]
    if 'prev_pct_neg' in filters and pct_thr is not None: df = df[df.p_pct<=-pct_thr]

    # relative volume
    df['relvol'] = df.p_vol/df.p_10d_avg_vol
    if 'relvol_gt' in filters and vol_thr is not None: df = df[df.relvol>vol_thr]
    if 'relvol_lt' in filters and vol_thr is not None: df = df[df.relvol<vol_thr]

    # exclude extremes
    if 'trim_extremes' in filters:
        df['pct_chg'] = (df.close-df.open)/df.open
        df['rng']     = df.high-df.low
        df = trim_extremes(df)
    return df

def scale_variance(v):
    if v is None or v<=0 or math.isnan(v): return 0.0,0
    exp = -math.floor(math.log10(v))+1
    return v*(10**exp), exp

def make_fig(x,y,title,yaxis):
    fig = go.Figure(go.Scatter(x=x,y=y,mode='lines+markers'))
    fig.update_layout(title=title,xaxis_title='Time',yaxis_title=yaxis,
                      margin=dict(l=40,r=20,t=50,b=40))
    return fig

# --- Dash app setup ---
app = dash.Dash(__name__)
app.title = "Futures Intraday Almanac"

filter_options = [
    {'label':'Prev-Day Close > Open','value':'prev_pos'},
    {'label':'Prev-Day Close < Open','value':'prev_neg'},
    {'label':'Prev-Day %∆ ≥ P','value':'prev_pct_pos'},
    {'label':'Prev-Day %∆ ≤ -P','value':'prev_pct_neg'},
    {'label':'Prev-Day Rel Vol > X','value':'relvol_gt'},
    {'label':'Prev-Day Rel Vol < X','value':'relvol_lt'},
    {'label':'Time A > Time B','value':'timeA_gt_timeB'},
    {'label':'Time A < Time B','value':'timeA_lt_timeB'},
    {'label':'Exclude Top/Bottom 5%','value':'trim_extremes'},
    {'label':'Monday','value':'monday'},
    {'label':'Tuesday','value':'tuesday'},
    {'label':'Wednesday','value':'wednesday'},
    {'label':'Thursday','value':'thursday'},
    {'label':'Friday','value':'friday'},
]

app.layout = html.Div([
    html.Div(style={'position':'fixed','width':'20%','height':'100vh',
                    'overflow':'auto','padding':'20px','borderRight':'1px solid #ccc'}, children=[
        html.H2("Controls"),
        html.Label("Product"),
        dcc.Dropdown(id='product-dropdown',
                     options=[{'label':p,'value':p} for p in ['ES','NQ','GC']],
                     value='GC', clearable=False, style={'marginBottom':'20px'}),
        html.Label("Start Date"),
        dcc.DatePickerSingle(id='start-date', date='2025-01-01',
                             min_date_allowed='2009-01-01', display_format='YYYY-MM-DD'),
        html.Br(), html.Br(),
        html.Label("End Date"),
        dcc.DatePickerSingle(id='end-date', date='2025-02-01',
                             min_date_allowed='2009-01-01', display_format='YYYY-MM-DD',
                             style={'marginBottom':'20px'}),
        html.Br(), html.Label("Minute Hour"),
        dcc.Dropdown(id='minute-hour', options=[{'label':h,'value':h} for h in range(0,24) if h not in (5,6)],
                     value=9, clearable=False, style={'marginBottom':'20px'}),
        html.Label("Filter Options"),
        dcc.Checklist(id='filters', options=filter_options,
                      value=['monday','tuesday','wednesday','thursday','friday'],
                      style={'marginBottom':'20px'}),
        html.Label("Relative Volume Multiplier (X)"),
        dcc.Input(id='vol-threshold', type='number', placeholder='X', style={'width':'100%'}, debounce=True),
        html.Br(), html.Br(),
        html.Label("Percentage Change Threshold (P %)"),
        dcc.Input(id='pct-threshold', type='number', placeholder='P', style={'width':'100%'}, debounce=True),
        html.Br(), html.Hr(),
        html.Label("Time A"),
        html.Div([
          dcc.Dropdown(id='timeA-hour', options=[{'label':h,'value':h} for h in range(0,24) if h not in (5,6)],
                       placeholder='Hour'),
          dcc.Dropdown(id='timeA-minute', options=[{'label':m,'value':m} for m in range(0,60)],
                       placeholder='Min')
        ], style={'display':'flex','gap':'10px','marginBottom':'10px'}),
        html.Label("Time B"),
        html.Div([
          dcc.Dropdown(id='timeB-hour', options=[{'label':h,'value':h} for h in range(0,24) if h not in (5,6)],
                       placeholder='Hour'),
          dcc.Dropdown(id='timeB-minute', options=[{'label':m,'value':m} for m in range(0,60)],
                       placeholder='Min')
        ], style={'display':'flex','gap':'10px','marginBottom':'20px'}),
        html.Button('Calculate', id='calc-btn', n_clicks=0,
                    style={'width':'100%','padding':'10px','fontWeight':'bold'}),
        html.Div(id='summary-box', style={
            'marginTop':'20px','padding':'10px','border':'1px solid #ccc',
            'borderRadius':'4px','backgroundColor':'#f9f9f9',
            'fontSize':'14px','lineHeight':'1.4'
        })
    ]),
    html.Div(style={'marginLeft':'22%','padding':'20px'}, children=[
        dcc.Loading(id='loading-graphs', type='default', children=[
            html.H3("Hourly Stats"),
            dcc.Graph(id='h-avg'), dcc.Graph(id='h-var'),
            dcc.Graph(id='h-range'), dcc.Graph(id='h-var-range'),
            html.H3("Minute Stats"),
            dcc.Graph(id='m-avg'), dcc.Graph(id='m-var'),
            dcc.Graph(id='m-range'), dcc.Graph(id='m-var-range'),
        ])
    ])
])

@app.callback(
    [
      Output('h-avg','figure'),
      Output('h-var','figure'),
      Output('h-range','figure'),
      Output('h-var-range','figure'),
      Output('m-avg','figure'),
      Output('m-var','figure'),
      Output('m-range','figure'),
      Output('m-var-range','figure'),
      Output('summary-box','children'),
    ],
    Input('calc-btn','n_clicks'),
    [
      State('product-dropdown','value'),
      State('start-date','date'),
      State('end-date','date'),
      State('minute-hour','value'),
      State('filters','value'),
      State('vol-threshold','value'),
      State('pct-threshold','value'),
      State('timeA-hour','value'),
      State('timeA-minute','value'),
      State('timeB-hour','value'),
      State('timeB-minute','value'),
    ]
)
def update_graphs(n, prod, start, end, mh, filters, vol_thr, pct_thr,
                  tA_h, tA_m, tB_h, tB_m):
    # 1) Load data
    daily = load_daily_data(prod, start, end).copy()
    minute = load_minute_data(prod, start, end).copy()

    # 2) Prev-day and relvol
    daily['10d_avg_vol'] = daily.volume.rolling(10, min_periods=1).mean()
    daily['relvol']      = daily.volume / daily['10d_avg_vol']

    # 3) Build daily2
    daily2 = daily.copy()
    daily2['prev_date'] = (pd.to_datetime(daily2.date) - BDay(1)).dt.date
    idx = daily2.set_index('date')
    for col in ['open','close','volume','10d_avg_vol']:
        daily2[f'p_{col}'] = daily2.prev_date.map(idx[col])
    daily2['p_pct'] = (daily2.p_close - daily2.p_open)/daily2.p_open*100
    daily2['weekday'] = daily2.date.map(lambda d: pd.Timestamp(d).day_name().lower())

    # 4) Price A/B on each date
    dfm = minute.copy()
    dfm['date'] = dfm.time.dt.date
    seriesA = dfm[(dfm.time.dt.hour==tA_h)&(dfm.time.dt.minute==tA_m)]\
              .set_index('date')['close']
    seriesB = dfm[(dfm.time.dt.hour==tB_h)&(dfm.time.dt.minute==tB_m)]\
              .set_index('date')['close']
    daily2['priceA'] = daily2.date.map(seriesA)
    daily2['priceB'] = daily2.date.map(seriesB)

    # 5) Build masks & counts
    weekdays = ['monday','tuesday','wednesday','thursday','friday']
    sel_days = [f for f in filters if f in weekdays]
    masks, counts = [], {}

    # weekday
    if set(sel_days)!=set(weekdays):
        m = ~daily2.weekday.isin(sel_days)
        masks.append(m); counts['week']=int(m.sum())
    else: counts['week']=0
    # prev_pos, prev_neg
    for key,cond in [
      ('prev_pos', daily2.p_close<=daily2.p_open),
      ('prev_neg', daily2.p_close>=daily2.p_open)
    ]:
        if key in filters:
            masks.append(cond); counts[key]=int(cond.sum())
        else: counts[key]=0
    # prev_pct_pos/_neg
    if 'prev_pct_pos' in filters and pct_thr is not None:
        m = daily2.p_pct< pct_thr; masks.append(m); counts['pct_pos']=int(m.sum())
    else: counts['pct_pos']=0
    if 'prev_pct_neg' in filters and pct_thr is not None:
        m = daily2.p_pct> -pct_thr; masks.append(m); counts['pct_neg']=int(m.sum())
    else: counts['pct_neg']=0
    # relvol_gt/lt
    if 'relvol_gt' in filters and vol_thr is not None:
        m = daily2.relvol<=vol_thr; masks.append(m); counts['rgt']=int(m.sum())
    else: counts['rgt']=0
    if 'relvol_lt' in filters and vol_thr is not None:
        m = daily2.relvol>=vol_thr; masks.append(m); counts['rlt']=int(m.sum())
    else: counts['rlt']=0
    # timeA_gt_timeB / timeA_lt_timeB
    if 'timeA_gt_timeB' in filters:
        m = daily2.priceA<=daily2.priceB; masks.append(m); counts['A> B']=int(m.sum())
    else: counts['A> B']=0
    if 'timeA_lt_timeB' in filters:
        m = daily2.priceA>=daily2.priceB; masks.append(m); counts['A< B']=int(m.sum())
    else: counts['A< B']=0

    # 6) combine masks
    combined = masks[0].copy() if masks else pd.Series(False,index=daily2.index)
    for m in masks[1:]: combined |= m
    days_filtered = int(combined.sum())
    total_days = len(daily2)
    days_rem   = total_days - days_filtered
    pct_rem    = days_rem/total_days*100 if total_days else 0

     # Compute how many days remain after all day-level filters
    remaining_days_df = daily2.loc[~combined]

    # Count filtered days
    filtered_green_days = int((remaining_days_df['close'] > remaining_days_df['open']).sum())
    filtered_red_days   = int((remaining_days_df['close'] < remaining_days_df['open']).sum())

    # Calculate percentages **against the original total_days**
    percentage_filtered_green = filtered_green_days * 100 / total_days
    percentage_filtered_red   = filtered_red_days   * 100 / total_days

    # Percentage of data remaining
    percentage_data_remaining = days_rem * 100 / total_days


    # 7) filter minute & compute charts
    fmin = apply_filters(minute, daily, filters, vol_thr, pct_thr)
    hc, hv, hr, hvr = compute_hourly_stats(fmin)
    mc, mv, mr, mvr = compute_minute_stats(fmin, mh)
    sh,_ = scale_variance(hv.mean()); sm,_ = scale_variance(mv.mean())

    # 8) period summary
    op,cl = daily.open.iloc[0], daily.close.iloc[-1]
    chg   = (cl-op)/op*100
    gd    = (daily.close>daily.open).sum()
    rd    = (daily.close<daily.open).sum()

    summary = [
        html.B("Date Range Summary"), html.Br(),
        f"Open: {op:.2f}", html.Br(),
        f"Close: {cl:.2f}", html.Br(),
        f"Change: {chg:.2f}%", html.Br(),
        f"Total Days: {total_days}", html.Br(),
        f"Green Days: {gd} ({gd/total_days*100:.2f}%)", html.Br(),
        f"Red Days: {rd} ({rd/total_days*100:.2f}%)", html.Br(), html.Br(),
        
        html.B("Mean Variances (scaled)"), html.Br(),
        f"Hourly %∆ Var: {sh:.1f}", html.Br(),
        f"Hourly Range Var: {hvr.mean():.6f}", html.Br(),
        f"Minute %∆ Var: {sm:.1f}", html.Br(),
        f"Minute Range Var: {mvr.mean():.6f}", html.Br(), html.Br(),
        html.B("Days Filtered Out"), html.Br(),
        f"By Weekday: {counts['week']}", html.Br(),
        f"By Prev+ : {counts['prev_pos']}", html.Br(),
        f"By Prev- : {counts['prev_neg']}", html.Br(),
        f"By %∆ ≥ P: {counts['pct_pos']}", html.Br(),
        f"By %∆ ≤ -P: {counts['pct_neg']}", html.Br(),
        f"By RelVol > X: {counts['rgt']}", html.Br(),
        f"By RelVol < X: {counts['rlt']}", html.Br(),
        f"By A>B: {counts['A> B']}", html.Br(),
        f"By A<B: {counts['A< B']}", html.Br(), html.Br(),
        html.B("Filtered Days Summary"), html.Br(),
        f"Filtered Green Days: {filtered_green_days} ({percentage_filtered_green:.2f}%)", html.Br(),
        f"Filtered Red Days: {filtered_red_days} ({percentage_filtered_red:.2f}%)", html.Br(),
        f"Data Remaining Studied: {days_rem} ({percentage_data_remaining:.2f}%)", html.Br(), html.Br(),

    ]

    return (
        make_fig(hc.index, hc,    "Hourly Avg % Change",    "Pct"),
        make_fig(hv.index, hv,    "Hourly Var % Change",    "Var"),
        make_fig(hr.index, hr,    "Hourly Avg Range",       "Price"),
        make_fig(hvr.index,hvr,   "Hourly Var Range",       "Var"),
        make_fig(mc.index, mc,    f"Min Avg %∆ @ {mh}:00",  "Pct"),
        make_fig(mv.index, mv,    f"Min Var %∆ @ {mh}:00",  "Var"),
        make_fig(mr.index, mr,    f"Min Avg Range @ {mh}:00","Price"),
        make_fig(mvr.index,mvr,   f"Min Var Range @ {mh}:00","Var"),
        summary
    )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8072, debug=False)
