This is interesting... I think.  I am sharing it with you because you are the only person I know who might find it interesting!  ;)  If not, oh well :/

So, I have about a million data points of closing prices for BTC/USDT.  My algo loops through the data and takes the previous 16 values and assigns a 1 to a value that is greater than the previous value, or a 0 if less than teh previous value.  I then record the original value from positions 0 and position 15, the first and last value, of each 16 element array. 

So, now there are 1,000,000 records that look like:

0000000000000000, 20000, 10000
0000000000000000, 21000, 9000
0000000000000001, 32123, 31321
...
1111111111111110, 32101, 34321
1111111111111111, 32101, 34326

But, I want only 2^16 (65536) of these records, one for each unique binary value, so I average the amounts to create one record for each of the binary values.  For example, all the 0000000000000000 entries now become one entry of:

0000000000000000, 20500, 15000

(20500 = avg(20000+10000),  15000 = avg(21000+9000)

Now there are 65536 entries, each with the average beginning price and ending price of its 16 elements.

Then, I plot the percentage difference of these two values on the Y-axis against the value of the first 8 bits of each binary value, which gives an X-axis of 0 - 255

The Y-axis, being % differences of two unpredictable values, should be a generally random number, so I was expecting to see something like

![perf](/home/jw/Downloads/perf.png)

This image is the plot of the average ratio of the number of BULL elements (last price > first price) over BEAR elements for each binary value that begin with value 0 - 255

Instead, I got this!

![pffd](/home/jw/Downloads/pffd.png)

This was pretty surprising as the values should be near random!  

Thinking this was some artefact of just looking at the firs 8 bits, I plotted all 64k points, and got generally the same pattern.

![pffd64](/home/jw/Downloads/pffd64.png)

Sorting the data by % instead of by hex values, I get:

![pffd-flipped](/home/jw/Downloads/pffd-flipped.png)

Which is equally surprising (the stepped aspect of the line)

What I was looking for was which patterns, based on the 1,000,000 patterns it analysed, tend to be BULLish??? and this shows that 16 bit patterns that start with a higher number generally have higher returns, but there is no reason I can think of why!

Especially interesting is how all the 2^n values are in the minus side (there is no 2^2, or 35 or 0), with half of them in the first four rows.  Also the last few on the bottom side all have some kind of prime number involved.

```
INDEX  HEX    DECIMAL PCT CHANGE          
0      40     64     -1.02509887984548   2^6
1      10     16     -1.02127495711676   2^4
2      20     32     -1.01956655163943   2^5
3      80     128    -0.98502897568431   2^7
4      18     24     -0.71028121711939   2^3 * 3
5      60     96     -0.70434142837315   
6      30     48     -0.70268061373682   
7      11     17     -0.70201302156016   
8      81     129    -0.6973832630699    
9      90     144    -0.69480959098486   
10     48     72     -0.69187015477882   
11     41     65     -0.6918031028651    
12     22     34     -0.685428145229     
13     82     130    -0.68368652024931   
14     21     33     -0.67919887494461   
15     44     68     -0.66380129381161   
16     A0     160    -0.66365297793366   
17     88     136    -0.66153525408518   
18     24     36     -0.65764561358731   
19     50     80     -0.65075624960831   
20     C0     192    -0.64978777007063   
21     12     18     -0.646561081279     
22     84     132    -0.64605055785897   
23     42     66     -0.64568840606085   
24     14     20     -0.63371730546032   
25     28     40     -0.63049126448853   
26     19     25     -0.38846662025565   
27     43     67     -0.38775407472705   
28     83     131    -0.38567245264061   
29     46     70     -0.38057991185809   
30     61     97     -0.3801853862583    
31     1A     26     -0.37652607878498   
32     86     134    -0.37292282306419   
33     32     50     -0.37229363318026   
34     8C     140    -0.37128721014      
35     C1     193    -0.37064416374885   
36     15     21     -0.37046893029202   
37     34     52     -0.37015593659722   
38     26     38     -0.37011867986965   
39     13     19     -0.36978467353526   
40     4C     76     -0.36922425761198   
41     31     49     -0.36540241954224   
42     2A     42     -0.36193596371766   
43     1      1      -0.36017294381876   2^0
44     230    560    -0.35989470099936   
45     29     41     -0.35918901678358   
46     4A     74     -0.35859551164066   
47     1C     28     -0.35559829537685   
48     40     64     -0.35538853851703   
49     2      2      -0.35392172464778   2^1
50     38     56     -0.35375430377372   
51     70     112    -0.35281325425486   
52     8      8      -0.35155473276132   2^3
53     16     22     -0.35038101683323   
54     54     84     -0.34835678815668   
55     B0     176    -0.34738488556415   
56     2C     44     -0.34721994604263   
57     D0     208    -0.34568759845204   
58     25     37     -0.34519740625605   
59     58     88     -0.34352280662545   
60     8A     138    -0.34206317390841   
61     98     152    -0.34171894976815   
62     94     148    -0.33880856036974   
63     68     104    -0.33732859523892   
64     A1     161    -0.33663913476694   
65     85     133    -0.33486641613739   
66     49     73     -0.3343238798243    
67     92     146    -0.33416076121603   
68     45     69     -0.33163239182555   
69     C2     194    -0.32962271664547   
70     91     145    -0.3287883399303    
71     52     82     -0.32757978489445   
72     51     81     -0.32728460002845   
73     62     98     -0.32545742053955   
74     A4     164    -0.32441117115833   
75     64     100    -0.32242586428829   
76     E0     224    -0.32214044844698   
77     89     137    -0.32079294623616   
78     C4     196    -0.32056579818683   
79     A8     168    -0.31855588149827   
80     C8     200    -0.3160739728734    
81     0      0      -0.31155932694674   
82     A2     162    -0.31075761506258   
83     1B     27     -0.06897065443808   
84     2B     43     -0.06260176291341   
85     33     51     -0.05955063407101   
86     53     83     -0.05774184463003   
87     55     85     -0.05355514421711   
88     17     23     -0.05313896083819   
89     A5     165    -0.04984541498308   
90     63     99     -0.04927984545103   
91     8D     141    -0.04775774730165   
92     C3     195    -0.04498160790546   
93     8B     139    -0.04318871923433   
94     4B     75     -0.04248311828597   
95     95     149    -0.04144283947398   
96     66     102    -0.04095146895707   
97     5C     92     -0.04030314773354   
98     D2     210    -0.03999786984928   
99     36     54     -0.03987390809051   
100    3A     58     -0.03957957900418   
101    35     53     -0.03821997923596   
102    69     105    -0.03797692958702   
103    99     153    -0.03745320098621   
104    87     135    -0.03652667559533   
105    A6     166    -0.03466282046213   
106    4E     78     -0.03415375943976   
107    C6     198    -0.03399596491022   
108    5      5      -0.03278623838953   
109    6      6      -0.03272751180271   
110    3      3      -0.03170035286432   
111    56     86     -0.03086197286328   
112    74     116    -0.03057591353403   
113    AA     170    -0.0299875261406    
114    71     113    -0.02830452392144   
115    1D     29     -0.02766279994241   
116    A      10     -0.02760255667199   
117    72     114    -0.02675591101681   
118    65     101    -0.0266362453638    
119    27     39     -0.02641713654093   
120    5A     90     -0.02415198906182   
121    C5     197    -0.02403141935134   
122    E2     226    -0.02356549741791   
123    A3     163    -0.02253019592926   
124    A9     169    -0.02187208972576   
125    93     147    -0.02147926872804   
126    47     71     -0.02039047383986   
127    9A     154    -0.02038937040789   
128    9      9      -0.0184632586503    
129    59     89     -0.01697405571842   
130    D8     216    -0.01587196640939   
131    6A     106    -0.01465626799368   
132    4D     77     -0.01410442444619   
133    C      12     -0.01329816725122   
134    6C     108    -0.01033889968716   
135    2E     46     -0.00969353687259   
136    39     57     -0.00789151236119   
137    C9     201    -0.00762034809914   
138    CA     202    -0.00587007582474   
139    AC     172    -0.00503717306549   
140    B1     177    -0.00460490705309   
141    2D     45     -0.00291658837279   
142    B8     184    -0.00097908624516   
143    B4     180    0.00044001971467    
144    E1     225    0.0006744683466     
145    1E     30     0.00080990286125    
146    78     120    0.00093523424798    
147    9C     156    0.00159957919793    
148    3C     60     0.00269179687777    
149    CC     204    0.00372167959581    
150    96     150    0.00410569785781    
151    B2     178    0.00441506660233    
152    8E     142    0.00764877524145    
153    D4     212    0.01029220526597    
154    E8     232    0.0139815659591     
155    D1     209    0.01507346714837    
156    E4     228    0.01585505705842    
157    F0     240    0.05329171060405    
158    6B     107    0.24692129154328    
159    57     87     0.24718041542594    
160    2F     47     0.25271653252769    
161    AD     173    0.25861533726148    
162    AB     171    0.26151470152317    
163    B5     181    0.2667365398159     
164    5B     91     0.26864710036941    
165    AE     174    0.26981635965516    
166    37     55     0.27370744478669    
167    67     103    0.27679556765297    
168    A7     167    0.27830819590802    
169    97     151    0.28011778254495    
170    5E     94     0.28566910741994    
171    D3     211    0.28701912388615    
172    D6     214    0.28924812494215    
173    3B     59     0.2918658002414     
174    5D     93     0.29253354052213    
175    D5     213    0.29455022197733    
176    DA     218    0.29573223976446    
177    B9     185    0.29603198282067    
178    6D     109    0.29636826724771    
179    6E     110    0.29898092781378    
180    B3     179    0.29904047237119    
181    8F     143    0.29922585858496    
182    E9     233    0.29927220223761    
183    9D     157    0.30003535940957    
184    75     117    0.30006840672931    
185    CD     205    0.30052026892628    
186    BC     188    0.30139013138709    
187    E3     227    0.30454545822711    
188    4F     79     0.30528702458875    
189    B      11     0.3056064272573     
190    D      13     0.30571312831916    
191    1F     31     0.30684969138803    
192    3D     61     0.31186816456386    
193    3E     62     0.31200868828582    
194    CB     203    0.31261816301388    
195    7      7      0.31497863528532    
196    B6     182    0.31559286565578    
197    E5     229    0.31854650231034    
198    C7     199    0.31922980265432    
199    7A     122    0.31966629407868    
200    9B     155    0.31977711065891    
201    76     118    0.32138929059882    
202    79     121    0.32154352169556    
203    D9     217    0.3219301712007     
204    E      14     0.32394925342077    
205    F1     241    0.32476781566044    
206    73     115    0.32550013993228    
207    DC     220    0.32573962476848    
208    BA     186    0.32633066627337    
209    9E     158    0.3281330400992     
210    CE     206    0.32967206606669    
211    EC     236    0.33736091139872    
212    EA     234    0.34080099059446    
213    E6     230    0.34398059026149    
214    F2     242    0.34799780105769    
215    7C     124    0.35099234670612    
216    F4     244    0.3599534690433     
217    F8     248    0.37157673355586    
218    BD     189    0.57193501868145    
219    DE     222    0.58451186920663    
220    7B     123    0.58741628761905    
221    B7     183    0.59969423210927    
222    5F     95     0.60393210923326    
223    AF     175    0.60809364620828    
224    D7     215    0.60984497183026    
225    6F     111    0.61103960633919    
226    BB     187    0.61246963205573    
227    DB     219    0.62261301230519    
228    EB     235    0.62517374592932    
229    CF     207    0.63141116633587    
230    77     119    0.6318512270517     
231    9F     159    0.6348783373321     
232    ED     237    0.63999022978389    
233    F5     245    0.64043610541648    
234    DD     221    0.64107662770128    
235    7D     125    0.64717842748426    
236    F6     246    0.6498878419215     
237    3F     63     0.65388964755024    
238    F3     243    0.65846268237899    
239    FA     250    0.66804981995425    
240    EE     238    0.66815190882364    
241    E7     231    0.67319856015663    
242    F      15     0.67332188361864    
243    BE     190    0.67609943686699    
244    7E     126    0.67893432532463    
245    F9     249    0.69215437892531    
246    FC     252    0.73400451191923    
247    F7     247    0.92646220528754    
248    EF     239    0.95362610582112    
249    BF     191    0.98101928186067    
250    7F     127    1.00082682661877    
251    DF     223    1.00469790566917    PRIME
252    FB     251    1.00978815571692    2^2 ?? 3^2 ?? 7
253    FE     254    1.01638907569396    2 ?? 127
254    FD     253    1.01879086299039    11 ?? 23
255    FF     255    1.31621984733317    3 ?? 5 ?? 17

```

And if I change the plot to only use the first 8 bit values and not 16 bit values when plotting (rather than only as ticks - as in the left image) I basically get the same plot but in a more loony, but predictable, fashion (right)

![pffd-2](/home/jw/Downloads/pffd-2.png)



All of this suggests that:

Any sequential 16 prices (in real time for BTC/USDT at least) will tend to end higher when there are more UP than DOWN values in the first 8 prices, and will tend end lower when there are more  UP than DOWN in the last 8, regardless of what the other 8 bits are doing.

