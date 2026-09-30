# 鎵归噺椤甸潰鐢熸垚鍣?
灏嗕綘瀵煎叆鐨?CSV 鎴?JSON 椤甸潰鏁版嵁娓叉煋涓虹嫭绔?Markdown 椤甸潰銆傛瘡鏉¤褰曞繀椤绘彁渚涚湡瀹炪€佸彲鏍搁獙涓斾笌涓婚鐩稿叧鐨勫唴瀹癸紱宸ュ叿涓嶄娇鐢ㄩ殣钘忛摼鎺ャ€佸叧閿瘝鍫嗙爩鎴栧叾浠栬閬挎悳绱㈠紩鎿庤鍒欑殑鏈哄埗銆?
## GitHub 鑷姩鐢熸垚

鐢熶骇鏁版嵁鏂囦欢鏄?`data/pages.csv`銆傚皢瀹冩彁浜ゅ埌 GitHub 鐨?`main` 鍒嗘敮鍚庯紝`.github/workflows/generate-pages.yml` 浼氳嚜鍔ㄨ繍琛?Python銆佺敓鎴?`generated/` 涓殑 Markdown 椤甸潰骞舵妸鍙樺寲鎻愪氦鍥炰粨搴撱€?
棣栨浣跨敤鍓嶏紝鍦ㄤ粨搴撶殑 **Settings 鈫?Actions 鈫?General 鈫?Workflow permissions** 閫夋嫨 **Read and write permissions**锛屼互鍏佽宸ヤ綔娴佹彁浜ょ敓鎴愮粨鏋溿€?
## 蹇€熷紑濮?
```powershell
py generate.py --input data/pages.sample.csv --output generated
```

杈撳嚭椤甸潰浣嶄簬 `generated/YYYY/MM/slug.md`锛屽悓鏃朵細鐢熸垚 `generated/manifest.json`銆?
## CSV 瀛楁

蹇呭～锛歚title`銆乣keyword`銆乣summary`銆乣body`銆?
鍙€夊瓧娈碉細

| 瀛楁 | 浣滅敤 |
|---|---|
| `style` | `guide`銆乣overview` 鎴?`update`锛屽喅瀹氶〉闈㈠竷灞€銆?|
| `source_id` | 鏁版嵁婧愪腑鐨勬案涔呭敮涓€ ID锛涚敤浜庤瘑鍒悓涓€鏉″唴瀹圭殑鏇存柊锛屽己鐑堝缓璁彁渚涖€?|
| `slug` | URL/鏂囦欢鍚嶏紱鐪佺暐鏃舵牴鎹爣棰樼敓鎴愩€?|
| `published_at`銆乣updated_at` | ISO 8601 鏃堕棿锛涚渷鐣ユ椂浣跨敤褰撳墠 UTC 鏃堕棿銆?|
| `image` | 鍥剧墖 HTTPS URL銆?|
| `source_url` | 鍘熷鎴栧畼鏂硅祫鏂?HTTPS URL銆?|
| `cta_label`銆乣cta_url` | 椤甸潰搴曢儴琛屽姩閾炬帴銆?|
| `markers` | 閫楀彿鍒嗛殧鐨勬爣绛炬垨瑕佺偣銆?|
| `news_json` | JSON 鏁扮粍锛屽 `[{"title":"璧勮鏍囬","url":"https://...","summary":"鎽樿"}]`銆?|
| `related_json` | JSON 鏁扮粍锛屾牸寮忓悓 `news_json`锛岀敤浜庣珯鍐呯浉鍏虫帹鑽愩€?|

JSON 瀵煎叆鏃讹紝鏂囦欢椤跺眰鏄〉闈㈠璞℃暟缁勶紝瀛楁鍚嶇浉鍚岋紱`news_json` 涓?`related_json` 鍙互鐩存帴濉啓鏁扮粍銆?
## 瀵煎叆浣犵殑鏁版嵁

澶嶅埗 `data/pages.sample.csv` 涓烘柊鐨?CSV锛屾浛鎹㈠叾涓暟鎹悗鎵ц锛?
```powershell
py generate.py --input data/your-pages.csv --output generated
```

绀轰緥 CSV 宸蹭娇鐢?UTF-8 BOM 缂栫爜锛屽彲鐩存帴鐢?Excel 鎵撳紑銆傜敤 Excel 淇濆瓨鑷繁鐨勬枃浠舵椂锛岃閫夋嫨鈥淐SV UTF-8锛堥€楀彿鍒嗛殧锛夆€濓紝鍚﹀垯涓枃鍙兘鏄剧ず涔辩爜銆?
鐢熸垚鍣ㄤ細鎷掔粷锛氱己澶卞繀濉瓧娈点€侀噸澶?slug銆侀潪 HTTP(S) 閾炬帴銆侀敊璇殑 JSON 鏁扮粍瀛楁銆?
## 闃查噸澶嶇瓥鐣?
姣忔杩愯閮戒細璇诲彇 `generated/manifest.json`锛?
- 鐩稿悓 `source_id` 涓斿唴瀹规湭鍙橈細璺宠繃锛?- 鐩稿悓 `source_id` 浣嗗唴瀹瑰彉鍖栵細鍘熻矾寰勬洿鏂帮紝涓嶆柊寤虹浜岄〉锛?- 涓嶅悓 `source_id` 浣嗗唴瀹规寚绾规垨鏍囬鐩稿悓锛氳烦杩囬噸澶嶉〉锛?- 鍚屼竴浠藉鍏ユ暟鎹唴閲嶅鐨?`source_id`銆佹爣棰樻垨鍐呭锛氬彧淇濈暀棣栨潯銆?
鍐呭鎸囩汗鍩轰簬鍏抽敭璇嶃€佹憳瑕併€佹鏂囥€佸浘鐗囥€佹潵婧愩€丆TA銆佹爣绛俱€佺浉鍏虫柊闂诲拰鐩稿叧鎺ㄨ崘璁＄畻銆傚畠妫€娴嬬殑鏄畬鍏ㄧ浉鍚岀殑鍐呭锛涚浉杩戜絾涓嶅悓鐨勬枃绔犱粛闇€鐢卞鍏ユ暟鎹拰浜哄伐瀹℃牳淇濊瘉璐ㄩ噺銆?
姝ゅ锛屾墍鏈夋柊椤甸潰蹇呴』涓庡唴瀹瑰簱涓凡鏈夐〉闈㈣嚦灏戞湁 **50% 鍐呭宸紓**銆傚樊寮傝绠楀彧浣跨敤椤甸潰鏍囬銆佸叧閿瘝銆佹憳瑕併€佹鏂囥€佹爣绛俱€佺浉鍏宠祫璁拰鐩稿叧鎺ㄨ崘锛屼笉浼氬洜涓烘ā鏉夸腑鐨勫浐瀹氭爣棰樻垨椤佃剼鑰岃鍒ゃ€傚樊寮備笉瓒?50% 鐨勬柊椤甸潰浼氳璺宠繃锛涘悓涓€ `source_id` 鐨勫凡鏈夐〉闈粛浼氬師浣嶆洿鏂般€?
榛樿闃堝€兼槸 `0.50`锛屽彲鎻愰珮瑕佹眰锛屼緥濡傝嚦灏?70% 涓嶅悓锛?
```powershell
py generate.py --input data/your-pages.csv --output generated --min-difference 0.70
```

