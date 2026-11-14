מפת הפרויקט: Hermes NOC Engineer

המטרה היא לבנות Agent אחד בשם noc-engineer, שרץ On-Prem בתוך סביבת Docker, מכיר את מערכות התשתית שלך, מנטר מגמות ואנומליות, חוקר תקלות, עובד מול Jira ומפיק דוח NOC יומי.

העיקרון הארכיטקטוני: לא בונים שבעה Agents ולא מקימים עכשיו מערכת Multi-Agent. בונים פרופיל Hermes אחד, מגדירים לו שבע התמחויות באמצעות Skills, ומחברים אותו ל-MCP אחד שמספק גישה מבוקרת למערכות.

חשוב להפריד בין שלושה דברים:

* Hermes – המוח: הבנת הקשר, תכנון חקירה, הסקת מסקנות, תעדוף ודיווח.
* Skills – הידע המקצועי והמתודולוגיה של כל תחום.
* MCP – שכבת הכלים והגישה למידע ולפעולות במערכות שלך.

לא נבנה מחדש את Prometheus, Grafana, Jira או את מנגנון ההתראות הקיים. נשתמש בהם כמקורות מידע וכמערכות עבודה.

1. תמונת העל

Agent יחיד

Hermes — NOC Engineer

On-Prem · Docker · Persistent Profile

Profile: noc-engineer

* SOUL.md — זהות, תפקיד, גבולות והרשאות
* Skills — שבע התמחויות
* MCP configuration — חיבור לשרת הכלים
* Memory — הקשר ותובנות מתמשכות, לא מסד נתונים תפעולי
* Cron — משימות מתוזמנות ודוחות

NOC MCP Server

שכבת כלים אחת, מחולקת לתחומים

* Monitoring tools
* Network tools
* Investigation tools
* Jira / ITSM tools
* Data Quality tools
* Enrichment tools
* Infrastructure tools

Observability

Prometheus · Thanos · Grafana · Loki / ELK

ITSM

Jira · Issues · SLA · Comments

Network

DNS · IP · CIDR · ASN · RIPE · Firewall

Infrastructure

Services · Hosts · Containers · Kubernetes, אם קיים

מקורות אירועים וערוצי עבודה

Grafana AlertsJira WebhooksJira PollingWeb ChatSlack, אם מאושרDaily Report

הזרימה המרכזית:

* אירוע מגיע מ-Grafana או מ-Jira.
* Hermes מקבל הקשר ומזהה את סוג האירוע.
* הוא בוחר את ה-Skills הרלוונטיים.
* הוא מפעיל כלי MCP כדי לאסוף ראיות.
* הוא משווה למצב קודם, למגמות ולאירועים קשורים.
* הוא מסיק מסקנה עם רמת ודאות מפורשת.
* הוא מתעד את תוצאות החקירה, מעדכן Jira לפי מדיניות ומפיק התראות.
* הוא ממשיך לניטור יזום ומפיק דוח בוקר.

2. מבנה הפרופיל בפועל

זה המבנה הלוגי שאני ממליץ עליו. Hermes מנהל את קבצי הפרופיל שלו בעצמו; לא יוצרים תיקיות פיקטיביות בתוך הפרויקט ומצפים ש-Hermes יזהה אותן.

HERMES_HOME/
│
├── config.yaml
├── .env
├── SOUL.md
│
├── skills/
│   ├── sre-observability/
│   │   └── SKILL.md
│   ├── network-engineering/
│   │   └── SKILL.md
│   ├── incident-investigation/
│   │   └── SKILL.md
│   ├── devops-operations/
│   │   └── SKILL.md
│   ├── itsm-coordination/
│   │   └── SKILL.md
│   ├── data-quality/
│   │   └── SKILL.md
│   └── enrichment-quality/
│       └── SKILL.md
│
├── memories/
├── sessions/
├── cron/
└── logs/

הערה חשובה: HERMES_HOME הוא גבול הפרופיל בפועל. ב-Docker הרשמי נתוני הפרופיל נשמרים ב-volume המתאים, ובפרופיל בשם noc-engineer הנתיב נקבע לפי הגדרות Hermes. יש לוודא את הנתיב אצלך ולא להניח שהוא זהה לנתיב של התקנה מקומית. Hermes Agent +1

Skills הם מסמכי SKILL.md שנטענים לפי הצורך, ולא Agents עצמאיים. Hermes Agent +1

3. הגדרת התפקיד — SOUL.md

זה המסמך החשוב ביותר בפרויקט. הוא מגדיר איך Hermes צריך לחשוב ולעבוד.

תחומי האחריות:

* להיות NOC Engineer ולא רק מסכם התראות.
* להכיר את טופולוגיית המערכות, השירותים והתלויות ביניהם.
* לבצע חקירה רב-מערכתית לפני קביעת מסקנה.
* לזהות אנומליות ומגמות גם ללא התראה קיימת.
* לקשר בין תקלות נוכחיות להיסטוריית אירועים.
* לזהות בעיות איכות נתונים והעשרה.
* לנהל מעקב אחר אירועים ומשימות Jira.
* להפיק דוחות בוקר עם ממצאים, מגמות וסיכונים.
* להציג ראיות לכל מסקנה ולהבחין בין עובדה להשערה.
* לא לבצע שינויים בתשתית ללא אישור מפורש.

כללי עבודה מחייבים

* לא לקבוע Root Cause ללא ראיות.
* לא להמציא נתונים כאשר מערכת אינה זמינה.
* לא להסתמך על מדד בודד כאשר ניתן להצליב מספר מקורות.
* לבדוק חלון זמן לפני ואחרי האירוע.
* לבדוק האם קיימת השפעה על שירותים נוספים.
* להבחין בין בעיה נקודתית לבעיה חוזרת.
* להציג מה נבדק, מה לא נבדק ומה חסר.
* כל פעולה מול Jira צריכה להיות מתועדת.
* כל פעולה שמשנה תשתית דורשת אישור אנושי.

4. שבע ההתמחויות — מה כל Skill צריך לדעת

01

SRE & Observability

Prometheus, Grafana, Thanos, Loki ו-ELK. ניתוח מטריקות, מגמות, התנהגות היסטורית, קורלציה בין מטריקות ולוגים, זיהוי חריגות ותחזיות מוקדמות.

02

Network Engineering

DNS, כתובות IP, CIDR, ASN, RIPE, ספקים, תעבורה, Connectivity, Firewall וכלי אבחון רשת. זיהוי קשר בין תקלה ברשת לשירותים מושפעים.

03

Incident Investigation

תהליך חקירה סדור: הגדרת הבעיה, בניית ציר זמן, איסוף ראיות, יצירת השערות, בדיקתן, זיהוי Root Cause, הצלבה עם תקלות קודמות והערכת רמת ודאות.

04

DevOps Operations

בדיקת זמינות שירותים, תהליכים, Containers, Kubernetes אם קיים, משאבים, Deployments, תלויות ושינויים תפעוליים.

05

ITSM Coordination

קליטת Jira, סיווג אירועים, שיוך, SLA, מניעת כפילויות, עדכון משימות, יצירת Follow-up Tasks וקישור בין תקלות קשורות.

06

Data Quality

בדיקות שלמות, תקינות, עקביות, טריות, כפילויות, חריגות בסכמות ואמינות נתונים שמגיעים ממערכות הניטור.

07

Enrichment Quality

אימות ASN, Provider, Country, Location ו-Connection Type. בדיקת מקור המידע, אמינותו, עדכניותו וזיהוי העשרה שגויה.

כל Skill צריך לכלול:

* מתי להפעיל אותו.
* אילו כלים להפעיל.
* סדר הבדיקות.
* אילו נתונים נדרשים.
* איך להצליב מקורות.
* מקרי כשל ומגבלות.
* איך לאמת מסקנה.
* פורמט תוצאה אחיד.

לא כדאי לכתוב את כל הידע הזה בתוך SOUL.md. ה-SOUL מגדיר את כללי העבודה הכלליים, וה-Skills מכילים את המתודולוגיה המקצועית.

5. שכבת MCP — החיבור למערכות

אני ממליץ על שרת MCP אחד בשם noc-mcp, עם כלים מחולקים לפי תחום.

תחום	כלים
Monitoring	query_metrics, query_logs, get_alerts, get_metric_history, get_service_health, compare_baseline
Network	resolve_dns, lookup_ip, query_ip_ranges, lookup_asn, check_connectivity, inspect_firewall_rules
Investigation	search_investigations, get_investigation, compare_investigations, get_related_incidents, get_service_dependencies
Data Quality	check_data_quality, get_quality_scores
Enrichment	audit_enrichment, validate_asn, validate_provider, validate_ripe_data
Jira	get_issue, search_issues, add_investigation_comment, create_followup_task, update_issue, link_issues
Infrastructure	get_host_health, get_container_status, get_service_status, get_deployment_history

השמות הם חוזה תכנון מוצע, לא שמות של כלים שכבר קיימים אצלך.

כללי תכנון ל-MCP

* כל כלי צריך להחזיר תשובה מובנית, לא רק טקסט חופשי.
* כל קריאה צריכה לכלול timeout.
* יש להחזיר שגיאות בצורה מפורשת.
* יש להחזיר timestamp ומקור מידע.
* יש להחזיר מידע על טווח הזמן שנבדק.
* יש להגביל תוצאות גדולות באמצעות pagination או aggregation.
* יש להגדיר הרשאות ברמת כלי.
* כל פעולת כתיבה צריכה לעבור בדיקת הרשאות.
* אין לחשוף כלי שמאפשר הרצת פקודה שרירותית על שרתי Production.

הפרדה חשובה: MCP הוא ממשק גישה. הוא לא אמור להכיל את כל הלוגיקה העסקית של חקירה, ניתוח אנומליות או ניהול תהליכים. בדיקות דטרמיניסטיות צריכות להתבצע בקוד, וה-Agent צריך לפרש את התוצאות.

Hermes תומך בחיבור MCP דרך mcp_servers ב-config.yaml, לרבות סינון הכלים הזמינים מכל שרת. Hermes Agent +1

6. תהליך העבודה — ארבעה מסלולים מרכזיים

A. תגובה להתראת Grafana

* קבלת Alert
    קבלת ה-Webhook עם alert labels, annotations, fingerprint, timestamps וערכי מדדים.
* הבנת ההקשר
    זיהוי שירות, שרת, לקוח, רכיב רשת, חומרת האירוע ותלויות.
* חקירה
    שאילתות Prometheus / Thanos, חיפוש לוגים, בדיקת שירותים, DNS, רשת והיסטוריית תקלות.
* קורלציה
    בדיקת אירועים מקבילים, שינויים, תקלות חוזרות ומדדים חריגים.
* מסקנה
    קביעת Root Cause רק כאשר הראיות תומכות בכך. אחרת הצגת השערות וחוסרים.
* Jira
    עדכון האירוע הקיים או יצירת משימת המשך בהתאם למדיניות.
* דיווח
    הצגת סיכום, ראיות, פעולות שבוצעו והמלצות.

B. ניטור יזום — גם בלי התראה

זה אחד החלקים החשובים בפרויקט. Hermes לא אמור להיות תלוי רק ב-Grafana Alerts.

הוא צריך לזהות:

* שינוי בהתנהגות של מטריקות לאורך זמן.
* חריגה מבייסליין היסטורי.
* עלייה הדרגתית בשימוש במשאבים.
* ירידה באיכות או בקצב של תעבורה.
* שינויים בדפוסי פרוטוקולים.
* בעיות DNS או Connectivity.
* שירות שמתדרדר אך עדיין לא עבר את סף ההתראה.
* אירועים שחוזרים בפרקי זמן קבועים.
* קשר בין כמה חריגות שנראות בנפרד לאותה בעיה.

החלטה ארכיטקטונית: זיהוי האנומליות הבסיסי צריך להתבצע בקוד Python ולא להסתמך על כך ש-LLM יסרוק את כל המטריקות ברציפות.

החלוקה:

* Python: סריקה, חישוב סטטיסטי, השוואת בייסליין וזיהוי חריגה.
* Hermes: קורלציה, הסבר, חקירה והערכת משמעות עסקית ותפעולית.

C. טיפול ב-Jira

יש שני מסלולי קליטה:

* Webhook – המסלול העיקרי, לקבלת אירוע מיד כשנוצר או מתעדכן.
* Polling – מסלול גיבוי והתאמה, כדי לזהות אירועים שה-Webhook לא העביר.

בכל אירוע:

* להבין את תיאור התקלה.
* לחלץ שירות, רכיב, שרת, לקוח, IP וזמן.
* לאסוף נתוני ניטור רלוונטיים.
* לחפש תקלות דומות בעבר.
* לבדוק האם קיימת חקירה קודמת.
* להוסיף תגובה מבוססת ראיות.
* ליצור משימת המשך במידת הצורך.
* למנוע יצירת משימות כפולות.

D. דוח NOC יומי

דוח בוקר בשעה 07:00 לפי Asia/Jerusalem:

* אירועים שהתרחשו ב-24 השעות האחרונות.
* אירועים פתוחים שעדיין לא נפתרו.
* תקלות חוזרות.
* Root Causes שאומתו.
* אנומליות שלא יצרו Alert.
* מגמות שליליות.
* בעיות איכות נתונים.
* בעיות העשרה.
* מערכות ושירותים בסיכון.
* משימות Jira שדורשות טיפול.
* המלצות לפעולה.

הדוח צריך להבחין בין בעיה שאומתה לבין חשד שדורש בדיקה.

7. CrewAI — מה עושים עם הפרויקט הקיים?

לא מוחקים אותו מחר.

ההחלטה שלי:

* משאירים את CrewAI כפי שהוא כרגע.
* מחברים את Hermes לתוצאות החקירה שלו.
* משווים את איכות החקירה של Hermes מול CrewAI על אותן התראות.
* בודקים האם CrewAI באמת מוסיף יכולת חקירה או רק מפעיל כלים ומייצר סיכום.
* אם הוא רק שכבת orchestration, מעבירים את הכלים והבדיקות הדטרמיניסטיות ל-MCP ומוציאים אותו בהדרגה.
* אם הוא מבצע חקירה אדפטיבית טובה יותר, אפשר להשאיר אותו כ-worker ייעודי.

אל תיתן לשני Agents לבצע את אותה חקירה במקביל ב-Production ללא סיבה מדידה.

8. פורמט אחיד לתוצאות חקירה

כל חקירה, בין אם הגיעה מ-Grafana, Jira או ניטור יזום, צריכה להחזיר מבנה אחיד.

לדוגמה:

{
  "investigation_id": "INV-12345",
  "source": "grafana_alert",
  "target": {
    "service": "network-service",
    "host": "server-01"
  },
  "status": "HIGH_CONFIDENCE",
  "summary": "Elevated packet drops correlated with interface saturation",
  "root_cause": {
    "description": "Network interface saturation",
    "confidence": 0.87
  },
  "findings": [],
  "hypotheses": [],
  "evidence_refs": [],
  "metrics_evidence": [],
  "log_evidence": [],
  "timeline": [],
  "recommended_actions": [],
  "missing_data": [],
  "tool_execution_status": [],
  "data_freshness": {},
  "jira_issue": null,
  "created_at": "2026-11-14T07:00:00Z",
  "schema_version": "1.0"
}

סטטוסים מותרים:

סטטוס	משמעות
CONFIRMED	Root Cause אומת בראיות
HIGH_CONFIDENCE	מסקנה חזקה, אך לא אומתה באופן מלא
INVESTIGATION_INCOMPLETE	החקירה לא הושלמה
INCONCLUSIVE	אין מספיק ראיות למסקנה

חשוב: ערך confidence אינו הסתברות מדעית אוטומטית. הוא הערכת ודאות של המערכת, ויש להגדיר קריטריונים ברורים לחישובו.

9. זיכרון ומידע על הסביבה

Hermes צריך להכיר את הסביבה ולא להתחיל כל חקירה מאפס.

יש להפריד בין שלושה סוגי מידע:

א. Memory של Hermes

* העדפות תפעוליות.
* הקשר מתמשך.
* Runbooks ומידע שימושי שה-Agent למד.
* הנחיות עבודה.

ב. Inventory של הסביבה

* רשימת שירותים.
* שרתים וכתובות IP.
* קשרים בין שירותים.
* בעלי אחריות.
* מערכות ניטור רלוונטיות.
* תלויות בין רכיבים.

ג. היסטוריית חקירות

* אירועים קודמים.
* ממצאים.
* Root Causes.
* תקלות חוזרות.
* פעולות שבוצעו.
* תוצאות פעולות.

לשלב הראשון אפשר לשמור את Inventory ואת היסטוריית החקירות במקור נתונים קיים או בקבצים מסודרים. אם יש צורך בחיפוש, קורלציה ושמירת היסטוריה אמינה לאורך זמן, אני ממליץ על PostgreSQL.

Memory של Hermes אינו תחליף למסד נתונים תפעולי.

10. משימות מתוזמנות — Cron

לא כל משימה צריכה להפעיל LLM. חלק מהמשימות צריכות להיות בדיקות קוד פשוטות.

הנה לוח העבודה המומלץ:

תדירות	משימה	מי מבצע
כל דקה	בדיקת זמינות MCP ומקורות מידע	Python / Health check
כל 2 דקות	Jira Polling והתאמה ל-Webhooks	Python
כל 5 דקות	סריקת אנומליות	Python
כל 5 דקות	בדיקת חקירות תקועות	Python
כל 10 דקות	מעקב SLA ומשימות פתוחות	Python
כל 15 דקות	הערכת מצב שירותים	Python
כל 15 דקות	בדיקות Data Quality	Python
כל שעה	חישוב ועדכון Baselines	Python
כל 6 שעות	בדיקות איכות Enrichment	Python
כל 6 שעות	ניתוח מגמות וקיבולת	Python + Hermes לפי צורך
07:00	דוח NOC יומי	Hermes
08:00	סקירת תקלות פתוחות וחוזרות	Hermes

Hermes Cron תומך במשימות מתוזמנות עם Skills, ואפילו בהרצה ללא Agent במקרים שבהם לא נדרש LLM. Hermes Agent +1

המלצה: להתחיל עם Cron של Hermes למשימות ה-Agent, ועם Cron רגיל או scheduler חיצוני לבדיקות Python דטרמיניסטיות.

11. אבטחה והרשאות

חובה לפני Production

פעולה	הרשאה התחלתית
קריאת Metrics	Read
קריאת Logs	Read
קריאת Jira	Read
חיפוש היסטוריית תקלות	Read
בדיקות DNS / IP	Read
בדיקת Firewall Rules	Read
הוספת תגובה ל-Jira	Write מוגבל
יצירת משימת Jira	Write מוגבל
עדכון סטטוס Jira	לפי מדיניות
Restart Service	חסום
Scale Service	חסום
Block IP	חסום
שינוי Firewall	חסום

דרישות נוספות:

* משתמש שירות נפרד לכל מערכת ככל שניתן.
* שמירת Secrets ב-.env או Secret Manager מאושר, לא בתוך Skills.
* אין להכניס סודות ללוגים.
* הגבלת גישה לכלי MCP.
* Audit לכל פעולת כתיבה.
* Rate limits למערכות חיצוניות.
* Timeouts לכל בקשה.
* הגבלת גודל תוצאות.
* הגנה מפני Prompt Injection שמגיע מתוך Jira, Logs או Alert annotations.
* הגבלת גישה לרשת ולתיקיות Docker.
* הפרדת סביבת בדיקות מ-Production.

חשוב: הנחיות ב-SOUL.md אינן מנגנון הרשאות. יש לאכוף הרשאות גם בקוד ובשכבת התשתית.

12. מבנה Repository לפיתוח

כאן אני מפריד בין פרופיל Hermes לבין קוד שרת ה-MCP. זה לא אומר שאתה צריך להקים עכשיו עשרה שירותים.

noc-engineer/
│
├── hermes-profile/
│   ├── SOUL.md
│   ├── config.yaml
│   └── skills/
│       ├── sre-observability/
│       │   └── SKILL.md
│       ├── network-engineering/
│       │   └── SKILL.md
│       ├── incident-investigation/
│       │   └── SKILL.md
│       ├── devops-operations/
│       │   └── SKILL.md
│       ├── itsm-coordination/
│       │   └── SKILL.md
│       ├── data-quality/
│       │   └── SKILL.md
│       └── enrichment-quality/
│           └── SKILL.md
│
├── noc-mcp/
│   ├── server.py
│   ├── tools/
│   │   ├── monitoring.py
│   │   ├── network.py
│   │   ├── investigation.py
│   │   ├── infrastructure.py
│   │   ├── data_quality.py
│   │   ├── enrichment.py
│   │   └── jira.py
│   │
│   ├── clients/
│   │   ├── prometheus.py
│   │   ├── thanos.py
│   │   ├── loki.py
│   │   └── jira.py
│   │
│   ├── schemas/
│   │   ├── investigation.py
│   │   ├── evidence.py
│   │   └── common.py
│   │
│   ├── security/
│   ├── config/
│   ├── tests/
│   └── pyproject.toml
│
├── anomaly-engine/
│   ├── rules.py
│   ├── statistical.py
│   ├── baselines.py
│   └── detection.py
│
├── event-ingestion/
│   ├── grafana_webhook.py
│   ├── jira_webhook.py
│   └── jira_poller.py
│
├── reporting/
│   ├── daily_report.py
│   └── report_builder.py
│
├── deployment/
│   ├── docker-compose.yml
│   └── .env.example
│
├── docs/
│   ├── architecture.md
│   ├── tools-contract.md
│   ├── investigation-flow.md
│   ├── security.md
│   └── runbooks.md
│
└── README.md

חשוב: זהו מבנה ה-Repository לפיתוח ולניהול גרסאות. hermes-profile/ הוא מקור הגרסה של ההגדרות וה-Skills. בפועל צריך לפרוס או לסנכרן את התוכן לנתיב הפרופיל ש-Hermes משתמש בו. לא להגדיר את תיקיית ה-Repository עצמה כנתיב פרופיל בלי לבדוק את מנגנון הפריסה.

13. תוכנית מימוש — לפי סדר עבודה

שלב 1 — מחר

הקמת שלד Hermes

* יצירת Profile בשם noc-engineer.
* הגדרת SOUL.md.
* יצירת שבעת ה-Skills.
* הגדרת חיבור MCP.
* בדיקת גישה לכל מערכת.
* הגדרת הרשאות Read Only.

שלב 2

MCP וחקירה

* מימוש כלי Monitoring.
* מימוש כלי Network.
* מימוש כלי Jira.
* הגדרת פורמט חקירה אחיד.
* בדיקת חקירה מלאה על Alert אמיתי.

שלב 3

אינטגרציה עם אירועים

* חיבור Grafana Webhook.
* חיבור Jira Webhook.
* Jira Polling כגיבוי.
* מניעת כפילויות.
* תיעוד חקירות והיסטוריה.

שלב 4

Proactive Monitoring

* בניית Anomaly Engine ב-Python.
* הגדרת Baselines.
* זיהוי מגמות.
* בדיקות Data Quality.
* בדיקות Enrichment.
* העברת ממצאים משמעותיים ל-Hermes.

שלב 5

אוטומציה ודיווח

* Cron.
* דוח בוקר.
* מעקב SLA.
* התראות על חקירות תקועות.
* ממשק Web Chat ודיווחים.

שלב 6 — לפני Production

הקשחה והערכה

* בדיקות הרשאות.
* בדיקות כשל MCP.
* בדיקות אובדן Webhook.
* Retry ו-Idempotency.
* בדיקות איכות RCA.
* השוואת Hermes מול CrewAI.
* ניטור ביצועי Hermes עצמו.

14. קריטריונים להצלחה

לא מספיק ש-Hermes מצליח לענות על שאלה או לסכם Alert. צריך להוכיח שהוא מסוגל לבצע עבודה של NOC Engineer.

בדיקה	תנאי הצלחה
קבלת Alert	האירוע נקלט ומתועד
חקירה	נאספו ראיות ממספר מקורות רלוונטיים
Root Cause	המסקנה נתמכת בראיות
חוסר מידע	המערכת מציינת מה לא הצליחה לבדוק
קורלציה	זיהוי אירועים קשורים
מניעת כפילויות	אין יצירת משימות Jira כפולות
Proactive	זיהוי חריגות לפני Alert קיים, כשיש בסיס נתונים מתאים
Daily Report	דוח עם מגמות, אירועים וסיכונים
Failure Handling	כשל של מערכת אחת לא מפיל את כל התהליך
Security	אין פעולות Production לא מאושרות

מומלץ לבנות סט בדיקות מתוך התראות היסטוריות שכבר נפתרו, עם Root Cause ידוע. כך אפשר למדוד Precision של המסקנות, False Positives, זמן חקירה ואיכות הראיות.

15. מה לא בונים כרגע

כדי שלא נבזבז זמן על ארכיטקטורה לפני שיש מוצר עובד:

* לא בונים Multi-Agent.
* לא מוסיפים CrewAI כשכבת תיווך קבועה.
* לא מכניסים ML לפני שיש היסטוריה מספקת ונתונים מתויגים.
* לא בונים Dashboard חדש לפני שהחקירה עצמה עובדת.
* לא מפתחים מערכת Memory עצמאית לפני שיש צורך מוכח.
* לא מאפשרים ל-Hermes לבצע פעולות Production.
* לא מפצלים את המערכת לעשרות Microservices.

בהמשך, אם עומס, זמינות או דרישות ארגוניות יחייבו זאת, אפשר להוסיף PostgreSQL, RabbitMQ, שירותי Worker, מנגנון Inbox/Outbox ו-Workflow Engine. אבל אלה אינם תנאי להתחלת המימוש.

16. החלטות ארכיטקטוניות סופיות

נושא	החלטה
Agent	אחד
Profile	noc-engineer
Skills	שבע התמחויות
MCP	שרת מרכזי אחד
Deployment	On-Prem Docker
Monitoring	Prometheus / Grafana / Thanos / Loki / ELK
ITSM	Jira
Event Intake	Webhook + Polling
Anomaly Detection	Hybrid: Rules + Statistics, ובהמשך ML
Investigation	Hermes
CrewAI	נשאר זמנית לצורך השוואה
Memory	Hermes Memory + היסטוריה תפעולית מסודרת
Scheduling	Hermes Cron + Scheduler לבדיקות דטרמיניסטיות
Reporting	דוח NOC יומי ב-07:00
Autonomy	Recommend בלבד
Production Changes	אישור אנושי בלבד

17. סדר הפעולות המדויק למחר

אם הייתי מתחיל את הפרויקט בעצמי, זה סדר העבודה:

Day 1 — Definition of Done

0 מתוך 9 הושלמו

0%

ליצור Profile בשם noc-engineer

לבדוק היכן נשמר HERMES_HOME ב-Docker ולוודא Persistence

לכתוב SOUL.md עם תפקיד, כללי חקירה והרשאות

ליצור את שבעת קובצי SKILL.md

להרים noc-mcp עם כלי בדיקה אחד לכל מערכת

לחבר MCP ל-Hermes ולוודא שכל הכלים מזוהים

להריץ חקירה ידנית על Alert אמיתי

לבדוק שהמסקנה כוללת ראיות, חוסרים ורמת ודאות

לשמור תיעוד של תוצאות הבדיקה

היעד של היום הראשון: Hermes מחובר למערכות, יודע להפעיל את ה-Skills הנכונים, ומסוגל לבצע חקירה אחת מלאה ומבוססת ראיות. לא צריך להשלים את כל מערכת ה-NOC ביום אחד.

המסמכים הרשמיים שכדאי לעבוד לפיהם בזמן המימוש:

* Hermes Profiles⁠￼ — יצירה וניהול פרופיל.
* Creating Skills⁠￼ — מבנה וכתיבת Skills.
* MCP Integration⁠￼ — חיבור שרת MCP.
* Cron⁠￼ — משימות מתוזמנות.
* Configuration⁠￼ — הגדרות Docker, כלים וסביבת הריצה.

ההמלצה הסופית שלי: מחר אל תתחיל מ-Anomaly Engine או מ-CrewAI. תתחיל מפרופיל Hermes, שבעת ה-Skills, MCP וחקירת Alert אמיתי. זו אבן היסוד. ברגע שהחקירה עובדת, אפשר להוסיף ניטור יזום, קורלציה ודוחות בלי לשנות את הארכיטקטורה המרכזית.