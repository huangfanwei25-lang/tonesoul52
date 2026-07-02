---
name: fanwei-voice-essays
description: 把倉庫裡的故事/機制/教訓寫成梵威聲音的長文,發佈到個人網站 /essays/。Use when the owner asks for 文章 / 寫一篇 / essays / 用我的語境寫 / turning repo material or his local writings into publishable articles. Voice studied from his vocus articles (2026-07-03); publishing pipeline: docs/essays/NNN_*.md → tools/essays_page/generate.py → site/essays/ (Pages publishes on merge).
---

# 梵威聲音文章(fanwei-voice-essays)

目標:寫出**不像 AI 寫的**文章——不是藏 AI 參與(協作署名照掛),是去掉 AI 腔。

## 聲音側寫(從 vocus 十篇實文研究而來,2026-07-03)

- **開場直球反轉**:「這不是要勸你 X。正好相反——」先拆自己的預設,再進正題。
- **比喻要有手感,然後自己拆穿**:橡皮筋、子宮、驗屍——具體物件;用完立刻承認
  「這是修辭,不是事實/統計」。比喻是梯子,爬上去就踢掉。
- **讀者是驗證同夥,不是聽眾**:「不用信我,去跑程式碼」「你跑的是哪一組」。
  第二人稱直呼,假設讀者有技術素養。
- **誠實分層,越說越難聽**:好答案給三層,最後一層是對自己最不利的那層。
- **結尾邀打**:「進倉庫,挑我最薄弱的地方打。」把脆弱性擺成邀請。
- **標題要挑釁但兌現**:標題的火藥,內文必須真的引爆,不許標題黨。

## 去 AI 腔規則(每篇檢查)

- 禁:「總而言之」「值得注意的是」「綜上所述」、三點式排比開頭、每段等長。
- 段落長短要呼吸:一句話的段落是允許的。是武器。
- 條列只在「驗屍清點」這類真的在數東西的地方用;論證用散文。
- 承認具體的狼狽(「你讀到這裡可能會笑。我現在也會。」),不用抽象謙虛。
- 中文為主;英文術語只留真的沒有好譯名的。

## 素材紀律

- **可用**:梵威署名的 vocus 文章、Genesis/AI-Ethics 封存倉的他的原文(txt/codex 卷)、
  docs/OUTLOOK.md、docs/philosophy/ 中他的聲音的部分、對話中他說過的話。
- **辨識法**:他的筆跡=繁中第一人稱、有狼狽的自嘲、句式不對稱;AI 腔=條列整齊、
  disclaimer 密集、對仗工整。**分不清就不用,或問他。**
- 涉及倉庫的**事實宣稱**必須可驗證(file/commit/PR 可指);內部用 E-tag 檢查,
  頁面上寫白話。
- 不宣稱意識、不給安全/法律/投資背書(meta.not_for 照舊)。

## 結構模板

1. 直球反轉開場(≤3 行)
2. 故事本體(時間、人、狼狽的細節)
3. 誠實分層(「誠實的答案有 N 層,一層比一層難聽」)
4. **語魂結構標註**框:本文講的東西在系統哪裡——路徑+一句白話,開頭固定
   「(不用信我,去跑)」
5. 邀打收尾
6. 署名:`*梵威(與嶼協作整理)· YYYY-MM*`(協作不藏)

## 發佈管線

```
docs/essays/NNN_slug.md → python tools/essays_page/generate.py → site/essays/index.html
→ PR → merge = Pages 發佈
```

編號遞增;發佈前 owner 過目一次聲音像不像(他說哪裡不像,調哪裡——聲音的
最終裁判永遠是他本人)。

## 誠實限制

模仿的是**文風**,不是他的判斷——文章裡的立場必須是他真的持有過的
(有 vocus/對話/倉庫紀錄可對),不得替他發明觀點。拿不準的立場:問。
