# OPEN-QUESTIONS: מידע שחייב להגיע מניר

> **LLM / AGENT INSTRUCTIONS (English):** This is the single list of facts only Nir can provide. At the start of every session run `python3 scripts/open_items.py`, which scans the repo and prints every open item with its question ID from this file. Before working on anything that depends on an open item, **ask Nir**: in Hebrew, at most 5 questions at a time, each with its ID, why it is needed, and an example/default he can approve. Never invent the answer and never proceed on a guess. When he answers, write the answer **into the target file** (not only into the chat), mark the question `✅` with the date here, and re-run the scanner. If he does not know yet, mark `⏳` with who can answer. Answers that are secrets (tokens, passwords) never go into git: tell him which Secret/env var to put them in.

**מקרא:** ❓ פתוח | ⏳ ממתין למישהו אחר | ✅ נענה

## A. ריפו ואבטחה
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| A1 | הריפו עבר לפרטי, או הועבר ל-git הארגוני? מה הכתובת? | לפני שנכנס מידע פנימי | `deployment/argocd/application.yaml` → `repoURL` | git פנימי | ❓ |
| A2 | איך מנהלים secrets ב-k8s: Secret רגיל, Sealed Secrets, Vault או External Secrets? | יצירת `hermes-noc-engineer-env` ו-`noc-mcp-env` | `deployment/k8s/README.md` | Secret רגיל בהתחלה | ❓ |

## B. Hermes והמודל
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| B1 | מה ה-image של Hermes, איזו גרסה (`hermes --version`), ומה `HERMES_HOME` בתוכו? | פריסה ו-PVC | `deployment/k8s/hermes.yaml` (TBD-hermes-image, TBD-path) | `/opt/data` או `~/.hermes` | ❓ |
| B2 | מה כתובת ה-endpoint של Kimi K3 ומה מזהה המודל (`GET /v1/models`)? | Hermes לא יענה בלי זה | `hermes-profile/config.yaml` → `model.base_url`, `model.default` | `https://<host>/v1`, `kimi-k3` | ❓ |
| B3 | האם אפשר לשלוט ב-`reasoning_effort` דרך ה-endpoint? | עלות ומהירות ב-cron ובשאלות | `docs/decisions.md` | נמוך ב-cron, מקסימלי בחקירה | ❓ |
| B4 | הפלט של `hermes cron create --help`, `hermes gateway --help` ו-`hermes mcp --help` | לאמת את הדגלים בסקריפטים | `deployment/cron/install-cron.sh`, `deployment/day0-check.sh` | — | ❓ |
| B5 | Cron ב-Hermes מפרש שעות ב-UTC או לפי שעון מקומי? | דוח הבוקר ב-07:00 שעון ישראל | `deployment/cron/README.md` | — | ❓ |

## C. פריסה
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| C1 | באיזה קלאסטר ו-namespace? OpenShift או Rancher? | Argo ו-kustomize | `deployment/k8s/kustomization.yaml`, `argocd/application.yaml` | OpenShift, `noc-engineer` | ❓ |
| C2 | Registry ו-base image מאושרים ל-Python (ל-noc-mcp)? | build של `noc-mcp/Dockerfile` | `deployment/k8s/noc-mcp.yaml`, `noc-mcp/Dockerfile` | `python:3.12-slim` במראה הפנימי | ❓ |
| C3 | storage class ל-PVC, ואיפה שומרים היסטוריה ו-audit: PVC או Postgres הארגוני? | זיכרון Hermes והיסטוריית חקירות | `deployment/k8s/*.yaml`, `noc-mcp/config/backends.yaml` → `history` | PVC של 10Gi, ו-Postgres בהמשך | ❓ |
| C4 | Argo project ושרת ה-API של הקלאסטר | אפליקציית Argo | `deployment/argocd/application.yaml` | — | ❓ |

## D. Slack ואפליקציה
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| D1 | מי מורשה להשתמש בבוט? (Slack member IDs) | בלי זה הבוט לא עונה לאף אחד | Secret → `SLACK_ALLOWED_USERS` | כל הצוות | ❓ |
| D2 | לאיזה ערוץ ילכו דוח הבוקר והסקירה היזומה? (channel ID) | פלט ה-cron | Secret → `SLACK_HOME_CHANNEL` | ערוץ התורן | ❓ |
| D3 | יש הרשאה ליצור Slack app עם Socket Mode? מי מאשר? | tokens מסוג xoxb ו-xapp | Secret → `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN` | — | ❓ |
| D4 | באיזו אפליקציה יהיה הצ'אט, ומה ה-backend שלה (FastAPI או אחר)? איך עובד ה-auth? | חיבור `examples/web-app` | `examples/web-app/hermes_proxy.py` | FastAPI + SSO קיים | ❓ |

## E. מפת המסלול (הכי חשוב)
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| E1 | מה סדר התחנות האמיתי מהתעבורה ועד הפלט? (שמות רכיבים בלבד) | חיפוש בינארי על המסלול | `noc-mcp/config/pipeline.yaml` → `hops`, ו-`docs/pipeline-map.md` | 10 התחנות המוצעות | ❓ |
| E2 | לכל תחנה: איזו מטריקה או שאילתה סופרת IN, ואיזו OUT, DROP או LAG? | `get_hop_counts` | `pipeline.yaml` → `*_query` | `sum by (instance) (increase(X{instance=~"{instances}"}[{range}]))` | ❓ |
| E3 | איך מוגדרת **הרמטיות** של חוק, ואיפה היא נמדדת? (שאילתה) | `get_rule_kpis`, אימות הסימפטום | `pipeline.yaml` → `kpis.hermeticity` | matched/expected | ❓ |
| E4 | איך מוגדר **צימוד** של חוק, מול איזה מקור העשרה, ואיפה נמדד? | `get_rule_kpis`, skill `coupling` | `pipeline.yaml` → `kpis.coupling` | coupled/eligible | ❓ |
| E5 | אילו תחנות נמדדות לכל חוק, ואילו רק לפי שרת, topic או pod? | בחירה בין `{rule_id}` ל-`{instances}` | `pipeline.yaml` → `per_rule` | — | ❓ |

## F. מערכת החוקים והקונפיגורציה
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| F1 | יש למערכת החוקים API? מה הכתובת, ה-auth והנתיב לקבלת חוק? | `get_rule` | `backends.yaml` → `rules.base_url`, `get_rule_path` | `/api/rules/{rule_id}` | ❓ |
| F2 | איך מקבלים היסטוריית שינויים של חוק ושל קונפיגורציה גלובלית? אילו שדות יש בתשובה? | `get_rule_changes` (שלב 0 בכל חקירה) | `backends.yaml` → `changes_path`, `global_changes_path`, `change_fields` | דוגמת JSON אחת מצונזרת | ❓ |
| F3 | איך יודעים אילו שרתים, topics, שירותים ומקורות העשרה משרתים חוק? API או טבלה? | `get_rule_path`, scope לחקירה | `backends.yaml` → `rule_path_path` או `noc-mcp/config/rule-paths.yaml` | קובץ סטטי בהתחלה | ❓ |
| F4 | יש dry-run או ולידציה לשינוי חוק? | מסלול `config-change` | `noc-mcp/tools/rules.py` (`validate_rule_change`) | אין | ❓ |

## G. Backends לניטור ולשינויים
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| G1 | כתובות Prometheus ו-Thanos, וכמה שעות שמירה מקומית ב-Prometheus? | כל כלי המטריקות | `backends.yaml` → `prometheus`, `thanos` | 24 שעות | ❓ |
| G2 | שמות המטריקות לשרתים: rx drops, drops של אפליקציית הקליטה, softirq | `get_server_drops`, skill `capture-servers` | `backends.yaml` → `server_queries` | node_exporter | ❓ |
| G3 | מטריקות Kafka (exporter): lag לכל partition, ו-produce/consume rate | `get_consumer_lag` | `backends.yaml` → `kafka_queries` | kafka_exporter | ❓ |
| G4 | כתובת ECK, index pattern ללוגים ושם שדה הזמן | `query_logs` | `backends.yaml` → `elasticsearch` | `@timestamp` | ❓ |
| G5 | כתובת Argo CD ו-token לקריאה בלבד. איך ממפים שירות לאפליקציית Argo? | `get_argo_sync_history` | `backends.yaml` → `argocd`, `rule-paths.yaml` → `argo_apps` | — | ❓ |
| G6 | כתובות ה-API של OpenShift ו-Rancher, ו-service account לקריאה בלבד | `get_deployment_history` | `backends.yaml` → `kubernetes.clusters` | — | ❓ |
| G7 | איפה מתועדים חלונות תחזוקה ושדרוגים: silences ב-Grafana, Jira או מקום אחר? | `get_maintenance_windows` | `backends.yaml` → `maintenance.source` (+ `jira_jql`) | Grafana silences | ❓ |

## H. Jira
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| H1 | כתובת Jira, וסוג ה-auth (PAT או user+token)? | כלי Jira | `backends.yaml` → `jira` + Secret | PAT | ❓ |
| H2 | באיזה project ואיזה issue type נפתחות התראות ותקלות לקוח? מה ה-label או ה-JQL למציאת כרטיס פתוח של אותה התראה? | dedup ו-`search_issues` | `hermes-profile/skills/jira-operations/SKILL.md` (Environment knowledge) | `project = NOC AND labels = ...` | ❓ |
| H3 | מתי מותר ל-Hermes להגיב ב-Jira, ומי מאשר להפעיל `allow_writes`? | ה-gate לכתיבה | `noc-mcp` env `NOC_MCP_ALLOW_WRITES`, `docs/decisions.md` | רק אחרי shadow mode | ❓ |

## I. ידע הסביבה (ל-skills)
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| I1 | הרמטיות: מה הסיבות החוזרות, מה טווח תקין, ומה ה-seasonality? | `traffic-hermetic` | הסעיף "Environment knowledge" ב-skill | — | ❓ |
| I2 | צימוד: אילו מקורות העשרה פנימיים יש, באיזו תדירות הם מתעדכנים, ומה הסיבות החוזרות? | `coupling`, `enrichment-quality` | Environment knowledge | — | ❓ |
| I3 | שרתים: אילו קבוצות feed יש, מה הקיבולת, ואיך נראה שדרוג? | `capture-servers` | Environment knowledge | — | ❓ |
| I4 | Kafka: topics ו-consumer groups עיקריים ו-retention | `kafka-pipeline` | Environment knowledge | — | ❓ |
| I5 | פלטפורמה: אילו שירותים רצים באיזה קלאסטר, ומי הבעלים? | `platform-operations`, `coatr` | Environment knowledge | — | ❓ |
| I6 | אילו 5 התראות חוזרות הכי הרבה, ומה ה-runbook האמיתי לכל אחת? | `docs/runbooks.md`, סט הערכה | `docs/runbooks.md` | — | ❓ |

## J. הערכה והשוואה
| ID | שאלה | למה צריך | איפה נשמרת התשובה | דוגמה / ברירת מחדל | מצב |
|---|---|---|---|---|---|
| J1 | 20–30 התראות או תקלות שנפתרו עם הגורם הידוע (תחנה, חוק, instance). מצונזר | מדידה מול CrewAI | `evals/cases/` (כשייבנה) | — | ❓ |
| J2 | כרטיס Jira אחד שבו המסקנה של CrewAI הייתה מעורפלת (מצונזר) | מקרה בדיקה ראשון | `evals/cases/` | — | ❓ |
| J3 | איך ההתראה מגיעה היום ל-CrewAI (פורמט ה-webhook מ-Grafana, איפה ה-router)? | bridge ל-Hermes | `event-ingestion/grafana_webhook.py`, `docs/migration-from-crewai.md` | — | ❓ |
