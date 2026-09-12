import random

class GossipGenerator:
    """
    Dedicated Malayalam Gossip & Complaint Generator.
    Produces natural, dynamic Gen-Z Kerala Malayalam complaints, gossips, and reactions
    by combining Activity + Duration + Need + Mood + Time.
    """

    # Dynamic Malayalam Complaint Templates combining contexts
    CONTEXT_TEMPLATES = {
        # Gaming + Thirst / Need
        ("game", "thirsty"): [
            "രണ്ട് മണിക്കൂറായി game കളിക്കുവാണല്ലേ… ഞാൻ ഇവിടെ വെള്ളമില്ലാതെ കിടക്കുവാ. Game ജയിച്ചിട്ട് ആദ്യം എന്റെ കാര്യം നോക്കിക്കോ 😭🌱",
            "Game-ൽ കില്ലുകൾ വാരിക്കൂട്ടാൻ സമയമുണ്ട്… പാവം ഈ ചെടിക്ക് ഒരു തുള്ളി വെള്ളം തരാൻ സമയം ഇല്ലല്ലേ 🥲",
            "അവിടെ ഗെയിം കളിച്ച് ആവേശത്തിലാണല്ലോ! ഇവിടെ ഒരു ചെടി ദാഹിച്ചു കരയുന്നത് കേൾക്കുന്നില്ലേ? 😭"
        ],
        ("game", "none"): [
            "Game-ൽ എത്ര ലെവൽ പൂർത്തിയായി മോളേ? എന്റെ ഒരു സുഖവിവരം കൂടി അന്വേഷിച്ചാൽ നന്നായിരുന്നു 👀",
            "ഇത് എന്താ… game-നും നീയും തമ്മിൽ എന്തോ serious relationship ആണെന്ന് തോന്നുന്നു 👀"
        ],

        # Coding + Need
        ("coding", "thirsty"): [
            "Code-ന്റെ bug കണ്ടുപിടിക്കാൻ പറ്റും… എന്റെ ദാഹം മാത്രം കണ്ടുപിടിക്കാൻ പറ്റില്ലേ? 🥲",
            "എപ്പോഴും coding തന്നെ! ആ കോഡിൽ എറർ വരും കേട്ടോ എനിക്ക് ഒരു ഗ്ലാസ് വെള്ളം തന്നില്ലെങ്കിൽ 😭"
        ],
        ("coding", "none"): [
            "എന്റെ കാര്യം ഒന്ന് നോക്കിയിട്ട് പിന്നെ coding ചെയ്യാം മോളേ. 😌🌱",
            "നീ busy ആണെന്ന് മനസ്സിലായി… പക്ഷേ ഞാൻ ഇവിടെ unemployed ആയി ഇരിക്കുവല്ലേ 😭"
        ],

        # Document / Studying
        ("document", "thirsty"): [
            "പഠനം important ആണെന്ന് എനിക്കും അറിയാം… പക്ഷേ മൂന്ന് മണിക്കൂറായി എന്നെ ഒന്ന് നോക്കിയിട്ടില്ലല്ലോ 🥲",
            "ഇത്രയും നേരം കൊണ്ട് ഒരു പേജ് ആണോ വായിച്ചത്? വായിച്ചു കഴിഞ്ഞെങ്കിൽ ഒരു കപ്പ് വെള്ളം താ കുട്ടാ! 😭"
        ],
        ("document", "none"): [
            "Why are you reading the document without caring for me? 🥲",
            "ഹലോ പ്രൊഫസർ! പുസ്തകം വായിച്ചു തളരേണ്ട, എനിക്ക് കുറച്ചു തമാശ കേൾക്കണം 😌"
        ],

        # YouTube / Videos
        ("youtube", "thirsty"): [
            "YouTube episode മാറാൻ സമയം ഉണ്ട്… ഈ പാവം ചെടിക്ക് ഒരു ഗ്ലാസ് വെള്ളം തരാൻ മാത്രം സമയം ഇല്ലേ? 😭",
            "YouTube-ൽ എന്തൊക്കെയോ കാണാൻ സമയമുണ്ട്… എന്നെ ഒന്ന് നോക്കാൻ മാത്രം സമയമില്ലല്ലേ 😒"
        ],
        ("youtube", "none"): [
            "YouTube and all, you need to care about me! 😌🌱",
            "അവിടെ ഇരുന്നു ചിരിക്കാതെ ഇങ്ങോട്ട് ഒന്നു നോക്കൂ! എനിക്ക് പുതിയ ഗോസിപ്പുകൾ കേൾക്കണം 👀"
        ],

        # Browsing
        ("browser", "thirsty"): [
            "ഗൂഗിളിൽ എന്താ തിരയുന്നത്? ചെടികളെ എങ്ങനെ രക്ഷിക്കണം എന്ന് തിരഞ്ഞാൽ കൊള്ളാമായിരുന്നു 😭",
            "ഇൻസ്റ്റാഗ്രാം റീൽസ് കണ്ടു സമയം കളയാതെ എനിക്ക് വെള്ളം ഒഴിക്കൂ! 🥲"
        ],
        ("browser", "none"): [
            "ഫേസ്ബുക്കും ഇൻസ്റ്റാഗ്രാമും കഴിഞ്ഞെങ്കിൽ ഇങ്ങോട്ട് ഒന്ന് നോക്കാമോ? 👀",
            "ഞാൻ ഇവിടെ ദിവസങ്ങളായി attention ചോദിക്കുവാ… പക്ഷേ laptop-നാണ് full priority 😒"
        ],

        # Idle / Neglected
        ("idle", "neglected"): [
            "ഇവിടെ ഒരു ചെടിയുണ്ട്… ജീവിച്ചിരിപ്പുണ്ടോ എന്ന് ആരെങ്കിലും check ചെയ്യുമോ? 🥲",
            "ഞാൻ ഈ വീട്ടിലെ furniture ആണോ? എന്നെ ആരും ശ്രദ്ധിക്കുന്നില്ലല്ലോ. 😭"
        ],

        # Needs Templates (General)
        ("any", "critical_water"): [
            "എടീ… എന്റെ തൊണ്ട വരണ്ടിട്ട് മരിക്കാറായി. കുറച്ച് വെള്ളം തന്നൂടെ? 😭",
            "ഇവിടെ ഒരു ചെടി dehydration-ൽ ആണെന്ന് ആരെങ്കിലും പറഞ്ഞോ? 🥲",
            "ഞാൻ ഇനി ഇവിടെ കിടന്ന് ഉണങ്ങി കരഞ്ഞു മരിക്കാം… 😭"
        ],
        ("any", "sunlight"): [
            "എനിക്ക് കുറച്ച് sunlight വേണം കേട്ടോ… vampire ആക്കി വെക്കല്ലേ ☀️😭",
            "എടീ, curtain ഒന്ന് തുറന്നാൽ എനിക്കും ഈ ലോകം കാണാമായിരുന്നു 😭☀️"
        ],
        ("any", "neglected"): [
            "ഇവിടെ ഒരു ചെടി ഉണ്ടെന്ന് ഓർമ്മയുണ്ടോ? Just checking. 🙂",
            "ഞാൻ ഇവിടെ ദിവസങ്ങളായി attention ചോദിക്കുവാ… 😒"
        ]
    }

    # Random Gossips (When plant is happy/normal and needs no emergency care)
    RANDOM_GOSSIPS = [
        "എന്താ എല്ലാവരും busy… ഈ വീട്ടിൽ ഞാൻ മാത്രമാണോ unemployed? 😭",
        "ഇന്ന് എന്തോ suspiciously quiet ആണല്ലോ 👀",
        "നീ എന്നോട് സംസാരിക്കാറില്ലെങ്കിലും ഞാൻ എല്ലാം ശ്രദ്ധിക്കുന്നുണ്ട് കേട്ടോ. 😌",
        "എനിക്ക് തോന്നുന്നു ഈ വീട്ടിൽ ഏറ്റവും consistent ആയിട്ട് ജീവിക്കുന്നത് ഞാൻ തന്നെയാ. 😌🌱",
        "ഇത് എന്താ… laptop-നും നീയും തമ്മിൽ എന്തോ serious relationship ആണെന്ന് തോന്നുന്നു 👀",
        "ഇവിടെ ചില ഗോസിപ്പുകൾ പുകയുന്നുണ്ട് കേട്ടോ… എനിക്കെല്ലാം അറിയാം! 🤫🌱"
    ]

    # Time-Aware Expressions
    TIME_EXPRESSIONS = {
        "morning": "Good morning ഒക്കെ പറഞ്ഞില്ലെങ്കിലും sunlight ഒന്ന് തന്നാൽ മതി 😭☀️",
        "afternoon": "ഇത്ര ചൂടിലും ഞാൻ ഇവിടെ നിൽക്കുവാ… വെള്ളം ഒന്ന് നോക്കിക്കോ. ☀️🌱",
        "evening": "വൈകുന്നേരമായിട്ടെങ്കിലും എന്നെ ഒന്ന് നോക്കാമെന്ന വിചാരം വന്നെങ്കിൽ നന്ന് 😌",
        "late_night": "രാത്രി 2 മണിക്കും laptop നോക്കുവാണോ? നിനക്കും എനിക്കും rest വേണം കേട്ടോ 😭"
    }

    # Event Reactions
    EVENT_REACTIONS = {
        "watered": [
            "അഹാ! Finally! വെള്ളം കിട്ടി. ഇനി ഞാൻ നിങ്ങളെ കുറിച്ച് നല്ലത് പറയാം 😌🌱",
            "അയ്യോ വെള്ളവും കിട്ടി! Life set ആണല്ലോ 🌱✨",
            "ഇന്നത്തെ service കൊള്ളാം. Keep it up 😌"
        ],
        "sunlight": [
            "ഇതാണ് പറയുന്നത് ജീവിതത്തിൽ ചെറിയ കാര്യങ്ങൾ മതി സന്തോഷിക്കാൻ ☀️🌱",
            "അഹാ! നല്ല വെയിൽ കിട്ടി. ചർമ്മമൊക്കെ മിനുങ്ങുന്നുണ്ട് ☀️✨"
        ],
        "startup": [
            "അയ്യോ system start ചെയ്തല്ലോ… ഇന്ന് എന്നെ നോക്കുമോ എന്ന് നോക്കാം 😌🌱"
        ],
        "user_return": [
            "എവിടെയായിരുന്നു ഇത്ര നേരം? ഞാൻ ഇവിടെ നിന്നെ കാത്തിരിക്കുവായിരുന്നു 😭"
        ]
    }

    @staticmethod
    def generate(context):
        """
        Generates a natural, dynamic Malayalam gossip or complaint string
        matching Context (Activity + Need + Mood + Time).
        """
        activity = context.get("activity", "other")
        need = context.get("primary_need", "none")
        time_of_day = context.get("time_of_day", "afternoon")

        # 1. Check for exact activity + need template
        key = (activity, need)
        if key in GossipGenerator.CONTEXT_TEMPLATES and GossipGenerator.CONTEXT_TEMPLATES[key]:
            return random.choice(GossipGenerator.CONTEXT_TEMPLATES[key])

        # 2. Check for generic need template
        need_key = ("any", need)
        if need_key in GossipGenerator.CONTEXT_TEMPLATES and GossipGenerator.CONTEXT_TEMPLATES[need_key]:
            return random.choice(GossipGenerator.CONTEXT_TEMPLATES[need_key])

        # 3. Check activity template
        act_key = (activity, "none")
        if act_key in GossipGenerator.CONTEXT_TEMPLATES and GossipGenerator.CONTEXT_TEMPLATES[act_key]:
            return random.choice(GossipGenerator.CONTEXT_TEMPLATES[act_key])

        # 4. Late Night / Morning Time-aware override (if active)
        if time_of_day in ["late_night", "morning"] and random.random() < 0.4:
            return GossipGenerator.TIME_EXPRESSIONS[time_of_day]

        # 5. Fallback to random gossip
        return random.choice(GossipGenerator.RANDOM_GOSSIPS)

    @staticmethod
    def get_event_reaction(event_name):
        if event_name in GossipGenerator.EVENT_REACTIONS:
            return random.choice(GossipGenerator.EVENT_REACTIONS[event_name])
        return "അഹാ! കൊള്ളാമല്ലോ 😌🌱"
