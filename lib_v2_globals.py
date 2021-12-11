dbc = False
cursor = False
logit = False
cvars = False
cfgfile = "config.toml"
df_priceconversion_data = False
autoclear = True
recover = False
session_name = False
state = False
gcounter = 0
startdate = False
tot_buys = 0
tot_sells = 0
current_run_count = 0
subtot_qty = 0
avg_price = 0
purch_qty = 0
pnl_running = 0
pct_running = 0

buy_fee = False
sell_fee = False
ffmaps_lothresh = False
ffmaps_hithresh = False
sigffdeltahi_lim = False

capital = False
purch_pct = False

purch_qty_adj_pct = False
lowerclose_pct = False

epoch_boundry_ready = False
epoch_boundry_countdown = False

interval = False
verbose = False

time_to_die = False
cwd = False
num_axes = False
ticker_src = False
spot_src = False

df_conv = False
ohlc = False
ohlc_conv = False
this_close = False
last_close = False
long_buys = 0
dshiamp = 0

idx = False
external_buy_signal = False
external_sell_signal = False
buys_permitted = True
cooldown = 0
stoplimit_price = False
df_buysell = False
covercost = False
coverprice = False
next_buy_price = False
market = False
curr_buys = 0
is_first_buy = True
running_buy_fee = False
est_buy_fee = False
est_sell_fee = False
subtot_cost = False
buymode = False
needs_reload = False
subtot_value = False
uid = False
running_total = 0
pct_return = 0
pct_cap_return = 0
bsuid = False
conversion = False
statefile = "state.json"
current_close = 0


dstot_ary = False
dstot_lo_ary = False
dstot_hi_ary = False
dstot_buy = False
dstot_sell = False
dstot_Dadj = 1


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

# datasetname = "noname"
# datawindow = False
# buyfiltername = ""
# sellfiltername = ""
# instance_num = 0
# can_load = True
# ohlc = False
# cfgfile = f"config_{instance_num}.hcl"
# statefile = f"state_{instance_num}.json"
# interval = 0
# state = False
# time_to_die = False
# cursor = False
# session_name = "noname"
# df_buysell = False
# # df_allrecords = False
# avg_price = float("Nan")
# conversion = 60000
# spot_src = False
# ticker_src = False
# last_conversion = conversion
# subtot_value = float("Nan")
# subtot_qty = 0
# subtot_cost = 0
# subtot_sold = 0
# curr_qty = 0
# curr_cost = 0
# current_run_count = 0
# ffmaps_lothresh = -5
# ffmaps_hithresh = 0
# lowerclose_pct = 0
# purch_qty = False  # ! loaded in main from cvars  (min amount for CB = 0.01)
# purch_qty_adj_pct = False  # ! loaded in main from cvars
# # purch_qty_adj_qty = False  # ! loaded in main from cvars
# capital = 1
# purch_pct = 0.01
# df_priceconversion_data = False
# df_conv = False
# ohlc_conv = False
#
# dstot_sell = 0
# dstot_buy = 0
#
# pct_gain_list = []
# pnl_record_list = []
# pct_record_list = []
#
# last_pct_gain = float("Nan")
# last_pnl_record = float("Nan")
# last_pct_record = float("Nan")
#
# buy_marker_color = "red"
# sigffdeltahi = 0
# pct_return = 0
# pct_cap_return = 0
# buymode = False
# CLOSE = 0
# amp_lim = 6
# stepctu = 0
# stepctd = 0
# buy_fee = 0.000003
# sell_fee = 0.000025
# pnl_running = float("Nan")
# pct_running = float("Nan")
# epoch_boundry_ready = False
# epoch_boundry_countdown = False
# stoplimit_price = False
# sell_mark = float("Nan")
# idx = 0
# gcounter = 0
# pt1 = 0
# previous_point = 0
# prev_md5 = 0
# batchmode = False
# num_axes = 6
# time_start = 0
# time_end = 0
# run_time = 0
# curr_buys = 0
# tot_buys = 0
# tot_sells = 0
# buys_permitted = True
# external_buy_signal = False
# external_sell_signal = False
# is_first_buy = True
# autoclear = False
# recover = False
# cooldown = 0
# cooldown_count = 0
# cooldown_mult = 1
# market = False
# last_close = 0
# this_close = 0
# running_total=0
# bsuid = 0
# uid = 0
# needs_reload = False
# startdate = "1970-01-01 00:00:00"
# current_close = 0
# lblow = None
# covercost = 0
# tmp_covercost = 0
# running_buy_fee = 0
# ffmaps_midline = 0
# adj_subtot_cost = 0
# adj_avg_price = 0
# next_buy_price = 0
#
# est_buy_fee=0
# est_sell_fee=0
# coverprice = False
#
# # ! these are the only fields allowed for the coinbase order(s), as determined by 'cb_order.py'
# cflds = {
#     'type': "--type",
#     'side': "--side",
#     'pair': "--pair",
#     'size': "--size",
#     'price': "--price",
#     'stop_price': "--stop_price",
#     'upper_stop_price': "--upper_stop_price",
#     'funds': "--funds",
#     'uid': "--uid"
# }
#
# ansi = {
#     # 'xxxx': '\u001b[30m'  # + black
#     # ,'xxxx': '\u001b[31m'     # + red
#     'INFO': '\u001b[32m',  # + green
#     # ,'xxxx': '\u001b[33m'  # + yellow
#     # ,'xxxx': '\u001b[34m'    # + blue
#     # ,'xxxx': '\u001b[35m' # + magenta
#     # ,'xxxx': '\u001b[36m'    # + cyan
#     # ,'xxxx': '\u001b[37m'   # + white
#     'reset': '\u001b[0m'  # + reset
# }
#
#
# _siglft = []
#
# # * general global place to store things
# bag = {
#     "siglft": [],
#     "sigfft": [],
#
#     "sigfft0": [],
#     "sigfft1": [],
#     "sigfft2": [],
#     "sigfft3": [],
#     "sigfft4": [],
#     "sigfft5": [],
#
#     "sigfft20": [],
#     "sigfft21": [],
#     "sigfft22": [],
#     "sigfft23": [],
#     "sigfft24": [],
#     "sigfft25": []
# }
# cwd = "."
