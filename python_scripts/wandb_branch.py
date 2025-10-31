import wandb
api = wandb.Api()
project = "mapanything-distillation"
# old = api.run("nico/mapanything-distillation/run_5_distillation")
old = api.run("nicolo-iacobone-politecnico-di-torino/mapanything-distillation/cea70w6j")

new = wandb.init(project=project, name="run_5_distillation_branch25E")
def _flatten_metrics(obj, parent_key='', sep='/'):
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith('_'):
                continue
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(_flatten_metrics(v, new_key, sep=sep))
            elif isinstance(v, (list, tuple)):
                for i, elem in enumerate(v):
                    items.update(_flatten_metrics(elem, f"{new_key}{sep}{i}", sep=sep))
            else:
                items[new_key] = v
    else:
        items[parent_key] = obj
    return items

for row in old.history(pandas=False):
    if "epoch" in row and row["epoch"] <= 25:
        metrics = _flatten_metrics(row)
        # ensure epoch exists at top level
        metrics.setdefault("epoch", row.get("epoch"))
        new.log(metrics)
new.finish()