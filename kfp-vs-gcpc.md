---

# Kubeflow Pipelines（KFP）と Google Cloud Pipeline Components（GCPC）の関係およびバージョン互換・API変更点報告書

## 1. 概要

本書では、Kubeflow Pipelines（以下、KFP）および Google Cloud Pipeline Components（以下、GCPC）の関係、役割分担、バージョン互換性、および v1 → v2 移行時の主要API変更点について整理する。

---

## 2. 全体構成のイメージ

```
┌─────────────────────────────┐
│       Kubeflow Pipelines (KFP)       │ ← パイプライン実行基盤・DSL
│ ┌─────────────────────────┐ │
│ │  Google Cloud Pipeline Components │ │ ← GCP専用コンポーネント群
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

* **KFP** はワークフローを定義・実行・管理する「パイプライン基盤」
* **GCPC** は Vertex AI・BigQuery・Dataflow などの GCP サービスを呼び出す「部品群」

---

## 3. 役割の比較

| 項目          | Kubeflow Pipelines (KFP)      | Google Cloud Pipeline Components (GCPC)        |
| ----------- | ----------------------------- | ---------------------------------------------- |
| 立ち位置        | パイプライン基盤（ワークフローエンジン）          | GCP サービスと連携するコンポーネント群                          |
| 主な役割        | パイプライン定義、DSL提供、実行管理           | Vertex AI / BigQuery / Dataflow などの呼び出し        |
| インストールパッケージ | `pip install kfp`             | `pip install google-cloud-pipeline-components` |
| 提供元         | Kubeflow OSS コミュニティ           | Google Cloud                                   |
| 実行環境        | OSS KFP / Vertex AI Pipelines | Vertex AI Pipelines（推奨）                        |
| 更新頻度        | OSSベース（安定重視）                  | GCPサービス更新に応じて頻繁                                |
| 関係          | GCPC は KFP 上で動作               | KFP の DSL 内で GCPC の部品を利用                       |

---

## 4. 実際の使用例

```python
from kfp import dsl
from google_cloud_pipeline_components import aiplatform as gcc_aip

@dsl.pipeline(name="sample-pipeline")
def my_pipeline():
    # Vertex AI の学習ジョブを実行する GCPC コンポーネント
    train_op = gcc_aip.CustomPythonPackageTrainingJobRunOp(
        project="my-project",
        display_name="train-job",
        python_package_gcs_uri="gs://my-bucket/train.tar.gz",
        python_module="trainer.task",
        container_uri="us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-13:latest"
    )
```

* `@dsl.pipeline`、`dsl.Condition` 等 → **KFP（DSL）** が提供
* `CustomPythonPackageTrainingJobRunOp` → **GCPC** が提供

---

## 5. バージョン互換性（2025年時点）

| 項目       | 安定ペア（推奨）                                                             | 備考                         |
| -------- | -------------------------------------------------------------------- | -------------------------- |
| **KFP**  | 2.10.1                                                               | DSL仕様が安定しており、v1コードからの移行も容易 |
| **GCPC** | 2.19.0                                                               | urllib3 v1系対応の最終安定版        |
| **注意点**  | GCPC 2.20.0 以降では `urllib3.method_whitelist` の削除に伴う互換性問題が発生           |                            |
| **総評**   | `kfp==2.10.1` + `google-cloud-pipeline-components==2.19.0` の組み合わせが最適 |                            |

---

## 6. API変更点比較（v1 → v2）

| 分類        | v1 系（旧）                                                   | v2 系（新）                                      | 主な変更点                     |
| --------- | --------------------------------------------------------- | -------------------------------------------- | ------------------------- |
| DSL インポート | `from kfp.v2 import dsl`                                  | `from kfp import dsl`                        | 名前空間が統一化。`.v2` が廃止        |
| コンポーネント呼出 | `dsl.ContainerOp(...)`                                    | `@dsl.component` デコレータを使用                    | `ContainerOp` は非推奨化       |
| パラメータ定義   | `dsl.InputArgumentPath`                                   | `dsl.Input`, `dsl.Output`                    | 型ヒントによる I/O 定義に移行         |
| 条件分岐      | `dsl.Condition(...)`                                      | `with dsl.If(condition=...):`                | Python の構文に近い書き方へ統一       |
| パイプライン登録  | `kfp.v2.compiler.Compiler().compile(...)`                 | `kfp.compiler.Compiler().compile(...)`       | 名前空間変更                    |
| 実行管理      | `client.create_run_from_job_spec(...)`                    | `client.create_run_from_job_spec(...)`（同名維持） | 引数の一部変更（runtime_config 等） |
| Vertex 連携 | `from google_cloud_pipeline_components import aiplatform` | 同左                                           | モジュール構造は維持、依存ライブラリ更新      |

---

## 7. コード移行時の注意点

1. **import構文の変更**

   ```python
   # v1 系（旧）
   from kfp.v2 import dsl

   # v2 系（新）
   from kfp import dsl
   ```

2. **DSLの記法変更**

   * `dsl.ContainerOp` → `@dsl.component`
   * `dsl.Input/Output` による型注釈必須
   * 例：

   ```python
   @dsl.component
   def preprocess(data: dsl.InputPath(str), output_data: dsl.OutputPath(str)):
       ...
   ```

3. **パラメータやI/O型の明示**

   * パイプライン間でのデータ受け渡しは `dsl.Output` → `dsl.Input` を明示的に宣言

4. **Cloud上での互換性**

   * Vertex AI Pipelines では KFP v2 構文のみサポート（旧記法不可）

---

## 8. 推奨構成まとめ

| 項目          | 推奨設定値                            | 理由                                           |
| ----------- | -------------------------------- | -------------------------------------------- |
| Python      | 3.12 系                           | Vertex AI Pipelines, Dataproc Serverless と整合 |
| KFP         | 2.10.1                           | v2 DSL 構文の安定版                                |
| GCPC        | 2.19.0                           | urllib3 v1系互換・Vertex AI実績多数                  |
| import構文    | `from kfp import dsl`            | v2準拠                                         |
| コンポーネント呼び出し | `gcc_aip.<ComponentName>Op(...)` | 最新GCPCに統一                                    |

---

## 9. まとめ

* **KFP** は「パイプライン基盤」、**GCPC** はその上で動作する「GCP専用コンポーネント群」である。
* 両者は密接に依存しており、**バージョンの整合性が非常に重要**。
* 旧記法（`from kfp.v2 import dsl`）は v2.x では非対応となるため、**コード側の修正が必須**。
* 現時点では、以下の組み合わせが最も安定：

  ```
  kfp = "2.10.1"
  google-cloud-pipeline-components = "2.19.0"
  ```
* 今後 Vertex AI Pipelines の完全移行を見据え、v2構文への統一を早期に完了させることを推奨する。

---

