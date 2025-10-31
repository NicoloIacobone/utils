import wandb
api = wandb.Api()
project = "mapanything-distillation"
old = api.run("nico/mapanything-distillation/run_5_distillation")

new = wandb.init(project=project, name="run_5_distillation_branch25E")
for row in old.history(keys=["epoch","train_loss","val_loss"], pandas=False):
    if "epoch" in row and row["epoch"] <= 25:
        new.log({k: v for k,v in row.items() if not k.startswith("_")})
new.finish()