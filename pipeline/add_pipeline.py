# add_pipeline.py
from kfp import dsl
from kfp.components import func_to_container_op

# パイプラインのコンポーネントを定義
@func_to_container_op
def add_op(a: float, b: float) -> float:
    """2つの数値を加算する簡単な関数"""
    return a + b

# パイプラインを定義
@dsl.pipeline(
    name="Addition pipeline",
    description="An example pipeline that adds two numbers."
)
def add_pipeline(a: float = 1, b: float = 7):
    # Add task
    add_task = add_op(a, b)

# パイプラインの実行
if __name__ == "__main__":
    import kfp
    # Kubeflow Pipelines のホスト URL に合わせてください
    client = kfp.Client(host="http://localhost:8888")
    client.create_run_from_pipeline_func(add_pipeline, arguments={'a': 3, 'b': 4})
