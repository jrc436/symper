library(lme4)
table <- read.csv(file="C:/work/home/sym-perception/analysis/symper_results.csv") 
model <- lmer(accuracy ~ rot_same + ref_same + gref_same + tile_same + (1|user_id) + (1|task_id) + distance, data = table)
