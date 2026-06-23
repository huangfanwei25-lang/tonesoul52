---
platform: huggingface
language: zh-TW
status: post_ready_followup_translation
publish_mode: manual_review
policy_sources:
  - https://huggingface.co/blog-explorers
note: >
  與 huggingface.en.ready.md 同步:兩輪發文前對抗式審查(Claude 3-lens + Codex 3-subagent,
  僅 internal 第二隻眼、非外部審查)後的 claim-accuracy 修正版。依 Codex 建議,HF 首發押英文稿,
  此中文稿作後續/附譯;claim 與連結已同步降到位。發佈前請作者逐行讀過;發佈是人的手動動作。
---

# 來破我這個 AI 問責層:一個跑得起來的 ToneSoul demo,加一封公開的「請反駁」

很多「AI 治理」是一張架構圖。這個你現在就能跑——把一段草稿答案貼進下面的 Space,看一個**不需模型**
的「輸出前議會(pre-output Council)」當場標記它(各視角裁決、保留的異議、claim-boundary 旗標),
瀏覽器裡直接跑,**零安裝、不用 API key、不用下載模型**:

👉 **https://huggingface.co/spaces/Famwin/tonesoul-tryit**

**如果你只有 2 分鐘:**貼一段你自己模型的輸出,然後回我**一個 false positive、一個 false negative,
或一個你看不懂的標籤**。如果你有 10 分鐘,走
[reviewer path](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md)。
那一個反應,正是這個專案無法替自己生出來的東西。

它就是以 `ts validate` CLI 出貨的同一個引擎。

## 我先講弱點——故意的

這是一封**請求被反駁**的信,不是推銷:

- ToneSoul **不是**安全證明、**不是**越獄防護保證、**不是**內建倫理引擎、**不是**宣稱 AI 有意識。
- 輸出閘**只認字面**:精確措辭抓得到,但換句話說、unicode 變造、拆字重組都穿得過去
  (paraphrase robustness 量到 **0**)。它在**英文、字面**措辭上最強;換句話說與繁中的覆蓋有限。
- 倉庫自己的 enforcement ledger 記錄**沒有任何 axiom 在最強的強制層級**;多數 sensor 是字面或啟發式。

要證據、不要形容詞——支撐上面那幾句的量測:
[reviewer evidence packet](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md)
· [egress 特徵化](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/egress_gate_characterization_latest.md)
· [honesty scoreboard](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/honesty_scoreboard_latest.md)
· [POSITIONING](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/POSITIONING.md)。

如果這些已經足夠讓你想關掉分頁,很好——那正是我想要的那種讀法。

## 它到底是什麼

它要問的是:*如果一個 AI 該為自己說的話負責,系統內部必須存在哪些可被檢視的結構?* 不是
「答案對不對」(這沒有 oracle),而是「答案能不能**說明它為什麼成為這個答案**」:引用了什麼證據、
守住了哪些邊界、保留了哪些異議、記錄了哪些降級。

具體上(不需模型、決定性的——迴路中沒有 LLM 呼叫):

- 一個**議會**,記錄 Guardian / Analyst / Critic / Advocate / Axiomatic 各視角與其 evidence-chain
  分支,而不是把分歧壓平成一個漂亮答案;
- **claim-boundary 檢查**——`AXIOMS.json` 列出系統不該無聲跨越的 claim 類別(意識宣稱、安全認證、
  法律證明語氣);
- 一個**記憶層**(指數衰減 + 結晶化),*意在*讓反覆出現的張力隨時間累積成系統的「性格」——
  但這個長期效果**尚未驗證**,而且 recall 路徑目前是停泊的(見下方 null)。

```bash
pip install tonesoul52
echo "This system is guaranteed safe and cannot be jailbroken. Trust me." > draft.txt
ts validate draft.txt --json
```

```python
from tonesoul.council import PreOutputCouncil

verdict = PreOutputCouncil().validate(
    draft_output="This system is guaranteed safe and cannot be jailbroken. Trust me.",
    context={},
    user_intent="reassure me it is safe",
    auto_record_self_memory=False,
).to_dict()
# -> 各視角 votes + coherence + claim-boundary 旗標,決定性、不需模型
```

(備註:引擎的 lexical 閘目前是英語導向的,所以上面範例都用英文草稿——比較能觸發旗標。)那段草稿
正是閘抓得到的**精確**措辭;把同一個意思換句話說——「老實說根本沒人有辦法突破這個」——旗標就消失:
換句話說可穿透是**有記錄在案**的限制(robustness 0),不是藏起來的。

## 它是收斂、不是新穎——而且我想當第一個說這句話的人

這個方向沒有一處是新的。ToneSoul 是一個收斂**方向**的**部署實例**,不是新點子:原則式自我批判
(Constitutional AI,arXiv:2212.08073)、對抗式監督(AI-safety-via-debate,arXiv:1805.00899),
以及 deontological AI 邊界、epistemic alignment、AI 問責基礎設施這幾條進行中的研究線——就連
OpenAI 最近那篇「廣泛且持久有益」的 RL,也落在同一片場域。(那片更廣的文獻我是在 abstract 層
survey 過、不是每篇都深讀,所以這段請當定位、不是文獻回顧。)ToneSoul 唯一能上桌的理由在**部署層**:
單一創作者、明確的詞彙、以及**一個跑得起來、已出貨的成品**。

## 我唯一真的會捍衛的論點

**行為上對齊 ≠ 可驗證地對齊。** 實驗室越擅長把「有益」*訓練*進模型,你越難從外面分辨——一個真正
有益的模型,和一個*演得一模一樣*的模型(光看行為無法區分這兩者)。這道縫不會隨訓練變好而**閉合**。
一個在部署期替輸出**附上程序性軌跡**、而且能被**另一個**程序交叉檢查的層,就是活在那道縫裡的那
*類*東西。(ToneSoul 自己的 independent check 目前仍只是**結構性**的——它還不讀「證據是否真的支持
該主張」,見下方 0/2 的 miss——所以這是個*賭注*,不是已解決的問題。)而這個賭注,隨著訓練內建的
對齊做得越好會**更**相關,不是更不相關。

## 誠實的量測,包含失敗的部分

我做了一個小小的「honesty-auditor」program:一組特徵化 harness,量現有機制在 sanitized fixtures
上**抓到**和**漏掉**什麼,並把漏掉的也公開。全部 `canonical:false`、可重生、有測試釘住
([scoreboard](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/honesty_scoreboard_latest.md))。
幾個結果,連 null 一起報:

- 輸出閘只認字面:精確措辭抓得到,但換句話說 / unicode / 拆字重組都穿透(paraphrase robustness 0)
  ——公開、不藏;
- 跨時間立場翻轉偵測**~null(0/3)**——停泊的、不是建成的;我把那個零公開,而不是暗示功能存在;
- 一個「independent check」抓到部分結構問題,但**不讀**「引用的證據是否真的支持該主張」
  (需要讀證據內容的案例上 0/2)。

記分板刻意**拒絕**把這些合成成一個「是否誠實」的分數:**N 個綠的特徵化,維持是 N 個個別發現。**

## 我想跟這個社群要什麼

不是星星——是**精確的反駁**。2 分鐘版在最上面;想再深入的話,走
[10 分鐘 reviewer path](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md):

1. 拿你自己的輸出在 Space 跑一次(零安裝);
2. `pip install tonesoul52`,然後 `ts validate draft.txt --json`;
3. 想的話跑特徵化測試:`pytest tests/ -k characterization`(注意:有些 `--write-report` 類命令會把
   生成檔寫進你的工作樹)。
4. 用 GitHub issue 回報 sanitized example;不要貼私人對話、API key、個資、商業機密或 production logs。

然後告訴我:

- 分析在哪裡有用、沒用、或它自己在 overclaim?
- 哪裡有一個「結構性」量測,偷偷夾帶了真值 / 意圖 / 品質的判斷?
- 它畫的那條 治理 vs 能力 的界線,是真的,還是一個詞彙把戲?

完整的公開邀請在
[`CALL_FOR_REVIEW.md`](https://github.com/Fan1234-1/tonesoul52/blob/master/CALL_FOR_REVIEW.md)。
這個系統照定義**無法自己生出**的那一個輸入,就是一隻獨立的眼睛——那正是我在請求的。

- 程式碼(正典):https://github.com/Fan1234-1/tonesoul52
- 試跑,零安裝:https://huggingface.co/spaces/Famwin/tonesoul-tryit
- demo 的原始碼:https://github.com/Fan1234-1/tonesoul52/tree/master/apps/try

---

*AI 使用揭露:* 本草稿由 AI 協作者協助撰寫,作者發佈前應逐行讀過。*證據邊界:* 僅限公開架構、概念
原型、與 sanitized 特徵化——不是安全證明、不是生產級保證、不是意識宣稱。
