from src.cfg import CFG
from src.cky import CKY
from src.functions import split_input, dynamic_round

racso_id = 34
text = open(f"./tests/racso_cfg_det{racso_id}.txt", "r").read()

cfg = CFG(from_text=text)

print(cfg.generate_words(3, round_probabilities=True))


