import os
from datetime import datetime

def log_debug_info(tool_brief, system_prompt, user_prompt, llm_reply, prefix="llm_debug"):
    # ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # date_str = datetime.now().strftime("%Y%m%d")
    # folder = "llm_debug_logs"
    # os.makedirs(folder, exist_ok=True)
    # # 將所有欄位組成一行純文字
    # log_line = f"[{ts}] [{prefix}]\nTOOL_BRIEF: {str(tool_brief)}\nSYSTEM_PROMPT: {str(system_prompt)}\nUSER_PROMPT: {str(user_prompt)}\nLLM_REPLY: {str(llm_reply)}\n{'-'*60}\n"
    # log_file = f"{folder}/{prefix}_{date_str}.txt"
    # with open(log_file, "a", encoding="utf-8") as f:
    #     f.write(log_line) 

    # 先關閉，有必要時再開啟
    pass
