library(lme4)
table <- read.csv(file="/work/research/symper/analysis/symper_results.csv") 
#model <- lmer(accuracy ~ rot_same + ref_same + gref_same + tile_same + (1|user_id) + (1|task_id) + distance, data = table)
model <- lmer(accuracy ~ ref_same + gref_same + tile_same + rot_same + distance + (1|user_id) + (1|task_id), data=table)
