"""World currencies: code -> (Arabic name, English name, aliases).

Multi-word Arabic aliases also get their definite form automatically:
"دينار كويتي" matches "الدينار الكويتي" too.
"""
_BASE = {
    # Gulf and Arab world
    "SAR": ("ريال سعودي", "Saudi riyal", ["ريال سعودي", "ريال", "ريالات", "riyal", "riyals", "sar"]),
    "AED": ("درهم إماراتي", "UAE dirham", ["درهم إماراتي", "درهم اماراتي", "درهم", "dirham", "dirhams", "aed"]),
    "KWD": ("دينار كويتي", "Kuwaiti dinar", ["دينار كويتي", "kwd", "kuwaiti dinar"]),
    "QAR": ("ريال قطري", "Qatari riyal", ["ريال قطري", "qar", "qatari riyal"]),
    "BHD": ("دينار بحريني", "Bahraini dinar", ["دينار بحريني", "bhd", "bahraini dinar"]),
    "OMR": ("ريال عماني", "Omani rial", ["ريال عماني", "omr", "omani rial"]),
    "EGP": ("جنيه مصري", "Egyptian pound", ["جنيه مصري", "جنيه", "egp", "egyptian pound"]),
    "JOD": ("دينار أردني", "Jordanian dinar", ["دينار اردني", "دينار أردني", "jod", "jordanian dinar"]),
    "IQD": ("دينار عراقي", "Iraqi dinar", ["دينار عراقي", "iqd", "iraqi dinar"]),
    "LBP": ("ليرة لبنانية", "Lebanese pound", ["ليرة لبنانية", "ليره لبنانيه", "lbp", "lebanese pound"]),
    "SYP": ("ليرة سورية", "Syrian pound", ["ليرة سورية", "ليره سوريه", "syp", "syrian pound"]),
    "MAD": ("درهم مغربي", "Moroccan dirham", ["درهم مغربي", "mad", "moroccan dirham"]),
    "DZD": ("دينار جزائري", "Algerian dinar", ["دينار جزائري", "dzd", "algerian dinar"]),
    "TND": ("دينار تونسي", "Tunisian dinar", ["دينار تونسي", "tnd", "tunisian dinar"]),
    "LYD": ("دينار ليبي", "Libyan dinar", ["دينار ليبي", "lyd", "libyan dinar"]),
    "SDG": ("جنيه سوداني", "Sudanese pound", ["جنيه سوداني", "sdg", "sudanese pound"]),
    "YER": ("ريال يمني", "Yemeni rial", ["ريال يمني", "yer", "yemeni rial"]),
    # Major world currencies
    "USD": ("دولار أمريكي", "US dollar", ["دولار امريكي", "دولار أمريكي", "دولار", "دولارات", "dollar",
                                         "dollars", "usd", "$"]),
    "EUR": ("يورو", "euro", ["يورو", "euro", "euros", "eur", "€"]),
    "GBP": ("جنيه إسترليني", "British pound", ["جنيه استرليني", "جنيه إسترليني", "استرليني", "إسترليني",
                                              "pound", "pounds", "sterling", "gbp", "£"]),
    "JPY": ("ين ياباني", "Japanese yen", ["ين ياباني", "ين", "yen", "jpy", "¥"]),
    "CNY": ("يوان صيني", "Chinese yuan", ["يوان صيني", "يوان", "yuan", "renminbi", "cny"]),
    "CHF": ("فرنك سويسري", "Swiss franc", ["فرنك سويسري", "chf", "swiss franc"]),
    "CAD": ("دولار كندي", "Canadian dollar", ["دولار كندي", "cad", "canadian dollar"]),
    "AUD": ("دولار أسترالي", "Australian dollar", ["دولار استرالي", "دولار أسترالي", "aud", "australian dollar"]),
    "NZD": ("دولار نيوزيلندي", "New Zealand dollar", ["دولار نيوزيلندي", "nzd", "new zealand dollar"]),
    "HKD": ("دولار هونغ كونغ", "Hong Kong dollar", ["دولار هونغ كونغ", "hkd", "hong kong dollar"]),
    "SGD": ("دولار سنغافوري", "Singapore dollar", ["دولار سنغافوري", "sgd", "singapore dollar"]),
    "SEK": ("كرونة سويدية", "Swedish krona", ["كرونة سويدية", "كرونه سويديه", "sek", "swedish krona"]),
    "NOK": ("كرونة نرويجية", "Norwegian krone", ["كرونة نرويجية", "nok", "norwegian krone"]),
    "DKK": ("كرونة دنماركية", "Danish krone", ["كرونة دنماركية", "dkk", "danish krone"]),
    "RUB": ("روبل روسي", "Russian ruble", ["روبل روسي", "روبل", "ruble", "rouble", "rub"]),
    "TRY": ("ليرة تركية", "Turkish lira", ["ليرة تركية", "ليره تركيه", "ليرة", "lira", "turkish lira"]),
    "INR": ("روبية هندية", "Indian rupee", ["روبية هندية", "روبيه هنديه", "روبية", "روبيه", "rupee", "rupees", "inr"]),
    "PKR": ("روبية باكستانية", "Pakistani rupee", ["روبية باكستانية", "روبيه باكستانيه", "pkr", "pakistani rupee"]),
    "BDT": ("تاكا بنغلاديشي", "Bangladeshi taka", ["تاكا", "taka", "bdt"]),
    "IDR": ("روبية إندونيسية", "Indonesian rupiah", ["روبية اندونيسية", "روبية إندونيسية", "rupiah", "idr"]),
    "MYR": ("رينغيت ماليزي", "Malaysian ringgit", ["رينغيت", "رنجت", "ringgit", "myr"]),
    "PHP": ("بيزو فلبيني", "Philippine peso", ["بيزو فلبيني", "philippine peso"]),
    "THB": ("بات تايلندي", "Thai baht", ["بات تايلندي", "baht", "thb"]),
    "KRW": ("وون كوري", "South Korean won", ["وون كوري", "وون", "korean won", "krw"]),
    "IRR": ("ريال إيراني", "Iranian rial", ["ريال ايراني", "ريال إيراني", "irr", "iranian rial"]),
    "ZAR": ("راند جنوب أفريقي", "South African rand", ["راند", "rand", "zar"]),
    "NGN": ("نايرا نيجيري", "Nigerian naira", ["نايرا", "naira", "ngn"]),
    "BRL": ("ريال برازيلي", "Brazilian real", ["ريال برازيلي", "brazilian real", "brl"]),
    "MXN": ("بيزو مكسيكي", "Mexican peso", ["بيزو مكسيكي", "mxn", "mexican peso"]),
    "PLN": ("زلوتي بولندي", "Polish zloty", ["زلوتي", "zloty", "pln"]),
    "ETB": ("بير إثيوبي", "Ethiopian birr", ["بير اثيوبي", "بير إثيوبي", "birr", "etb"]),
}


def _with_definite(aliases: list[str]) -> list[str]:
    out = list(aliases)
    for a in aliases:
        words = a.split()
        if len(words) == 2 and "؀" <= a[0] <= "ۿ" and not words[1].startswith("ال"):
            out.append(f"{words[0]} ال{words[1]}")
    return out


CURRENCIES = {code: (ar, en, _with_definite(al)) for code, (ar, en, al) in _BASE.items()}
