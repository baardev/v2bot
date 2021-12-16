dbc             = False
cursor          = False
logit           = False
cvars           = False
cfgfile         = "config.toml"
statefile       = "state.json"
df_priceconversion_data = False
autoclear       = True
recover         = False
session_name    = False
state           = False
gcounter        = 0
startdate       = False
tot_buys        = 0
tot_sells       = 0
curr_run_ct = 0
subtot_qty      = 0
avg_price       = 0
purch_qty       = 0
pnl_running     = 0
pct_running     = 0
batchmode       = 0

buy_fee          = False
sell_fee         = False
ffmaps_lothresh  = False
ffmaps_hithresh  = False
sigffdeltahi_lim = False

capital         = False
purch_pct       = False

purch_qty_adj_pct   = False
lowerclose_pct      = False

epoch_boundry_ready     = False
epoch_boundry_countdown = False

interval        = False
verbose         = False
facecolor       = "black"

time_to_die     = False
cwd             = False
num_axes        = False
ticker_src      = False
spot_src        = False

df_conv         = False
xohlc           = False
ohlc            = False
bigdata         = False
ohlc_conv       = False
this_close      = False
last_close      = False
long_buys       = 0
short_buys      = 0
since_short_buy = 0
dshiamp         = 0

external_buy_signal  = False
external_sell_signal = False
idx             = False
buys_permitted  = True
cooldown        = 0
stoplimit_price = False
df_buysell      = False
covercost       = False
coverprice      = False
next_buy_price  = False
last_purch_qty  = False
market          = False
curr_buys       = 0
is_first_buy    = True
running_buy_fee = False
est_buy_fee     = False
est_sell_fee    = False
subtot_cost     = False
buymode         = False
needs_reload    = False
subtot_value    = False
uid             = False
running_total   = 0
pct_return      = 0
pct_cap_return  = 0
bsuid           = False
conversion      = False
last_conversion = False
current_close   = 0
total_reserve   = 0
reserve_cap = 0
dstot_ary       = False
dstot_lo_ary    = False
dstot_hi_ary    = False
dstot_Dadj      = 1

margin_interest_cost        = 0
total_margin_interest_cost  = 0
session_first_buy_time      = False

conv_mask       = False
deltatime       = False
mav_ary         = [False,False,False,False]

# ! these are the only fields allowed for the coinbase order(s), as determined by 'cb_order.py'
cflds = {
    'type': "--type",
    'side': "--side",
    'pair': "--pair",
    'size': "--size",
    'price': "--price",
    'stop_price': "--stop_price",
    'upper_stop_price': "--upper_stop_price",
    'funds': "--funds",
    'uid': "--uid"
}

# * general global place to store things
bag = {
    "siglft": [],
    "sigfft": [],

    "sigfft0": [],
    "sigfft1": [],
    "sigfft2": [],
    "sigfft3": [],
    "sigfft4": [],
    "sigfft5": [],

    "sigfft20": [],
    "sigfft21": [],
    "sigfft22": [],
    "sigfft23": [],
    "sigfft24": [],
    "sigfft25": []
}

