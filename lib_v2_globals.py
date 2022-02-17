dbc                 = False
cursor              = False
logit               = False
cvars               = False
cfgfile             = "config.toml"
statefile           = "state.json"
autoclear           = True
recover             = False
session_name        = False
state               = False
gcounter            = 0
startdate           = False
tot_buys            = 0
tot_sells           = 0
curr_run_ct         = 0
subtot_qty          = 0
avg_price           = 0
adj_avg_price           = 0
purch_qty           = 0
initial_purch_qty           = 0
pnl_running         = 0
pct_running         = 0
batchmode           = 0
BASE                = False
QUOTE               = False
keys                = False
datatype            = False
buy_fee             = False
sell_fee            = False
ffmaps_lothresh     = False
ffmaps_hithresh     = False
sigffdeltahi_lim    = False
stdscr = False
capital             = False
purch_pct           = False
override = False
last_side = False
opening_price = False
purch_qty_adj_pct   = False
lowerclose_pct      = False

interval            = False
verbose             = False
facecolor           = "black"

time_to_die         = False
cwd                 = False
num_axes            = False
ticker_src          = False
spot_src            = False
cap_seed            = False

df_conv             = False
xohlc               = False
ohlc                = False
bigdata             = False
ohlc_conv           = False
this_close          = False
last_close          = False
long_buys           = 0
short_buys          = 0
since_short_buy     = 0
dshiamp             = 0
wss_filters         = False
idx                 = False
buys_permitted      = True
cooldown            = 0
stoplimit_price     = False
df_buysell          = False
adjusted_covercost  = False
coverprice          = False
next_buy_price      = False
last_purch_qty      = False
market              = False
curr_buys           = 0
is_first_buy        = True
running_buy_fee     = False
est_buy_fee         = False
est_sell_fee        = False
subtot_cost         = False
buymode             = False
needs_reload        = False
subtot_value        = False
uid                 = False
running_total       = 0
pct_return          = 0
pct_cap_return      = 0
pct_capseed_return  = 0
bsuid               = False
conversion          = False
last_conversion     = False
current_close       = 0
reserve_seed       = False
total_reserve       = 0
reserve_cap         = 0
dstot_ary           = False
dstot_lo_ary        = False
dstot_hi_ary        = False
dstot_avg_ary       = False
dstot_Dadj          = 1
multicursor         = False
last_date           = False
pfile               = False
showdates = False
showeach = False
mmphi = False
live_balance = False
tm = False
next_buy_increments = False
cfile_states_str = False
cdata = False
sell_count = False
buy_count = False
# rootperf            = False
# rootperf2            = False
# rootperf3            = False
# rootperf4            = False
rootperf            = [False,False,False,False,False]

bsig                = [False,False,False,False,False]
# bsig                = False
# bsig4                = False

df_perf             = False
conv_mask           = False
deltatime           = False
mav_ary             = [False,False,False,False]

now_time            = False
last_time           = False
sub_now_time        = False
sub_last_time       = False
display             = True
headless            = False
units               = "ms"
filemd5             = False

dprep               = False
thread_ready        = False
ax_patches          = False

message_out         = False
mmap_long_file      = False
mmap_short_file     = False
issue               = False

margin_interest_cost        = 0
total_margin_interest_cost  = 0
session_first_buy_time      = False
external_buy_signal         = False
external_sell_signal        = False
epoch_boundry_ready         = False
epoch_boundry_countdown     = False
df_priceconversion_data     = False
tmp1 = False
dtime = False
tmpdir = "/tmp"
# * for wss
ppjson      = False
filteramt   = False
filertime   = False
wss_large   = []
wss_small   = []
patsig      = []
pair        = False
mult = False

rtime = {
    0: []*1000,
    1: []*1000,
    2: []*1000,
    3: []*1000,
    4: []*1000,
}

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
    "siglft": []*288,
    "sigfft": []*288,

    "sigfft0": []*288,
    "sigfft1": []*288,
    "sigfft2": []*288,
    "sigfft3": []*288,
    "sigfft4": []*288,
    "sigfft5": []*288,

    "sigfft20": []*288,
    "sigfft21": []*288,
    "sigfft22": []*288,
    "sigfft23": []*288,
    "sigfft24": []*288,
    "sigfft25": []*288
}

# * db field order
c_id                = 0
c_uid               = 1
c_pair              = 2
c_fees              = 3
c_price             = 4
c_stop_price        = 5
c_upper_stop_price  = 6
c_size              = 7
c_funds             = 8
c_record_time       = 9
c_order_time        = 10
c_side              = 11
c_type              = 12
c_state             = 13
c_session           = 14
c_pct               = 15
c_cap_pct           = 16
c_credits           = 17
c_netcredits        = 18
c_runtot            = 19
c_runtotnet         = 20
c_bsuid             = 21
c_fintot            = 22
c_mxint             = 23
c_mxinttot          = 24
c_sl                = 25
