def norm_scheme_adjust(game_params, q):
    """根据上一轮的结果调整“常人”玩家的选择概率。"""
    if q == 1:
        ans_list = game_params.ans_list
        crowds_ans = game_params.crowds_ans
        score_list = game_params.score_list
        is_communicate = game_params.is_communicate
        iter = game_params.iter
        pList = game_params.pList
        LEARN_RATE_UP = game_params.LEARN_RATE_UP
        LEARN_RATE_DOWN = game_params.LEARN_RATE_DOWN
        SOLID_VALUE = game_params.SOLID_VALUE

        # 增加选择收益最高选项的概率
        if 4 not in ans_list:  # 没有人选择“勇气”？冲！
            pList[4] = pList[4] * LEARN_RATE_UP
        else:
            best_option = crowds_ans[score_list.index(max(score_list))]
            pList[best_option] *= LEARN_RATE_UP
        # 如果当前选项收益最低，降低此选项的概率
        worst_option = crowds_ans[score_list.index(min(score_list))]
        pList[worst_option] /= LEARN_RATE_DOWN

        # 如果“智慧”缺乏，冲！
        if ans_list.index(min(ans_list)) == 3 or ans_list[3] == 0:
            pList[3] = pList[3] * LEARN_RATE_UP
        else:
            pList[3] = pList[3] / LEARN_RATE_DOWN

        # 如果上一轮“团结”成功，继续增加选择“团结”的概率
        if ans_list.index(min(ans_list)) == 2:
            pList[2] = pList[3] * LEARN_RATE_UP

        # 信息交流
        if is_communicate:
            # 每过一定轮次，有人呼吁要“团结”！
            if iter % 20 == 0:
                if ans_list[2] == 0:
                    pList[2] *= LEARN_RATE_UP  # 当有人呼吁“团结”，但上一轮没有人选择“团结”的时候
                else:  # 正反馈调节
                    pList[2] = pList[2] * max(ans_list) / ans_list[2] * SOLID_VALUE  # 呼吁“团结”时的反应（可以根据需要进行更改，可能会产生意想不到的结果）

        #归一化plist
        return [i / sum(pList) for i in pList]
