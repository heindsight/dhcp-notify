def prune_config(cfg, *exclude):
    return {key: value for key, value in cfg.items() if key not in exclude}
