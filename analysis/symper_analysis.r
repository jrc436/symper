library(lme4)
table <- read.csv(file="/work/research/symper/analysis/symper_results.csv")
table_rot <- read.csv(file="/work/research/symper/analysis/symper_rot_results.csv")
table_refl <- read.csv(file="/work/research/symper/analysis/symper_ref_results.csv")
model_summary <- glmer(accuracy ~ rot_same + ref_same + gref_same + tile_same + (1|user_id) + (1|task_id) + distance, data = table, family=binomial)
model_distance <- glmer(accuracy ~ distance + (1|user_id) + (1|task_id), data=table, family=binomial)
model_rot <- glmer(accuracy ~ same2fold + same3fold + same4fold + same6fold + (1|user_id) + (1|task_id), data=table_rot, family=binomial)
model_ref <- glmer(accuracy ~ T1_same + T2_same + D1_same + D2_same + (1|user_id) + (1|task_id), data=table_refl, family=binomial)

