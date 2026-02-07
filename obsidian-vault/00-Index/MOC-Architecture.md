---
title: 架構概覽
aliases: [MOC Architecture, 架構地圖]
tags: [moc, architecture, index]
---

# 架構概覽 (MOC)

> ToneSoul 的三層架構設計

---

## 🏗️ 三層架構

```
┌─────────────────────────────────────────┐
│           APPLICATION LAYER             │
│  apps/, integrations/, tools/           │
├─────────────────────────────────────────┤
│           GOVERNANCE LAYER              │
│  tonesoul/ (核心邏輯)                   │
├─────────────────────────────────────────┤
│         INFRASTRUCTURE LAYER            │
│  memory/, gateway/, law/                │
└─────────────────────────────────────────┘
```

---

## 🧠 核心模組

| 模組 | 說明 |
|------|------|
| [[Council]] | 多視角審議系統 |
| [[Genesis]] | 責任追蹤 |
| [[Benevolence]] | 仁慈函數 |
| [[VTP]] | 終止協議 |

---

## 🛡️ 治理機制

| 機制 | 說明 |
|------|------|
| [[7D-Framework]] | 七維審計 |
| [[Axioms]] | 核心公理 |
| [[Responsibility-Tier]] | 責任層級 |

---

## 📜 協議

| 協議 | 說明 |
|------|------|
| [[VTP-Spec]] | 終止協議規格 |
| [[Honesty-Mechanism]] | 誠實機制 |
| [[Systemic-Betrayal]] | 背叛防護 |

---

## 🗺️ 視覺地圖

參見 Canvas: `Canvas/Architecture-Overview.canvas`
