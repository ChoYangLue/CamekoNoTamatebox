# KASANE — GIMP多重露光プラグイン

GIMP 3.xで、選択した2〜5個のレイヤーを非破壊で多重露光合成します。

## インストール

`kasane-multiple-exposure`フォルダーを、GIMPのユーザープラグインフォルダーへコピーします。フォルダー名とPythonファイル名（拡張子を除く）は同じにしてください。

### Windows

通常は次の場所です。

```text
%APPDATA%\GIMP\3.0\plug-ins\kasane-multiple-exposure\kasane-multiple-exposure.py
```

同梱の`install-windows.ps1`をPowerShellで実行すると自動でコピーできます。

### Linux

```text
~/.config/GIMP/3.0/plug-ins/kasane-multiple-exposure/kasane-multiple-exposure.py
```

Pythonファイルに実行権限を付けてください。

```sh
chmod u+x kasane-multiple-exposure.py
```

インストール後、GIMPを再起動します。

## 使い方

1. 合成したい写真を同じ画像内のレイヤーとして読み込みます。
2. レイヤーパネルで2〜5個のレイヤーを複数選択します。
3. `フィルター` → `合成` → `KASANE — 多重露光…`を実行します。
4. 重なり方と濃度を選び、`OK`を押します。

結果は`KASANE — 多重露光`グループに作成されます。元レイヤーは削除されず、初期設定では非表示になります。操作全体は1回の「元に戻す」で取り消せます。

## 合成方法

- **スクリーン**: 明部を重ね、明るく幻想的に仕上げます。
- **比較（明）**: 各位置で明るい方を採用し、光跡や星空に適します。
- **平均**: 全レイヤーを等しい比率で混ぜ、自然になじませます。
- **乗算**: 暗部や質感を強調します。

## 動作要件

- GIMP 3.0以降
- RGBまたはグレースケール画像

GIMP 2.10ではAPIが異なるため動作しません。
