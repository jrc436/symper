library(lme4)
library(LMERConvenienceFunctions)
symper_data <- read.csv(file="/work/research/symper/analysis/fullresults.csv")
#model_summary <- glmer(correct ~ rot_same + ref_same + gref_same + tile_same + (1|user_id) + (1|task_id) + distance, data = symper_data, family=binomial)
#model_distance <- glmer(correct ~ distance + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_rot <- glmer(correct ~ same2fold + same3fold + same4fold + same6fold + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_ref <- glmer(correct ~ T1_same + T2_same + D1_same + D2_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test <- glmer(correct ~ D1_same + distance + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_tile <- glmer(correct ~ tile_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test2 <- glmer(correct ~ tile_same + distance + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test3 <- glmer(correct ~ tile_same + distance + D1_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_D1 <- model_tile <- glmer(correct ~ D1_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test4 <- glmer(correct ~ tile_same + distance + D1_same + same3fold + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test5 <- glmer(correct ~ tile_same + distance + D1_same + T1_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test6 <- glmer(correct ~ tile_same + distance + D1_same + T1_same + same3fold + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test7 <- glmer(correct ~ tile_same + distance + D1_same + T1_same + same3fold + same2fold + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
#model_test8 <- glmer(correct ~ distance + D1_same + same3fold + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
model_features <- glmer(correct ~ T1_same + T2_same + D1_same + D2_same +  same2fold + same3fold + same4fold + same6fold + tile_same + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
model_distance <- glmer(correct ~ distance, + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
model_to_fit <- glmer(correct ~ T1_same + T2_same + D1_same + D2_same +  same2fold + same3fold + same4fold + same6fold + tile_same + distance + (1|user_id) + (1|task_id), data=symper_data, family=binomial)
model_converged <- bfFixefLMER_t.fnc(model_to_fit, method="AIC")