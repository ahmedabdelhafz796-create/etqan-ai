# ملحق أ: إعداد بيئة العمل خطوة بخطوة

## أ.1 تثبيت Python

1. حمّل Python 3.11 أو أحدث من python.org (ويندوز/ماك) أو عبر مدير حزم نظامك (لينكس).
2. أثناء التثبيت على ويندوز فعّل خيار **Add Python to PATH**.
3. تحقق: `python --version` في الطرفية يجب أن يطبع الإصدار.

## أ.2 بيئة معزولة لكل مشروع

```bash
python -m venv trading-env            # إنشاء البيئة (مرة واحدة)
source trading-env/bin/activate       # تفعيلها (ماك/لينكس)
trading-env\Scripts\activate          # (ويندوز)
```

البيئة المعزولة تمنع تضارب إصدارات المكتبات بين مشاريعك — عادة إلزامية لا رفاهية.

## أ.3 تثبيت مكتبات الكتاب

```bash
pip install numpy pandas matplotlib scikit-learn xgboost backtesting jupyter
# للأجزاء المتقدمة (اختياري بحسب الفصل):
pip install tensorflow            # الجزء الرابع (أو torch)
pip install transformers          # الجزء الخامس (FinBERT)
pip install anthropic             # الفصل 14 (LLM API)
pip install stable-baselines3     # الجزء السادس (Deep RL)
```

## أ.4 Jupyter: مختبرك التفاعلي

```bash
jupyter notebook       # يفتح المتصفح — نفّذ الخلايا واحدة واحدة وشاهد النتائج
```

ابدأ كل استكشاف في دفتر Jupyter، وحين ينضج الكود انقله لملف `.py` منظم — نفس مسار هذا الكتاب: تجارب في `scripts/` وأكواد جاهزة في `code/`.

## أ.5 اختبار التثبيت بسطرين

```python
from backtesting.test import GOOG
print(GOOG.tail())     # جدول أسعار حقيقية = البيئة جاهزة تمامًا
```

# ملحق ب: مصادر البيانات المالية

## ب.1 بيانات الأسعار

| المصدر | النوع | التكلفة | ملاحظات |
|---|---|---|---|
| مكتبة backtesting.py | GOOG يومي + EURUSD ساعة | مجاني | بيانات الكتاب — تعمل بلا إنترنت |
| yfinance | أسهم/مؤشرات/عملات، يومي ولحظي محدود | مجاني | الأشهر للتعلم؛ غير مضمون للإنتاج |
| Alpha Vantage | أسهم وعملات وفوركس | مجاني بحدود | يتطلب مفتاح API مجانيًا |
| Polygon / Tiingo | لحظي احترافي | مدفوع | جودة إنتاج |
| واجهات الوسطاء (Alpaca, IBKR, Binance) | لحظي + تنفيذ | مع الحساب | الخيار الطبيعي للروبوت الحي |

```python
import yfinance as yf
df = yf.download("AAPL", start="2020-01-01")   # مثال جلب — يتطلب إنترنت
```

## ب.2 بيانات الأخبار والنصوص

- **خلاصات RSS** للمواقع المالية: مجانية وكافية للنمذجة الأولية.
- **NewsAPI / Finnhub / Benzinga:** واجهات أخبار منظمة بطوابع زمنية (الأهم! — القسم 15.3).
- **تقارير الشركات (10-K/10-Q):** موقع EDGAR الأمريكي مجانًا.

## ب.3 قواعد الجودة قبل أي استخدام

1. افحص الفجوات والقيم الشاذة (منهجية الفصل 3) على كل مصدر جديد.
2. تحقق من تعديل الأسعار للتوزيعات والتجزئات (Adjusted).
3. سجّل بجانب كل ملف بيانات: مصدره وتاريخ جلبه وإصداره — قابلية إعادة الإنتاج تبدأ هنا.

# ملحق ج: مرجع سريع لمكتبات Python

| المكتبة | دورها | السطر النموذجي |
|---|---|---|
| numpy | مصفوفات وحساب علمي | `rets = np.diff(p) / p[:-1]` |
| pandas | جداول وسلاسل زمنية | `df["ma20"] = df.Close.rolling(20).mean()` |
| matplotlib | رسوم (كل أشكال الكتاب) | `plt.plot(df.Close)` |
| scikit-learn | التعلم الآلي الكلاسيكي | `LogisticRegression().fit(X, y)` |
| xgboost | الأشجار المعززة | `xgb.XGBClassifier(max_depth=3)` |
| backtesting | الاختبار الخلفي | `Backtest(GOOG, SmaCross).run()` |
| tensorflow/keras | التعلم العميق | `keras.layers.LSTM(32)` |
| transformers | نماذج اللغة (FinBERT) | `pipeline("sentiment-analysis")` |
| anthropic | LLM عبر API | `client.messages.create(...)` |
| stable-baselines3 | تعلم معزز جاهز | `PPO("MlpPolicy", env).learn(100_000)` |

القاعدة الذهبية في التعامل معها جميعًا: اقرأ توقيع الدالة في التوثيق الرسمي عند أول استخدام — نصف أخطاء المبتدئين معاملات افتراضية لم يعرفوا بوجودها.

# ملحق د: مسرد المصطلحات

| العربية | English | الفصل |
|---|---|---|
| التعلم الآلي | Machine Learning | 1 |
| الإفراط في التجهيز | Overfitting | 1، 9 |
| هندسة المميزات | Feature Engineering | 4 |
| التسريب المستقبلي | Look-ahead Bias / Leakage | 4، 10 |
| التقسيم الزمني | Time-based Split | 1، 5 |
| التصنيف / الانحدار | Classification / Regression | 5، 6 |
| مصفوفة الالتباس | Confusion Matrix | 5 |
| الدقة الإيجابية / الاستدعاء | Precision / Recall | 5 |
| التجميع | Clustering | 7 |
| أنظمة السوق | Market Regimes | 7 |
| اكتشاف الشذوذ | Anomaly Detection | 7 |
| بحث المعايير | Hyperparameter Tuning | 8 |
| الانتشار الخلفي | Backpropagation | 9 |
| الإيقاف المبكر | Early Stopping | 9 |
| تلاشي التدرج | Vanishing Gradient | 10 |
| الذاكرة الطويلة قصيرة المدى | LSTM | 10 |
| الانتباه الذاتي | Self-Attention | 11 |
| المحوّل | Transformer | 11 |
| الترميز الموضعي | Positional Encoding | 11 |
| تحليل المشاعر | Sentiment Analysis | 13 |
| النموذج اللغوي الكبير | Large Language Model (LLM) | 14 |
| التوليد المعزز بالاسترجاع | RAG | 14 |
| الهلوسة | Hallucination | 14 |
| انجراف ما بعد الإعلان | Post-Earnings Drift (PEAD) | 15 |
| التعلم المعزز | Reinforcement Learning | 16 |
| الحالة / الفعل / المكافأة | State / Action / Reward | 16 |
| الاستكشاف والاستغلال | Exploration vs Exploitation | 16 |
| ذاكرة إعادة التشغيل | Replay Buffer | 17 |
| هندسة المكافأة | Reward Shaping | 18 |
| الاختبار الخلفي | Backtesting | 19 |
| التداول الورقي | Paper Trading | 19 |
| الانزلاق | Slippage | 20 |
| دفتر التشغيل | Runbook | 20 |
| انجراف النموذج | Model Drift | 21 |
| التلصص على البيانات | Data Snooping | 21 |
| التراجع الأقصى | Maximum Drawdown | 19 |
| نسبة شارب | Sharpe Ratio | 19 |
| التلاعب بالإيحاء | Spoofing | 22 |

# ملحق هـ: أكواد الكتاب وإعادة إنتاج كل نتيجة

## هـ.1 البنية

```
ai-trading-book/
├── chapters/            # نصوص الفصول (Markdown)
├── figures/             # كل الأشكال (SVG مولدة بالكود)
├── code/                # أكواد جاهزة للتشغيل بأرقام الفصول
└── scripts/
    ├── figlib.py            # مكتبة الرسم المشتركة
    ├── experiments_part3.py # تجارب الفصول 5-8
    ├── experiments_part4.py # تجارب الفصول 9-12
    ├── experiments_part5.py # تجارب الفصول 13-15
    ├── experiments_part6.py # تجارب الفصول 16-18
    ├── experiments_part7_8.py # تجارب الفصول 19-22
    └── metrics_part*.json   # الأرقام الفعلية المقتبسة في المتن
```

## هـ.2 ميثاق إعادة الإنتاج

كل رقم نتيجة في هذا الكتاب — من دقة 54.2% في الفصل 1 إلى فجوة التلصص في الفصل 21 — ناتج تشغيل فعلي على بيانات ياهو فاينانس الحقيقية المرفقة بمكتبة backtesting.py، **ببذور عشوائية مثبتة**. لإعادة توليد أي شكل:

```bash
cd scripts
python experiments_part6.py            # كل تجارب الجزء السادس
python experiments_part6.py fig_18_01  # شكل واحد بعينه
```

وستجد الأرقام المحسوبة مطبوعة ومحفوظة في ملف metrics المقابل — قارنها بالمتن بنفسك؛ هذه الشفافية هي الفارق بين كتاب تعليمي ومنشور تسويقي.

# ملحق و: خارطة ما بعد الكتاب

مرتبة بالأولوية العملية لمن أتم الكتاب:

1. **التعمق الكمي المنهجي:** فترات صمود المميزات، اختبارات Walk-Forward، وWhite's Reality Check لتقييم صدق الاستراتيجيات إحصائيًا.
2. **نمذجة التقلب:** عائلة GARCH والتنبؤ بالتقلب — المهمة القابلة للتنبؤ فعلًا (القسم 6.4) ومدخل إدارة المخاطر الكمية.
3. **تحسين المحافظ:** من ماركوفيتز إلى Hierarchical Risk Parity — توزيع رأس المال على استراتيجيات وأصول.
4. **البيانات البديلة:** صور الأقمار، حركة الشحن، بيانات البطاقات — حيث تبقى إشارات لم تُسحق بعد.
5. **مسابقات Kaggle المالية:** تدريب مجاني على بيانات ضخمة بتقييم صارم خارج العينة.
6. **بنية أنظمة الإنتاج:** أنماط Event-Driven، وقوائم انتظار الرسائل، وموثوقية الأنظمة الموزعة.

# ملحق ز: المراجع والقراءات الموصى بها

## كتب مؤسِّسة

1. **Advances in Financial Machine Learning** — Marcos López de Prado: المرجع الأول لمنهجية ML المالية الصارمة (تقسيمات زمنية متقدمة، أوزان العينات، اختبارات الصدق).
2. **Machine Learning for Asset Managers** — Marcos López de Prado: مكثف وعملي في بناء المميزات والمحافظ.
3. **An Introduction to Statistical Learning** — James, Witten, Hastie, Tibshirani: أفضل مدخل رياضي رصين للجزء الثالث (متاح مجانًا من مؤلفيه).
4. **Deep Learning** — Goodfellow, Bengio, Courville: مرجع الجزء الرابع النظري (متاح مجانًا إلكترونيًا).
5. **Reinforcement Learning: An Introduction** — Sutton & Barto: إنجيل الجزء السادس (متاح مجانًا من مؤلفيه).
6. **Algorithmic Trading** — Ernest Chan: جسر عملي بين النمذجة والتشغيل الحي.

## أوراق مفصلية (بترتيب فصول الكتاب)

- Gu, Kelly & Xiu (2020), *Empirical Asset Pricing via Machine Learning* — المسح الأشمل لأداء نماذج ML على عوائد الأسهم.
- Hochreiter & Schmidhuber (1997), *Long Short-Term Memory* — الورقة الأم للفصل 10.
- Vaswani et al. (2017), *Attention Is All You Need* — ورقة المحولات (الفصل 11).
- Araci (2019), *FinBERT* — نموذج المشاعر المالية (الفصل 13).
- Mnih et al. (2015), *Human-level control through deep RL* — ورقة DQN (الفصل 17).
- Bailey et al. (2014), *Pseudo-Mathematics and Financial Charlatanism* — الأساس الرياضي لتجربة التلصص (الفصل 21).

## توثيق رسمي (محدَّث دائمًا)

scikit-learn.org، xgboost.readthedocs.io، keras.io، huggingface.co/docs، kernc.github.io/backtesting.py، stable-baselines3.readthedocs.io، docs.anthropic.com

## ومن المؤلفَين

**«التحليل الثلاثي: منهج متكامل للتداول»** — الكتاب الشقيق: المنهج التحليلي (SMC + أساسي + فني) الذي يشكل مع أدوات هذا الكتاب منظومة واحدة: هناك «ماذا نحلل»، وهنا «كيف نؤتمت التحليل ونختبره» — والقارئ الجاد يقرؤهما معًا.
